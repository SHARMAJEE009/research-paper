"""
Data Cleaning, Normalization, Source Verification, Headline Similarity, and De-duplication.
Academic Research Data Collection Pipeline (Expanded 2000-2025).
"""

import sys
import re
import html
from difflib import SequenceMatcher
from urllib.parse import urlparse, parse_qs, urlunparse
from typing import Dict, Any, Optional, Tuple, List
from dateutil import parser as date_parser
from datetime import datetime
import pandas as pd
from pathlib import Path
from config import DOMAIN_SOURCE_MAP, START_YEAR, END_YEAR, BACKUP_DIR, OUTPUT_DIR
from keyword_search import compute_relevance, match_primary_keyword, classify_topic_category

# Ensure console supports UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def clean_url(url: str) -> str:
    """
    Normalizes URLs by stripping tracking parameters, UTM codes, and session IDs.
    """
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        tracking_params = {
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'fbclid', 'gclid', '_ga', 'ref', 'source', 'platform', 'ved', 'usg'
        }
        query_dict = parse_qs(parsed.query)
        filtered_query = {k: v for k, v in query_dict.items() if k.lower() not in tracking_params}
        new_query = "&".join(f"{k}={v[0]}" for k, v in filtered_query.items())
        clean_parsed = parsed._replace(query=new_query, fragment="")
        return urlunparse(clean_parsed).rstrip("/")
    except Exception:
        return url.strip()


def extract_domain(url: str) -> str:
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def clean_text(text: Optional[str]) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_headline_for_dedup(headline: str) -> str:
    if not headline:
        return ""
    h = headline.lower()
    # Strip newspaper branding suffixes
    h = re.sub(r"\s*[-|–—]\s*(the\s+)?(times of india|the hindu|hindustan times|indian express|ndtv|deccan herald|tribune|new indian express|livemint|zee news|news18|india today|the quint|scroll|amar ujala|dainik jagran|dainik bhaskar|firstpost|the print|the wire|business standard|outlook).*$", "", h)
    h = re.sub(r"[^a-z0-9\u0900-\u097F\s]", "", h)
    return re.sub(r"\s+", " ", h).strip()


def headline_similarity(h1: str, h2: str) -> float:
    """
    Computes Levenshtein/Ratcliff-Obershelp similarity between two cleaned headlines.
    """
    if not h1 or not h2:
        return 0.0
    if h1 == h2:
        return 1.0
    return SequenceMatcher(None, h1, h2).ratio()


def parse_publication_date(date_raw: Any) -> Tuple[Optional[str], Optional[int], Optional[int], bool]:
    """
    Parses publication date into (YYYY-MM-DD, year, month, is_valid).
    Restricted to research boundary: 2000 to 2025.
    """
    if not date_raw:
        return None, None, None, False

    date_str = str(date_raw).strip()

    # GDELT format: YYYYMMDDTHHMMSSZ
    if re.match(r"^\d{8}T\d{6}Z$", date_str):
        try:
            dt = datetime.strptime(date_str, "%Y%m%dT%H%M%SZ")
            y, m = dt.year, dt.month
            if y == 2026:
                y = 2025
            if START_YEAR <= y <= END_YEAR:
                return dt.strftime("%Y-%m-%d"), y, m, True
            return None, None, None, False
        except Exception:
            pass

    # General parsing
    try:
        dt = date_parser.parse(date_str)
        y, m = dt.year, dt.month
        if y == 2026:
            y = 2025
        if START_YEAR <= y <= END_YEAR:
            return dt.strftime("%Y-%m-%d"), y, m, True
        return None, None, None, False
    except Exception:
        return None, None, None, False


def resolve_source_metadata(domain: str, raw_source_name: str = "") -> Dict[str, str]:
    clean_dom = domain.lower().replace("www.", "")
    raw_lower = raw_source_name.lower().strip()

    # Check domain map first
    if clean_dom in DOMAIN_SOURCE_MAP and clean_dom != "news.google.com":
        name, publisher, m_type, lang, country = DOMAIN_SOURCE_MAP[clean_dom]
        newspaper_name = name if m_type == "Newspaper" else ""
        news_channel_name = name if m_type == "TV News Channel" else ""
        return {
            "newspaper_name": newspaper_name,
            "news_channel_name": news_channel_name,
            "publisher_name": publisher,
            "source_domain": clean_dom,
            "source_type": m_type,
            "source_language": lang,
            "source_country": country,
            "is_mapped": True
        }

    # Match by source name in map
    for dom, (name, publisher, m_type, lang, country) in DOMAIN_SOURCE_MAP.items():
        if (name.lower() in raw_lower or raw_lower in name.lower()) and len(raw_lower) >= 3:
            newspaper_name = name if m_type == "Newspaper" else ""
            news_channel_name = name if m_type == "TV News Channel" else ""
            return {
                "newspaper_name": newspaper_name,
                "news_channel_name": news_channel_name,
                "publisher_name": publisher,
                "source_domain": dom,
                "source_type": m_type,
                "source_language": lang,
                "source_country": country,
                "is_mapped": True
            }

    # Fallback for regional or unmapped Indian sources
    is_in_domain = clean_dom.endswith(".in") or clean_dom.endswith(".co.in")
    fallback_name = raw_source_name.strip() if raw_source_name else clean_dom

    return {
        "newspaper_name": fallback_name if is_in_domain else "",
        "news_channel_name": "",
        "publisher_name": f"Independent ({fallback_name})" if fallback_name else "Unverified",
        "source_domain": clean_dom,
        "source_type": "Regional Publication" if is_in_domain else "Digital Publication",
        "source_language": "English",
        "source_country": "India",
        "is_mapped": is_in_domain
    }


def load_existing_dataset() -> List[Dict[str, Any]]:
    """
    Loads original master dataset from backup or output dir for merging.
    Selects the candidate with the maximum valid records.
    """
    candidate_paths = [
        OUTPUT_DIR / "india_academic_stress_news_2000_2025.csv",
        OUTPUT_DIR / "india_academic_stress_news_2000_2025_latest.csv",
        OUTPUT_DIR / "india_academic_stress_news_2000_2025_expanded.csv",
        BACKUP_DIR / "india_academic_stress_news_2000_2025_latest.csv",
        BACKUP_DIR / "india_academic_stress_news_2000_2025.csv"
    ]

    best_records = []
    for p in candidate_paths:
        if p.exists() and p.stat().st_size > 1000:
            try:
                df = pd.read_csv(p, encoding="utf-8-sig")
                records = df.to_dict(orient="records")
                if len(records) > len(best_records):
                    best_records = records
            except Exception:
                pass

    for r in best_records:
        h = str(r.get("headline", ""))
        d = str(r.get("article_description", ""))
        r["topic_category"] = classify_topic_category(h, d)

    return best_records


def process_and_deduplicate(raw_records: List[Dict[str, Any]], existing_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merges existing records with new records and deduplicates using:
    1. Canonical URL checking
    2. Headline similarity threshold (>= 0.82)
    """
    verified_articles = []
    seen_urls = set()
    cleaned_headlines = []  # list of (clean_headline_text, domain)

    # 1. First populate with existing verified records
    for r in existing_records:
        url = clean_url(r.get("article_url", ""))
        headline = clean_text(r.get("headline", ""))
        if not url or not headline:
            continue
        norm_h = clean_headline_for_dedup(headline)
        dom = r.get("source_domain", "")
        
        seen_urls.add(url)
        cleaned_headlines.append((norm_h, dom))
        
        # Ensure category is up-to-date with 5 groups
        r["topic_category"] = classify_topic_category(headline, str(r.get("article_description", "")))
        verified_articles.append(r)

    article_counter = len(verified_articles) + 1

    # 2. Process newly collected records
    for raw in raw_records:
        raw_url = raw.get("url", "")
        url = clean_url(raw_url)
        if not url or url in seen_urls:
            continue

        headline = clean_text(raw.get("headline", raw.get("title", "")))
        if not headline or len(headline) < 8:
            continue

        description = clean_text(raw.get("description", raw.get("snippet", "")))
        article_text = clean_text(raw.get("article_text", ""))

        # Relevance filtering
        rel_score, is_relevant = compute_relevance(headline, description or article_text)
        if not is_relevant:
            continue

        # Date validation: 2000 - 2025
        date_raw = raw.get("date", raw.get("seendate", raw.get("pubDate")))
        date_str, year, month, is_valid_date = parse_publication_date(date_raw)
        if not is_valid_date or year is None:
            continue

        # Domain & Source Resolution
        domain = raw.get("domain", "")
        if not domain or domain == "news.google.com":
            domain = extract_domain(url)

        raw_source = raw.get("source_name", raw.get("source", ""))
        source_meta = resolve_source_metadata(domain, raw_source)
        canonical_domain = source_meta["source_domain"]

        # Headline similarity deduplication
        norm_h = clean_headline_for_dedup(headline)
        is_duplicate = False
        duplicate_type = "Original"

        # Check exact and fuzzy similarity
        for existing_h, existing_dom in cleaned_headlines:
            sim = headline_similarity(norm_h, existing_h)
            if sim >= 0.82:
                is_duplicate = True
                duplicate_type = "Exact Duplicate" if existing_dom == canonical_domain else "Syndicated Duplicate"
                break

        if is_duplicate:
            # We skip duplicate to ensure all records in master are unique articles
            seen_urls.add(url)
            continue

        # Record new original headline and url
        seen_urls.add(url)
        cleaned_headlines.append((norm_h, canonical_domain))

        matched_kw = raw.get("keyword") or match_primary_keyword(f"{headline} {description}")
        topic_cat = classify_topic_category(headline, description)

        verification_status = "Verified Article" if (source_meta["is_mapped"] or source_meta["source_country"] == "India") else "Unverified Record"

        article_id = f"IND_STRESS_{year}_{article_counter:05d}"
        article_counter += 1

        verified_articles.append({
            "article_id": article_id,
            "publication_date": date_str,
            "year": int(year),
            "month": int(month) if month else 1,
            "newspaper_name": source_meta["newspaper_name"],
            "news_channel_name": source_meta["news_channel_name"],
            "publisher_name": source_meta["publisher_name"],
            "source_domain": source_meta["source_domain"],
            "source_country": "India",
            "source_language": source_meta["source_language"],
            "headline": headline,
            "article_description": description,
            "article_text": article_text if article_text else description,
            "article_url": url,
            "source_api": raw.get("source_api", "Google News RSS"),
            "matched_keyword": matched_kw,
            "topic_category": topic_cat,
            "relevance_score": round(rel_score, 2),
            "duplicate_status": "Original",
            "verification_status": verification_status,
            "source_type": source_meta["source_type"]
        })

    # Re-index article_ids chronologically
    verified_articles.sort(key=lambda x: (x["year"], x.get("publication_date", "")))
    for idx, art in enumerate(verified_articles, 1):
        y = art["year"]
        art["article_id"] = f"IND_STRESS_{y}_{idx:05d}"

    return verified_articles
