"""
Data Collection Engine for Indian Academic Stress News (Expanded 2000-2025).
Supports 5 Keyword Groups:
1. Competitive Exams & Coaching
2. Student Mental Health
3. Family & Parental Pressure
4. Economic & Social Pressure
5. Hindi Keywords

Harvests from:
- GDELT Project 2.0 Doc API
- Google News RSS Search
- Bing News RSS Search
- Indian Publisher Direct Feeds & APIs (The Hindu, Indian Express, Hindustan Times, TOI, The Quint)
- Media Cloud API

Generates comprehensive search_log.csv documenting queries, date ranges, and yield.
"""

import sys
import time
import logging
import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote, quote
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from pathlib import Path

from config import (
    DEFAULT_HEADERS,
    GOOGLE_NEWS_DELAY,
    GDELT_RATE_LIMIT_DELAY,
    REQUEST_TIMEOUT,
    MEDIACLOUD_API_KEY,
    ALL_YEARS,
    LOG_FILE,
    SEARCH_LOG_FILE,
    DOMAIN_SOURCE_MAP
)
from keyword_search import (
    build_grouped_gdelt_queries,
    build_broad_topic_queries,
    build_yearly_topic_queries,
    build_publisher_queries
)

# Ensure console supports UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("DataCollection")
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(fh)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(sh)


def extract_netloc(url: str) -> str:
    if not url:
        return ""
    try:
        p = urlparse(url)
        netloc = p.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc
    except Exception:
        return ""


def extract_canonical_from_bing(link: str) -> str:
    """Extracts actual destination publisher URL from Bing RSS redirect link."""
    if not link:
        return ""
    try:
        parsed = urlparse(link)
        qs = parse_qs(parsed.query)
        if "url" in qs:
            return unquote(qs["url"][0])
        return link
    except Exception:
        return link


class SearchLogger:
    """Tracks every query executed and exports search_log.csv"""
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
        self.counter = 1

    def log_query(self, source_api: str, query_string: str, target_category: str,
                  date_range: str, records_retrieved: int):
        self.logs.append({
            "query_id": f"QRY_{self.counter:04d}",
            "source_api": source_api,
            "query_string": query_string,
            "target_category": target_category,
            "date_range": date_range,
            "records_retrieved": records_retrieved,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.counter += 1

    def export(self, filepath: Path):
        df = pd.DataFrame(self.logs)
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        logger.info(f"Saved search log: {filepath.name} ({len(df)} queries recorded)")


class GDELTCollector:
    """Client for GDELT 2.0 Doc API with rate limiting and retry."""
    ENDPOINT = "https://api.gdeltproject.org/api/v2/doc/doc"

    def __init__(self, search_logger: SearchLogger):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.last_request = 0.0
        self.search_logger = search_logger

    def query_artlist(self, query: str, category: str, max_records: int = 100) -> List[Dict[str, Any]]:
        elapsed = time.time() - self.last_request
        if elapsed < GDELT_RATE_LIMIT_DELAY:
            time.sleep(GDELT_RATE_LIMIT_DELAY - elapsed)
        self.last_request = time.time()

        params = {
            "query": query,
            "mode": "artlist",
            "maxrecords": str(max_records),
            "format": "json"
        }
        retrieved_count = 0
        try:
            logger.info(f"GDELT request: query='{query[:65]}...'")
            resp = self.session.get(self.ENDPOINT, params=params, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                articles = data.get("articles", [])
                retrieved_count = len(articles)
                logger.info(f"GDELT returned {retrieved_count} articles.")
                self.search_logger.log_query("GDELT Project API v2", query, category, "2017-2025", retrieved_count)
                return articles
            elif resp.status_code == 429:
                logger.warning("GDELT Rate Limit (429). Sleeping 8s before retry...")
                time.sleep(8.0)
                self.last_request = time.time()
                resp2 = self.session.get(self.ENDPOINT, params=params, timeout=REQUEST_TIMEOUT)
                if resp2.status_code == 200:
                    data = resp2.json()
                    articles = data.get("articles", [])
                    retrieved_count = len(articles)
                    logger.info(f"GDELT retry succeeded: {retrieved_count} articles.")
                    self.search_logger.log_query("GDELT Project API v2", query, category, "2017-2025", retrieved_count)
                    return articles
                self.search_logger.log_query("GDELT Project API v2", query, category, "2017-2025", 0)
                return []
            else:
                self.search_logger.log_query("GDELT Project API v2", query, category, "2017-2025", 0)
                return []
        except Exception as e:
            logger.warning(f"GDELT query error: {e}")
            self.search_logger.log_query("GDELT Project API v2", query, category, "2017-2025", 0)
            return []

    def collect(self) -> List[Dict[str, Any]]:
        collected = []
        queries = build_grouped_gdelt_queries()
        logger.info(f"Executing GDELT collection ({len(queries)} grouped queries)...")
        for q_info in queries:
            q_str = q_info["query"]
            cat = q_info["category"]
            kw = q_info["keyword"]
            arts = self.query_artlist(q_str, category=cat, max_records=100)
            for a in arts:
                collected.append({
                    "title": a.get("title", ""),
                    "url": a.get("url", ""),
                    "date": a.get("seendate", ""),
                    "domain": a.get("domain", ""),
                    "language": a.get("language", "English"),
                    "keyword": kw,
                    "category": cat,
                    "source_api": "GDELT Project API v2"
                })
        logger.info(f"GDELT collection complete: harvested {len(collected)} raw records.")
        return collected


class BingNewsCollector:
    """Client for Bing News RSS search interface."""
    BASE_URL = "https://www.bing.com/news/search"

    def __init__(self, search_logger: SearchLogger):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.last_request = 0.0
        self.search_logger = search_logger

    def _wait_delay(self):
        elapsed = time.time() - self.last_request
        if elapsed < 0.6:
            time.sleep(0.6 - elapsed)
        self.last_request = time.time()

    def search_rss(self, query: str, keyword: str = "", category: str = "",
                   date_range: str = "2000-2025", default_source: str = "",
                   offset: int = 1) -> List[Dict[str, Any]]:
        self._wait_delay()
        params = {
            "q": query,
            "format": "rss",
            "first": str(offset)
        }
        retrieved_count = 0
        try:
            logger.info(f"Bing News RSS query (offset {offset}): '{query[:60]}...'")
            resp = self.session.get(self.BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "xml")
                items = soup.find_all("item")
                results = []
                for it in items:
                    title = it.title.text if it.title else ""
                    raw_link = it.link.text if it.link else ""
                    link = extract_canonical_from_bing(raw_link)
                    pub_date = it.pubDate.text if it.pubDate else ""
                    description = it.description.text if it.description else ""

                    source_elem = it.find("source")
                    source_name = source_elem.text if source_elem else default_source
                    domain = extract_netloc(link)

                    results.append({
                        "title": title,
                        "url": link,
                        "date": pub_date,
                        "description": description,
                        "source_name": source_name,
                        "domain": domain,
                        "keyword": keyword,
                        "category": category,
                        "source_api": "Bing News RSS"
                    })
                retrieved_count = len(results)
                logger.info(f"Bing News RSS returned {retrieved_count} items.")
                self.search_logger.log_query("Bing News RSS", f"{query} [p={offset}]", category, date_range, retrieved_count)
                return results
            else:
                self.search_logger.log_query("Bing News RSS", query, category, date_range, 0)
                return []
        except Exception as e:
            logger.warning(f"Bing News RSS error: {e}")
            self.search_logger.log_query("Bing News RSS", query, category, date_range, 0)
            return []

    def collect(self) -> List[Dict[str, Any]]:
        collected = []
        queries = build_broad_topic_queries()
        logger.info(f"Executing Bing News collection ({len(queries)} queries across 5 groups)...")
        for q_info in queries:
            q_clean = q_info["query"].replace("location:India", "India")
            # Page 1
            items = self.search_rss(
                q_clean,
                keyword=q_info["keyword"],
                category=q_info["category"],
                date_range="2000-2025",
                offset=1
            )
            collected.extend(items)

            # For high-volume phrases, also query page 2 (offset 11) and page 3 (offset 21)
            is_high_volume = any(k in q_clean.lower() for k in ["suicide", "stress", "kota", "neet", "jee", "pressure", "तनाव", "दबाव", "आत्महत्या"])
            if is_high_volume and len(items) >= 8:
                items_p2 = self.search_rss(
                    q_clean,
                    keyword=q_info["keyword"],
                    category=q_info["category"],
                    date_range="2000-2025",
                    offset=11
                )
                collected.extend(items_p2)
                if len(items_p2) >= 8:
                    items_p3 = self.search_rss(
                        q_clean,
                        keyword=q_info["keyword"],
                        category=q_info["category"],
                        date_range="2000-2025",
                        offset=21
                    )
                    collected.extend(items_p3)

        # Publisher-Specific Searches on Bing
        publisher_targets = [
            ("timesofindia.indiatimes.com", "The Times of India", "exam stress student"),
            ("thehindu.com", "The Hindu", "exam stress student"),
            ("hindustantimes.com", "Hindustan Times", "student suicide NEET JEE"),
            ("indianexpress.com", "The Indian Express", "exam pressure coaching"),
            ("deccanherald.com", "Deccan Herald", "student distress counseling"),
            ("tribuneindia.com", "The Tribune", "exam stress board"),
            ("newindianexpress.com", "The New Indian Express", "student suicide Tele-MANAS"),
            ("thestatesman.com", "The Statesman", "student exam pressure"),
            ("telegraphindia.com", "The Telegraph India", "board exam stress student"),
            ("livemint.com", "Mint", "Kota coaching student suicide"),
            ("freepressjournal.in", "Free Press Journal", "Kota student suicide"),
            ("ndtv.com", "NDTV", "exam stress student depression"),
            ("indiatoday.in", "India Today", "NEET JEE coaching suicide"),
            ("news18.com", "News18", "student suicide exam results"),
            ("thequint.com", "The Quint", "academic pressure mental health"),
            ("theprint.in", "The Print", "Kota coaching factory suicide"),
            ("amarujala.com", "Amar Ujala", "परीक्षा तनाव छात्र आत्महत्या"),
            ("jagran.com", "Dainik Jagran", "परीक्षा का दबाव छात्र आत्महत्या"),
            ("bhaskar.com", "Dainik Bhaskar", "कोटा छात्र आत्महत्या तनाव"),
            ("livehindustan.com", "Hindustan", "पढ़ाई का तनाव छात्र आत्महत्या"),
            ("navbharattimes.indiatimes.com", "Navbharat Times", "परीक्षा का दबाव बोर्ड रिजल्ट"),
            ("patrika.com", "Rajasthan Patrika", "कोटा कोचिंग छात्र आत्महत्या")
        ]
        logger.info(f"Executing Bing publisher-targeted queries ({len(publisher_targets)} publishers)...")
        for dom, name, search_phrase in publisher_targets:
            q_pub = f"site:{dom} {search_phrase}"
            items = self.search_rss(q_pub, keyword="academic stress", category="Student Mental Health", default_source=name, offset=1)
            for it in items:
                if not it.get("source_name"):
                    it["source_name"] = name
                if not it.get("domain"):
                    it["domain"] = dom
            collected.extend(items)

        logger.info(f"Bing News collection complete: gathered {len(collected)} raw records.")
        return collected


class PublisherFeedCollector:
    """Client for direct Indian newspaper RSS feeds and open search APIs."""
    def __init__(self, search_logger: SearchLogger):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.search_logger = search_logger

    def collect(self) -> List[Dict[str, Any]]:
        collected = []

        # 1. Direct Publisher Education RSS Feeds
        direct_feeds = [
            ("The Indian Express", "https://indianexpress.com/section/education/feed/", "indianexpress.com"),
            ("The Hindu", "https://www.thehindu.com/education/feeder/default.rss", "thehindu.com"),
            ("Hindustan Times", "https://www.hindustantimes.com/feeds/rss/education/rssfeed.xml", "hindustantimes.com"),
            ("The Times of India", "https://timesofindia.indiatimes.com/rssfeeds/913168846.cms", "timesofindia.indiatimes.com")
        ]

        logger.info(f"Executing direct publisher RSS feed harvesting ({len(direct_feeds)} feeds)...")
        for name, feed_url, dom in direct_feeds:
            try:
                r = self.session.get(feed_url, timeout=REQUEST_TIMEOUT)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, "xml")
                    items = soup.find_all("item")
                    for it in items:
                        title = it.title.text if it.title else ""
                        link = it.link.text if it.link else ""
                        pub_date = it.pubDate.text if it.pubDate else ""
                        description = it.description.text if it.description else ""
                        collected.append({
                            "title": title,
                            "url": link,
                            "date": pub_date,
                            "description": description,
                            "source_name": name,
                            "domain": dom,
                            "keyword": "academic stress",
                            "category": "Student Mental Health",
                            "source_api": f"{name} RSS Feed"
                        })
                    logger.info(f"{name} RSS feed returned {len(items)} items.")
                    self.search_logger.log_query(f"{name} RSS Feed", feed_url, "Student Mental Health", "Live Archives", len(items))
                else:
                    self.search_logger.log_query(f"{name} RSS Feed", feed_url, "Student Mental Health", "Live Archives", 0)
            except Exception as e:
                logger.warning(f"Error fetching {name} feed: {e}")
                self.search_logger.log_query(f"{name} RSS Feed", feed_url, "Student Mental Health", "Live Archives", 0)

        # 2. The Quint Search API
        quint_terms = [
            ("exam stress", "Student Mental Health", "exam stress"),
            ("student suicide", "Student Mental Health", "student suicide"),
            ("Kota suicide", "Competitive Exams & Coaching", "Kota"),
            ("NEET JEE stress", "Competitive Exams & Coaching", "NEET"),
            ("parental pressure", "Family & Parental Pressure", "parental expectations"),
            ("education loan", "Economic & Social Pressure", "education loan")
        ]
        logger.info("Harvesting from The Quint search API...")
        for term, cat, kw in quint_terms:
            try:
                q_url = f"https://www.thequint.com/api/v1/search?q={quote(term)}&limit=50&offset=0"
                r = self.session.get(q_url, timeout=REQUEST_TIMEOUT)
                if r.status_code == 200:
                    data = r.json()
                    stories = data.get("results", {}).get("stories", [])
                    for s in stories:
                        title = s.get("headline", "")
                        slug = s.get("slug", "")
                        url = f"https://www.thequint.com/{slug}" if slug else ""
                        pub_ms = s.get("published-at")
                        pub_date = ""
                        if pub_ms:
                            try:
                                dt = datetime.datetime.fromtimestamp(pub_ms / 1000.0)
                                pub_date = dt.strftime("%Y-%m-%d")
                            except Exception:
                                pass
                        collected.append({
                            "title": title,
                            "url": url,
                            "date": pub_date,
                            "description": s.get("summary", ""),
                            "source_name": "The Quint",
                            "domain": "thequint.com",
                            "keyword": kw,
                            "category": cat,
                            "source_api": "The Quint Search API"
                        })
                    logger.info(f"The Quint API returned {len(stories)} stories for '{term}'.")
                    self.search_logger.log_query("The Quint Search API", term, cat, "2015-2025", len(stories))
                else:
                    self.search_logger.log_query("The Quint Search API", term, cat, "2015-2025", 0)
            except Exception as e:
                logger.warning(f"Error querying The Quint API: {e}")
                self.search_logger.log_query("The Quint Search API", term, cat, "2015-2025", 0)

        logger.info(f"Publisher direct feed harvesting complete: gathered {len(collected)} raw records.")
        return collected


class GoogleNewsCollector:
    """Client for Google News RSS Search interface."""
    BASE_URL = "https://news.google.com/rss/search"

    def __init__(self, search_logger: SearchLogger):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.last_request = 0.0
        self.search_logger = search_logger

    def _wait_delay(self):
        elapsed = time.time() - self.last_request
        if elapsed < GOOGLE_NEWS_DELAY:
            time.sleep(GOOGLE_NEWS_DELAY - elapsed)
        self.last_request = time.time()

    def search_rss(self, query: str, keyword: str = "", category: str = "",
                   date_range: str = "2000-2025", default_source: str = "") -> List[Dict[str, Any]]:
        self._wait_delay()
        params = {
            "q": query,
            "hl": "en-IN",
            "gl": "IN",
            "ceid": "IN:en"
        }
        retrieved_count = 0
        try:
            resp = self.session.get(self.BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "xml")
                items = soup.find_all("item")
                results = []
                for it in items:
                    title = it.title.text if it.title else ""
                    link = it.link.text if it.link else ""
                    pub_date = it.pubDate.text if it.pubDate else ""
                    description = it.description.text if it.description else ""

                    source_elem = it.find("source")
                    source_name = source_elem.text if source_elem else default_source
                    source_url = source_elem.get("url", "") if source_elem else ""
                    domain = extract_netloc(source_url)

                    results.append({
                        "title": title,
                        "url": link,
                        "date": pub_date,
                        "description": description,
                        "source_name": source_name,
                        "domain": domain,
                        "keyword": keyword,
                        "category": category,
                        "source_api": "Google News RSS"
                    })
                retrieved_count = len(results)
                self.search_logger.log_query("Google News RSS", query, category, date_range, retrieved_count)
                return results
            else:
                self.search_logger.log_query("Google News RSS", query, category, date_range, 0)
                return []
        except Exception as e:
            self.search_logger.log_query("Google News RSS", query, category, date_range, 0)
            return []

    def collect(self) -> List[Dict[str, Any]]:
        collected = []
        broad_queries = build_broad_topic_queries()[:20]
        logger.info(f"Executing Google News collection ({len(broad_queries)} queries)...")
        for q_info in broad_queries:
            items = self.search_rss(
                q_info["query"],
                keyword=q_info["keyword"],
                category=q_info["category"],
                date_range="2000-2025"
            )
            collected.extend(items)
        logger.info(f"Google News collection complete: gathered {len(collected)} raw records.")
        return collected


class MediaCloudCollector:
    """Client for Media Cloud API."""
    def __init__(self, search_logger: SearchLogger):
        self.api_key = MEDIACLOUD_API_KEY
        self.search_logger = search_logger

    def collect(self) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.info("Media Cloud API key (MEDIACLOUD_API_KEY) not configured. Logged to search_log.csv.")
            self.search_logger.log_query("Media Cloud API", "academic stress (API key required)", "Student Mental Health", "2014-2025", 0)
            return []
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            url = "https://search.mediacloud.org/api/v3/stories"
            params = {
                "q": '("academic stress" OR "exam stress" OR "student suicide") AND tags_id_media:1865487',
                "rows": 100
            }
            r = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                data = r.json()
                stories = data.get("stories", [])
                logger.info(f"Media Cloud returned {len(stories)} stories.")
                self.search_logger.log_query("Media Cloud API", params["q"], "Student Mental Health", "2014-2025", len(stories))
                return [{
                    "title": s.get("title", ""),
                    "url": s.get("url", ""),
                    "date": s.get("publish_date", ""),
                    "source_name": s.get("media_name", ""),
                    "keyword": "academic stress",
                    "category": "Student Mental Health",
                    "source_api": "Media Cloud API"
                } for s in stories]
            else:
                self.search_logger.log_query("Media Cloud API", params["q"], "Student Mental Health", "2014-2025", 0)
                return []
        except Exception as e:
            logger.warning(f"Media Cloud API error: {e}")
            self.search_logger.log_query("Media Cloud API", "Error during request", "Student Mental Health", "2014-2025", 0)
            return []


def run_all_collections() -> Tuple[List[Dict[str, Any]], SearchLogger]:
    search_logger = SearchLogger()
    all_raw = []

    # 1. Bing News RSS (Very robust, high yield, no rate limit blocking)
    try:
        bing = BingNewsCollector(search_logger)
        b_records = bing.collect()
        all_raw.extend(b_records)
    except Exception as e:
        logger.error(f"Bing News collector failure: {e}")

    # 2. Publisher Direct Feeds & Search APIs (IE, The Hindu, HT, TOI, The Quint)
    try:
        pub_col = PublisherFeedCollector(search_logger)
        p_records = pub_col.collect()
        all_raw.extend(p_records)
    except Exception as e:
        logger.error(f"Publisher feeds collector failure: {e}")

    # 3. GDELT Project API
    try:
        gdelt = GDELTCollector(search_logger)
        g_records = gdelt.collect()
        all_raw.extend(g_records)
    except Exception as e:
        logger.error(f"GDELT collector failure: {e}")

    # 4. Google News RSS
    try:
        gn = GoogleNewsCollector(search_logger)
        gn_records = gn.collect()
        all_raw.extend(gn_records)
    except Exception as e:
        logger.error(f"Google News collector failure: {e}")

    # 5. Media Cloud API
    try:
        mc = MediaCloudCollector(search_logger)
        mc_records = mc.collect()
        all_raw.extend(mc_records)
    except Exception as e:
        logger.error(f"Media Cloud collector failure: {e}")

    # Export Search Log
    search_logger.export(SEARCH_LOG_FILE)

    logger.info(f"Total raw news records harvested across all collectors: {len(all_raw)}")
    return all_raw, search_logger
