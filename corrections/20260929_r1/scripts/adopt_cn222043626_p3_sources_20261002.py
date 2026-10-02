"""Archive received originals and independently verify dated grant event, not current validity."""
from pathlib import Path
import datetime,hashlib,json,subprocess,sys,zipfile
H=Path(__file__).resolve().parents[3]; BASE='4c513590f1faf9b349c51bfae083cb76ee4bdeaf'
ROOT=H.parent/'work_logs/artifacts/controller-20261002/P3状态补证'
OUT=H/'corrections/20260929_r1/search/CN222043626U_P3_raw_20261002.zip'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if '--archive' in sys.argv:
    receipt=json.loads((ROOT/'artifact_receipt.json').read_text(encoding='utf8'))
    assert len(receipt['files'])==24 and not OUT.exists()
    payload=[('artifact_receipt.json',(ROOT/'artifact_receipt.json').read_bytes())]
    for item in receipt['files']:
        p=ROOT/item['relative_path'];assert p.resolve().is_relative_to(ROOT.resolve())
        data=p.read_bytes();assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
        payload.append((item['relative_path'],data))
    with zipfile.ZipFile(OUT,'x',zipfile.ZIP_DEFLATED) as z:
        for name,data in payload:z.writestr(name,data)
with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
    receipt=json.loads(z.read('artifact_receipt.json'));assert len(z.namelist())==25
    for item in receipt['files']:
        data=z.read(item['relative_path']);assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
    manifest=json.loads(z.read('CN222043626U_status_manifest.json'))
    assert manifest['grant_publication_event']['date']=='2024-11-22'
    assert manifest['status_as_of_attempted_check']['current_legal_status']=='unknown'
    assert not manifest['target_query_submitted_to_official_case_system']
    assert manifest['new_access_limitations']['public_service_entry_request']['status']==412
    assert manifest['search_evidence']['interface_hit_count'] is None
    assert not manifest['search_evidence']['export_complete']
    assert hashlib.sha256(z.read('cnipa_public_service_entry/error_response.bin')).hexdigest()=='3585f769aeb70a1928f28c4349b508fda4a4c21f397680a54ce4315bc043ee6b'
archive=H/'revision_20260929/legal/raw_official_20260929/CN_quanweiwendang_20260630.zip'
assert sha(archive)=='91ca661a0372a3cf5ec4134a33f89c41e5334441ea827478ce66d1173429cd39'
digest=hashlib.sha256();total=0;lines=0;tail=b'';found=set()
with zipfile.ZipFile(archive) as z:
    item=next(i for i in z.infolist() if 'UTILITY_MODEL' in i.filename)
    with z.open(item) as stream:
        while True:
            chunk=stream.read(8*1024*1024)
            if not chunk:break
            digest.update(chunk);total+=len(chunk)
            merged=tail+chunk; needle=b'CN,222043626,U,20241122\r\n';at=merged.find(needle)
            if at>=0:
                found.add((lines-tail.count(b'\n')+merged[:at].count(b'\n')+1,needle.hex()))
            lines+=chunk.count(b'\n');tail=merged[-128:]
assert total==609172943 and digest.hexdigest()=='3c30999f2831413871ed082033a731fbbfa07df7043edb850b7eedd5a812ce30'
assert found=={(21297581,'434e2c3232323034333632362c552c32303234313132320d0a')}
for path in ['corrections/20260929_r1/data/analysis_master.json','corrections/20260929_r1/data/review_coverage.csv']:
    assert (H/path).read_bytes()==subprocess.check_output(['git','show',BASE+':'+path],cwd=H)
m=json.loads((H/'corrections/20260929_r1/data/analysis_master.json').read_text(encoding='utf8'))
assert all(s['sample_role']=='pending' for s in m['samples']) and len(m['samples'])==14
assert not m['formal_statistics_allowed'] and not m['final_report_ready']
assert sha(H/'patents/CN222043626U.pdf')=='27b93dc08a6e684face981d4b2d7afedbb8dfad39b59c222d91c09132b0b08b2'
print(json.dumps({'verified':True,'baseline':BASE,'raw_archive_path':str(OUT),'raw_archive_sha256':sha(OUT),
 'raw_archive_files':25,'all_received_24_file_hashes_verified':True,'grant_event_date':'2024-11-22',
 'official_utility_member_line':21297581,'member_read_to_EOF_CRC_passed':True,'member_bytes':total,
 'member_sha256':digest.hexdigest(),'original_pdf_sha256':'27b93dc08a6e684face981d4b2d7afedbb8dfad39b59c222d91c09132b0b08b2',
 'official_current_case_query_submitted':False,'official_current_case_record_obtained':False,
 'current_status':'unknown','candidate_role':'pending','interface_entry_HTTP_status':412,
 'interface_hit_count':None,'export_complete':False,'genuine_case_screenshot_saved':False,
 'technical_master_and_coverage_bytes_unchanged':True,'observations':137,'all_14_pending':True,
 'main_phase':'P2','P3_complete':False,'formal_statistics_allowed':False,
 'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()},ensure_ascii=False,indent=2))
