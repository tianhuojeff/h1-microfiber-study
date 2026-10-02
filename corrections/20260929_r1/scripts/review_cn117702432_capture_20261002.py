"""One positive saved-text field; no whole-document absence inference."""
from pathlib import Path
import ast,csv,datetime,difflib,hashlib,io,json,subprocess,sys
from local_source import read_anchors
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json';C=R/'data/review_coverage.csv'
BASE='a55a419ba3196c23b1766cff904d1320cad71084';PUB='CN117702432A';SID='H1-F90159083'
SRC=H/'team_package_20260928/sources/CN117702432A.html';EXPECTED='9fa4ff02688811243b49ac3fee8c9c6f5f4966f7dd72f06e01d7663c07714438'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def target(m):
    t=[s for s in m['samples'] if s['sample_id']==SID and s['representative_publication']==PUB];assert len(t)==1
    return t[0]
helper=ast.parse((R/'scripts/review_cn118273060_positive_20261002.py').read_text(encoding='utf8'))
function=next(n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='patch')
exec(compile(ast.Module(body=[function],type_ignores=[]),'<unique-sample-patch>','exec'))
old=json.loads(subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/analysis_master.json'],cwd=H))
m=json.loads(M.read_text(encoding='utf8'));s=target(m);a=read_anchors(SRC);assert sha(SRC)==EXPECTED
quoted=['p0047','p0053','p0054','p0055','p0056','zh-cl0001','zh-cl0010']
read_ids=['p0004','p0005','p0029','p0030','p0047','p0049','p0050','p0051','p0053','p0054','p0055','p0056','p0058','p0070','p0075','p0076']+['zh-cl'+str(i).zfill(4) for i in range(1,11)]
if '--verify' in sys.argv:
    for x,y in zip(old['samples'],m['samples']):
        if x['sample_id']!=SID:assert x==y
        else:
            for k in x:
                if k not in ['features','review_completeness']:assert x[k]==y[k]
            for field,f in x['features'].items():
                if field!='capture':assert f==y['features'][field]
                else:assert not f['observations'] and f['prior_field']==y['features'][field]['prior_field'] and len(y['features'][field]['observations'])==1
            for k in x['review_completeness']:
                if k!='current_scope':assert x['review_completeness'][k]==y['review_completeness'][k]
            assert y['review_completeness']['current_scope'][:-1]==x['review_completeness']['current_scope']
    idx={o['observation_id']:o for z in m['samples'] for f in z['features'].values() for o in f['observations']}
    before=[o for z in old['samples'] for f in z['features'].values() for o in f['observations']]
    assert len(idx)==157 and len(before)==156 and all(idx[o['observation_id']]==o for o in before)
    for e in s['features']['capture']['observations'][0]['evidence']:assert e['evidence_excerpt']==a[e['html_anchor']] and e['source_sha256']==sha(SRC)
    rows=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()));prior=list(csv.DictReader(subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/review_coverage.csv'],cwd=H).decode('utf-8-sig').splitlines()))
    assert len(rows)==len(prior)==182
    for x,y in zip(prior,rows):
        if y['sample_id']==SID and y['field']=='capture':assert y['observation_count']=='1' and y['support_status']=='explicit'
        else:assert x==y
    rel=json.loads((H/'current_release.json').read_text(encoding='utf8'));assert rel['master_sha256']==sha(M) and rel['current_observations']==157
    assert not rel['project_completion_accepted'] and rel['phase']=='P2' and rel['status']=='draft'
    assert all(z['sample_role']=='pending' and not z['review_completeness']['full_text_rechecked'] for z in m['samples'])
    assert not m['formal_statistics_allowed'] and not m['final_report_ready']
    print(dump({'verified':True,'baseline':BASE,'observations':157,'added':1,'old_156_unchanged':True,'other_13_candidates_unchanged':True,'all_legal_evidence_unchanged':True,'master_sha256':sha(M),'source_html_sha256':sha(SRC),'new_source_excerpts_verified':True,'CSV_verified':True,'executor_read_anchor_ids':read_ids,'executor_complete_saved_text_read':False,'original_pdf_checked':False,'drawings_checked':False,'all_14_pending':True,'full_text_complete_count':0,'formal_statistics_allowed':False}));raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();f=s['features']['capture'];assert not f['observations']
meaning='洗衣排水管上的盒体310设至少两个过滤腔室313，每腔对应过滤网320；阀330选通其中一个腔与进出水，水通过该腔网320时过滤并收集至少部分微塑料。依据权1与权10及p0053—56，不拼成每次水必经全部网的串联过滤，不把背景35%或减少清理/寿命效果当实测捕获率；末端或分段夹装是可选位置，原PDF/图未核。'
ev=[{'locator':'保存HTML #'+k,'html_anchor':k,'evidence_excerpt':a[k],'source_role':'claim' if k.startswith('zh-cl') else 'description_embodiment','subject_role':'this_invention_or_optional_embodiment','source_path':str(SRC),'source_url':'https://patents.google.com/patent/'+PUB+'/zh','source_sha256':sha(SRC),'verified_at':now,'extraction_note':'Positive saved-text anchor, not physical page; no complete-text negative judgment.'} for k in quoted]
f['observations'].append({'observation_id':PUB+'-capture-selected_chamber_net-20261002','publication_id':PUB,'grant_publication_id':None,'sample_role':'pending','embodiment_id':'selected_chamber_filter_net','stage':'capture','technical_feature':meaning,'object':'洗衣排水微塑料、过滤网320','start':'水进入盒体310当前选通腔313','end':'网320过滤并收集至少部分微塑料','boundary':'仅已读保存锚点；选通腔不拼全部网串联；未核原PDF/图或效率','operation_order':[],'support_status':'explicit','review_status':'complete_in_stated_saved_text_scope','claim_dependency':'权1基本过滤组件；权10洗衣机包括权1—9任一过滤组件','evidence':ev,'interpretation':meaning,'performance_status':'not_verified','verified_at':now,'old_value':f['prior_field'],'new_value':meaning,'change_reason':'明确正向原句补单一空字段，保留原值及未知。','removal_kind':None})
f['review_status']='partial_saved_text_targeted';f['support_status']='explicit'
s['review_completeness']['current_scope'].append({'publication':PUB,'anchors':quoted,'field':'capture','at':now})
s['review_completeness']['capture_saved_targeted_20261002']={'executor_read_anchor_ids':read_ids,'source_sha256':sha(SRC),'executor_complete_saved_text_read':False,'original_pdf_checked':False,'drawings_checked':False,'not_a_full_text_completion':True}
m['updated_at']=now
rows=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()));cols=rows[0].keys()
for row in rows:
    if row['sample_id']==SID and row['publication']==PUB and row['field']=='capture':row.update(review_status=f['review_status'],support_status='explicit',observation_count='1')
buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=cols,lineterminator='\n');w.writeheader();w.writerows(rows)
print('*** Begin Patch\n'+patch(M,dump(m))+patch(C,'\ufeff'+buf.getvalue())+'*** End Patch')
