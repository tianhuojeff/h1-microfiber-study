"""Merge four source-checked conflict decisions into the working coding table."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from extract_patent_html import extract


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent
MASTER = HERE / "master_technical_coding_v1.json"
PROPOSALS = HERE / "matrix_audit" / "pending_field_evidence_suggestions.json"
BACKUP = HERE / "history" / "master_before_conflict_evidence_20260929.json"
CHECK = HERE / "evidence" / "conflict_evidence_acceptance_20260929.json"

SUMMARIES = {
    ("CN118273060A", "seals_connections"): "权1明确帽构件与入口开口边缘密封接合，操作构件又使封头板与帽构件密封接合；仅描述该版本的连接与密封结构。",
    ("WO2022084677A1", "removal"): "说明书[0097]明确公开可拆卸的截留物收集腔以便倒空；该处用may，属于可选实施例，并非所有方案必备。",
    ("WO2022084677A1", "state_switch"): "在平面滤介质可选实施例中，过滤后可转第二构型、移动接触元件，再恢复第一构型；不外推至其他实施例。",
    ("WO2024250011A1", "seals_connections"): "说明书[0007]公开两半外壳可用柔性卡扣、螺钉或铰接连接；这只证明连接方式，未从本段证明液密。",
}


def normalized(text: str) -> str:
    return " ".join(text.split())


def main() -> None:
    table = json.loads(MASTER.read_text(encoding="utf-8"))
    records = {record["publication"]: record for record in table["records"]}
    proposals = json.loads(PROPOSALS.read_text(encoding="utf-8"))["records"]
    changed = []
    for record in proposals:
        pub = record["publication"]
        for field in record["fields"]:
            key = (pub, field["field"])
            if key not in SUMMARIES:
                continue
            target = records[pub]["fields"][key[1]]
            if target["judgment"] != "unresolved" or field["recommended_judgment"] != "explicit":
                raise ValueError(f"unexpected transition: {key}")
            checked = []
            for item in field["evidence"]:
                source = Path(item["source_path"])
                if not source.is_absolute():
                    source = PROJECT / source
                digest = hashlib.sha256(source.read_bytes()).hexdigest()
                if digest.casefold() != item["source_sha256"].casefold():
                    raise ValueError(f"hash mismatch: {key}")
                locator = re.search(r"(?:zh-)?cl\d+|p\d+", item["locator"], re.I)
                if not locator:
                    raise ValueError(f"no HTML row locator: {key}")
                row_id = locator.group(0)
                rows = [row for row in extract(source)["rows"] if row["id"] == row_id]
                if len(rows) != 1 or normalized(item["quote"]) not in normalized(rows[0]["text"]):
                    raise ValueError(f"quote does not match specified row: {key}: {row_id}")
                checked.append({**item, "source_path": str(source.resolve())})
            target["judgment"] = "explicit"
            target["summary"] = SUMMARIES[key]
            target["evidence"] = checked
            target["unknown_reason"] = ""
            target["review_scope"] = "此公开版本的所引权项或说明书段落；可选实施例不外推为全部方案。"
            changed.append({"publication": pub, "field": key[1], "locator": checked[0]["locator"]})
    if set(SUMMARIES) != {(item["publication"], item["field"]) for item in changed}:
        raise ValueError("not all four expected decisions were found")
    before = MASTER.read_bytes()
    if BACKUP.exists() and BACKUP.read_bytes() != before:
        raise ValueError("existing backup differs from current master")
    BACKUP.write_bytes(before)
    MASTER.write_text(json.dumps(table, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CHECK.write_text(json.dumps({"status": "literal_hash_and_bounded_semantic_review", "changed": changed, "before_sha256": hashlib.sha256(before).hexdigest(), "after_sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest()}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"changed": len(changed), "master_sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
