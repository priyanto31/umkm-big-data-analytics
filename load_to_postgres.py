"""Loader idempoten CSV UMKM ke PostgreSQL 15 dengan audit log."""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

from run_pipeline import CSV_PATH, quality_checks, transform_umkm


load_dotenv(Path(__file__).resolve().parent / ".env")


def get_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE", "big_data_umkm_lab"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.environ["PGPASSWORD"],
        sslmode=os.getenv("PGSSLMODE", "disable"),
    )


def main() -> None:
    if "PGPASSWORD" not in os.environ:
        raise RuntimeError("PGPASSWORD belum diatur. Salin .env.example menjadi .env lalu isi kredensial.")
    raw = pd.read_csv(CSV_PATH)
    df = transform_umkm(raw)
    checks = quality_checks(df)
    if not all(checks.values()):
        raise ValueError(f"Quality gate gagal: {[key for key, value in checks.items() if not value]}")

    columns = [
        "umkm_id", "monthly_revenue", "net_profit_margin_pct", "burn_rate_ratio",
        "transaction_count", "avg_historical_rating", "review_text", "review_volatility",
        "business_tenure_months", "repeat_order_rate_pct", "digital_adoption_score",
        "peak_hour_latency", "location_competitiveness", "sentiment_score", "business_class",
        "estimated_monthly_profit", "estimated_monthly_cost", "revenue_per_transaction",
        "tenure_years", "tenure_band", "digital_adoption_band", "sentiment_band", "operational_risk",
    ]
    records = [tuple(row) for row in df[columns].astype(object).where(pd.notna(df[columns]), None).to_numpy()]
    conn = get_connection()
    conn.autocommit = False
    cur = conn.cursor()
    started_at = datetime.now(timezone.utc)
    cur.execute(
        """
        INSERT INTO umkm_lab.etl_audit(job_name, started_at, input_rows, status, details)
        VALUES (%s, %s, %s, 'RUNNING', %s) RETURNING audit_id
        """,
        ("umkm_csv_bulk_load", started_at, len(df), "Memulai idempotent bulk load"),
    )
    audit_id = cur.fetchone()[0]
    conn.commit()
    try:
        started = time.perf_counter()
        cur.execute("TRUNCATE TABLE umkm_lab.umkm_performance")
        query = f"""
            INSERT INTO umkm_lab.umkm_performance ({', '.join(columns)})
            VALUES %s ON CONFLICT (umkm_id) DO NOTHING
        """
        execute_values(cur, query, records, page_size=5000)
        cur.execute("SELECT COUNT(*) FROM umkm_lab.umkm_performance")
        output_rows = cur.fetchone()[0]
        if output_rows != len(df):
            raise ValueError(f"Jumlah baris database {output_rows:,} tidak sama dengan input {len(df):,}")
        duration = time.perf_counter() - started
        cur.execute(
            """
            UPDATE umkm_lab.etl_audit
            SET finished_at=%s, output_rows=%s, status='SUCCESS', details=%s
            WHERE audit_id=%s
            """,
            (datetime.now(timezone.utc), output_rows, f"Selesai dalam {duration:.2f} detik", audit_id),
        )
        conn.commit()
        print(f"SUCCESS: {output_rows:,} baris dimuat dalam {duration:.2f} detik")
    except Exception as exc:
        conn.rollback()
        cur.execute(
            """
            UPDATE umkm_lab.etl_audit
            SET finished_at=%s, status='FAILED', details=%s WHERE audit_id=%s
            """,
            (datetime.now(timezone.utc), str(exc)[:1000], audit_id),
        )
        conn.commit()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()

