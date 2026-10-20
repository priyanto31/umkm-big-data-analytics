-- 1. Validasi jumlah baris dan ID unik
SELECT COUNT(*) AS total_rows,
       COUNT(DISTINCT umkm_id) AS unique_ids
FROM umkm_lab.umkm_performance;

-- 2. Quality checks SQL
SELECT
    COUNT(*) FILTER (WHERE monthly_revenue <= 0) AS invalid_revenue,
    COUNT(*) FILTER (WHERE transaction_count <= 0) AS invalid_transactions,
    COUNT(*) FILTER (WHERE avg_historical_rating NOT BETWEEN 1 AND 5) AS invalid_rating,
    COUNT(*) FILTER (WHERE repeat_order_rate_pct NOT BETWEEN 0 AND 100) AS invalid_repeat_order,
    COUNT(*) FILTER (WHERE digital_adoption_score NOT BETWEEN 0 AND 10) AS invalid_adoption
FROM umkm_lab.umkm_performance;

-- 3. Ringkasan kelas kinerja
SELECT business_class,
       COUNT(*) AS umkm_count,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS class_share_pct,
       ROUND(AVG(monthly_revenue), 2) AS avg_monthly_revenue,
       ROUND(AVG(net_profit_margin_pct), 2) AS avg_profit_margin_pct,
       ROUND(SUM(estimated_monthly_profit), 2) AS total_estimated_profit,
       ROUND(AVG(repeat_order_rate_pct), 2) AS avg_repeat_order_pct,
       ROUND(AVG(digital_adoption_score), 2) AS avg_digital_adoption
FROM umkm_lab.umkm_performance
GROUP BY business_class
ORDER BY avg_monthly_revenue DESC;

-- 4. Cohort umur usaha (dimensi waktu)
SELECT tenure_band,
       COUNT(*) AS umkm_count,
       ROUND(AVG(monthly_revenue), 2) AS avg_monthly_revenue,
       ROUND(AVG(net_profit_margin_pct), 2) AS avg_profit_margin_pct,
       ROUND(AVG(repeat_order_rate_pct), 2) AS avg_repeat_order_pct
FROM umkm_lab.umkm_performance
GROUP BY tenure_band
ORDER BY MIN(business_tenure_months);

-- 5. Adopsi digital dan loyalitas pelanggan
SELECT digital_adoption_band,
       COUNT(*) AS umkm_count,
       ROUND(AVG(repeat_order_rate_pct), 2) AS avg_repeat_order_pct,
       ROUND(AVG(avg_historical_rating), 2) AS avg_rating,
       ROUND(AVG(sentiment_score), 3) AS avg_sentiment,
       ROUND(AVG(net_profit_margin_pct), 2) AS avg_profit_margin_pct
FROM umkm_lab.umkm_performance
GROUP BY digital_adoption_band
ORDER BY MIN(digital_adoption_score);

-- 6. Dampak latensi jam sibuk
SELECT peak_hour_latency,
       COUNT(*) AS umkm_count,
       ROUND(AVG(monthly_revenue), 2) AS avg_monthly_revenue,
       ROUND(AVG(net_profit_margin_pct), 2) AS avg_profit_margin_pct,
       ROUND(AVG(repeat_order_rate_pct), 2) AS avg_repeat_order_pct,
       ROUND(AVG(avg_historical_rating), 2) AS avg_rating
FROM umkm_lab.umkm_performance
GROUP BY peak_hour_latency
ORDER BY CASE peak_hour_latency WHEN 'Low' THEN 1 WHEN 'Med' THEN 2 ELSE 3 END;

-- 7. Profil risiko
SELECT operational_risk,
       COUNT(*) AS umkm_count,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_pct,
       ROUND(AVG(net_profit_margin_pct), 2) AS avg_profit_margin_pct,
       ROUND(AVG(burn_rate_ratio), 3) AS avg_burn_rate
FROM umkm_lab.umkm_performance
GROUP BY operational_risk
ORDER BY CASE operational_risk WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END;

-- 8. Validasi formula metrik turunan
SELECT COUNT(*) AS profit_formula_mismatch
FROM umkm_lab.umkm_performance
WHERE ABS(estimated_monthly_profit - ROUND(monthly_revenue * net_profit_margin_pct / 100, 2)) > 0.01;

-- 9. Audit ETL terakhir
SELECT audit_id, job_name, started_at, finished_at, input_rows, output_rows, status, details
FROM umkm_lab.etl_audit
ORDER BY audit_id DESC
LIMIT 10;

