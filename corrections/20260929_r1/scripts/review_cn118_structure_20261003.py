"""Six original structural drawing pages, preserving all accepted observations."""
from pathlib import Path
import ast,datetime,difflib,hashlib,json,subprocess,sys
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='72fa269a442d158dabbb958b5d23c0b6e811d209';SID='H1-F91644784';PUB='CN118273060A';KEY='original_structure_drawing_review_20261003'
PAGES=list(range(27,33));PDF=H/'patents/CN118273060A.pdf';EXPECTED='fcfde50da413b25f2b5dadcca389a44fc41a3aa682027825617ef51c309be80d'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def baseline(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=H)
def target(m):
    out=[x for x in m['samples'] if x['sample_id']==SID and x['representative_publication']==PUB];assert len(out)==1
    return out[0]
old=json.loads(baseline('corrections/20260929_r1/data/analysis_master.json'));m=json.loads(M.read_text(encoding='utf8'))
matches=[s for s in m['samples'] if s['sample_id']==SID and s['representative_publication']==PUB];assert len(matches)==1;s=matches[0]
assert sha(PDF)==EXPECTED
images=[R/'evidence'/('CN118273060A_structure_20261003-'+str(i)+'.png') for i in PAGES];assert all(p.is_file() for p in images)
def patch(p,new):
    prior=p.read_text(encoding='utf8');a=json.loads(prior);b=json.loads(new)
    assert all(x==y for x,y in zip(a['samples'],b['samples']) if x['sample_id']!=SID)
    second='\n'.join('    '+line for line in dump(target(b)).strip().splitlines())
    marker='      "representative_publication": "'+PUB+'",'
    assert prior.count(marker)==1
    start=prior.rfind('\n    {',0,prior.index(marker))+1
    decoded,length=json.JSONDecoder().raw_decode(prior[start+4:])
    assert decoded==target(a)
    first=prior[start:start+4+length]
    assert prior.count(first)==prior.count(marker)==1
    if prior[start+4+length:start+5+length]==',':
        first+=',';second+=','
    body=['@@\n','-  "updated_at": '+json.dumps(a['updated_at'])+',\n','+  "updated_at": '+json.dumps(b['updated_at'])+',\n']
    before=(first+'\n').splitlines(True);after=(second+'\n').splitlines(True);started=False
    for group in difflib.SequenceMatcher(None,before,after,autojunk=False).get_grouped_opcodes(3):
        body.append('@@ '+marker+'\n' if not started else '@@\n');started=True
        for tag,a0,a1,b0,b1 in group:
            if tag=='equal':body.extend(' '+line for line in before[a0:a1])
            if tag in ['delete','replace']:body.extend('-'+line for line in before[a0:a1])
            if tag in ['insert','replace']:body.extend('+'+line for line in after[b0:b1])
    return '*** Update File: '+p.as_posix()+'\n'+''.join(body)
if '--verify' in sys.argv:
    assert [x['sample_id'] for x in old['samples']]==[x['sample_id'] for x in m['samples']]
    for x,y in zip(old['samples'],m['samples']):
        if x['sample_id']!=SID:assert x==y
        else:
            for k in x:
                if k!='review_completeness':assert x[k]==y[k]
            assert {k:v for k,v in y['review_completeness'].items() if k!=KEY}==x['review_completeness']
    for k in old:
        if k not in ['updated_at','samples']:assert old[k]==m[k]
    rc=s['review_completeness'][KEY];assert rc['source_sha256']==sha(PDF) and rc['executor_visual_pages_this_transaction']==PAGES
    assert rc['cumulative_drawing_visual_pages']==list(range(15,38)) and rc['remaining_drawing_visual_pages']==[38,39,40,41]
    for img in rc['rendered_pages']:assert sha(Path(img['path']))==img['sha256']
    assert (R/'data/review_coverage.csv').read_bytes()==baseline('corrections/20260929_r1/data/review_coverage.csv')
    assert sum(len(f['observations']) for z in m['samples'] for f in z['features'].values())==168
    assert all(z['sample_role']=='pending' and not z['review_completeness']['full_text_rechecked'] for z in m['samples'])
    rel=json.loads((H/'current_release.json').read_text(encoding='utf8'));assert rel['master_sha256']==sha(M) and rel['current_observations']==168 and rel['phase']=='P2' and not rel['project_completion_accepted']
    assert not m['formal_statistics_allowed'] and not m['final_report_ready']
    print(dump({'verified':True,'baseline':BASE,'observations':168,'added_observations':0,'all_old_168_features_unchanged':True,'other_13_candidates_unchanged':True,'all_legal_evidence_unchanged':True,'CSV_bytes_unchanged':True,'master_sha256':sha(M),'source_pdf_sha256':sha(PDF),'executor_visual_pages_this_transaction':PAGES,'cumulative_drawing_visual_pages':rc['cumulative_drawing_visual_pages'],'remaining_drawing_visual_pages':[38,39,40,41],'all_27_drawing_pages_read':False,'all_image_bytes_verified':True,'all_14_pending':True,'formal_statistics_allowed':False,'reset_consumed':False,'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()}));raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
s['review_completeness'][KEY]={'source_path':str(PDF),'source_sha256':sha(PDF),'at':now,
'executor_visual_pages_this_transaction':PAGES,'figures_this_transaction':['4','4a','4a prime','4b','5','5a','5a prime','5b'],
'cumulative_drawing_visual_pages':list(range(15,38)),'remaining_drawing_visual_pages':[38,39,40,41],
'all_drawings_visually_read':False,'original_technical_full_review_complete':False,
'figure_observations':[
{'pages':[27,28,29],'judgment':'图4轴线X-X与壳体3/盖4/锁7；图4a剖面给定心部511、操作41、插塞40、连接部510、滤板512/侧壁513/通路540与T1/T3等位置。图4a′原标516,406仍为合列标记，不从这条引线裁定槽/突起谁正确；图4b可见301/302、5131,311引导配合及T4。'},
{'pages':[30,31,32],'judgment':'图5/5a/5a′为另一所画操作与耦合细部，原标405/415与511及操作41、插塞40；图5b另一剖面给50介质/5滤组、301/302及5131,311。保持这组与4a方式的结构区别，不把螺纹/定位槽及所有T1-T4并成每种布局必备。'}],
'boundaries':'原件剖面与细部支持所画连接/介质界面定位；线条及阴影不证明实测防漏、完全排干、介质干燥、固体脱水，409外形不推为储渣盒。原四组文字编号差异继续保持，不以图示默修。',
'rendered_pages':[{'physical_page':i,'path':str(p),'sha256':sha(p)} for i,p in zip(PAGES,images)]}
m['updated_at']=now;print('*** Begin Patch\n'+patch(M,dump(m))+'*** End Patch')

