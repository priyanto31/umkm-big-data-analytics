-- PostgreSQL 15 - jalankan pada database praktikum big_data_umkm_lab.
-- Pembuatan database dilakukan terpisah sebagai administrator:
-- CREATE DATABASE big_data_umkm_lab;

CREATE SCHEMA IF NOT EXISTS umkm_lab;

CREATE TABLE IF NOT EXISTS umkm_lab.umkm_performance (
    umkm_id BIGINT PRIMARY KEY,
    monthly_revenue NUMERIC(18,2) NOT NULL CHECK (monthly_revenue > 0),
    net_profit_margin_pct NUMERIC(7,2) NOT NULL CHECK (net_profit_margin_pct BETWEEN -100 AND 100),
    burn_rate_ratio NUMERIC(8,3) NOT NULL CHECK (burn_rate_ratio > 0),
    transaction_count INTEGER NOT NULL CHECK (transaction_count > 0),
    avg_historical_rating NUMERIC(4,2) NOT NULL CHECK (avg_historical_rating BETWEEN 1 AND 5),
    review_text TEXT NOT NULL,
    review_volatility NUMERIC(6,3) NOT NULL CHECK (review_volatility >= 0),
    business_tenure_months INTEGER NOT NULL CHECK (business_tenure_months > 0),
    repeat_order_rate_pct NUMERIC(7,2) NOT NULL CHECK (repeat_order_rate_pct BETWEEN 0 AND 100),
    digital_adoption_score NUMERIC(5,2) NOT NULL CHECK (digital_adoption_score BETWEEN 0 AND 10),
    peak_hour_latency VARCHAR(8) NOT NULL CHECK (peak_hour_latency IN ('Low', 'Med', 'High')),
    location_competitiveness INTEGER NOT NULL CHECK (location_competitiveness >= 0),
    sentiment_score NUMERIC(6,3) NOT NULL CHECK (sentiment_score BETWEEN -1 AND 1),
    business_class VARCHAR(20) NOT NULL CHECK (business_class IN ('Critical', 'Struggling', 'Growth', 'Elite')),
    estimated_monthly_profit NUMERIC(18,2) NOT NULL,
    estimated_monthly_cost NUMERIC(18,2) NOT NULL,
    revenue_per_transaction NUMERIC(18,2) NOT NULL,
    tenure_years NUMERIC(7,2) NOT NULL,
    tenure_band VARCHAR(20) NOT NULL,
    digital_adoption_band VARCHAR(20) NOT NULL,
    sentiment_band VARCHAR(10) NOT NULL,
    operational_risk VARCHAR(10) NOT NULL CHECK (operational_risk IN ('Low', 'Medium', 'High')),
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_umkm_class ON umkm_lab.umkm_performance(business_class);
CREATE INDEX IF NOT EXISTS idx_umkm_tenure_band ON umkm_lab.umkm_performance(tenure_band);
CREATE INDEX IF NOT EXISTS idx_umkm_adoption_band ON umkm_lab.umkm_performance(digital_adoption_band);
CREATE INDEX IF NOT EXISTS idx_umkm_risk ON umkm_lab.umkm_performance(operational_risk);

CREATE TABLE IF NOT EXISTS umkm_lab.etl_audit (
    audit_id BIGSERIAL PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ,
    input_rows BIGINT,
    output_rows BIGINT,
    status VARCHAR(20) NOT NULL CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED')),
    details TEXT
);

