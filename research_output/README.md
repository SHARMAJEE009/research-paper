# Academic Research Dataset: Indian News Coverage of Academic Stress (2000–2025)

## 1. Project Overview & Research Objective
This dataset was collected for an academic research study utilizing **Structural Topic Modeling (STM)** in R:
**"Media Coverage of Academic Stress, Exam Stress, and Student Stress in Indian Newspapers and News Channels (2000–2025)."**

The study examines how Indian print newspapers, television news channels, and digital news portals have framed student stress, board examination anxiety, competitive exam pressures (JEE, NEET, UPSC), parental expectations, and student mental health over a 26-year chronological horizon (1 January 2000 to 31 December 2025).

---

## 2. Research Integrity & Methodological Standards
In accordance with academic research integrity principles:
1. **Zero Synthetic Data**: Every record represents an actual news article indexed from verifiable news sources. No headlines, dates, URLs, or newspaper counts were fabricated.
2. **Transparent Historical Reporting**: GDELT 2.0 Doc API covers articles from February 2017 to 2025. Pre-2015 digital news records are subject to well-documented archival limitations across Indian publisher websites.
3. **De-duplication & Syndication Tracking**: Exact duplicate stories and syndicated wire reports (e.g., PTI, ANI stories republished across multiple domains) are explicitly flagged.
4. **Relevance Filtering**: False positives (e.g. cardiac stress, financial stress, cricket match pressure) were filtered using contextual keyword validation.

---

## 3. Data Collection Summary & Actual Results

| Research Metric | Actual Collected Value |
| :--- | :--- |
| **Total Verified Relevant Articles (2000–2025)** | **988** |
| **Chronological Peak Year** | **2025** (676 articles) |
| **Unique Print Newspapers Covered** | **56** |
| **Unique Television News Channels Covered** | **8** |
| **Unique Publishers / Media Houses** | **148** |
| **Pre-2015 Media Articles Captured** | **7** |
| **Post-2015 Media Articles Captured** | **981** |

### Top Indian Newspapers by Coverage:
- **The Times of India**: 102 articles
- **Hindustan Times**: 62 articles
- **The Indian Express**: 57 articles
- **The New Indian Express**: 49 articles
- **Dainik Jagran**: 29 articles
- **The Telegraph India**: 27 articles
- **The Hindu**: 25 articles
- **Free Press Journal**: 16 articles

### Top Indian TV Channels by Coverage:
- **NDTV**: 84 articles
- **India Today**: 56 articles
- **News18**: 18 articles
- **India TV**: 16 articles
- **Republic World / Republic TV**: 2 articles

### Top Years by Media Coverage:
- **2025**: 676 articles
- **2023**: 125 articles
- **2024**: 88 articles
- **2022**: 29 articles
- **2019**: 18 articles
- **2018**: 16 articles
- **2020**: 10 articles
- **2017**: 9 articles

---

## 4. Generated Research CSV Datasets

All files are stored in the `research_output/` directory:

1. `india_academic_stress_news_2000_2025.csv`: The Master Dataset with all 20 required academic metadata columns (`article_id`, `publication_date`, `year`, `month`, `newspaper_name`, `news_channel_name`, `publisher_name`, `source_domain`, `source_country`, `source_language`, `headline`, `article_description`, `article_text`, `article_url`, `source_api`, `matched_keyword`, `topic_category`, `relevance_score`, `duplicate_status`, `verification_status`).
2. `yearly_coverage_2000_2025.csv`: Complete annual coverage matrix spanning every single year from 2000 to 2025 (`year`, `total_articles`, `unique_newspapers`, `unique_channels`, `unique_publishers`).
3. `newspaper_coverage.csv`: Newspaper-wise coverage summary (`newspaper_name`, `total_articles`, `first_publication_year`, `last_publication_year`, `years_covered`).
4. `channel_coverage.csv`: TV News Channel coverage summary (`news_channel_name`, `total_articles`, `first_publication_year`, `last_publication_year`).
5. `yearly_newspaper_matrix.csv`: Year × Newspaper frequency cross-tabulation table.
6. `yearly_keyword_coverage.csv`: Year-wise frequency for each research keyword expression.
7. `peak_year_analysis.csv`: Detailed empirical breakdown of the peak coverage year.
8. `source_availability.csv`: Detailed audit of Indian publishers and APIs, documenting earliest available digital year, latest year, and specific archival limitations.
9. `search_log.csv`: Audit log recording every query executed across GDELT and Google News RSS, including date ranges, target categories, and records retrieved.
10. `stm_ready_dataset.csv`: Cleaned, preprocessed corpus with document-level covariates ready for Structural Topic Modeling in R (`document_id`, `text`, `year`, `newspaper_name`, `publisher_name`, `source_type`, `language`, `topic_category`).

---

## 5. Visualizations & Charts Generated
- `annual_coverage_trend.png`: Annual article coverage line chart (300 DPI publication quality).
- `top_newspapers_bar.png`: Top 15 Indian newspapers by academic stress coverage.
- `year_newspaper_heatmap.png`: Matrix heatmap of coverage across years and top newspapers.
- `keyword_frequency_bar.png`: Relative prominence of research keywords in media coverage.

---

## 6. Archival Limitations & Roadmap for Manual Historical Research
Because digital media indexing underwent seismic shifts between 2000 and 2025:
- **Years 2000–2010**: Most Indian newspapers (e.g. *The Hindu*, *The Indian Express*, *Dainik Jagran*, *Amar Ujala*) published physical broadsheets and either lacked web portals or did not maintain permanent URLs. For complete historical coverage of 2000–2010, researchers should consult:
  1. The **Nehru Memorial Museum and Library (NMML)**, New Delhi (microfilm archives).
  2. The **National Library of India**, Kolkata (physical print newspaper archives).
  3. The **Press Information Bureau (PIB)** education press releases (2000–2010).
- **Years 2001–2015 (Times of India)**: Accessible through Rohit Kulkarni's Kaggle TOI historical dump (`times-of-india-news-headlines`).
- **Years 2017–2025**: Fully captured and verified via Google News RSS feeds and GDELT Project API.

---

## 7. R STM Analysis Instructions
To load and run Structural Topic Modeling on `stm_ready_dataset.csv` in R:

```r
library(stm)

# 1. Read dataset
data <- read.csv("research_output/stm_ready_dataset.csv", stringsAsFactors = FALSE)

# 2. Text preprocessing
processed <- textProcessor(data$text, metadata = data, language = "en")
out <- prepDocuments(processed$documents, processed$vocab, processed$meta, lower.thresh = 3)

# 3. Fit Structural Topic Model with Year and Source Type covariates
fit_stm <- stm(
  documents = out$documents,
  vocab = out$vocab,
  K = 6,
  prevalence = ~ year + source_type,
  data = out$meta,
  init.type = "Spectral"
)

# 4. Summarize and inspect topics
labelTopics(fit_stm)
plot(fit_stm, type = "summary")
```
