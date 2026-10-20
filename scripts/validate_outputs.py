"""Validasi ulang dataset sumber dan artefak pipeline."""

import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from run_pipeline import PARQUET_PATH, CSV_PATH, quality_checks, transform_umkm  # noqa: E402


raw = pd.read_csv(CSV_PATH)
df = transform_umkm(raw)
checks = quality_checks(df)
checks["parquet_exists"] = PARQUET_PATH.exists()
if PARQUET_PATH.exists():
    parquet = pd.read_parquet(PARQUET_PATH)
    checks["parquet_row_count_matches"] = len(parquet) == len(df)
    checks["parquet_ids_unique"] = bool(parquet["umkm_id"].is_unique)
else:
    checks["parquet_row_count_matches"] = False
    checks["parquet_ids_unique"] = False

for name, passed in checks.items():
    print(f"{'PASS' if passed else 'FAIL'}: {name}")
if not all(checks.values()):
    raise SystemExit("Validasi gagal.")

report = json.loads((ROOT / "output" / "validation_report.json").read_text(encoding="utf-8"))
assert report["all_checks_passed"] is True
print(f"Semua validasi lulus untuk {len(df):,} baris.")
