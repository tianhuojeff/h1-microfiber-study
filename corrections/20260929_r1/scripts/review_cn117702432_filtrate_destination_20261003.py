"""Independent positive filtrate destination refinement; preserves accepted observations."""
from pathlib import Path
import ast,csv,datetime,difflib,hashlib,io,json,subprocess,sys
from local_source import read_anchors
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json';C=R/'data/review_coverage.csv'
BASE='2e745e69c2a48dd98d77abed63c3e80955ea80cf';PUB='CN117702432A';SID='H1-F90159083';FIELD='liquid_route'
SRC=H/'team_package_20260928/sources/CN117702432A.html';EXPECTED='9fa4ff02688811243b49ac3fee8c9c6f5f4966f7dd72f06e01d7663c07714438'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def baseline(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=H)
def target(m):
    out=[x for x in m['samples'] if x['sample_id']==SID and x['representative_publication']==PUB];assert len(out)==1
    return out[0]
helper=ast.parse((R/'scripts/review_cn118273060_positive_20261002.py').read_text(encoding='utf8'))
function=next(n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='patch')
exec(compile(ast.Module(body=[function],type_ignores=[]),'<unique-sample-patch>','exec'))
a=read_anchors(SRC);assert sha(SRC)==EXPECTED
old=json.loads(baseline('corrections/20260929_r1/data/analysis_master.json'));m=json.loads(M.read_text(encoding='utf8'));s=target(m)
if '--verify' in sys.argv:
    assert len(old['samples'])==len(m['samples'])==14 and [z['sample_id'] for z in old['samples']]==[z['sample_id'] for z in m['samples']]
    for x,y in zip(old['samples'],m['samples']):
        if x['sample_id']!=SID:assert x==y
        else:
            for k in x:
                if k not in ['features','review_completeness']:assert x[k]==y[k]
            for field,f in x['features'].items():
                g=y['features'][field]
                if field!=FIELD:assert f==g
                else:
                    for k in f:
                        if k!='observations':assert f[k]==g[k]
                    assert g['observations'][:-1]==f['observations'] and len(g['observations'])==2
            for k in x['review_completeness']:
                if k!='current_scope':assert x['review_completeness'][k]==y['review_completeness'][k]
            assert y['review_completeness']['current_scope'][:-1]==x['review_completeness']['current_scope']
    for k in old:
        if k not in ['samples','updated_at']:assert old[k]==m[k]
    obs=[o for z in m['samples'] for f in z['features'].values() for o in f['observations']];idx={o['observation_id']:o for o in obs}
    prior=[o for z in old['samples'] for f in z['features'].values() for o in f['observations']]
    assert len(obs)==len(idx)==168 and len(prior)==167 and all(idx[o['observation_id']]==o for o in prior)
    cache={}
    for o in obs:
        for e in o['evidence']:
            p=Path(e['source_path']);assert sha(p)==e['source_sha256']
            if e.get('html_anchor'):
                if str(p) not in cache:cache[str(p)]=read_anchors(p)
                assert e['evidence_excerpt'] in cache[str(p)][e['html_anchor']]
            else:assert sha(Path(e['page_image_path']))==e['page_image_sha256']
    before=list(csv.DictReader(baseline('corrections/20260929_r1/data/review_coverage.csv').decode('utf-8-sig').splitlines()))
    after=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()));assert len(before)==len(after)==182
    for x,y in zip(before,after):
        if x['sample_id']==SID and x['field']==FIELD:
            assert y['observation_count']=='2' and {k:v for k,v in x.items() if k!='observation_count'}=={k:v for k,v in y.items() if k!='observation_count'}
        else:assert x==y
    rel=json.loads((H/'current_release.json').read_text(encoding='utf8'));assert rel['master_sha256']==sha(M) and rel['current_observations']==168
    assert rel['phase']=='P2' and rel['status']=='draft' and not rel['project_completion_accepted']
    assert all(z['sample_role']=='pending' and not z['review_completeness']['full_text_rechecked'] for z in m['samples'])
    assert not m['formal_statistics_allowed'] and not m['final_report_ready']
    print(dump({'verified':True,'baseline':BASE,'observations':168,'added':1,'old_167_unchanged':True,'other_13_candidates_unchanged':True,
    'other_12_target_fields_and_legal_unchanged':True,'master_sha256':sha(M),'source_html_sha256':sha(SRC),'all_source_bytes_and_excerpts_verified':True,
    'CSV_only_target_count_changed':True,'quoted_anchors':['p0045','p0047','p0048'],'full_saved_text_read_anchor_count':89,
    'original_pdf_checked':False,'drawings_checked':False,'all_14_pending':True,'formal_statistics_allowed':False,
    'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()}));raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();f=s['features'][FIELD];assert len(f['observations'])==1
meaning='p0048明确经过组件过滤的水可直接排下水道；另可选排水管末端一端接下水道、末端分支接本体100供水系统回收再利用。两种液体去向是原文可选，不作同时必需或零颗粒/安全实测。对象是经过过滤的水，不是截留固体后续处置，也不是维护前腔排空；未明分流控制阀、比例、再利用水质或最终环境安全，不能自行补画。'
ev=[{'locator':'保存HTML #'+k,'html_anchor':k,'evidence_excerpt':a[k],'source_role':'description_embodiment','subject_role':'this_invention_or_optional_embodiment',
'source_path':str(SRC),'source_url':'https://patents.google.com/patent/'+PUB+'/zh','source_sha256':sha(SRC),'verified_at':now,
'extraction_note':'Saved text positive filtrate destination; physical original/figures not checked.'} for k in ['p0045','p0047','p0048']]
f['observations'].append({'observation_id':PUB+'-liquid_route-sewer_or_optional_reuse-20261003','publication_id':PUB,'grant_publication_id':None,'sample_role':'pending',
'embodiment_id':'filtrate_sewer_or_optional_reuse','stage':FIELD,'technical_feature':meaning,'object':'组件过滤后的水','start':'过滤组件300后的排水管末端',
'end':'可选下水道或末端分支接本体供水系统','boundary':'说明书p0048可选液体目的地，不是固体处置或质量/安全实测','operation_order':[],
'support_status':'explicit','review_status':'complete_in_stated_saved_text_scope','claim_dependency':'说明书可选方式；未把分支再利用作为权1/10必需结构',
'evidence':ev,'interpretation':meaning,'performance_status':'not_verified','verified_at':now,'old_value':f['prior_field'],'new_value':meaning,
'change_reason':'完整保存文本识别明确后续滤液去向，另添观察，旧已验路线不改写。','removal_kind':None})
s['review_completeness']['current_scope'].append({'publication':PUB,'anchors':['p0045','p0047','p0048'],'field':FIELD,'at':now})
m['updated_at']=now
rows=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()));cols=rows[0].keys()
for row in rows:
    if row['sample_id']==SID and row['publication']==PUB and row['field']==FIELD:row['observation_count']='2'
buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=cols,lineterminator='\n');w.writeheader();w.writerows(rows)
print('*** Begin Patch\n'+patch(M,dump(m))+patch(C,'\ufeff'+buf.getvalue())+'*** End Patch')
