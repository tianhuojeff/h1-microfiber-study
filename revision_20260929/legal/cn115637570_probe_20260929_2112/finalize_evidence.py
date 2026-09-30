from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json, zipfile

out = Path(__file__).resolve().parent
legal = out.parent
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

archive = legal / 'raw_official_20260929/CN_quanweiwendang_20260630.zip'
archive_sha = sha(archive)
assert archive_sha == '91ca661a0372a3cf5ec4134a33f89c41e5334441ea827478ce66d1173429cd39'
rows = []
with zipfile.ZipFile(archive) as z:
    for member in z.infolist():
        if 'INVENTION ' not in member.filename:
            continue
        with z.open(member) as stream:
            for number, line in enumerate(stream, 1):
                if b'115637570' in line:
                    full = line.decode('utf-8-sig').strip()
                    rows.append({'archive_member': member.filename, 'line_number': number, 'row': ','.join(full.split(',')[:4]), 'full_line': full})
                    if {x['row'] for x in rows} >= {'CN,115637570,A,20230124', 'CN,115637570,B,20260217'}:
                        break
assert {x['row'] for x in rows} >= {'CN,115637570,A,20230124', 'CN,115637570,B,20260217'}, rows
(out / 'official_archive_crosscheck.json').write_text(json.dumps({'archive_sha256':archive_sha,'source_url':'https://www.cnipa.gov.cn/attach/0/CN_quanweiwendang_20260630.zip','observed_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'rows':rows,'limit':'publication numbers, kinds and dates only; not current legal status'}, ensure_ascii=False, indent=2), encoding='utf-8')

register = legal / 'official_status_register_20260929.json'
backup = out / 'official_status_register_before.json'
assert not backup.exists(), 'Refuse overwrite'
backup.write_bytes(register.read_bytes())
data = json.loads(register.read_text(encoding='utf-8'))
record = next(x for x in data['records'] if x['sample']=='CN115637570A')
assert record['application_no']=='CN202110818324.6A'
record['application_no_previous_aggregator_identifier']='CN202110818324.6A'
record['application_no']='202110818324.6'
record['application_number_evidence']={
    'source_type':'CNIPA-issued application-publication PDF mirrored by Google Patents, not a current official register',
    'source_url':'https://patentimages.storage.googleapis.com/d1/de/63/bced35d87bb972/CN115637570A.pdf',
    'pdf_sha256':sha(out/'CN115637570A_original.pdf'),
    'page':1,
    'field':'(21) application number',
    'title':'一种微纤维过滤器及洗衣机',
    'applicants_at_publication':['青岛海尔洗衣机有限公司','青岛海尔智能技术研发有限公司','海尔智家股份有限公司'],
    'publication_number':'CN115637570A',
    'publication_date':'2023-01-24',
    'visual_readback':True,
    'official_archive_crosscheck':'cn115637570_probe_20260929_2112/official_archive_crosscheck.json'
}
record['latest_access_observation']={
    'checked_at':'2026-09-29T21:11:30.523795+08:00',
    'url':'https://cpquery.cponline.cnipa.gov.cn/chinesepatent/index',
    'method':'single unauthenticated urllib request; no retry',
    'http_status':412,
    'error':'HTTP Error 412: Precondition Failed',
    'response_bytes':2470,
    'response_sha256':sha(out/'cpquery_current_response.html'),
    'case_record_read':False,
    'browser_session_checked':False,
    'limitation':'This establishes rejection of this unauthenticated request only; it does not diagnose the current signed-in browser or prove that login fixes it.'
}
record['official_record']='CNIPA archive A/B rows reread; publication PDF page 1 establishes application number 202110818324.6. Current single unauthenticated CPQuery entry request returned HTTP 412 at 2026-09-29T21:11:30+08:00; no individual legal-status or fee record was read.'
assert record['status_as_of']=='unknown'
register.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
manifest={'observed_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'register_before_sha256':sha(backup),'register_after_sha256':sha(register),'status_counts':{'unknown':sum(x['status_as_of']=='unknown' for x in data['records'])},'r1_passed':False,'files':[]}
for path in sorted(out.iterdir()):
    if path.is_file() and path.name != 'acceptance_manifest.json':
        manifest['files'].append({'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path)})
(out/'acceptance_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'archive_rows':rows,'register_after_sha256':sha(register),'unknown_count':manifest['status_counts']['unknown'],'r1_passed':False},ensure_ascii=False,indent=2))
