"""Pipeline lokal Big Data UMKM Performance & Resilience Analytics."""

from __future__ import annotations

import json
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "synthetic_umkm_data.csv"
OUTPUT_DIR = BASE_DIR / "output"
CHARTS_DIR = OUTPUT_DIR / "charts"
AGG_DIR = OUTPUT_DIR / "aggregates"
PARQUET_PATH = OUTPUT_DIR / "parquet" / "umkm_transformed.parquet"

COLUMN_MAP = {
    "ID": "umkm_id",
    "Monthly_Revenue": "monthly_revenue",
    "Net_Profit_Margin (%)": "net_profit_margin_pct",
    "Burn_Rate_Ratio": "burn_rate_ratio",
    "Transaction_Count": "transaction_count",
    "Avg_Historical_Rating": "avg_historical_rating",
    "Review_Text": "review_text",
    "Review_Volatility": "review_volatility",
    "Business_Tenure_Months": "business_tenure_months",
    "Repeat_Order_Rate (%)": "repeat_order_rate_pct",
    "Digital_Adoption_Score": "digital_adoption_score",
    "Peak_Hour_Latency": "peak_hour_latency",
    "Location_Competitiveness": "location_competitiveness",
    "Sentiment_Score": "sentiment_score",
    "Class": "business_class",
}

TENURE_LABELS = ["<2 tahun", "2-5 tahun", "5-10 tahun", ">=10 tahun"]
ADOPTION_LABELS = ["Rendah", "Menengah", "Tinggi", "Lanjutan"]
CLASS_ORDER = ["Critical", "Struggling", "Growth", "Elite"]


def transform_umkm(raw: pd.DataFrame) -> pd.DataFrame:
    """Standarkan nama kolom dan bentuk metrik bisnis turunan."""
    df = raw.rename(columns=COLUMN_MAP).copy()
    missing_columns = sorted(set(COLUMN_MAP.values()) - set(df.columns))
    if missing_columns:
        raise ValueError(f"Kolom wajib tidak ditemukan: {missing_columns}")

    numeric_columns = [
        "umkm_id",
        "monthly_revenue",
        "net_profit_margin_pct",
        "burn_rate_ratio",
        "transaction_count",
        "avg_historical_rating",
        "review_volatility",
        "business_tenure_months",
        "repeat_order_rate_pct",
        "digital_adoption_score",
        "location_competitiveness",
        "sentiment_score",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["estimated_monthly_profit"] = (
        df["monthly_revenue"] * df["net_profit_margin_pct"] / 100
    ).round(2)
    df["estimated_monthly_cost"] = (
        df["monthly_revenue"] - df["estimated_monthly_profit"]
    ).round(2)
    df["revenue_per_transaction"] = (
        df["monthly_revenue"] / df["transaction_count"]
    ).round(2)
    df["tenure_years"] = (df["business_tenure_months"] / 12).round(2)
    df["tenure_band"] = pd.cut(
        df["business_tenure_months"],
        bins=[0, 24, 60, 120, np.inf],
        labels=TENURE_LABELS,
        right=False,
    )
    df["digital_adoption_band"] = pd.cut(
        df["digital_adoption_score"],
        bins=[0, 3, 6, 8, np.inf],
        labels=ADOPTION_LABELS,
        right=False,
    )
    df["sentiment_band"] = np.select(
        [df["sentiment_score"] < 0, df["sentiment_score"] > 0],
        ["Negatif", "Positif"],
        default="Netral",
    )
    df["operational_risk"] = np.select(
        [
            (df["net_profit_margin_pct"] < 0) & (df["burn_rate_ratio"] > 1),
            (df["net_profit_margin_pct"] < 0) | (df["burn_rate_ratio"] > 1),
        ],
        ["High", "Medium"],
        default="Low",
    )
    return df


def quality_checks(df: pd.DataFrame) -> dict[str, bool]:
    """Quality gate yang dapat dipakai ulang oleh runner dan validator."""
    required = list(COLUMN_MAP.values())
    return {
        "minimum_100k_rows": len(df) >= 100_000,
        "unique_umkm_id": bool(df["umkm_id"].is_unique),
        "no_missing_required": not bool(df[required].isna().any().any()),
        "monthly_revenue_positive": bool((df["monthly_revenue"] > 0).all()),
        "transaction_count_positive": bool((df["transaction_count"] > 0).all()),
        "profit_margin_valid": bool(df["net_profit_margin_pct"].between(-100, 100).all()),
        "rating_in_1_to_5": bool(df["avg_historical_rating"].between(1, 5).all()),
        "repeat_order_in_0_to_100": bool(df["repeat_order_rate_pct"].between(0, 100).all()),
        "digital_adoption_in_0_to_10": bool(df["digital_adoption_score"].between(0, 10).all()),
        "positive_burn_rate": bool((df["burn_rate_ratio"] > 0).all()),
        "valid_latency_category": bool(set(df["peak_hour_latency"]).issubset({"Low", "Med", "High"})),
        "valid_business_class": bool(set(df["business_class"]).issubset(set(CLASS_ORDER))),
        "derived_profit_formula": bool(
            np.allclose(
                df["estimated_monthly_profit"],
                (df["monthly_revenue"] * df["net_profit_margin_pct"] / 100).round(2),
                atol=0.01,
            )
        ),
    }


def build_aggregates(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    class_summary = (
        df.groupby("business_class", observed=True)
        .agg(
            umkm_count=("umkm_id", "count"),
            avg_monthly_revenue=("monthly_revenue", "mean"),
            avg_profit_margin_pct=("net_profit_margin_pct", "mean"),
            total_estimated_profit=("estimated_monthly_profit", "sum"),
            avg_repeat_order_pct=("repeat_order_rate_pct", "mean"),
            avg_digital_adoption=("digital_adoption_score", "mean"),
            avg_rating=("avg_historical_rating", "mean"),
            high_risk_count=("operational_risk", lambda s: int((s == "High").sum())),
        )
        .reindex(CLASS_ORDER)
        .reset_index()
    )
    class_summary["class_share_pct"] = (class_summary["umkm_count"] / len(df) * 100).round(2)
    class_summary["high_risk_pct"] = (
        class_summary["high_risk_count"] / class_summary["umkm_count"] * 100
    ).round(2)

    tenure_summary = (
        df.groupby("tenure_band", observed=False)
        .agg(
            umkm_count=("umkm_id", "count"),
            avg_monthly_revenue=("monthly_revenue", "mean"),
            avg_profit_margin_pct=("net_profit_margin_pct", "mean"),
            avg_repeat_order_pct=("repeat_order_rate_pct", "mean"),
            avg_digital_adoption=("digital_adoption_score", "mean"),
        )
        .reindex(TENURE_LABELS)
        .reset_index()
    )

    adoption_summary = (
        df.groupby("digital_adoption_band", observed=False)
        .agg(
            umkm_count=("umkm_id", "count"),
            avg_monthly_revenue=("monthly_revenue", "mean"),
            avg_profit_margin_pct=("net_profit_margin_pct", "mean"),
            avg_repeat_order_pct=("repeat_order_rate_pct", "mean"),
            avg_rating=("avg_historical_rating", "mean"),
            avg_sentiment=("sentiment_score", "mean"),
        )
        .reindex(ADOPTION_LABELS)
        .reset_index()
    )

    latency_summary = (
        df.groupby("peak_hour_latency", observed=True)
        .agg(
            umkm_count=("umkm_id", "count"),
            avg_monthly_revenue=("monthly_revenue", "mean"),
            avg_profit_margin_pct=("net_profit_margin_pct", "mean"),
            avg_repeat_order_pct=("repeat_order_rate_pct", "mean"),
            avg_rating=("avg_historical_rating", "mean"),
        )
        .reindex(["Low", "Med", "High"])
        .reset_index()
    )
    return {
        "class_summary": class_summary,
        "tenure_summary": tenure_summary,
        "digital_adoption_summary": adoption_summary,
        "latency_summary": latency_summary,
    }


def save_charts(aggregates: dict[str, pd.DataFrame]) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    colors = ["#C44E52", "#DD8452", "#4C72B0", "#55A868"]
    class_summary = aggregates["class_summary"]

    fig, ax = plt.subplots(figsize=(9, 5), dpi=140)
    bars = ax.bar(class_summary["business_class"], class_summary["umkm_count"], color=colors)
    ax.set_title("Distribusi Kelas Kinerja UMKM", fontweight="bold")
    ax.set_xlabel("Kelas UMKM")
    ax.set_ylabel("Jumlah UMKM")
    for bar, value in zip(bars, class_summary["umkm_count"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{int(value):,}", ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "01_distribusi_kelas_umkm.png", bbox_inches="tight")
    plt.close(fig)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=140)
    ax1.bar(class_summary["business_class"], class_summary["avg_monthly_revenue"] / 1_000_000, color=colors)
    ax1.set_title("Rata-rata Pendapatan Bulanan", fontweight="bold")
    ax1.set_ylabel("Juta Rupiah")
    ax1.tick_params(axis="x", rotation=20)
    ax2.bar(class_summary["business_class"], class_summary["avg_profit_margin_pct"], color=colors)
    ax2.axhline(0, color="black", linewidth=0.8)
    ax2.set_title("Rata-rata Margin Laba Bersih", fontweight="bold")
    ax2.set_ylabel("Persen")
    ax2.tick_params(axis="x", rotation=20)
    fig.suptitle("Kinerja Finansial menurut Kelas UMKM", fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "02_kinerja_finansial_per_kelas.png", bbox_inches="tight")
    plt.close(fig)

    adoption = aggregates["digital_adoption_summary"]
    fig, ax = plt.subplots(figsize=(9, 5), dpi=140)
    bars = ax.bar(adoption["digital_adoption_band"].astype(str), adoption["avg_repeat_order_pct"], color="#4C72B0")
    ax.set_title("Repeat Order menurut Tingkat Adopsi Digital", fontweight="bold")
    ax.set_xlabel("Kelompok Adopsi Digital")
    ax.set_ylabel("Rata-rata Repeat Order (%)")
    for bar, value in zip(bars, adoption["avg_repeat_order_pct"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.2f}%", ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "03_adopsi_digital_dan_repeat_order.png", bbox_inches="tight")
    plt.close(fig)


def benchmark(raw: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for size in (10_000, 100_000, len(raw)):
        sample = raw.head(size).copy()
        timings = []
        for _ in range(3):
            started = time.perf_counter()
            transformed = transform_umkm(sample)
            _ = transformed.groupby("business_class")["estimated_monthly_profit"].sum()
            timings.append(time.perf_counter() - started)
        rows.append({"engine": "Pandas", "rows": size, "median_transform_seconds": round(float(np.median(timings)), 4), "runs": 3})
    return pd.DataFrame(rows).drop_duplicates(subset=["engine", "rows"])


def write_insights(df: pd.DataFrame, aggregates: dict[str, pd.DataFrame]) -> dict[str, object]:
    class_summary = aggregates["class_summary"].set_index("business_class")
    adoption = aggregates["digital_adoption_summary"].set_index("digital_adoption_band")
    high_risk_share = float((df["operational_risk"] == "High").mean() * 100)
    loss_share = float((df["net_profit_margin_pct"] < 0).mean() * 100)
    top_revenue_class = str(class_summary["avg_monthly_revenue"].idxmax())
    top_margin_class = str(class_summary["avg_profit_margin_pct"].idxmax())
    low_repeat = float(adoption.loc["Rendah", "avg_repeat_order_pct"])
    advanced_repeat = float(adoption.loc["Lanjutan", "avg_repeat_order_pct"])
    correlations = df[["digital_adoption_score", "repeat_order_rate_pct", "net_profit_margin_pct", "monthly_revenue"]].corr(numeric_only=True)
    digital_repeat_corr = float(correlations.loc["digital_adoption_score", "repeat_order_rate_pct"])

    insights = {
        "rows": int(len(df)),
        "loss_making_share_pct": round(loss_share, 2),
        "high_operational_risk_share_pct": round(high_risk_share, 2),
        "top_average_revenue_class": top_revenue_class,
        "top_average_margin_class": top_margin_class,
        "repeat_order_low_adoption_pct": round(low_repeat, 2),
        "repeat_order_advanced_adoption_pct": round(advanced_repeat, 2),
        "digital_adoption_repeat_order_correlation": round(digital_repeat_corr, 4),
    }
    lines = [
        "# Ringkasan Insight Otomatis",
        "",
        f"- Dataset berisi **{len(df):,} UMKM** tanpa ID duplikat dan tanpa nilai kosong pada kolom wajib.",
        f"- Sebanyak **{loss_share:.2f}%** UMKM memiliki margin laba bersih negatif.",
        f"- Sebanyak **{high_risk_share:.2f}%** masuk risiko operasional tinggi (margin negatif sekaligus burn rate > 1).",
        f"- Kelas dengan rata-rata pendapatan bulanan tertinggi adalah **{top_revenue_class}**; margin rata-rata tertinggi juga **{top_margin_class}**.",
        f"- Repeat order rata-rata berubah dari **{low_repeat:.2f}%** pada adopsi digital rendah menjadi **{advanced_repeat:.2f}%** pada tingkat lanjutan.",
        f"- Korelasi Pearson adopsi digital dan repeat order adalah **{digital_repeat_corr:.4f}**; ini adalah asosiasi, bukan bukti sebab-akibat.",
        "",
        "## Rekomendasi",
        "",
        "1. Prioritaskan pendampingan arus kas untuk UMKM berisiko tinggi, terutama margin negatif dengan burn rate di atas 1.",
        "2. Segmentasikan program adopsi digital berdasarkan kesiapan usaha dan ukur dampaknya pada repeat order serta rating.",
        "3. Tinjau bottleneck pada kelompok latensi tinggi melalui analisis proses checkout dan kapasitas layanan jam sibuk.",
        "4. Gunakan cohort umur usaha untuk membedakan kebutuhan UMKM baru dan matang; jangan menafsirkannya sebagai tren kalender.",
    ]
    (OUTPUT_DIR / "insights_summary.md").write_text("\n".join(lines), encoding="utf-8")
    return insights


def main() -> None:
    print("=" * 72)
    print("BIG DATA UMKM PERFORMANCE & RESILIENCE ANALYTICS")
    print("=" * 72)
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Dataset tidak ditemukan: {CSV_PATH}")
    for directory in (OUTPUT_DIR, CHARTS_DIR, AGG_DIR, PARQUET_PATH.parent):
        directory.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    raw = pd.read_csv(CSV_PATH)
    read_seconds = time.perf_counter() - started
    print(f"[1/6] CSV dibaca: {len(raw):,} baris ({read_seconds:.2f} detik)")

    started = time.perf_counter()
    df = transform_umkm(raw)
    transform_seconds = time.perf_counter() - started
    print(f"[2/6] Transformasi selesai ({transform_seconds:.2f} detik)")

    checks = quality_checks(df)
    for name, passed in checks.items():
        print(f"      {'PASS' if passed else 'FAIL'} - {name}")
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"Quality gate gagal: {failed}")
    print("[3/6] Semua quality gate lulus")

    aggregates = build_aggregates(df)
    for name, table in aggregates.items():
        table.to_csv(AGG_DIR / f"{name}.csv", index=False)
    save_charts(aggregates)
    print("[4/6] Empat agregasi dan tiga grafik disimpan")

    parquet_started = time.perf_counter()
    df.to_parquet(PARQUET_PATH, index=False, compression="snappy")
    parquet_write_seconds = time.perf_counter() - parquet_started
    readback = pd.read_parquet(PARQUET_PATH)
    if len(readback) != len(df) or not readback["umkm_id"].is_unique:
        raise ValueError("Validasi baca ulang Parquet gagal")
    print(f"[5/6] Parquet Snappy diverifikasi: {len(readback):,} baris")

    benchmark_df = benchmark(raw)
    benchmark_df.to_csv(OUTPUT_DIR / "performance_benchmark.csv", index=False)
    insights = write_insights(df, aggregates)
    validation_report = {
        "dataset": str(CSV_PATH.name),
        "input_rows": int(len(raw)),
        "output_rows": int(len(df)),
        "read_seconds": round(read_seconds, 4),
        "transform_seconds": round(transform_seconds, 4),
        "parquet_write_seconds": round(parquet_write_seconds, 4),
        "checks": checks,
        "all_checks_passed": all(checks.values()),
        "parquet_readback_rows_match": len(readback) == len(df),
        "insights": insights,
    }
    (OUTPUT_DIR / "validation_report.json").write_text(
        json.dumps(validation_report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("[6/6] Benchmark, insight, dan laporan validasi disimpan")
    print("Pipeline selesai dengan sukses.")


if __name__ == "__main__":
    main()

