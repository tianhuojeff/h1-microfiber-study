"""Apply reviewed literal-quote repairs to the single working coding table."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from extract_patent_html import extract


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent
MASTER = HERE / "master_technical_coding_v1.json"
REPAIRS = HERE / "method_review" / "coding_group_remaining_quote_repair_20260929.json"
BACKUP = HERE / "history" / "master_before_literal_quote_repair_20260929.json"
CHECK = HERE / "evidence" / "literal_quote_repair_acceptance_20260929.json"


def norm(value: str) -> str:
    return " ".join(value.split())


def main() -> None:
    current = json.loads(MASTER.read_text(encoding="utf-8"))
    proposals = json.loads(REPAIRS.read_text(encoding="utf-8"))["repairs"]
    by_pub = {record["publication"]: record for record in current["records"]}
    checks = []
    seen = set()
    for proposal in proposals:
        key = (proposal["publication"], proposal["field"])
        if key in seen:
            raise ValueError(f"duplicate repair: {key}")
        seen.add(key)
        target = by_pub[key[0]]["fields"][key[1]]
        if target["judgment"] != proposal["judgment"]:
            raise ValueError(f"judgment changed under quote-only repair: {key}")
        if not any("..." in item["quote"] or "…" in item["quote"] for item in target["evidence"]):
            raise ValueError(f"target no longer has an abbreviated quote: {key}")
        for item in proposal["replacement_evidence"]:
            source = Path(item["source_path"])
            if not source.is_absolute():
                source = PROJECT / source
            actual_hash = hashlib.sha256(source.read_bytes()).hexdigest()
            if actual_hash.casefold() != item["source_sha256"].casefold():
                raise ValueError(f"source hash differs: {key}: {source}")
            quote = norm(item["quote"])
            if source.suffix.lower() == ".html":
                match = re.search(r"p\d+|cl\d+", item["locator"], re.I)
                rows = extract(source)["rows"]
                if match:
                    rows = [row for row in rows if row["id"] == match.group(0)]
                if not rows or not any(quote in norm(row["text"]) for row in rows):
                    raise ValueError(f"quote not in identified HTML row: {key}: {item['locator']}")
            elif quote not in norm(source.read_text(encoding="utf-8-sig")):
                raise ValueError(f"quote not in source text: {key}: {item['locator']}")
            checks.append({"publication": key[0], "field": key[1], "locator": item["locator"], "sha256_ok": True, "literal_ok": True})
        target["evidence"] = proposal["replacement_evidence"]
    if len(seen) != 6 or len(checks) != 7:
        raise ValueError(f"unexpected repair count: {len(seen)}, evidence count: {len(checks)}")
    backup_bytes = MASTER.read_bytes()
    if BACKUP.exists() and BACKUP.read_bytes() != backup_bytes:
        raise ValueError("existing backup differs from current master")
    BACKUP.write_bytes(backup_bytes)
    MASTER.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CHECK.write_text(json.dumps({"status": "literal_and_hash_verified_only", "repaired_fields": len(seen), "checked_evidence": checks, "before_sha256": hashlib.sha256(backup_bytes).hexdigest(), "after_sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest()}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"repaired_fields": len(seen), "evidence": len(checks), "master_sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
