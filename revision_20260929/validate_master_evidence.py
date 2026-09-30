"""Check literal anchors and file identities in the working H1 coding table."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from extract_patent_html import extract


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent
MASTER = HERE / "master_technical_coding_v1.json"
OUTPUT = HERE / "evidence" / "master_evidence_acceptance_20260929_v2.json"
MANUAL_PDF_NOTE = HERE / "evidence" / "WO2024199585A1_原页人工回读.md"


def norm(value: str) -> str:
    return " ".join(value.split())


def main() -> None:
    table = json.loads(MASTER.read_text(encoding="utf-8"))
    cache = {}
    errors = []
    verified = 0
    manual_pdf = 0
    for record in table["records"]:
        for field_name, field in record["fields"].items():
            key = f"{record['publication']}/{field_name}"
            if field["judgment"] in {"explicit", "inferred"} and not field["evidence"]:
                errors.append({"key": key, "reason": "assertive judgment without evidence"})
            for evidence in field["evidence"]:
                source = Path(evidence["source_path"])
                if not source.is_absolute():
                    source = PROJECT / source
                if not source.exists():
                    errors.append({"key": key, "reason": "source missing", "path": str(source)})
                    continue
                digest = hashlib.sha256(source.read_bytes()).hexdigest()
                if digest.casefold() != evidence["source_sha256"].casefold():
                    errors.append({"key": key, "reason": "source hash mismatch", "path": str(source)})
                    continue
                if source.suffix.lower() == ".pdf":
                    if not MANUAL_PDF_NOTE.exists() or source.name != "WO2024199585A1.pdf":
                        errors.append({"key": key, "reason": "no matching manual PDF review"})
                    else:
                        manual_pdf += 1
                    continue
                quote = norm(evidence["quote"])
                if source.suffix.lower() == ".html":
                    if source not in cache:
                        cache[source] = extract(source)["rows"]
                    rows = cache[source]
                    row_id = evidence.get("html_id")
                    if not row_id:
                        candidate = re.search(r"(?:zh-)?cl\d+|p\d+", evidence["locator"], re.I)
                        row_id = candidate.group(0) if candidate else None
                    if row_id:
                        rows = [row for row in rows if row["id"] == row_id]
                    if not any(quote in norm(row["text"]) for row in rows):
                        errors.append({"key": key, "reason": "quote not in anchored HTML row", "locator": evidence["locator"], "html_id": row_id})
                        continue
                elif source.suffix.lower() == ".txt":
                    if quote not in norm(source.read_text(encoding="utf-8-sig")):
                        errors.append({"key": key, "reason": "quote not literal in text source", "locator": evidence["locator"]})
                        continue
                else:
                    errors.append({"key": key, "reason": "unsupported source type", "path": str(source)})
                    continue
                verified += 1
    result = {"status": "literal_and_hash_checked_not_semantic_final", "records": len(table["records"]), "field_count": sum(len(r["fields"]) for r in table["records"]), "literal_verified": verified, "pdf_manual_prior_review": manual_pdf, "errors": errors, "master_sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest(), "final_statistics_allowed": table["final_statistics_allowed"]}
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"literal_verified": verified, "pdf_manual_prior_review": manual_pdf, "errors": len(errors), "output": str(OUTPUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
