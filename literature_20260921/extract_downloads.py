from pathlib import Path
import hashlib
import json
from pypdf import PdfReader

base = Path(__file__).parent
rows = []
for pdf in sorted((base / 'papers').glob('*.pdf')):
    raw = pdf.read_bytes()
    reader = PdfReader(str(pdf))
    text = '\n\n'.join(page.extract_text() or '' for page in reader.pages)
    text_path = base / 'texts' / f'{pdf.stem}.txt'
    text_path.write_text(text, encoding='utf-8')
    rows.append({
        'filename': pdf.name,
        'bytes': len(raw),
        'sha256': hashlib.sha256(raw).hexdigest(),
        'pdf_header': raw[:4].decode('ascii', 'replace'),
        'pages': len(reader.pages),
        'extracted_characters': len(text),
        'text_file': str(text_path),
    })
(base / 'metadata' / 'download_results.json').write_text(
    json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8'
)
print(json.dumps(rows, ensure_ascii=False, indent=2))
