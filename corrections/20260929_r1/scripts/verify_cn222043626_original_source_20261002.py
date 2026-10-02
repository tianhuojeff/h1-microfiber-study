"""Verify original downloaded bytes, identity, page parsing; not legal status."""
from pathlib import Path
import datetime,hashlib,json,subprocess
from pypdf import PdfReader
H=Path(__file__).resolve().parents[3]; BASE='9c60e12970692d273b46e3a92e269f52045e0d1f'
P=H/'patents/CN222043626U.pdf'; E=H/'corrections/20260929_r1/sources/CN222043626U_original_20261002'
EXPECTED='27b93dc08a6e684face981d4b2d7afedbb8dfad39b59c222d91c09132b0b08b2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P)==EXPECTED and P.stat().st_size==869902 and P.read_bytes().startswith(b'%PDF-')
request=json.loads((E/'request_manifest.json').read_text(encoding='utf8'))
assert request['sha256']==EXPECTED and request['status']==200 and request['bytes']==869902
assert request['requested_url']=='https://patentimages.storage.googleapis.com/0c/27/f7/b98ebf05098854/CN222043626U.pdf'
html=H/'team_package_20260928/sources/CN222043626U.html'
assert sha(html)=='0b33a8ec1dbee2049d6577493caf639d76b76326200c6725dc99c958f89ee621'
assert request['requested_url'] in html.read_text(encoding='utf8')
reader=PdfReader(P);assert len(reader.pages)==14
texts=[p.extract_text() or '' for p in reader.pages]
compact=''.join(texts[0].split())
assert all(k in compact for k in ['CN222043626U','202420066261.2','2024.11.22','过滤组件和洗衣机'])
assert 'CN222043626U' in ''.join(texts[-1].split())
assert all(t for t in texts)
for path in ['corrections/20260929_r1/data/analysis_master.json','corrections/20260929_r1/data/review_coverage.csv']:
    assert (H/path).read_bytes()==subprocess.check_output(['git','show',BASE+':'+path],cwd=H)
m=json.loads((H/'corrections/20260929_r1/data/analysis_master.json').read_text(encoding='utf8'))
assert sum(len(f['observations']) for s in m['samples'] for f in s['features'].values())==137
assert all(s['sample_role']=='pending' and not s['review_completeness']['full_text_rechecked'] for s in m['samples'])
print(json.dumps({'verified':True,'baseline':BASE,'original_pdf_path':str(P),'original_pdf_sha256':sha(P),
 'bytes':P.stat().st_size,'physical_pages':14,'all_14_pages_parsed':True,'extracted_page_lengths':[len(t) for t in texts],
 'cover_identity_verified':True,'executor_visual_pages':[1],'drawings_visual_checked':False,
 'page_partition_cover_claims_description_drawings':[1,1,6,6],'original_download_manifest_sha256':sha(E/'request_manifest.json'),
 'saved_html_sha256':sha(html),'original_download_url_matches_saved_html':True,'cover_image_sha256':sha(E/'cover.png'),
 'technical_master_and_coverage_bytes_unchanged':True,'all_137_observations_unchanged':True,'all_14_pending':True,
 'current_legal_status_verified':False,'full_text_complete_count':0,'formal_statistics_allowed':False,
 'limits':'Source adoption/integrity only; no complete technical review or maintenance/legal validity conclusion.',
 'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()},ensure_ascii=False,indent=2))
