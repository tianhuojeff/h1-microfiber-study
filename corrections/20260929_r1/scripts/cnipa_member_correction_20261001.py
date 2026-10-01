"""Read the two original ZIP members; print patches or verify, never write files."""
from pathlib import Path
import csv, hashlib, io, json, subprocess, sys, zipfile, datetime
H = Path(__file__).resolve().parents[3]
R = H/'corrections/20260929_r1'
M = R/'data/analysis_master.json'
Z = H/'revision_20260929/legal/raw_official_20260929/CN_quanweiwendang_20260630.zip'
EXPECTED = '91ca661a0372a3cf5ec4134a33f89c41e5334441ea827478ce66d1173429cd39'
BASE = 'd6ed64f03a5932561b11b672677a5d37cd5752f4'
def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()
def dumps(o): return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
assert sha(Z) == EXPECTED
records=[]
with zipfile.ZipFile(Z) as archive:
    for suffix, needle, expected_line, pub in [
        ('INVENTION 19850910-20260630.txt',b'CN,112914464,A,20210608',17863021,'CN112914464A'),
        ('UTILITY_MODEL 19850910-20260630.csv',b'CN,222043626,U,20241122',21297581,'CN222043626U')]:
        name=next(n for n in archive.namelist() if n.endswith(suffix))
        count=0; carry=b''; found=None
        with archive.open(name) as f:
            while True:
                block=f.read(8*1024*1024)
                if not block: break
                data=carry+block; end=data.rfind(b'\n')
                if end<0: carry=data; continue
                complete=data[:end+1]; carry=data[end+1:]
                at=complete.find(needle)
                if at>=0:
                    start=complete.rfind(b'\n',0,at)+1
                    stop=complete.find(b'\n',at)+1
                    found=(count+complete[:start].count(b'\n')+1,complete[start:stop])
                    break
                count+=complete.count(b'\n')
        assert found and found[0]==expected_line
        assert found[1].startswith(needle+b',') or found[1].rstrip(b'\r\n')==needle
        records.append({'sample':pub,'archive_sha256':EXPECTED,'member':name.encode('cp437').decode('gbk'),
            'line_number':found[0],'raw_record':found[1].decode('ascii').rstrip('\r\n'),
            'line_ending':'CRLF' if found[1].endswith(b'\r\n') else 'LF'})
old=json.loads(subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/analysis_master.json'],cwd=H))
current=json.loads(M.read_text(encoding='utf-8'))
ledger_path=R/'data/cnipa_member_correction_20261001.json'
if '--verify' in sys.argv:
    ledger=json.loads(ledger_path.read_text(encoding='utf-8'))
    assert ledger['records']==records
    rows=list(csv.DictReader((R/'data/official_publication_corrections_20261001.csv').read_text(encoding='utf-8').splitlines()))
    assert len(rows)==2
    for rec,row in zip(records,rows):
        assert all(str(rec[k])==row[k] for k in ['sample','member','line_number','raw_record','archive_sha256'])
        assert row['sample_role']=='pending' and row['status_as_of']=='unknown'
    for a,b in zip(old['samples'],current['samples']):
        pub=a['representative_publication']
        assert a['features']==b['features'] and a['scene_material']==b['scene_material']
        assert a['prior_working_evidence']==b['prior_working_evidence']
        assert b['sample_role']=='pending' and b['legal_evidence']['status_as_of']=='unknown'
        if pub not in ['CN112914464A','CN222043626U']: assert a==b
        else:
            assert b['legal_evidence']['official_version_source']['records']==[next(r['raw_record'] for r in records if r['sample']==pub)]
            assert b['legal_evidence_source']['sha256']==sha(ledger_path)
    u=next(s for s in current['samples'] if s['representative_publication']=='CN222043626U')
    assert u['grant_publication_id']==u['legal_evidence']['grant_no']=='CN222043626U'
    assert not current['formal_statistics_allowed'] and not current['final_report_ready']
    release=json.loads((H/'current_release.json').read_text(encoding='utf-8'))
    assert release['master_sha256']==sha(M) and not release['project_completion_accepted']
    print(dumps({'verified':True,'records':records,'master_sha256':sha(M),'all_technical_data_unchanged':True,'all_14_pending':True}))
    raise SystemExit
assert current==old, 'Must run on untouched baseline for this one correction'
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
ledger={'checked_at':now,'source_path':str(Z),'archive_sha256':EXPECTED,'records':records,
    'supersedes':{'path':'revision_20260929/legal/cnipa_authoritative_document_version_check_20260929.json',
        'old_CN222043626U_fact':'No matching U record was present in the downloaded authoritative-document text entry inspected.',
        'correction':'旧核验漏查UTILITY_MODEL成员；当前实用新型成员有U公告。旧文件保留为历史，不再作为此两件版本事实的最新结论。'},
    'supports':'Publication kind/version and publication date only; not present maintenance or validity.',
    'does_not_support':'个案法律事件、年费、终止、现时有效或14候选资格放行。',
    'previous_values':[{k:s[k] for k in ['representative_publication','grant_publication_id','legal_evidence','legal_evidence_source']} for s in old['samples'] if s['representative_publication'] in ['CN112914464A','CN222043626U']]}
ledger_text=dumps(ledger)
ledger_sha=hashlib.sha256(ledger_text.encode('utf-8')).hexdigest()
def block(key,value):
    lines=json.dumps(value,ensure_ascii=False,indent=2).splitlines()
    return ['      '+json.dumps(key)+': '+lines[0]]+['      '+v for v in lines[1:-1]]+['      '+lines[-1]+',']
patch='*** Begin Patch\n*** Add File: '+str(ledger_path).replace('\\','/')+'\n'+''.join('+'+l+'\n' for l in ledger_text.splitlines())
patch+='*** Update File: '+str(M).replace('\\','/')+'\n'
for s in current['samples']:
    pub=s['representative_publication']
    if pub not in ['CN112914464A','CN222043626U']: continue
    prior=next(x for x in old['samples'] if x['representative_publication']==pub)
    record=next(x for x in records if x['sample']==pub)
    s['legal_evidence']['official_record']='CNIPA authoritative original ZIP member row verified on '+now+'; prior PSS HTTP 412 obstacle remains; current individual legal-status record not read.'
    s['legal_evidence']['supports']='Official publication-version and publication-date fact only.'
    s['legal_evidence']['official_version_source']={'authority':'CNIPA authoritative document through 2026-06-30',
        'download_url':'https://www.cnipa.gov.cn/attach/0/CN_quanweiwendang_20260630.zip',
        'archive_sha256':EXPECTED,'member':record['member'],'line_number':record['line_number'],
        'records':[record['raw_record']],'checked_at':now}
    s['legal_evidence_source']={'path':str(ledger_path),'sha256':ledger_sha,'imported_at':now,'new_online_query_performed':False,'scope':'新增版本事实纠错；既有入口阻塞和关联待核见previous_values，不代表现时法律状态核验'}
    if pub=='CN222043626U':
        s['grant_publication_id']='CN222043626U'; s['legal_evidence']['grant_no']='CN222043626U'
        s['legal_evidence']['status_note']='U publication kind confirmed; no maintenance/effectiveness finding.'
    before=['      "grant_publication_id": '+json.dumps(prior['grant_publication_id'])+',']
    after=['      "grant_publication_id": '+json.dumps(s['grant_publication_id'])+',']
    before+=block('legal_evidence',prior['legal_evidence'])+block('legal_evidence_source',prior['legal_evidence_source'])
    after+=block('legal_evidence',s['legal_evidence'])+block('legal_evidence_source',s['legal_evidence_source'])
    patch+='@@\n'+''.join('-'+l+'\n' for l in before)+''.join('+'+l+'\n' for l in after)
out=io.StringIO(); w=csv.writer(out,lineterminator='\n'); w.writerow(['sample','member','line_number','raw_record','archive_sha256','status_as_of','sample_role'])
for rec in records: w.writerow([rec['sample'],rec['member'],rec['line_number'],rec['raw_record'],EXPECTED,'unknown','pending'])
patch+='*** Add File: '+str(R/'data/official_publication_corrections_20261001.csv').replace('\\','/')+'\n'+''.join('+'+l+'\n' for l in out.getvalue().splitlines())
patch+='*** End Patch'
print(patch)
