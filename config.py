"""
Configuration file for Indian News Coverage of Academic Stress (2000-2025)
Academic Research Data Collection Pipeline for Structural Topic Modeling (STM)
Expanded with 5 Research Keyword Groups:
1. Competitive Exams & Coaching
2. Student Mental Health
3. Family & Parental Pressure
4. Economic & Social Pressure
5. Hindi Keywords
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "research_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = OUTPUT_DIR / "data_collection_pipeline.log"
SEARCH_LOG_FILE = OUTPUT_DIR / "search_log.csv"
BACKUP_DIR = OUTPUT_DIR / "backup_original"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Date Scope
START_YEAR = 2000
END_YEAR = 2025
ALL_YEARS = list(range(START_YEAR, END_YEAR + 1))
START_DATE = f"{START_YEAR}-01-01"
END_DATE = f"{END_YEAR}-12-31"

# Target Research Keyword Groups
KEYWORDS_COMPETITIVE_COACHING = [
    "Kota", "IIT-JEE", "JEE", "NEET", "UPSC", "coaching institute",
    "cut-throat competition", "rank obsession", "percentile race",
    "elimination exam", "coaching factory", "peer pressure", "mock test scores",
    "competitive examination pressure", "competitive exam stress", "IIT JEE stress", "NEET exam stress"
]

KEYWORDS_STUDENT_MENTAL_HEALTH = [
    "student suicide", "academic stress", "mental health", "depression",
    "anxiety", "exam pressure", "examination stress", "student distress",
    "psychological pressure", "board examination stress", "board exam stress",
    "student stress", "study pressure", "student anxiety"
]

KEYWORDS_FAMILY_PARENTAL = [
    "parental expectations", "family burden", "family pride", "parents' sacrifices",
    "parents sacrifices", "parents' dreams", "parents dreams", "middle-class aspirations",
    "forced career choice", "academic legacy", "career pressure", "parental pressure",
    "parental pressure related to education"
]

KEYWORDS_ECONOMIC_SOCIAL = [
    "education loan", "financial burden", "social expectations", "societal pressure",
    "education as social mobility", "education loan burden", "tuition debt"
]

KEYWORDS_HINDI = [
    "कोटा", "नीट परीक्षा", "आईआईटी जेईई", "यूपीएससी", "कोचिंग संस्थान",
    "परीक्षा का दबाव", "पढ़ाई का तनाव", "छात्रों की आत्महत्या", "मानसिक स्वास्थ्य",
    "अवसाद", "अभिभावकों का दबाव", "माता-पिता की अपेक्षाएं", "प्रतियोगी परीक्षा",
    "रैंक की दौड़", "परीक्षा तनाव", "छात्रों का तनाव", "शैक्षणिक तनाव"
]

ALL_KEYWORDS = (
    KEYWORDS_COMPETITIVE_COACHING +
    KEYWORDS_STUDENT_MENTAL_HEALTH +
    KEYWORDS_FAMILY_PARENTAL +
    KEYWORDS_ECONOMIC_SOCIAL +
    KEYWORDS_HINDI
)

# 5 Target Topic Categories
TOPIC_CATEGORIES = {
    "Competitive Exams & Coaching": [
        "kota", "iit-jee", "iit jee", "jee", "neet", "upsc", "coaching institute", "coaching factory",
        "cut-throat competition", "rank obsession", "percentile race", "elimination exam",
        "mock test scores", "mock test", "competitive exam", "competitive examination", "allen", "resonance", "fiitjee"
    ],
    "Student Mental Health": [
        "student suicide", "suicide", "academic stress", "mental health", "depression", "anxiety",
        "exam pressure", "examination stress", "student distress", "psychological pressure",
        "student stress", "study pressure", "student anxiety", "tele-manas", "manodarpan",
        "counseling", "helpline", "distress", "counsellor", "board exam stress", "board examination stress"
    ],
    "Family & Parental Pressure": [
        "parental expectations", "family burden", "family pride", "parents sacrifices",
        "parents' sacrifices", "parents dreams", "parents' dreams", "middle-class aspirations",
        "forced career choice", "academic legacy", "career pressure", "parental pressure",
        "parents pressure", "family expectations", "expectation"
    ],
    "Economic & Social Pressure": [
        "education loan", "financial burden", "social expectations", "societal pressure",
        "education as social mobility", "tuition debt", "loan burden", "poverty", "fees", "fee hike"
    ],
    "Hindi Coverage": [
        "कोटा", "नीट परीक्षा", "आईआईटी जेईई", "यूपीएससी", "कोचिंग संस्थान", "परीक्षा का दबाव",
        "पढ़ाई का तनाव", "छात्रों की आत्महत्या", "मानसिक स्वास्थ्य", "अवसाद", "अभिभावकों का दबाव",
        "माता-पिता की अपेक्षाएं", "प्रतियोगी परीक्षा", "रैंक की दौड़", "परीक्षा तनाव", "छात्रों का तनाव"
    ]
}

# Negative Filtering / False Positive Exclusion Words
NEGATIVE_FILTER_TERMS = [
    "cardiac stress", "stress test", "heart attack", "stock market stress",
    "financial stress test", "bank stress", "cricket stress", "match stress",
    "geopolitical stress", "stress on the border", "crop stress", "drought stress",
    "yield stress", "shear stress", "stress tensor", "mechanical stress", "structural stress",
    "nifty", "sensex", "wall street", "cricket match", "world cup"
]

# Education Context Terms required to validate relevance
EDUCATION_CONTEXT_TERMS = [
    "student", "students", "exam", "exams", "examination", "examinations",
    "school", "schools", "college", "colleges", "university", "universities",
    "cbse", "icse", "board", "jee", "neet", "iit", "upsc", "teacher", "teachers", "parents",
    "education", "academic", "study", "studies", "coaching", "marks", "grade", "kota",
    "aspirant", "aspirants", "syllabus", "hostel", "tuition", "campus",
    "छात्र", "छात्रा", "छात्रों", "परीक्षा", "स्कूल", "कॉलेज", "पढ़ाई", "शिक्षा", "कोचिंग", "प्रतियोगी"
]

# Comprehensive Source Domain Mapping
DOMAIN_SOURCE_MAP = {
    # Major National English Newspapers
    "timesofindia.indiatimes.com": ("The Times of India", "Bennett, Coleman & Co. Ltd. (Times Group)", "Newspaper", "English", "India"),
    "thehindu.com": ("The Hindu", "THG Publishing Pvt. Ltd. (The Hindu Group)", "Newspaper", "English", "India"),
    "hindustantimes.com": ("Hindustan Times", "HT Media Ltd.", "Newspaper", "English", "India"),
    "indianexpress.com": ("The Indian Express", "Indian Express Group", "Newspaper", "English", "India"),
    "economictimes.indiatimes.com": ("The Economic Times", "Bennett, Coleman & Co. Ltd. (Times Group)", "Newspaper", "English", "India"),
    "telegraphindia.com": ("The Telegraph India", "ABP Group", "Newspaper", "English", "India"),
    "deccanherald.com": ("Deccan Herald", "The Printers (Mysore) Pvt. Ltd.", "Newspaper", "English", "India"),
    "tribuneindia.com": ("The Tribune", "The Tribune Trust", "Newspaper", "English", "India"),
    "newindianexpress.com": ("The New Indian Express", "Express Publications (Madurai) Ltd.", "Newspaper", "English", "India"),
    "thestatesman.com": ("The Statesman", "The Statesman Ltd.", "Newspaper", "English", "India"),
    "livemint.com": ("Mint", "HT Media Ltd.", "Newspaper", "English", "India"),
    "business-standard.com": ("Business Standard", "Business Standard Pvt. Ltd.", "Newspaper", "English", "India"),
    "financialexpress.com": ("Financial Express", "Indian Express Group", "Newspaper", "English", "India"),
    "millenniumpost.in": ("Millennium Post", "Millennium Post Ltd.", "Newspaper", "English", "India"),
    "dailypioneer.com": ("The Pioneer", "CMYK Printech Ltd.", "Newspaper", "English", "India"),
    "deccanchronicle.com": ("Deccan Chronicle", "Deccan Chronicle Holdings Ltd.", "Newspaper", "English", "India"),
    "asianage.com": ("The Asian Age", "Deccan Chronicle Holdings Ltd.", "Newspaper", "English", "India"),
    "mid-day.com": ("Mid-Day", "Jagran Prakashan Ltd.", "Newspaper", "English", "India"),
    "ahmedabadmirror.com": ("Ahmedabad Mirror", "Bennett, Coleman & Co. Ltd.", "Newspaper", "English", "India"),
    "bangaloremirror.indiatimes.com": ("Bangalore Mirror", "Bennett, Coleman & Co. Ltd.", "Newspaper", "English", "India"),
    "mumbaimirror.indiatimes.com": ("Mumbai Mirror", "Bennett, Coleman & Co. Ltd.", "Newspaper", "English", "India"),
    "punemirror.com": ("Pune Mirror", "Lexicon Group", "Newspaper", "English", "India"),
    "freepressjournal.in": ("Free Press Journal", "Indian National Press", "Newspaper", "English", "India"),
    "dailyexcelsior.com": ("Daily Excelsior", "Daily Excelsior Group", "Newspaper", "English", "India"),
    "sentinelassam.com": ("The Sentinel", "Omega Printers and Publishers", "Newspaper", "English", "India"),
    "morungexpress.com": ("The Morung Express", "Morung Media", "Newspaper", "English", "India"),

    # Major Hindi Newspapers
    "jagran.com": ("Dainik Jagran", "Jagran Prakashan Ltd.", "Newspaper", "Hindi", "India"),
    "amarujala.com": ("Amar Ujala", "Amar Ujala Publications Ltd.", "Newspaper", "Hindi", "India"),
    "bhaskar.com": ("Dainik Bhaskar", "DB Corp Ltd.", "Newspaper", "Hindi", "India"),
    "livehindustan.com": ("Hindustan", "Hindustan Media Ventures Ltd.", "Newspaper", "Hindi", "India"),
    "navbharattimes.indiatimes.com": ("Navbharat Times", "Bennett, Coleman & Co. Ltd. (Times Group)", "Newspaper", "Hindi", "India"),
    "patrika.com": ("Rajasthan Patrika", "Rajasthan Patrika Pvt. Ltd.", "Newspaper", "Hindi", "India"),
    "prabhatkhabar.com": ("Prabhat Khabar", "Neutral Publishing House Ltd.", "Newspaper", "Hindi", "India"),
    "punjabkesari.in": ("Punjab Kesari", "The Hind Samachar Ltd.", "Newspaper", "Hindi", "India"),
    "jansatta.com": ("Jansatta", "Indian Express Group", "Newspaper", "Hindi", "India"),
    "lokmatnews.in": ("Lokmat Samachar", "Lokmat Media Group", "Newspaper", "Hindi", "India"),
    "haribhoomi.com": ("Hari Bhoomi", "Hari Bhoomi Group", "Newspaper", "Hindi", "India"),
    "deshbandhu.co.in": ("Deshbandhu", "Deshbandhu Media", "Newspaper", "Hindi", "India"),

    # TV News Channels
    "ndtv.com": ("NDTV", "NDTV Convergence Ltd. / Adani Group", "TV News Channel", "English", "India"),
    "ndtv.in": ("NDTV India", "NDTV Convergence Ltd. / Adani Group", "TV News Channel", "Hindi", "India"),
    "indiatoday.in": ("India Today", "Living Media India Ltd. (India Today Group)", "TV News Channel", "English", "India"),
    "aajtak.in": ("Aaj Tak", "Living Media India Ltd. (India Today Group)", "TV News Channel", "Hindi", "India"),
    "abplive.com": ("ABP News", "ABP Network Pvt. Ltd.", "TV News Channel", "Hindi/English", "India"),
    "news18.com": ("News18", "Network18 Media & Investments Ltd.", "TV News Channel", "English/Hindi", "India"),
    "zeenews.india.com": ("Zee News", "Zee Media Corporation Ltd.", "TV News Channel", "Hindi/English", "India"),
    "timesnownews.com": ("Times Now", "Times Network (BCCL)", "TV News Channel", "English", "India"),
    "republicworld.com": ("Republic World / Republic TV", "ARG Outlier Media", "TV News Channel", "English", "India"),
    "wionews.com": ("WION", "Zee Media Corporation Ltd.", "TV News Channel", "English", "India"),
    "cnbctv18.com": ("CNBC-TV18", "Network18 Media", "TV News Channel", "English", "India"),
    "etnownews.com": ("ET Now", "Times Network", "TV News Channel", "English", "India"),
    "indiatvnews.com": ("India TV", "Independent News Service Pvt. Ltd.", "TV News Channel", "Hindi/English", "India"),
    "tv9bharatvarsh.com": ("TV9 Bharatvarsh", "Associated Broadcasting Company", "TV News Channel", "Hindi", "India"),
    "ddnews.gov.in": ("DD News", "Prasar Bharati (Doordarshan)", "TV News Channel", "Hindi/English", "India"),
    "news24online.com": ("News 24", "B.A.G. Films and Media Ltd.", "TV News Channel", "Hindi", "India"),

    # Digital News & Education Portals
    "thequint.com": ("The Quint", "Quint Digital Media Ltd.", "Digital News Portal", "English/Hindi", "India"),
    "scroll.in": ("Scroll.in", "Scroll Media Inc.", "Digital News Portal", "English", "India"),
    "thewire.in": ("The Wire", "Foundation for Independent Journalism", "Digital News Portal", "English/Hindi", "India"),
    "theprint.in": ("The Print", "Printline Media Pvt. Ltd.", "Digital News Portal", "English", "India"),
    "newsclick.in": ("NewsClick", "PPK NewsClick Media Pvt. Ltd.", "Digital News Portal", "English", "India"),
    "firstpost.com": ("Firstpost", "Network18 Media", "Digital News Portal", "English", "India"),
    "outlookindia.com": ("Outlook India", "Outlook Publishing (India) Pvt. Ltd.", "Digital News Portal", "English", "India"),
    "oneindia.com": ("OneIndia", "Greynium Information Technologies", "Digital News Portal", "English/Hindi", "India"),
    "rediff.com": ("Rediff News", "Rediff.com India Ltd.", "Digital News Portal", "English", "India"),
    "bbc.com/hindi": ("BBC News Hindi", "BBC World Service", "Digital News Portal", "Hindi", "India"),
    "careers360.com": ("Careers360 News", "Pathfinder Publishing Pvt. Ltd.", "Digital News Portal", "English", "India"),
    "edexlive.com": ("EdexLive", "The New Indian Express Group", "Digital News Portal", "English", "India"),
    "educationtimes.com": ("Education Times", "Bennett, Coleman & Co. Ltd.", "Digital News Portal", "English", "India"),
    "news9live.com": ("News9Live", "Associated Broadcasting Co. Pvt. Ltd.", "Digital News Portal", "English", "India"),
    "abpeducation.com": ("ABP Education", "ABP Group", "Digital News Portal", "English", "India"),
    "dtnext.in": ("DT Next", "Daily Thanthi Group", "Newspaper", "English", "India"),
    "odishatv.in": ("Odisha TV", "Odisha Television Ltd.", "TV News Channel", "English/Odia", "India")
}

# API Credentials & Settings
MEDIACLOUD_API_KEY = os.environ.get("MEDIACLOUD_API_KEY", "")
GDELT_RATE_LIMIT_DELAY = 6.0  # seconds between consecutive GDELT requests
GOOGLE_NEWS_DELAY = 0.8      # seconds between RSS requests
MAX_RETRIES = 3
REQUEST_TIMEOUT = 25         # seconds

# User Agent for HTTP requests
DEFAULT_HEADERS = {
    "User-Agent": "AcademicStressResearchPipeline/2.0 (Academic Research; Structural Topic Modeling; mailto:researcher@university.ac.in)"
}
