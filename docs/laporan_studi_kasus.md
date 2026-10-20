# Laporan Studi Kasus Big Data: UMKM Performance & Resilience Analytics

**Nama:** [Isi nama mahasiswa]  
**NIM:** [Isi NIM]  
**Kelas/Kelompok:** [Isi kelas atau kelompok]  
**Tanggal:** [Isi tanggal pengumpulan]

## 1. Rumusan masalah

UMKM memiliki karakteristik finansial, transaksi, pengalaman pelanggan, tingkat adopsi digital, dan risiko operasional yang berbeda. Studi ini menjawab:

1. Bagaimana distribusi kelas kinerja UMKM dan apa ciri finansial tiap kelas?
2. Apakah tingkat adopsi digital berkaitan dengan repeat order, rating, sentimen, dan margin?
3. Kelompok mana yang memiliki risiko operasional tinggi berdasarkan margin dan burn rate?
4. Bagaimana kinerja berbeda menurut umur usaha dan latensi jam sibuk?
5. Rekomendasi bisnis apa yang dapat diturunkan dari hasil agregasi?

Analisis bersifat deskriptif dan diagnostik. Label `Class` sudah ada pada dataset dan tidak dipakai untuk melatih model prediksi.

## 2. Dataset dan pemahaman data

Dataset publik sintetis berasal dari Kaggle, berisi 150.000 baris dan 15 kolom. Seluruh ID unik dan tidak ditemukan nilai kosong. Variabel mencakup pendapatan, margin, burn rate, transaksi, rating, teks ulasan, volatilitas ulasan, umur usaha, repeat order, adopsi digital, latensi, kompetisi lokasi, sentimen, dan kelas kinerja.

Dataset tidak memiliki kolom tanggal observasi. Agar tidak menciptakan data palsu, dimensi waktu direpresentasikan sebagai cohort umur usaha (`tenure_band`), bukan tren kalender. Ini menjadi keterbatasan utama studi.

## 3. Arsitektur dan metode

```text
CSV Kaggle
   -> profiling Pandas + SQL
   -> quality gates
   -> transformasi PySpark
   -> Parquet Snappy (data lake)
   -> PostgreSQL 15 (data mart, opsional sesuai akses lab)
   -> Matplotlib + insight + rekomendasi
```

Transformasi utama:

1. Standarisasi nama dan tipe kolom.
2. Perhitungan estimasi laba, estimasi biaya, dan pendapatan per transaksi.
3. Pembentukan cohort umur usaha dan segmen adopsi digital.
4. Klasifikasi sentimen serta risiko operasional.

Quality checks meliputi ukuran dataset, keunikan ID, missing value, validitas rentang numerik/kategori, nilai positif, dan konsistensi formula laba turunan.

## 4. Hasil utama

Hasil terukur setelah pipeline dijalankan tersimpan di `output/insights_summary.md`, `output/validation_report.json`, dan folder `output/aggregates/`. Ringkasan angka utama:

- 150.000 baris berhasil diproses dan diverifikasi kembali dari Parquet.
- Komposisi kelas adalah `Growth` 85.678 UMKM (57,12%), `Struggling` 41.571 (27,71%), `Critical` 12.561 (8,37%), dan `Elite` 10.190 (6,79%).
- Sebanyak 44,40% UMKM memiliki margin laba bersih negatif dan 38,93% masuk risiko operasional tinggi menurut aturan proyek.
- `Elite` memiliki pendapatan bulanan rata-rata tertinggi sekitar Rp10,02 juta dan margin rata-rata tertinggi 23,24%. Sebaliknya, margin rata-rata `Critical` adalah -24,66%.
- Repeat order rata-rata meningkat dari 16,82% pada adopsi digital rendah menjadi 30,03% pada adopsi digital lanjutan.
- Korelasi Pearson antara skor adopsi digital dan repeat order adalah 0,4050. Hubungan ini tergolong asosiasi positif sedang dan tidak boleh dianggap sebagai bukti sebab-akibat.
- Risiko tinggi terkonsentrasi pada `Critical` (97,87%) dan `Struggling` (95,08%), sedangkan tidak ada baris `Elite` yang memenuhi definisi risiko tinggi proyek.

Tiga grafik utama:

1. Distribusi kelas kinerja UMKM.
2. Perbandingan pendapatan dan margin rata-rata per kelas.
3. Repeat order rata-rata menurut tingkat adopsi digital.

## 5. Validasi dan performa

Pipeline menerapkan 13 quality gates dan menghentikan proses jika satu saja gagal. Output Parquet dibaca ulang untuk membandingkan jumlah baris dan keunikan ID. Benchmark Pandas dilakukan tiga kali per ukuran pada 10.000, 100.000, dan 150.000 baris; nilai yang dilaporkan adalah median waktu transformasi.

Eksperimen 1.000.000 baris tidak dilakukan karena dataset sumber berisi 150.000 baris. Replikasi data untuk mengejar angka 1 juta sengaja dihindari karena dapat memberi gambaran kinerja yang tidak representatif. Notebook PySpark tetap menunjukkan pola komputasi terdistribusi yang dapat diskalakan.

## 6. Rekomendasi bisnis

1. Prioritaskan pendampingan arus kas bagi UMKM dengan margin negatif sekaligus burn rate di atas 1.
2. Jalankan program adopsi digital bertahap dan ukur perubahan repeat order, rating, dan sentimen setelah intervensi.
3. Investigasi bottleneck pada UMKM dengan latensi tinggi, terutama proses transaksi pada jam sibuk.
4. Bedakan dukungan bagi UMKM baru dan matang berdasarkan cohort umur usaha.
5. Gunakan hasil sebagai dasar segmentasi awal, lalu validasi dengan data longitudinal sebelum membuat keputusan kredit atau investasi.

## 7. Keterbatasan

- Data bersifat sintetis sehingga tidak otomatis mewakili seluruh populasi UMKM Indonesia.
- Tidak tersedia tanggal atau wilayah; analisis tren kalender dan geografis tidak dapat dilakukan.
- Definisi teknis beberapa skor berasal dari penyedia dataset dan perlu dokumentasi tambahan untuk interpretasi operasional.
- Hubungan antarvariabel tidak membuktikan sebab-akibat.
- Estimasi laba dihitung dari pendapatan x margin dan bukan laporan keuangan audit.

## 8. Kesimpulan

Studi ini membangun pipeline analitik end-to-end yang dapat direproduksi untuk 150.000 baris data UMKM. Implementasi memenuhi komponen Pandas/SQL, PySpark, transformasi bisnis, quality gates, agregasi, Parquet, rancangan PostgreSQL, tiga visualisasi, validasi, benchmark, insight, dan rekomendasi. Penggunaan cohort umur usaha menjaga analisis tetap jujur terhadap data karena tidak membuat tanggal yang tidak tersedia.

## Referensi

1. ZkyFauzi, *UMKM Dataset*, Kaggle: https://www.kaggle.com/datasets/zkyfauzi/umkm-dataset
2. Ruhyana, *Big Data Sales Analytics*, GitHub: https://github.com/ruhyana/big-data-sales-analytics
3. Apache Spark Documentation: https://spark.apache.org/docs/latest/api/python/
4. PostgreSQL 15 Documentation: https://www.postgresql.org/docs/15/
