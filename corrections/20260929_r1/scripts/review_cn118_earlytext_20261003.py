"""Three original claim and early description visual pages, preserving all accepted observations."""
from pathlib import Path
import ast,datetime,difflib,hashlib,json,subprocess,sys
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='7b568ca48dd5a68c16fcf8a92feea6afd710a214';SID='H1-F91644784';PUB='CN118273060A';KEY='original_early_text_visual_20261003'
PAGES=[3,4,5];PDF=H/'patents/CN118273060A.pdf';EXPECTED='fcfde50da413b25f2b5dadcca389a44fc41a3aa682027825617ef51c309be80d'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def baseline(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=H)
def target(m):
    out=[x for x in m['samples'] if x['sample_id']==SID and x['representative_publication']==PUB];assert len(out)==1
    return out[0]
old=json.loads(baseline('corrections/20260929_r1/data/analysis_master.json'));m=json.loads(M.read_text(encoding='utf8'))
matches=[s for s in m['samples'] if s['sample_id']==SID and s['representative_publication']==PUB];assert len(matches)==1;s=matches[0]
assert sha(PDF)==EXPECTED
images=[R/'evidence'/('CN118273060A_earlytext_20261003-'+str(i)+'.png') for i in PAGES];assert all(p.is_file() for p in images)
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
    assert rc['cumulative_drawing_visual_pages']==list(range(15,42)) and rc['remaining_drawing_visual_pages']==[]
    assert rc['cumulative_original_visual_pages']==list(range(1,6))+list(range(10,42)) and rc['remaining_original_visual_pages']==[6,7,8,9]
    assert len(rc['visual_confirmations'])==3 and rc['visual_confirmations'][-1]['printed_paragraph_partially_visible']==31
    for img in rc['rendered_pages']:assert sha(Path(img['path']))==img['sha256']
    assert (R/'data/review_coverage.csv').read_bytes()==baseline('corrections/20260929_r1/data/review_coverage.csv')
    assert sum(len(f['observations']) for z in m['samples'] for f in z['features'].values())==168
    assert all(z['sample_role']=='pending' and not z['review_completeness']['full_text_rechecked'] for z in m['samples'])
    rel=json.loads((H/'current_release.json').read_text(encoding='utf8'));assert rel['master_sha256']==sha(M) and rel['current_observations']==168 and rel['phase']=='P2' and not rel['project_completion_accepted']
    assert not m['formal_statistics_allowed'] and not m['final_report_ready']
    print(dump({'verified':True,'baseline':BASE,'observations':168,'added_observations':0,'all_old_168_features_unchanged':True,'other_13_candidates_unchanged':True,'all_legal_evidence_unchanged':True,'CSV_bytes_unchanged':True,'master_sha256':sha(M),'source_pdf_sha256':sha(PDF),'executor_visual_pages_this_transaction':PAGES,'cumulative_drawing_visual_pages':rc['cumulative_drawing_visual_pages'],'remaining_drawing_visual_pages':[],'all_27_drawing_pages_read':True,'all_image_bytes_verified':True,'all_14_pending':True,'formal_statistics_allowed':False,'reset_consumed':False,'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()}));raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
s['review_completeness'][KEY]={'source_path':str(PDF),'source_sha256':sha(PDF),'at':now,
'executor_visual_pages_this_transaction':PAGES,
'cumulative_original_visual_pages':list(range(1,6))+list(range(10,42)),
'remaining_original_visual_pages':[6,7,8,9],
'cumulative_drawing_visual_pages':list(range(15,42)),'remaining_drawing_visual_pages':[],
'all_drawings_visually_read':True,'original_technical_full_review_complete':False,
'visual_confirmations':[
{'physical_page':3,'judgment':'权10-19全文目视：权12多层和权13开孔泡沫分别从前述任一项从属，权14仅从属13，不能把开孔泡沫/梯度均变权1必需。权16轴向锁/解锁与滤组移入/移出；权17排放和/或再循环，权18泵在滚筒下游且过滤器上游、权19洗衣机内置均保留从属范围。'},
{'physical_page':4,'printed_paragraphs_complete':[1,13],'judgment':'[0004]/[0005]对象包括合成与天然纤维，不把所有纤维自动定塑料。[0006]洗衣烘干机含烘干功能不是滤介质使用后干燥。[0007]-[0012]已有技术堵塞/维护背景，不当核心实施例专用储渣结构或实验性能证据。'},
{'physical_page':5,'printed_paragraphs_complete':[14,30],'printed_paragraph_partially_visible':31,'judgment':'[0017]本发明过滤室脏/净区由滤组分开，操作件穿贯通孔接定心件促封头板/帽密封；[0018]排放和/或再循环；[0020]明确1a-1u每图一个优选方式，[0021]2′组装及2″抽移/插入状态，支持此前附图独立方式边界。说明末[0031]跨下一物理6，不冒此页完整该段。'}],
'boundaries':'本项只原页目视与范围绑定，旧观察不改；未定位技术字段仍需全部原文/图字段映射，剩6-9正文视觉未完成。',
'rendered_pages':[{'physical_page':i,'path':str(p),'sha256':sha(p)} for i,p in zip(PAGES,images)]}
m['updated_at']=now;print('*** Begin Patch\n'+patch(M,dump(m))+'*** End Patch')
