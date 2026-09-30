from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json, urllib.request, urllib.error

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'cn115637570_probe_20260929_2112'
OUT.mkdir(exist_ok=True)
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def get(label, url, suffix):
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    dest = OUT / (label + suffix)
    if dest.exists():
        raise RuntimeError('No repeated requests or evidence overwrite: ' + str(dest))
    rec = {'label': label, 'requested_url': url, 'observed_at': now, 'login_session': False}
    try:
        with urllib.request.urlopen(url, timeout=25) as response:
            body = response.read()
            rec.update(http_status=response.status, final_url=response.url, content_type=response.headers.get('Content-Type'))
    except urllib.error.HTTPError as error:
        body = error.read()
        rec.update(http_status=error.code, final_url=error.url, error=str(error), content_type=error.headers.get('Content-Type'))
    except Exception as error:
        body = str(error).encode('utf-8')
        rec.update(http_status=None, error=repr(error))
    dest.write_bytes(body)
    rec.update(path=str(dest), bytes=len(body), sha256=digest(dest))
    return rec

records = []
records.append(get('CN115637570A_original', 'https://patentimages.storage.googleapis.com/d1/de/63/bced35d87bb972/CN115637570A.pdf', '.pdf'))
records.append(get('cpquery_current_response', 'https://cpquery.cponline.cnipa.gov.cn/chinesepatent/index', '.html'))
(OUT / 'request_manifest.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(records, ensure_ascii=False, indent=2))

pdf = OUT / 'CN115637570A_original.pdf'
if pdf.read_bytes().startswith(b'%PDF'):
    from pypdf import PdfReader
    doc = PdfReader(pdf)
    first_text = doc.pages[0].extract_text()
    (OUT / 'CN115637570A_first_page.txt').write_text(first_text, encoding='utf-8')
    print(first_text)
