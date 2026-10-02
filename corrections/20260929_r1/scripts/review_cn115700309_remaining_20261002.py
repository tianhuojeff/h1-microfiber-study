"""Bound absence to the complete saved text; preserve every prior observation."""
from pathlib import Path
import ast, csv, datetime, hashlib, io, json, subprocess, sys
from local_source import read_anchors
H=Path(__file__).resolve().parents[3]; R=H/'corrections/20260929_r1'
M=R/'data/analysis_master.json'; C=R/'data/review_coverage.csv'
BASE='bcba9794b91c6f4334895cbffcc274cb007e9e50'; PUB='CN115700309A'; SID='H1-F85120837'
SRC=H/'team_package_20260928/sources/CN115700309A.html'
EXPECTED='38adeb9c51ddfdc9acf91a091a12cb2ec8ad16e78b346d0df3e5df27970066e5'
FIELDS=['solids_dewatering','carrier_conditioning']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o): return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def baseline(p): return subprocess.check_output(['git','show',BASE+':'+p],cwd=H)
def target(m):
    matches=[s for s in m['samples'] if s['sample_id']==SID and s['representative_publication']==PUB]
    assert len(matches)==1
    return matches[0]
# Reuse only the inspected pure function, not the predecessor's execution body.
import difflib
helper=ast.parse((R/'scripts/review_cn115700309_performance_20261002.py').read_text(encoding='utf8'))
function=next(n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='patch')
exec(compile(ast.Module(body=[function],type_ignores=[]),'<unique-sample-patch>','exec'))
original_patch=patch
def patch(path,new):
    emitted=original_patch(path,new)
    if path==M:
        jump='@@       "representative_publication": "'+PUB+'",\n'
        pieces=emitted.split(jump)
        assert len(pieces)>=2
        # apply_patch searches forward: one publication jump, subsequent groups
        # remain in the same prevalidated object and must not jump backward.
        emitted=pieces[0]+jump+('@@\n'.join(pieces[1:]))
    return emitted
assert sha(SRC)==EXPECTED
a=read_anchors(SRC)
keys=['p'+str(i).zfill(4) for i in range(1,214)]+['cl'+str(i).zfill(4) for i in range(1,11)]
assert len(a)==223 and set(a)==set(keys)
old=json.loads(baseline('corrections/20260929_r1/data/analysis_master.json'))
m=json.loads(M.read_text(encoding='utf8')); s=target(m); prev=target(old)
if '--verify' in sys.argv:
    assert [z['sample_id'] for z in m['samples']]==[z['sample_id'] for z in old['samples']]
    for x,y in zip(old['samples'],m['samples']):
        if x['sample_id']!=SID: assert x==y
        else:
            for k in x:
                if k not in ['features','review_completeness']: assert x[k]==y[k]
            for field,f in x['features'].items():
                if field not in FIELDS: assert f==y['features'][field]
                else:
                    g=y['features'][field]
                    assert not f['observations'] and g['prior_field']==f['prior_field']
                    assert len(g['observations'])==1
                    assert g['support_status']=='not_located_in_reviewed_scope'
                    assert g['observations'][0]['availability_judgment']=='unknown'
            rc=y['review_completeness']; pr=x['review_completeness']
            assert rc['current_scope'][:-2]==pr['current_scope']
            for k in pr:
                if k!='current_scope': assert rc[k]==pr[k]
    obs=[o for z in m['samples'] for f in z['features'].values() for o in f['observations']]
    assert len(obs)==137 and len({o['observation_id'] for o in obs})==137
    index={o['observation_id']:o for o in obs}
    prior=[o for z in old['samples'] for f in z['features'].values() for o in f['observations']]
    assert len(prior)==135 and all(index[o['observation_id']]==o for o in prior)
    cache={}
    for o in obs:
        for e in o['evidence']:
            p=Path(e['source_path']); assert sha(p)==e['source_sha256']
            if e.get('html_anchor'):
                if str(p) not in cache: cache[str(p)]=read_anchors(p)
                assert e['evidence_excerpt'] in cache[str(p)][e['html_anchor']]
            else: assert sha(Path(e['page_image_path']))==e['page_image_sha256']
    before=list(csv.DictReader(baseline('corrections/20260929_r1/data/review_coverage.csv').decode('utf-8-sig').splitlines()))
    after=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()))
    assert len(before)==len(after)==182
    for x,y in zip(before,after):
        if x['publication']!=PUB or x['field'] not in FIELDS: assert x==y
        f=next(z for z in m['samples'] if z['representative_publication']==y['publication'])['features'][y['field']]
        assert y['review_status']==f['review_status'] and y['support_status']==(f['support_status'] or '')
        assert int(y['observation_count'])==len(f['observations'])
    rel=json.loads((H/'current_release.json').read_text(encoding='utf8'))
    assert rel['master_sha256']==sha(M) and rel['current_observations']==137
    assert not rel['project_completion_accepted'] and rel['phase']=='P2' and rel['status']=='draft'
    assert not m['formal_statistics_allowed'] and not m['final_report_ready']
    assert all(z['sample_role']=='pending' and not z['review_completeness']['full_text_rechecked'] for z in m['samples'])
    receipt=s['review_completeness']['saved_text_complete_remaining_fields_20261002']
    assert receipt['read_anchor_ids']==keys and receipt['source_sha256']==sha(SRC)
    assert not receipt['original_pdf_checked'] and not receipt['drawings_checked']
    print(dump({'verified':True,'baseline':BASE,'observations':137,'added':2,'old_135_unchanged':True,
      'other_13_candidates_unchanged':True,'all_legal_evidence_unchanged':True,'all_14_pending':True,
      'master_sha256':sha(M),'source_html_sha256':sha(SRC),'all_source_bytes_and_excerpts_verified':True,
      'CSV_verified':True,'full_text_complete_count':0,'original_pdf_checked':False,'drawings_checked':False,
      'fields':FIELDS,'executor_read_anchor_count':223,'executor_read_ranges':['p0001-p0213','cl0001-cl0010'],
      'unknown_not_zero':True,'formal_statistics_allowed':False,'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()}))
    raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
data=[
 ('solids_dewatering',['p0072','p0118','p0119','p0186','p0187','cl0010'],
  '过滤杂质501附着或夹带液体',
  '完整保存说明书213锚点与10权项范围未定位专门降低已收集501附着/夹带液体的压滤、离心脱水或其他脱水动作。p0118/0119及权10是污水经520过滤分离，未描述收集滤渣另行脱水；p0072/0186的离心力用于从620表面剥离线屑并融入水中，p0187空气压排对象是腔内携屑污水，均不能转成滤渣脱水。缺含水率实测，保持未知，不填0；结论仅该保存文本，原PDF/图未核。'),
 ('carrier_conditioning',['p0082','p0121','p0143','p0172','p0187','cl0001'],
  '过滤机构620/网625与过滤组件520自身',
  '完整保存说明书213锚点与10权项范围未定位过滤介质620/625或520自身专门排水、干燥或调理工序。p0121取出滤件清理不等于干燥；p0082清洗颗粒680随再次进水回浮是清洗颗粒复用，非滤介质干燥；p0143/0172的轴承安装环境无水是密封保护对象，非介质干燥；p0187腔污水压排不等于过滤载体已干燥。限定未定位、保持未知，不填0；原PDF/图未核。')]
for field,quoted,obj,meaning in data:
    f=s['features'][field]; assert not f['observations'] and f['support_status'] is None
    ev=[{'locator':'保存HTML #'+k,'html_anchor':k,'evidence_excerpt':a[k],
      'source_role':'claim' if k.startswith('cl') else 'description_embodiment',
      'subject_role':'this_invention_or_optional_embodiment','source_path':str(SRC),
      'source_url':'https://patents.google.com/patent/'+PUB+'/zh','source_sha256':sha(SRC),
      'verified_at':now,'extraction_note':'Saved mirror anchor, not a physical page; excerpt is a boundary contrast, absence is limited to all 223 reviewed anchors.'} for k in quoted]
    o={'observation_id':PUB+'-'+field+'-complete_saved_scope_unlocated-20261002','publication_id':PUB,
      'grant_publication_id':None,'sample_role':'pending','embodiment_id':'complete_saved_scope_distinct_objects',
      'stage':field,'technical_feature':meaning,'object':obj,'start':'限定全文范围；该字段专门动作未定位',
      'end':'未知；不转成0或功能不存在','boundary':'保存HTML p0001-p0213 / cl0001-cl0010；实施例一至四分别核对象，不拼互斥动作',
      'operation_order':[],'support_status':'not_located_in_reviewed_scope','review_status':'complete_in_stated_saved_text_scope',
      'availability_judgment':'unknown','claim_dependency':'权1至10完整读；权10经权9/8限定回收分离，不能由其补写脱水/干燥工序',
      'evidence':ev,'interpretation':meaning,'performance_status':'not_verified','verified_at':now,
      'old_value':f['prior_field'],'new_value':meaning,'change_reason':'完整保存文本回读后填入限定未定位复核；保留旧值与未知。',
      'removal_kind':None,'reviewed_anchor_ranges':['p0001-p0213','cl0001-cl0010']}
    f['observations'].append(o); f['review_status']='complete_saved_text_scope'; f['support_status']='not_located_in_reviewed_scope'
    s['review_completeness']['current_scope'].append({'publication':PUB,'anchors':keys,'field':field,'at':now})
s['review_completeness']['saved_text_complete_remaining_fields_20261002']={'source_path':str(SRC),'source_sha256':sha(SRC),
  'read_anchor_ids':keys,'description_anchors':213,'claim_anchors':10,'read_method':'Executor directly read five complete normalized saved-HTML blocks',
  'fields_added':FIELDS,'original_pdf_checked':False,'drawings_checked':False,'not_a_full_text_completion':True,'verified_at':now}
m['updated_at']=now
rows=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines())); columns=rows[0].keys()
for row in rows:
    if row['sample_id']==SID and row['publication']==PUB and row['field'] in FIELDS:
        f=s['features'][row['field']]; row.update(review_status=f['review_status'],support_status=f['support_status'],observation_count='1')
buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=columns,lineterminator='\n');w.writeheader();w.writerows(rows)
print('*** Begin Patch\n'+patch(M,dump(m))+patch(C,'\ufeff'+buf.getvalue())+'*** End Patch')
