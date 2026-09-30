"""Update the conservative R1 register with CNIPA publication-version facts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REGISTER = HERE / "official_status_register_20260929.json"
FACTS = HERE / "cnipa_authoritative_document_version_check_20260929.json"
ARCHIVE = HERE / "raw_official_20260929" / "CN_quanweiwendang_20260630.zip"
BACKUP = HERE.parent / "history" / "official_status_register_before_cnipa_versions.json"
OUTPUT = HERE / "cnipa_version_register_acceptance_20260929.json"


def main() -> None:
    source = json.loads(FACTS.read_text(encoding="utf-8"))
    expected_hash = source["source"]["raw_file_sha256"].casefold()
    actual_hash = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    if actual_hash != expected_hash:
        raise ValueError("CNIPA archive identity mismatch")
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    by_pub = {record["sample"]: record for record in register["records"]}
    changed = []
    for item in source["records"]:
        pub = item["sample"]
        record = by_pub[pub]
        if record["status_as_of"] != "unknown":
            raise ValueError(f"unexpected non-unknown status: {pub}")
        docs = item["official_document_records"]
        if not docs:
            continue
        record["official_version_source"] = {
            "authority": "CNIPA authoritative document through 2026-06-30",
            "download_url": source["source"]["download_url"],
            "archive_sha256": actual_hash,
            "records": docs,
            "checked_at": "2026-09-29",
        }
        bs = [entry for entry in docs if entry.split(",")[2] == "B"]
        if bs:
            if len(bs) != 1:
                raise ValueError(f"ambiguous B-version: {pub}")
            record["grant_no"] = pub[:-1] + "B"
            record["official_record"] = "CNIPA authoritative document confirms A and B publication rows; individual current legal-status record remains unread (PSS HTTP 412)."
            record["supports"] = "A/B publication-version and publication-date facts only."
            record["gap"] = "Read individual CNIPA register/legal-status and maintenance history as of the analysis date."
        else:
            record["official_record"] = "CNIPA authoritative document confirms the A publication row; individual current legal-status record remains unread (PSS HTTP 412)."
            record["supports"] = "A publication-version and publication-date fact only."
        record["does_not_support"] = "Current validity, maintenance, lapse, withdrawal, or pending status."
        changed.append(pub)
    if len(changed) != 8:
        raise ValueError(f"expected eight CN publication records, got {len(changed)}")
    before = REGISTER.read_bytes()
    if BACKUP.exists() and BACKUP.read_bytes() != before:
        raise ValueError("existing backup differs from current register")
    BACKUP.write_bytes(before)
    REGISTER.write_text(json.dumps(register, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = {"changed_publications": changed, "B_versions": [pub for pub in changed if by_pub[pub]["grant_no"]], "all_status_unknown": all(r["status_as_of"] == "unknown" for r in register["records"]), "source_sha256": actual_hash, "register_sha256": hashlib.sha256(REGISTER.read_bytes()).hexdigest()}
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
