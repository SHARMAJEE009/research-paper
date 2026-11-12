"""
Data Analysis and Scientific Visualization Module.
Academic Research Data Collection Pipeline.
Generates publication-quality charts and computes summary statistics.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from config import OUTPUT_DIR, ALL_YEARS, LOG_FILE

# Ensure console supports UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = logging.getLogger("Analysis")
logger.setLevel(logging.INFO)


def compute_summary_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    df_core = df[df["duplicate_status"].isin(["Original", "Syndicated Duplicate"])].copy()
    if df_core.empty:
        df_core = df.copy()

    total_articles = len(df_core)
    year_counts = df_core["year"].value_counts().reindex(ALL_YEARS, fill_value=0)
    peak_year = int(year_counts.idxmax())
    peak_count = int(year_counts.max())

    news_df = df_core[df_core["newspaper_name"].str.strip() != ""]
    unique_newspapers = news_df["newspaper_name"].nunique()
    top_newspapers = news_df["newspaper_name"].value_counts().head(10).to_dict()

    chan_df = df_core[df_core["news_channel_name"].str.strip() != ""]
    unique_channels = chan_df["news_channel_name"].nunique()
    top_channels = chan_df["news_channel_name"].value_counts().head(10).to_dict()

    unique_publishers = df_core["publisher_name"].nunique()
    top_years = year_counts.sort_values(ascending=False).head(10).to_dict()

    articles_pre_2015 = int(year_counts.loc[:2014].sum())
    articles_post_2015 = int(year_counts.loc[2015:].sum())
    
    logger.info(f"Summary Stats: Total Articles={total_articles}, Peak Year={peak_year} ({peak_count} articles)")
    logger.info(f"Unique Newspapers={unique_newspapers}, Unique Channels={unique_channels}")

    return {
        "total_articles": total_articles,
        "peak_year": peak_year,
        "peak_count": peak_count,
        "unique_newspapers": unique_newspapers,
        "unique_channels": unique_channels,
        "unique_publishers": unique_publishers,
        "top_10_newspapers": top_newspapers,
        "top_10_channels": top_channels,
        "top_10_years": top_years,
        "year_counts": year_counts,
        "articles_pre_2015": articles_pre_2015,
        "articles_post_2015": articles_post_2015
    }


def plot_annual_coverage(df: pd.DataFrame, output_path: Path):
    plt.figure(figsize=(12, 6), dpi=300)
    sns.set_theme(style="whitegrid")
    
    year_counts = df["year"].value_counts().reindex(ALL_YEARS, fill_value=0)
    
    ax = sns.lineplot(
        x=year_counts.index,
        y=year_counts.values,
        marker="o",
        color="#1f77b4",
        linewidth=2.5,
        markersize=6
    )
    
    plt.fill_between(year_counts.index, year_counts.values, alpha=0.15, color="#1f77b4")
    
    peak_yr = int(year_counts.idxmax())
    peak_val = int(year_counts.max())
    if peak_val > 0:
        plt.annotate(
            f"Peak Year: {peak_yr} ({peak_val} articles)",
            xy=(peak_yr, peak_val),
            xytext=(peak_yr - 3, peak_val + max(1, int(peak_val * 0.08))),
            arrowprops=dict(facecolor="#d62728", shrink=0.08, width=1.5, headwidth=6),
            fontweight="bold",
            color="#d62728",
            fontsize=10
        )

    plt.title("Annual Indian News Media Coverage of Academic Stress (2000–2025)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Publication Year", fontsize=12, labelpad=10)
    plt.ylabel("Number of Articles Published", fontsize=12, labelpad=10)
    plt.xticks(ALL_YEARS, rotation=45, ha="right", fontsize=9)
    plt.ylim(bottom=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved chart: {output_path}")


def plot_top_newspapers(df: pd.DataFrame, output_path: Path):
    news_df = df[df["newspaper_name"].str.strip() != ""]
    if news_df.empty:
        news_df = df[df["publisher_name"].str.strip() != ""]
        col_to_plot = "publisher_name"
        title_label = "Publishers"
    else:
        col_to_plot = "newspaper_name"
        title_label = "Newspapers"

    top15 = news_df[col_to_plot].value_counts().head(15)
    if top15.empty:
        return

    plt.figure(figsize=(12, 7), dpi=300)
    sns.set_theme(style="whitegrid")
    
    ax = sns.barplot(
        x=top15.values,
        y=top15.index,
        hue=top15.index,
        palette="Blues_r",
        edgecolor="black",
        linewidth=0.5,
        legend=False
    )
    
    for i, v in enumerate(top15.values):
        ax.text(v + max(0.5, top15.max() * 0.01), i, f" {v}", va="center", fontsize=10, fontweight="bold")

    plt.title(f"Top 15 Indian {title_label} by Academic Stress Coverage (2000–2025)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Number of Articles Published", fontsize=12, labelpad=10)
    plt.ylabel(title_label, fontsize=12, labelpad=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved chart: {output_path}")


def plot_year_newspaper_heatmap(df: pd.DataFrame, output_path: Path):
    news_df = df[df["newspaper_name"].str.strip() != ""]
    if news_df.empty:
        news_df = df[df["publisher_name"].str.strip() != ""]
        entity_col = "publisher_name"
    else:
        entity_col = "newspaper_name"

    top10_entities = news_df[entity_col].value_counts().head(10).index.tolist()
    if not top10_entities:
        return

    filtered = news_df[news_df[entity_col].isin(top10_entities)]
    matrix = pd.crosstab(filtered["year"], filtered[entity_col]).reindex(ALL_YEARS, fill_value=0)

    # Focus on active period for readability
    active_years = matrix[matrix.sum(axis=1) > 0].index
    if len(active_years) > 0:
        min_yr = max(2000, active_years.min() - 1)
        matrix = matrix.loc[min_yr:]

    plt.figure(figsize=(14, 8), dpi=300)
    sns.set_theme(style="white")
    
    ax = sns.heatmap(
        matrix.T,
        cmap="YlGnBu",
        annot=True,
        fmt="d",
        linewidths=0.5,
        cbar_kws={"label": "Article Count"}
    )
    
    plt.title("Coverage Matrix: Year vs Top Indian Newspapers (2000–2025)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Year", fontsize=12, labelpad=10)
    plt.ylabel("Newspaper Name", fontsize=12, labelpad=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved heatmap: {output_path}")


def plot_keyword_frequency(df: pd.DataFrame, output_path: Path):
    kw_counts = df["matched_keyword"].value_counts().head(15)
    if kw_counts.empty:
        return

    plt.figure(figsize=(12, 6), dpi=300)
    sns.set_theme(style="whitegrid")
    
    ax = sns.barplot(
        x=kw_counts.values,
        y=kw_counts.index,
        hue=kw_counts.index,
        palette="crest",
        edgecolor="black",
        linewidth=0.5,
        legend=False
    )
    
    for i, v in enumerate(kw_counts.values):
        ax.text(v + max(0.5, kw_counts.max() * 0.01), i, f" {v}", va="center", fontsize=10, fontweight="bold")

    plt.title("Frequency of Academic Stress Research Keywords in Indian Media", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Number of Articles Matched", fontsize=12, labelpad=10)
    plt.ylabel("Research Keyword / Theme", fontsize=12, labelpad=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved chart: {output_path}")


def run_full_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    stats = compute_summary_statistics(df)
    plot_annual_coverage(df, OUTPUT_DIR / "annual_coverage_trend.png")
    plot_top_newspapers(df, OUTPUT_DIR / "top_newspapers_bar.png")
    plot_year_newspaper_heatmap(df, OUTPUT_DIR / "year_newspaper_heatmap.png")
    plot_keyword_frequency(df, OUTPUT_DIR / "keyword_frequency_bar.png")
    return stats
