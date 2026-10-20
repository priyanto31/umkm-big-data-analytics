# Kamus Data

## Kolom sumber

| Kolom sumber | Tipe | Nama terstandar | Makna |
|---|---|---|---|
| ID | integer | umkm_id | ID anonim unik untuk setiap UMKM |
| Monthly_Revenue | integer | monthly_revenue | Estimasi pendapatan bulanan dalam rupiah |
| Net_Profit_Margin (%) | float | net_profit_margin_pct | Margin laba bersih dalam persen |
| Burn_Rate_Ratio | float | burn_rate_ratio | Rasio laju pengeluaran; nilai > 1 digunakan sebagai sinyal risiko |
| Transaction_Count | integer | transaction_count | Jumlah transaksi pada periode observasi |
| Avg_Historical_Rating | float | avg_historical_rating | Rata-rata rating historis (1-5) |
| Review_Text | string | review_text | Ulasan sintetis |
| Review_Volatility | float | review_volatility | Tingkat variasi ulasan/rating |
| Business_Tenure_Months | integer | business_tenure_months | Umur usaha dalam bulan |
| Repeat_Order_Rate (%) | float | repeat_order_rate_pct | Persentase repeat order |
| Digital_Adoption_Score | float | digital_adoption_score | Skor adopsi digital (0-10) |
| Peak_Hour_Latency | category | peak_hour_latency | Latensi jam sibuk: Low, Med, High |
| Location_Competitiveness | integer | location_competitiveness | Indeks kompetisi lokasi |
| Sentiment_Score | float | sentiment_score | Skor sentimen ulasan (-1 sampai 1) |
| Class | category | business_class | Kelas kinerja: Critical, Struggling, Growth, Elite |

## Kolom turunan

| Kolom | Formula/aturan | Tujuan |
|---|---|---|
| estimated_monthly_profit | revenue x margin / 100 | Mendekati nominal laba/rugi bulanan |
| estimated_monthly_cost | revenue - estimated profit | Mendekati biaya bulanan implisit |
| revenue_per_transaction | revenue / transaction count | Membandingkan produktivitas transaksi |
| tenure_years | tenure months / 12 | Umur usaha dalam tahun |
| tenure_band | <2, 2-5, 5-10, >=10 tahun | Cohort temporal tanpa membuat tanggal palsu |
| digital_adoption_band | Rendah, Menengah, Tinggi, Lanjutan | Segmentasi tingkat adopsi digital |
| sentiment_band | Negatif, Netral, Positif | Ringkasan sentimen |
| operational_risk | High, Medium, Low | Gabungan margin negatif dan burn rate > 1 |

`estimated_monthly_profit`, `estimated_monthly_cost`, dan `operational_risk` adalah metrik analitis yang dibuat dalam proyek, bukan kolom resmi dari penyedia dataset.

