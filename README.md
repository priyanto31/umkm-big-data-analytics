# Big Data UMKM Performance & Resilience Analytics

Proyek studi kasus Big Data Analytics untuk menganalisis kinerja, ketahanan finansial, adopsi digital, loyalitas pelanggan, dan risiko operasional UMKM menggunakan 150.000 baris data sintetis.

Struktur dan alurnya diadaptasi dari proyek referensi [big-data-sales-analytics](https://github.com/ruhyana/big-data-sales-analytics), lalu disesuaikan penuh dengan skema UMKM dari [Kaggle](https://www.kaggle.com/datasets/zkyfauzi/umkm-dataset).

## Tujuan analisis

1. Membandingkan profil keuangan dan operasional antara kelas `Elite`, `Growth`, `Struggling`, dan `Critical`.
2. Mengukur hubungan adopsi digital dengan repeat order, rating, sentimen, dan profitabilitas.
3. Mengidentifikasi indikator risiko dari margin negatif, burn rate tinggi, dan latensi jam sibuk.
4. Menilai pola kinerja berdasarkan kelompok umur usaha sebagai dimensi waktu/cohort.
5. Menghasilkan pipeline yang dapat direproduksi: CSV -> Pandas/PySpark -> validasi -> Parquet/PostgreSQL -> visualisasi.

## Struktur proyek

```text
umkm-big-data-analytics/
|-- .env.example
|-- README.md
|-- requirements.txt
|-- run_pipeline.py
|-- load_to_postgres.py
|-- data/
|   `-- synthetic_umkm_data.csv
|-- notebooks/
|   |-- 01_exploration.ipynb
|   |-- 02_pyspark_transform.ipynb
|   `-- 03_etl_validation.ipynb
|-- sql/
|   |-- postgresql15_setup.sql
|   `-- analysis_queries.sql
|-- scripts/
|   `-- validate_outputs.py
|-- docs/
|   |-- data_dictionary.md
|   `-- laporan_studi_kasus.md
`-- output/
    |-- charts/
    |-- parquet/
    |-- aggregates/
    |-- validation_report.json
    `-- performance_benchmark.csv
```

## Menjalankan proyek

Prasyarat: Python 3.11 atau 3.12. Untuk notebook PySpark lokal gunakan JDK 17.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run_pipeline.py
python scripts\validate_outputs.py
```

Pipeline lokal menghasilkan tiga grafik, empat tabel agregasi, dataset tertransformasi dalam Parquet Snappy, laporan validasi JSON, ringkasan insight, dan benchmark Pandas pada 10 ribu, 100 ribu, dan 150 ribu baris.

## Notebook

1. `01_exploration.ipynb`: data understanding, profiling, quality gate, KPI, dan visualisasi Pandas.
2. `02_pyspark_transform.ipynb`: schema eksplisit, transformasi bisnis, validasi, serta agregasi PySpark.
3. `03_etl_validation.ipynb`: ETL Parquet, read-back validation, benchmark, dan contoh load PostgreSQL yang aman.

Notebook mendeteksi struktur folder proyek lokal. Di Google Colab, upload CSV ke `/content/synthetic_umkm_data.csv` lalu sesuaikan variabel `CSV_PATH` jika diperlukan.

## PostgreSQL

1. Buat database praktikum dan jalankan `sql/postgresql15_setup.sql` pada database tersebut.
2. Salin `.env.example` menjadi `.env`, lalu isi kredensial milik sendiri.
3. Jalankan `python load_to_postgres.py`.
4. Gunakan `sql/analysis_queries.sql` untuk validasi dan analisis data mart.

Password tidak pernah ditulis di notebook atau source code. PostgreSQL bersifat opsional sampai koneksi lab tersedia; Parquet tetap menjadi output utama yang sudah dapat diuji secara lokal.

## Catatan metodologis

Dataset tidak memiliki tanggal observasi. Karena itu proyek tidak membuat tanggal sintetis. `business_tenure_months` dipakai sebagai dimensi waktu/cohort melalui `tenure_years` dan `tenure_band`. Konsekuensinya, hasil tidak dapat ditafsirkan sebagai tren kalender atau perubahan dari bulan ke bulan.

Label `Class` sudah tersedia dari sumber. Proyek menggunakannya sebagai dimensi deskriptif, bukan target untuk membangun model machine learning, sesuai batas tugas yang menekankan analitik deskriptif dan diagnostik.

## Sumber

- Dataset: https://www.kaggle.com/datasets/zkyfauzi/umkm-dataset
- Referensi struktur: https://github.com/ruhyana/big-data-sales-analytics

