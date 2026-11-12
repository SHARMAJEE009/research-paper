"""
Keyword search strategies, query formulation, relevance scoring, and classification.
Academic Research Data Collection Pipeline (Expanded 2000-2025).
Supports 5 Keyword Groups:
1. Competitive Exams & Coaching
2. Student Mental Health
3. Family & Parental Pressure
4. Economic & Social Pressure
5. Hindi Keywords
"""

import re
from typing import Dict, List, Optional, Tuple
from config import (
    KEYWORDS_COMPETITIVE_COACHING,
    KEYWORDS_STUDENT_MENTAL_HEALTH,
    KEYWORDS_FAMILY_PARENTAL,
    KEYWORDS_ECONOMIC_SOCIAL,
    KEYWORDS_HINDI,
    ALL_KEYWORDS,
    TOPIC_CATEGORIES,
    NEGATIVE_FILTER_TERMS,
    EDUCATION_CONTEXT_TERMS
)


def build_grouped_gdelt_queries() -> List[Dict[str, str]]:
    """
    Constructs clean phrase queries for GDELT 2.0 Doc API.
    """
    return [
        {"category": "Competitive Exams & Coaching", "query": '"Kota" "suicide" sourcecountry:IN', "keyword": "Kota"},
        {"category": "Competitive Exams & Coaching", "query": '"coaching institute" "student stress" sourcecountry:IN', "keyword": "coaching institute"},
        {"category": "Competitive Exams & Coaching", "query": '"NEET" "exam stress" sourcecountry:IN', "keyword": "NEET"},
        {"category": "Competitive Exams & Coaching", "query": '"JEE" "exam stress" sourcecountry:IN', "keyword": "JEE"},
        {"category": "Competitive Exams & Coaching", "query": '"IIT" "student suicide" sourcecountry:IN', "keyword": "IIT-JEE"},
        {"category": "Competitive Exams & Coaching", "query": '"UPSC" "depression" sourcecountry:IN', "keyword": "UPSC"},
        {"category": "Competitive Exams & Coaching", "query": '"cut-throat competition" student sourcecountry:IN', "keyword": "cut-throat competition"},
        {"category": "Competitive Exams & Coaching", "query": '"rank obsession" student sourcecountry:IN', "keyword": "rank obsession"},

        {"category": "Student Mental Health", "query": '"student suicide" sourcecountry:IN', "keyword": "student suicide"},
        {"category": "Student Mental Health", "query": '"academic stress" sourcecountry:IN', "keyword": "academic stress"},
        {"category": "Student Mental Health", "query": '"exam stress" sourcecountry:IN', "keyword": "exam stress"},
        {"category": "Student Mental Health", "query": '"examination stress" sourcecountry:IN', "keyword": "examination stress"},
        {"category": "Student Mental Health", "query": '"student anxiety" sourcecountry:IN', "keyword": "student anxiety"},
        {"category": "Student Mental Health", "query": '"student mental health" sourcecountry:IN', "keyword": "mental health"},
        {"category": "Student Mental Health", "query": '"board exam stress" sourcecountry:IN', "keyword": "board examination stress"},

        {"category": "Family & Parental Pressure", "query": '"parental expectations" student sourcecountry:IN', "keyword": "parental expectations"},
        {"category": "Family & Parental Pressure", "query": '"parental pressure" student sourcecountry:IN', "keyword": "parental pressure"},
        {"category": "Family & Parental Pressure", "query": '"parents sacrifices" student sourcecountry:IN', "keyword": "parents' sacrifices"},
        {"category": "Family & Parental Pressure", "query": '"career pressure" student sourcecountry:IN', "keyword": "career pressure"},

        {"category": "Economic & Social Pressure", "query": '"education loan" "student" sourcecountry:IN', "keyword": "education loan"},
        {"category": "Economic & Social Pressure", "query": '"financial burden" student education sourcecountry:IN', "keyword": "financial burden"},
        {"category": "Economic & Social Pressure", "query": '"societal pressure" student sourcecountry:IN', "keyword": "societal pressure"},

        {"category": "Hindi Coverage", "query": '"कोटा" आत्महत्या sourcecountry:IN', "keyword": "कोटा"},
        {"category": "Hindi Coverage", "query": '"परीक्षा का दबाव" sourcecountry:IN', "keyword": "परीक्षा का दबाव"},
        {"category": "Hindi Coverage", "query": '"छात्रों की आत्महत्या" sourcecountry:IN', "keyword": "छात्रों की आत्महत्या"}
    ]


def build_broad_topic_queries() -> List[Dict[str, str]]:
    """
    Constructs comprehensive queries covering all 5 groups in depth.
    """
    return [
        # Group 1: Competitive Exams & Coaching
        {"query": '"Kota" student suicide India', "keyword": "Kota", "category": "Competitive Exams & Coaching"},
        {"query": '"Kota" coaching student stress India', "keyword": "Kota", "category": "Competitive Exams & Coaching"},
        {"query": '"Kota" coaching suicide NEET JEE India', "keyword": "coaching factory", "category": "Competitive Exams & Coaching"},
        {"query": '"Kota" NEET aspirant suicide India', "keyword": "Kota", "category": "Competitive Exams & Coaching"},
        {"query": '"Kota" JEE aspirant suicide India', "keyword": "Kota", "category": "Competitive Exams & Coaching"},
        {"query": '"Kota" coaching guidelines suicide prevention India', "keyword": "coaching institute", "category": "Competitive Exams & Coaching"},
        {"query": '"Kota" coaching death student India', "keyword": "Kota", "category": "Competitive Exams & Coaching"},
        {"query": '"Kota" student hanging PG hostel India', "keyword": "Kota", "category": "Competitive Exams & Coaching"},
        {"query": '"Sikar" coaching student suicide India', "keyword": "coaching institute", "category": "Competitive Exams & Coaching"},
        {"query": '"Patna" coaching student suicide India', "keyword": "coaching institute", "category": "Competitive Exams & Coaching"},
        {"query": '"IIT-JEE" student stress OR suicide India', "keyword": "IIT-JEE", "category": "Competitive Exams & Coaching"},
        {"query": '"IIT" student suicide stress mental health India', "keyword": "IIT-JEE", "category": "Competitive Exams & Coaching"},
        {"query": '"IIT Delhi" student suicide stress India', "keyword": "IIT-JEE", "category": "Competitive Exams & Coaching"},
        {"query": '"IIT Bombay" student suicide pressure India', "keyword": "IIT-JEE", "category": "Competitive Exams & Coaching"},
        {"query": '"IIT Madras" student suicide pressure India', "keyword": "IIT-JEE", "category": "Competitive Exams & Coaching"},
        {"query": '"IIT Kharagpur" student suicide stress India', "keyword": "IIT-JEE", "category": "Competitive Exams & Coaching"},
        {"query": '"IIT Kanpur" student suicide stress India', "keyword": "IIT-JEE", "category": "Competitive Exams & Coaching"},
        {"query": '"AIIMS" MBBS student suicide stress India', "keyword": "NEET", "category": "Competitive Exams & Coaching"},
        {"query": '"Old Rajinder Nagar" UPSC aspirant stress India', "keyword": "UPSC", "category": "Competitive Exams & Coaching"},
        {"query": '"Mukherjee Nagar" UPSC aspirant suicide India', "keyword": "UPSC", "category": "Competitive Exams & Coaching"},
        {"query": '"JEE Main" exam stress student India', "keyword": "JEE", "category": "Competitive Exams & Coaching"},
        {"query": '"JEE Advanced" exam pressure student India', "keyword": "JEE", "category": "Competitive Exams & Coaching"},
        {"query": '"NEET" exam stress student India', "keyword": "NEET", "category": "Competitive Exams & Coaching"},
        {"query": '"NEET" student suicide India', "keyword": "NEET", "category": "Competitive Exams & Coaching"},
        {"query": '"NEET UG" anxiety stress student counseling India', "keyword": "NEET", "category": "Competitive Exams & Coaching"},
        {"query": '"NEET" paper leak stress protest students India', "keyword": "NEET", "category": "Competitive Exams & Coaching"},
        {"query": '"UPSC" aspirant suicide OR depression OR stress India', "keyword": "UPSC", "category": "Competitive Exams & Coaching"},
        {"query": '"UPSC" prelims failure depression aspirant India', "keyword": "UPSC", "category": "Competitive Exams & Coaching"},
        {"query": '"coaching institute" student stress India', "keyword": "coaching institute", "category": "Competitive Exams & Coaching"},
        {"query": '"coaching factory" student pressure India', "keyword": "coaching factory", "category": "Competitive Exams & Coaching"},
        {"query": '"coaching hub" Kota Sikar student stress India', "keyword": "coaching institute", "category": "Competitive Exams & Coaching"},
        {"query": '"cut-throat competition" student exam India', "keyword": "cut-throat competition", "category": "Competitive Exams & Coaching"},
        {"query": '"rank obsession" students India', "keyword": "rank obsession", "category": "Competitive Exams & Coaching"},
        {"query": '"percentile race" student exam India', "keyword": "percentile race", "category": "Competitive Exams & Coaching"},
        {"query": '"mock test scores" student stress OR suicide India', "keyword": "mock test scores", "category": "Competitive Exams & Coaching"},
        {"query": '"mock test" low marks depression student India', "keyword": "mock test scores", "category": "Competitive Exams & Coaching"},
        {"query": '"elimination exam" student India', "keyword": "elimination exam", "category": "Competitive Exams & Coaching"},
        {"query": '"peer pressure" student exam India', "keyword": "peer pressure", "category": "Competitive Exams & Coaching"},
        {"query": '"competitive examination pressure" India', "keyword": "competitive examination pressure", "category": "Competitive Exams & Coaching"},
        {"query": '"dummy school" coaching stress student India', "keyword": "coaching factory", "category": "Competitive Exams & Coaching"},
        {"query": '"CUET" exam stress student confusion India', "keyword": "competitive examination pressure", "category": "Competitive Exams & Coaching"},
        {"query": '"CAT" exam stress management student India', "keyword": "competitive examination pressure", "category": "Competitive Exams & Coaching"},

        # Group 2: Student Mental Health
        {"query": '"student suicide" exam stress India', "keyword": "student suicide", "category": "Student Mental Health"},
        {"query": '"student suicide" academic pressure India', "keyword": "student suicide", "category": "Student Mental Health"},
        {"query": '"student suicide" exam failure India', "keyword": "student suicide", "category": "Student Mental Health"},
        {"query": '"student suicide" board results India', "keyword": "student suicide", "category": "Student Mental Health"},
        {"query": '"student suicide" Class 10 OR Class 12 India', "keyword": "student suicide", "category": "Student Mental Health"},
        {"query": '"student suicide note" exam failure India', "keyword": "student suicide", "category": "Student Mental Health"},
        {"query": '"student suicide" fear of failing exams India', "keyword": "student suicide", "category": "Student Mental Health"},
        {"query": '"academic stress" student India', "keyword": "academic stress", "category": "Student Mental Health"},
        {"query": '"exam stress" student India', "keyword": "exam stress", "category": "Student Mental Health"},
        {"query": '"examination stress" student India', "keyword": "examination stress", "category": "Student Mental Health"},
        {"query": '"student distress" exam India', "keyword": "student distress", "category": "Student Mental Health"},
        {"query": '"psychological pressure" student exam India', "keyword": "psychological pressure", "category": "Student Mental Health"},
        {"query": '"student depression" exam India', "keyword": "depression", "category": "Student Mental Health"},
        {"query": '"student anxiety" exam stress India', "keyword": "student anxiety", "category": "Student Mental Health"},
        {"query": '"student mental health" exam pressure India', "keyword": "mental health", "category": "Student Mental Health"},
        {"query": '"board exam stress" India', "keyword": "board examination stress", "category": "Student Mental Health"},
        {"query": '"board examination stress" India', "keyword": "board examination stress", "category": "Student Mental Health"},
        {"query": '"CBSE board" exam stress helpline counseling India', "keyword": "board examination stress", "category": "Student Mental Health"},
        {"query": '"CBSE Class 10" exam stress counseling India', "keyword": "board examination stress", "category": "Student Mental Health"},
        {"query": '"CBSE Class 12" exam stress counseling India', "keyword": "board examination stress", "category": "Student Mental Health"},
        {"query": '"ICSE board" exam stress helpline student India', "keyword": "board examination stress", "category": "Student Mental Health"},
        {"query": '"State board" exam failure student suicide India', "keyword": "board examination stress", "category": "Student Mental Health"},
        {"query": '"compartment exam" stress student suicide India', "keyword": "board examination stress", "category": "Student Mental Health"},
        {"query": 'Tele-MANAS student exam stress counseling India', "keyword": "student anxiety", "category": "Student Mental Health"},
        {"query": 'Tele-MANAS student mental health helpline calls India', "keyword": "mental health", "category": "Student Mental Health"},
        {"query": 'Manodarpan student mental health exam counseling India', "keyword": "mental health", "category": "Student Mental Health"},
        {"query": 'Pariksha Pe Charcha exam stress board India', "keyword": "exam pressure", "category": "Student Mental Health"},
        {"query": '"NCRB" student suicide exam failure India', "keyword": "student suicide", "category": "Student Mental Health"},
        {"query": '"Supreme Court" student suicide coaching guidelines India', "keyword": "student suicide", "category": "Student Mental Health"},

        # Group 3: Family & Parental Pressure
        {"query": '"parental expectations" student exam stress India', "keyword": "parental expectations", "category": "Family & Parental Pressure"},
        {"query": '"parental pressure" student education India', "keyword": "parental expectations", "category": "Family & Parental Pressure"},
        {"query": '"parental pressure" engineering medical career India', "keyword": "parental expectations", "category": "Family & Parental Pressure"},
        {"query": '"parental pressure" board marks student suicide India', "keyword": "parental expectations", "category": "Family & Parental Pressure"},
        {"query": '"parents pressure" children marks student suicide India', "keyword": "parental expectations", "category": "Family & Parental Pressure"},
        {"query": '"parents high expectations" student depression India', "keyword": "parental expectations", "category": "Family & Parental Pressure"},
        {"query": '"family burden" student education India', "keyword": "family burden", "category": "Family & Parental Pressure"},
        {"query": '"family pride" student exam India', "keyword": "family pride", "category": "Family & Parental Pressure"},
        {"query": '"parents sacrifices" student education India', "keyword": "parents' sacrifices", "category": "Family & Parental Pressure"},
        {"query": '"parents sacrifices" coaching fees student guilt India', "keyword": "parents' sacrifices", "category": "Family & Parental Pressure"},
        {"query": '"parents dreams" student exam pressure India', "keyword": "parents' dreams", "category": "Family & Parental Pressure"},
        {"query": '"parents dreams" student pressure engineering medical India', "keyword": "parents' dreams", "category": "Family & Parental Pressure"},
        {"query": '"middle-class aspirations" student education exam India', "keyword": "middle-class aspirations", "category": "Family & Parental Pressure"},
        {"query": '"forced career choice" student India', "keyword": "forced career choice", "category": "Family & Parental Pressure"},
        {"query": '"forced career choice" engineering medicine student suicide India', "keyword": "forced career choice", "category": "Family & Parental Pressure"},
        {"query": '"career pressure" student exam India', "keyword": "career pressure", "category": "Family & Parental Pressure"},
        {"query": '"academic legacy" student pressure India', "keyword": "academic legacy", "category": "Family & Parental Pressure"},

        # Group 4: Economic & Social Pressure
        {"query": '"education loan" student suicide India', "keyword": "education loan", "category": "Economic & Social Pressure"},
        {"query": '"education loan" student stress OR burden India', "keyword": "education loan", "category": "Economic & Social Pressure"},
        {"query": '"education loan" repayment debt student distress India', "keyword": "education loan", "category": "Economic & Social Pressure"},
        {"query": '"financial burden" student education stress India', "keyword": "financial burden", "category": "Economic & Social Pressure"},
        {"query": '"financial burden" coaching fees student suicide India', "keyword": "financial burden", "category": "Economic & Social Pressure"},
        {"query": '"coaching fees" debt parents student suicide India', "keyword": "financial burden", "category": "Economic & Social Pressure"},
        {"query": '"tuition fees" hike student distress suicide India', "keyword": "financial burden", "category": "Economic & Social Pressure"},
        {"query": '"social expectations" student exam stress India', "keyword": "social expectations", "category": "Economic & Social Pressure"},
        {"query": '"societal pressure" student exam pressure India', "keyword": "societal pressure", "category": "Economic & Social Pressure"},
        {"query": '"societal pressure" student suicide marks India', "keyword": "societal pressure", "category": "Economic & Social Pressure"},
        {"query": '"education as social mobility" student pressure India', "keyword": "education as social mobility", "category": "Economic & Social Pressure"},

        # Group 5: Hindi Keywords
        {"query": '"कोटा" छात्र आत्महत्या', "keyword": "कोटा", "category": "Hindi Coverage"},
        {"query": '"कोटा" कोचिंग छात्र तनाव', "keyword": "कोटा", "category": "Hindi Coverage"},
        {"query": '"कोटा" नीट छात्र आत्महत्या', "keyword": "कोटा", "category": "Hindi Coverage"},
        {"query": '"कोटा में छात्र ने की आत्महत्या"', "keyword": "कोटा", "category": "Hindi Coverage"},
        {"query": '"कोटा में नीट छात्र ने दी जान"', "keyword": "कोटा", "category": "Hindi Coverage"},
        {"query": '"कोटा में जेईई छात्र ने की खुदकुशी"', "keyword": "कोटा", "category": "Hindi Coverage"},
        {"query": '"नीट परीक्षा" तनाव OR आत्महत्या', "keyword": "नीट परीक्षा", "category": "Hindi Coverage"},
        {"query": '"नीट" छात्र आत्महत्या', "keyword": "नीट परीक्षा", "category": "Hindi Coverage"},
        {"query": '"नीट की तैयारी कर रहे छात्र ने की खुदकुशी"', "keyword": "नीट परीक्षा", "category": "Hindi Coverage"},
        {"query": '"आईआईटी जेईई" तनाव OR दबाव', "keyword": "आईआईटी जेईई", "category": "Hindi Coverage"},
        {"query": '"आईआईटी" छात्र आत्महत्या तनाव', "keyword": "आईआईटी जेईई", "category": "Hindi Coverage"},
        {"query": '"जेईई की तैयारी कर रहे छात्र ने लगाई फांसी"', "keyword": "आईआईटी जेईई", "category": "Hindi Coverage"},
        {"query": '"यूपीएससी" छात्र तनाव OR आत्महत्या', "keyword": "यूपीएससी", "category": "Hindi Coverage"},
        {"query": '"कोचिंग संस्थान" छात्र तनाव', "keyword": "कोचिंग संस्थान", "category": "Hindi Coverage"},
        {"query": '"कोचिंग संस्थान" मानसिक दबाव', "keyword": "कोचिंग संस्थान", "category": "Hindi Coverage"},
        {"query": '"परीक्षा का दबाव" छात्र', "keyword": "परीक्षा का दबाव", "category": "Hindi Coverage"},
        {"query": '"बोर्ड परीक्षा में फेल होने पर आत्महत्या"', "keyword": "परीक्षा का दबाव", "category": "Hindi Coverage"},
        {"query": '"10वीं में फेल होने पर छात्र ने की खुदकुशी"', "keyword": "परीक्षा का दबाव", "category": "Hindi Coverage"},
        {"query": '"12वीं में कम नंबर आने पर छात्र ने दी जान"', "keyword": "परीक्षा का दबाव", "category": "Hindi Coverage"},
        {"query": '"पढ़ाई का तनाव" छात्र', "keyword": "पढ़ाई का तनाव", "category": "Hindi Coverage"},
        {"query": '"पढ़ाई के दबाव में छात्र की खुदकुशी"', "keyword": "पढ़ाई का तनाव", "category": "Hindi Coverage"},
        {"query": '"छात्रों की आत्महत्या" परीक्षा', "keyword": "छात्रों की आत्महत्या", "category": "Hindi Coverage"},
        {"query": '"मानसिक स्वास्थ्य" छात्र परीक्षा', "keyword": "मानसिक स्वास्थ्य", "category": "Hindi Coverage"},
        {"query": '"अवसाद" छात्र परीक्षा', "keyword": "अवसाद", "category": "Hindi Coverage"},
        {"query": '"अभिभावकों का दबाव" छात्र परीक्षा', "keyword": "अभिभावकों का दबाव", "category": "Hindi Coverage"},
        {"query": '"माता-पिता की अपेक्षाएं" छात्र तनाव', "keyword": "माता-पिता की अपेक्षाएं", "category": "Hindi Coverage"},
        {"query": '"माता पिता के दबाव में छात्र ने की खुदकुशी"', "keyword": "अभिभावकों का दबाव", "category": "Hindi Coverage"},
        {"query": '"प्रतियोगी परीक्षा" तनाव दबाव', "keyword": "प्रतियोगी परीक्षा", "category": "Hindi Coverage"},
        {"query": '"रैंक की दौड़" छात्र तनाव', "keyword": "रैंक की दौड़", "category": "Hindi Coverage"},
        {"query": '"सीबीएसई बोर्ड परीक्षा तनाव हेल्पलाइन"', "keyword": "परीक्षा तनाव", "category": "Hindi Coverage"},
        {"query": '"हॉस्टल में छात्र ने की आत्महत्या कोटा"', "keyword": "कोटा", "category": "Hindi Coverage"}
    ]


def build_yearly_topic_queries(years: List[int]) -> List[Dict[str, str]]:
    """
    Constructs year-specific queries across 2000-2025.
    """
    yearly_queries = []
    core_terms = [
        ("exam stress student", "exam stress", "Student Mental Health"),
        ("student suicide exam", "student suicide", "Student Mental Health"),
        ("academic stress student", "academic stress", "Student Mental Health"),
        ("board exam stress student", "board examination stress", "Student Mental Health"),
        ("Kota coaching student suicide", "Kota", "Competitive Exams & Coaching"),
        ("NEET JEE student stress", "NEET", "Competitive Exams & Coaching"),
        ("parental pressure student exam", "parental expectations", "Family & Parental Pressure"),
        ("education loan student stress", "education loan", "Economic & Social Pressure"),
        ("परीक्षा का दबाव छात्र", "परीक्षा का दबाव", "Hindi Coverage"),
        ("पढ़ाई का तनाव छात्र", "पढ़ाई का तनाव", "Hindi Coverage"),
        ("छात्रों की आत्महत्या परीक्षा", "छात्रों की आत्महत्या", "Hindi Coverage")
    ]

    for y in years:
        for phrase, kw, cat in core_terms:
            q_str = f'"{phrase}" location:India after:{y}-01-01 before:{y}-12-31'
            yearly_queries.append({
                "query": q_str,
                "keyword": kw,
                "category": cat,
                "year": y
            })
    return yearly_queries


def build_publisher_queries(publishers: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    """
    Constructs publisher-targeted queries across Indian news outlets.
    """
    queries = []
    query_templates = [
        ('site:{domain} ("exam stress" OR "student suicide" OR "academic pressure" OR "student stress")', "Student Mental Health", "academic stress"),
        ('site:{domain} ("Kota" OR "NEET" OR "JEE" OR "coaching institute" OR "UPSC") ("stress" OR "suicide" OR "pressure")', "Competitive Exams & Coaching", "coaching institute"),
        ('site:{domain} ("parental expectations" OR "parental pressure" OR "family burden" OR "parents sacrifices")', "Family & Parental Pressure", "parental expectations"),
        ('site:{domain} ("education loan" OR "financial burden" OR "societal pressure") ("student" OR "suicide" OR "stress")', "Economic & Social Pressure", "education loan"),
        ('site:{domain} ("परीक्षा का दबाव" OR "पढ़ाई का तनाव" OR "छात्रों की आत्महत्या" OR "कोटा" OR "मानसिक स्वास्थ्य")', "Hindi Coverage", "परीक्षा का दबाव")
    ]

    for domain, name in publishers:
        for tmpl, cat, kw in query_templates:
            is_hindi_pub = any(h in domain for h in ["jagran", "amarujala", "bhaskar", "livehindustan", "navbharat", "patrika", "punjabkesari", "jansatta", "aajtak"])
            if tmpl.startswith('site:{domain} ("परीक्षा') and not is_hindi_pub:
                continue
            if is_hindi_pub and not tmpl.startswith('site:{domain} ("परीक्षा'):
                continue

            q = tmpl.format(domain=domain)
            queries.append({
                "query": q,
                "keyword": kw,
                "category": cat,
                "publisher_name": name,
                "domain": domain
            })
    return queries


def match_primary_keyword(text: str) -> str:
    """
    Identifies the best matched research keyword across all 5 groups.
    """
    text_lower = text.lower()

    # 1. Hindi Keywords
    for kw in KEYWORDS_HINDI:
        if kw in text:
            return kw

    # 2. Competitive Exams & Coaching
    for kw in KEYWORDS_COMPETITIVE_COACHING:
        if kw.lower() in text_lower:
            return kw

    # 3. Student Mental Health
    for kw in KEYWORDS_STUDENT_MENTAL_HEALTH:
        if kw.lower() in text_lower:
            return kw

    # 4. Family & Parental Pressure
    for kw in KEYWORDS_FAMILY_PARENTAL:
        if kw.lower() in text_lower:
            return kw

    # 5. Economic & Social Pressure
    for kw in KEYWORDS_ECONOMIC_SOCIAL:
        if kw.lower() in text_lower:
            return kw

    # Contextual matches
    if "kota" in text_lower and ("suicide" in text_lower or "stress" in text_lower or "death" in text_lower or "hanging" in text_lower):
        return "Kota"
    if "neet" in text_lower and ("stress" in text_lower or "suicide" in text_lower or "pressure" in text_lower or "aspirant" in text_lower):
        return "NEET"
    if "jee" in text_lower and ("stress" in text_lower or "suicide" in text_lower or "pressure" in text_lower or "aspirant" in text_lower):
        return "JEE"
    if "upsc" in text_lower and ("stress" in text_lower or "suicide" in text_lower or "anxiety" in text_lower or "depression" in text_lower):
        return "UPSC"
    if "suicide" in text_lower and ("student" in text_lower or "exam" in text_lower or "aspirant" in text_lower):
        return "student suicide"
    if "parent" in text_lower and ("pressure" in text_lower or "expectation" in text_lower):
        return "parental expectations"
    if "loan" in text_lower and ("student" in text_lower or "education" in text_lower):
        return "education loan"
    if "exam" in text_lower and ("stress" in text_lower or "pressure" in text_lower):
        return "exam stress"

    return "academic stress"


def classify_topic_category(headline: str, description: str = "") -> str:
    """
    Classifies an article strictly into one of the 5 requested keyword categories:
    1. Competitive Exams & Coaching
    2. Student Mental Health
    3. Family & Parental Pressure
    4. Economic & Social Pressure
    5. Hindi Coverage
    """
    combined = f"{headline} {description}".lower()

    has_hindi_chars = bool(re.search(r"[\u0900-\u097F]", combined))
    if has_hindi_chars:
        for term in TOPIC_CATEGORIES["Hindi Coverage"]:
            if term in f"{headline} {description}":
                return "Hindi Coverage"

    for term in TOPIC_CATEGORIES["Family & Parental Pressure"]:
        if term.lower() in combined:
            return "Family & Parental Pressure"

    for term in TOPIC_CATEGORIES["Economic & Social Pressure"]:
        if term.lower() in combined:
            return "Economic & Social Pressure"

    for term in TOPIC_CATEGORIES["Competitive Exams & Coaching"]:
        if term.lower() in combined:
            return "Competitive Exams & Coaching"

    for term in TOPIC_CATEGORIES["Student Mental Health"]:
        if term.lower() in combined:
            return "Student Mental Health"

    if has_hindi_chars:
        return "Hindi Coverage"

    return "Student Mental Health"


def compute_relevance(headline: str, description: str = "") -> Tuple[float, bool]:
    """
    Validates article relevance to Academic Stress in India across the 5 categories.
    """
    combined = f"{headline} {description}".lower()

    for neg in NEGATIVE_FILTER_TERMS:
        if neg in combined:
            return 0.0, False

    for kw in KEYWORDS_STUDENT_MENTAL_HEALTH + KEYWORDS_FAMILY_PARENTAL + KEYWORDS_ECONOMIC_SOCIAL:
        if kw.lower() in combined:
            if kw.lower() in ["mental health", "depression", "anxiety", "education loan", "financial burden", "societal pressure"]:
                has_edu = any(term in combined for term in EDUCATION_CONTEXT_TERMS)
                if has_edu:
                    return 0.90, True
            else:
                return 0.95, True

    for kw in KEYWORDS_HINDI:
        if kw in f"{headline} {description}":
            return 0.95, True

    has_exam_coaching = any(term in combined for term in [
        "kota", "iit-jee", "iit jee", "jee", "neet", "upsc", "coaching",
        "mock test", "percentile race", "rank obsession", "competitive exam",
        "cat", "gate", "cuet", "clat"
    ])
    has_distress = any(term in combined for term in [
        "stress", "pressure", "suicide", "depression", "anxiety", "mental health",
        "distress", "toll", "death", "crisis", "struggle", "burden", "counseling",
        "hanging", "dead", "died",
        "तनाव", "दबाव", "आत्महत्या", "अवसाद", "फांसी", "खुदकुशी"
    ])
    if has_exam_coaching and has_distress:
        return 0.92, True

    has_edu_context = any(term in combined for term in EDUCATION_CONTEXT_TERMS)
    if has_edu_context and has_distress:
        return 0.85, True

    return 0.20, False
