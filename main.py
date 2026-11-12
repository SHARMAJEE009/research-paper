"""
Main Orchestration Script for Indian News Coverage of Academic Stress (2000-2025).
Executes the expanded research data pipeline:
1. Data Collection across 5 Keyword Groups (GDELT, Google News RSS, Media Cloud)
2. Merging with existing dataset & headline-similarity deduplication
3. Statistical Analysis & Publication-Ready Visualizations
4. Generation of all Research CSV files, search_log.csv, and STM dataset
"""

import sys
import logging
from datetime import datetime
import pandas as pd
from config import OUTPUT_DIR, LOG_FILE, SEARCH_LOG_FILE
from data_collection import run_all_collections
from data_cleaning import load_existing_dataset, process_and_deduplicate
from analysis import run_full_analysis
from export_csv import export_all

# Configure UTF-8 encoding on Windows console
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

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("PipelineMain")


def run_pipeline():
    logger.info("=" * 70)
    logger.info("STARTING EXPANDED INDIAN ACADEMIC STRESS NEWS PIPELINE (2000-2025)")
    logger.info("Target: Expand to >= 1,500 Unique Genuine Articles Across 5 Groups")
    logger.info("=" * 70)

    start_time = datetime.now()

    # -------------------------------------------------------------
    # Step 1: Ingest Existing Master Dataset for Seamless Merging
    # -------------------------------------------------------------
    logger.info("[STEP 1/5] Loading existing verified dataset from storage...")
    existing_records = load_existing_dataset()
    logger.info(f"Loaded {len(existing_records)} existing verified articles as baseline.")

    # -------------------------------------------------------------
    # Step 2: Data Collection Across 5 Groups
    # -------------------------------------------------------------
    logger.info("[STEP 2/5] Harvesting new records across 5 keyword groups from APIs & archives...")
    raw_records, search_logger = run_all_collections()
    logger.info(f"Raw records harvested across all collectors: {len(raw_records)}")

    # -------------------------------------------------------------
    # Step 3: Cleaning, Normalizing, Merging & Headline Deduplication
    # -------------------------------------------------------------
    logger.info("[STEP 3/5] Merging, validating relevance, and deduplicating (URL & Headline similarity)...")
    verified_articles = process_and_deduplicate(raw_records, existing_records)
    logger.info(f"Total unique, genuine, verified articles after merge: {len(verified_articles)}")

    if not verified_articles:
        logger.error("No valid records available. Exiting pipeline.")
        return

    df = pd.DataFrame(verified_articles)
    logger.info(f"Master DataFrame assembled with {len(df)} rows and {len(df.columns)} columns.")

    # -------------------------------------------------------------
    # Step 4: Statistical Analysis & Visualizations
    # -------------------------------------------------------------
    logger.info("[STEP 4/5] Performing statistical analysis and rendering charts...")
    stats = run_full_analysis(df)

    # -------------------------------------------------------------
    # Step 5: Export Research CSVs & Documentation
    # -------------------------------------------------------------
    logger.info("[STEP 5/5] Exporting all research CSV files, search_log.csv, and STM dataset...")
    export_all(df, stats, OUTPUT_DIR)

    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"Pipeline executed successfully in {elapsed:.1f} seconds.")

    # -------------------------------------------------------------
    # Final Summary Table
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("           RESEARCH PIPELINE EXPANDED EXECUTION REPORT           ")
    print("=" * 70)
    tot_art = stats['total_articles']
    target_status = 'TARGET MET' if tot_art >= 1500 else f"{tot_art}/1500"
    print(f"Total Verified Unique Articles (2000–2025)    : {tot_art}")
    print(f"Target Achievement (>= 1,500 Articles)        : {target_status}")
    print(f"Actual Peak Coverage Year                     : {stats['peak_year']} ({stats['peak_count']} articles)")
    print(f"Number of Unique Print Newspapers             : {stats['unique_newspapers']}")
    print(f"Number of Unique Television News Channels     : {stats['unique_channels']}")
    print(f"Number of Unique Media Houses / Publishers    : {stats['unique_publishers']}")
    print(f"Pre-2015 Articles (Historical Archive Scope)  : {stats['articles_pre_2015']}")
    print(f"Post-2015 Articles (Digital Modern Scope)     : {stats['articles_post_2015']}")
    print("-" * 70)
    print("TOP 5 KEYWORD CATEGORIES DISTRIBUTION:")
    cat_counts = df['topic_category'].value_counts()
    for cat, cnt in cat_counts.items():
        pct = (cnt / len(df)) * 100
        print(f"  - {cat:<32} : {cnt} articles ({pct:.1f}%)")
    print("-" * 70)
    print("TOP NEWSPAPERS BY ARTICLE COUNT:")
    for rank, (name, count) in enumerate(list(stats['top_10_newspapers'].items())[:8], 1):
        print(f"  {rank}. {name:<35} : {count} articles")
    print("-" * 70)
    print("TOP TV CHANNELS BY ARTICLE COUNT:")
    for rank, (name, count) in enumerate(list(stats.get('top_10_channels', {}).items())[:5], 1):
        print(f"  {rank}. {name:<35} : {count} articles")
    print("-" * 70)
    print("TOP YEARS BY MEDIA COVERAGE:")
    for rank, (yr, count) in enumerate(list(stats['top_10_years'].items())[:6], 1):
        print(f"  {rank}. Year {yr:<30} : {count} articles")
    print("-" * 70)
    print("GENERATED RESEARCH ARTIFACTS IN research_output/:")
    print("  - india_academic_stress_news_2000_2025.csv (Master Dataset - 20 columns)")
    print("  - yearly_coverage_2000_2025.csv (Full 2000-2025 Continuous Matrix)")
    print("  - newspaper_coverage.csv")
    print("  - channel_coverage.csv")
    print("  - yearly_newspaper_matrix.csv")
    print("  - yearly_keyword_coverage.csv")
    print("  - peak_year_analysis.csv")
    print("  - source_availability.csv")
    print("  - search_log.csv (Documenting all queries, date ranges & yield)")
    print("  - stm_ready_dataset.csv (Ready for Structural Topic Modeling in R)")
    print("  - annual_coverage_trend.png (300 DPI)")
    print("  - top_newspapers_bar.png (300 DPI)")
    print("  - year_newspaper_heatmap.png (300 DPI)")
    print("  - keyword_frequency_bar.png (300 DPI)")
    print("  - README.md (Academic Documentation & Methodology)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_pipeline()
