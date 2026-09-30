"""Integrate reviewed Chinese summaries without changing source evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MASTER = HERE / "master_technical_coding_v1.json"
GROUP_A = HERE / "matrix_audit" / "summary_semantic_readback_suggestions.json"
GROUP_B = HERE / "method_review" / "coding_group_remaining_chinese_summary_suggestions_20260929.json"
BACKUP = HERE / "history" / "master_before_semantic_summaries_20260929.json"
CHECK = HERE / "evidence" / "semantic_summaries_acceptance_20260929.json"


def main() -> None:
    table = json.loads(MASTER.read_text(encoding="utf-8"))
    by_pub = {record["publication"]: record for record in table["records"]}
    seen = set()
    modified = []
    for record in json.loads(GROUP_A.read_text(encoding="utf-8"))["records"]:
        pub = record["publication"]
        if pub == "WO2024199585A1":
            # PDF-backed fields were checked separately after this group's snapshot.
            continue
        for suggestion in record["fields"]:
            key = (pub, suggestion["field"])
            if key in seen:
                raise ValueError(f"duplicate summary {key}")
            seen.add(key)
            field = by_pub[pub]["fields"][key[1]]
            proposed = suggestion["proposed_judgment"]
            if key == ("WO2024250011A1", "chamber_drainage"):
                if field["judgment"] != "explicit" or proposed != "unresolved":
                    raise ValueError("unexpected drainage downgrade state")
                field["judgment"] = "unresolved"
                field["unknown_reason"] = "原文只说明非使用时翻起设备借重力排水；未说明维护前过滤腔残液排空。"
            elif field["judgment"] != proposed:
                raise ValueError(f"unexpected judgment mismatch {key}: {field['judgment']} != {proposed}")
            new_summary = suggestion["proposed_summary"]
            if not new_summary:
                raise ValueError(f"empty summary {key}")
            if field["summary"] != new_summary:
                field["summary"] = new_summary
                modified.append(key)
    for record in json.loads(GROUP_B.read_text(encoding="utf-8"))["records"]:
        pub = record["publication"]
        for field_name, suggestion in record["fields"].items():
            key = (pub, field_name)
            if key in seen:
                raise ValueError(f"duplicate summary {key}")
            seen.add(key)
            field = by_pub[pub]["fields"][field_name]
            if field["judgment"] != suggestion["judgment"]:
                raise ValueError(f"unexpected judgment mismatch {key}")
            new_summary = suggestion["summary_zh"]
            if not new_summary:
                raise ValueError(f"empty summary {key}")
            if field["summary"] != new_summary:
                field["summary"] = new_summary
                modified.append(key)
            if "review_scope" in suggestion and field["judgment"] == "not_found":
                field["review_scope"] = suggestion["review_scope"]
    if len(seen) != 81:
        raise ValueError(f"expected 9 records x 9 fields, got {len(seen)}")
    removal = by_pub["CN118273060A"]["fields"]["removal"]
    removal["removal_object"] = ["filter_element"]
    removal["unknown_reason"] = ""
    removal["review_scope"] = "权16可移出滤器组；未据此推断有独立集渣腔或已实测取渣。"
    before = MASTER.read_bytes()
    if BACKUP.exists() and BACKUP.read_bytes() != before:
        raise ValueError("existing backup differs from current master")
    BACKUP.write_bytes(before)
    MASTER.write_text(json.dumps(table, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = {"status": "summary_and_semantic_scope_integrated_not_final", "reviewed_fields": len(seen), "summaries_modified": len(modified), "drainage_downgraded": "WO2024250011A1/chamber_drainage", "removal_object_corrected": "CN118273060A/filter_element", "before_sha256": hashlib.sha256(before).hexdigest(), "after_sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest()}
    CHECK.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
