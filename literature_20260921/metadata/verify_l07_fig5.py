"""Read-only reproduction of the paper's Figure 5 summary, using supplied data."""
from pathlib import Path
from collections import defaultdict
from statistics import mean, stdev
import hashlib
import json
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "supplements/hamann2025_data.xlsx"
EXPECTED_HASH = "99682d2076b04c72402462e132ec9c69ba1f112bfa11f3ae3f9d016502f8444e"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED_HASH
sheet = load_workbook(SOURCE, data_only=True, read_only=True)["filtration-efficiency"]
rows = iter(sheet.values)
header = next(rows)
groups = defaultdict(list)
for excel_row, values in enumerate(rows, 2):
    row = dict(zip(header, values))
    row["excel_row"] = excel_row
    if (row["inlet"] == "snail" and row["FiF_length"] in ("Large", "DE")
            and row["Vol_filt_L"] == 20 and row["mesh_size_µm"] == 100):
        groups[(row["analyst"], row["trial"], row["FiF_length"])].append(row)

trials = []
for key, group in groups.items():
    assert len(group) == 3
    parts = {row["name"]: row for row in group}
    assert set(parts) == {"concentrate", "retentate", "permeate"}
    totals = {row["recovery_ABS"] for row in group}
    assert len(totals) == 1
    total = totals.pop()
    assert total > 0
    trials.append({
        "analyst": key[0], "trial": key[1], "filter": key[2],
        "source_rows": [row["excel_row"] for row in group],
        "ER_percent": 100 * (1 - parts["permeate"]["P_diff_g"] / total),
        "EC_percent": 100 * parts["concentrate"]["P_diff_g"] / total,
        "retentate_percent": 100 * parts["retentate"]["P_diff_g"] / total,
        "concentrate_volume_L": parts["concentrate"]["sample_vol_L"],
        "recovery_percent": group[0]["recovery_REL"],
    })
summaries = {}
for kind in ("Large", "DE"):
    subset = [row for row in trials if row["filter"] == kind]
    assert len(subset) == 5
    summaries[kind] = {
        "n": 5,
        **{field: {"mean": mean(row[field] for row in subset),
                   "sample_sd": stdev(row[field] for row in subset)}
           for field in ("ER_percent", "EC_percent", "retentate_percent",
                         "concentrate_volume_L", "recovery_percent")},
    }
result = {
    "source_sha256": EXPECTED_HASH,
    "method": "Use stored P_diff_g numerator and stored recovery_ABS denominator. ER uses 1-MP/total. Reported component masses are rounded; do not replace the supplied denominator with their rounded sum.",
    "scope": "Figure 5 primary summary only; not a full audit of every figure or preprocessing decision.",
    "summaries": summaries, "trials": trials,
}
(ROOT / "metadata/L07_fig5_reproduction.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summaries, ensure_ascii=False, indent=2))
