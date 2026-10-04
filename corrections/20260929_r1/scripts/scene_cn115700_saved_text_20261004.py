"""Saved-HTML scene/material classification, not original-PDF acceptance."""
from pathlib import Path
import ast,datetime,difflib,hashlib,importlib.util,json,subprocess,sys
from local_source import read_anchors
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='d543dbfaf3f4804ed5cf38542e5d83eb6c62c297';SID='H1-F85120837';PUB='CN115700309A';KEY='saved_text_scene_classification_20261004'
SOURCE=H/'team_package_20260928/sources/CN115700309A.html';EXPECTED='38adeb9c51ddfdc9acf91a091a12cb2ec8ad16e78b346d0df3e5df27970066e5'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(v):return json.dumps(v,ensure_ascii=False,indent=2)+'\n'
def target(m):
 v=[s for s in m['samples'] if s['sample_id']==SID and s['representative_publication']==PUB];assert len(v)==1;return v[0]
old=json.loads(subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/analysis_master.json'],cwd=H));m=json.loads(M.read_bytes());s=target(m)
assert sha(SOURCE)==EXPECTED;a=read_anchors(SOURCE)
scope=['p'+str(n).zfill(4) for n in range(1,214)]+['cl'+str(n).zfill(4) for n in range(1,11)]
previous=target(old)['review_completeness']['saved_text_complete_remaining_fields_20261002'];assert previous['read_anchor_ids']==scope and all(k in a for k in scope)
assert all('微塑料' not in a[k] and '微纤维' not in a[k] for k in scope)
scene={'classification':'laundry_lint_and_impurities_material_not_explicit_in_saved_text','review_status':'saved_text_scope_reviewed_original_pending','publication_id':PUB,'source_path':str(SOURCE),'source_sha256':EXPECTED,'basis':[{'html_anchor':k,'source_role':'background_context' if k=='p0004' else 'description_of_this_invention','evidence_excerpt':a[k]} for k in ['p0002','p0004','p0070','p0090']],'boundary':'明确洗衣/漂洗循环水线屑及杂物；已存213描述+10权项未明确微塑料/微纤维材料称谓，不把全部线屑自动判塑料或已核微塑料核心。该未定位仅保存文本范围，原PDF/图仍缺。'}
record={'source_path':str(SOURCE),'source_sha256':EXPECTED,'previous_full_saved_read_record':'saved_text_complete_remaining_fields_20261002','read_scope':'p0001-p0213 and cl0001-cl0010 saved HTML; not original physical pages','executor_revisited_anchors':['p0001-p0020','p0070','p0090','p0150-p0152'],'positive_scene_basis':['p0002','p0004','p0070','p0090'],'saved_material_term_scan_anchors':223,'microplastic_microfibre_terms_found':0,'original_pdf_checked':False,'drawings_checked':False,'full_text_acceptance':False,'previous_scene':target(old)['scene_material']}
if '--verify' in sys.argv:
 for x,y in zip(old['samples'],m['samples']):
  if x['sample_id']!=SID:assert x==y
  else:
   for k in x:
    if k not in ['scene_material','publications','review_completeness']:assert x[k]==y[k]
   assert y['scene_material']==scene and y['review_completeness'][KEY]==record
   assert {k:v for k,v in y['review_completeness'].items() if k!=KEY}==x['review_completeness']
   for xp,yp in zip(x['publications'],y['publications']):assert {k:v for k,v in yp.items() if k not in ['review_status','previous_review_status']}=={k:v for k,v in xp.items() if k!='review_status'}
 assert subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/review_coverage.csv'],cwd=H)==(R/'data/review_coverage.csv').read_bytes()
 sp=importlib.util.spec_from_file_location('scene_current_validator',R/'scripts/verify_and_export.py');v=importlib.util.module_from_spec(sp);sys.modules[sp.name]=v;sp.loader.exec_module(v);q=v.validate(m)
 assert q['observations']==168 and q['full_text_complete_count']==4 and not s['review_completeness']['full_text_rechecked']
 q.update({'baseline':BASE,'target':PUB,'all168_observations_and_features_unchanged':True,'other13_whole_objects_unchanged':True,'all_legal_unchanged':True,'CSV_exact_bytes_unchanged':True,'scene_quotes_verified':4,'saved_scope_anchor_scan':223,'classification':scene['classification'],'original_pdf_and_drawings_not_checked':True,'full_text_flag_not_promoted':True,'reset_consumed':False})
 print(dump(q));raise SystemExit
assert m==old;s['scene_material']=scene;s['review_completeness'][KEY]=record
for p in s['publications']:p['previous_review_status']=p['review_status'];p['review_status']='complete_saved_text_scope_original_pending'
m['updated_at']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
tree=ast.parse((R/'scripts/accept_cn118_publication_20261004.py').read_text(encoding='utf8'));fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='patch');exec(compile(ast.Module(body=[fn],type_ignores=[]),'unique_sample_patch','exec'))
print('*** Begin Patch\n'+patch(M,dump(m))+'*** End Patch')
