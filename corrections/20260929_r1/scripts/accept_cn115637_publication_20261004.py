"""Explicit original-A acceptance after five-page visual completion; old evidence preserved."""
from pathlib import Path
import copy,datetime,hashlib,importlib.util,json,re,subprocess,sys
from pypdf import PdfReader
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='5aed910a3c8ae035da18680a07bcc5e9122e212b';SID='H1-F84940183';PUB='CN115637570A'
KEY='publication_technical_acceptance';RECORD='original_A_field_bindings_20261004';STATUS='accepted_in_original_published_scope'
PDF=H/'revision_20260929/legal/cn115637570_probe_20260929_2112/CN115637570A_original.pdf';EXPECTED='ce0112648ae509c464bb45ab3fb639cbc98f53b3a3f4f146a80abc48de43d456'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(v):return json.dumps(v,ensure_ascii=False,indent=2)+'\n'
def baseline(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=H)
def target(m):
 hits=[s for s in m['samples'] if s['sample_id']==SID and s['representative_publication']==PUB];assert len(hits)==1;return hits[0]
def module(path,name):
 sp=importlib.util.spec_from_file_location(name,path);v=importlib.util.module_from_spec(sp);sys.modules[name]=v;sys.path.insert(0,str(R/'scripts'));sp.loader.exec_module(v);return v
old=json.loads(baseline('corrections/20260929_r1/data/analysis_master.json'));m=json.loads(M.read_bytes());s=target(m);prior=target(old)
assert sha(PDF)==EXPECTED
reader=PdfReader(str(PDF));assert len(reader.pages)==11
body='\n'.join(re.sub(r'说\s*明\s*书\s*\d+/6\s*页\s*\d+\s*CN\s*115637570\s*A\s*\d+','',p.extract_text() or '') for p in reader.pages[2:8])
markers=list(re.finditer(r'\[(\d{4})\]',body));paras={int(z.group(1)):re.sub(r'\s+','',body[z.end():(markers[j+1].start() if j+1<len(markers) else len(body))]) for j,z in enumerate(markers)}
assert sorted(paras)==list(range(1,80))
read=prior['review_completeness']['original_A_complete_readback'];assert read['physical_pages_read']==list(range(1,12))
assert read['all_13_fields_addressed_in_A_scope'] and read['source_sha256']==EXPECTED
qa_path=R/'QA/CN115637570A_complete_A_20261001.json';pq=json.loads(qa_path.read_bytes())
assert pq['verified'] and pq['original_A_complete_readback']['all_13_fields_addressed_in_A_scope'] and pq['original_A_complete_readback']['drawing_pages_visually_read']==[9,10,11]
rendered=[]
for n in range(1,12):
 p=R/'evidence'/('CN115637570A_visual_completion_20261004-'+str(n)+'.png' if n in [1,2,6,7,8] else 'CN115637570A_full_A_20261001-'+str(n).zfill(2)+'.png' if n in [3,4,5] else 'CN115637570A_20261001-'+str(n).zfill(2)+'.png')
 assert p.is_file();rendered.append({'physical_page':n,'path':str(p),'sha256':sha(p)})
MAP={'capture':[55,59,61,62,63],'cleaning':[51,52],'transfer':[51,52],'chamber_drainage':[58,78],'solids_dewatering':[52,58,74],'liquid_route':[56,58],'storage':[73,74],'removal':[77,78],'state_switch':[66,67,68,69],'seals_connections':[77,78],'performance':[34,35,36,54],'endpoint':[73,78],'carrier_conditioning':[70,71,74,78]}
J={
 'capture':'筒形权3、上部敞开半筒权4、仅上部进水口局部敞开权5为不同从属构造；3→2→1、4→3、5→3，不把互斥几何拼为单一实施方式。孔径/捕获率未给。',
 'cleaning':'螺旋叶片同水流旋进刮掉网面纤维，借水带入127；刮离动作不等于全部孔隙再生或固体干燥。',
 'transfer':'126把网122纤维刮送至靠出水口的127；模块内转移，不是最终处置。',
 'chamber_drainage':'正常下部排水与开门取袋分开；完整A0001—0079、权1—10、图1—6未定位维护前专用腔排空/残液确认，unknown保持。',
 'solids_dewatering':'刮离、借水输送、袋收集不是独立固体压榨/离心/干燥；完整A范围未定位该工序，unknown保持。',
 'liquid_route':'进水连网内，滤后水经下网与筒下壁间流道到124；仅正常液路，不推维护腔或袋已排干。',
 'storage':'可拆过滤袋与袋中纤维积累明确；0074原文随后说更换过滤网122，原文保留不默修成袋。',
 'removal':'前板安装口和可选门盖使取袋或取整个过滤器可达；不同取出选项分开，不推安全终点。',
 'state_switch':'可选传感器/控制器按较多开电机、较少停并可间歇；不同传感器或组合无统一量化阈值，不强加独立权1。',
 'seals_connections':'前面板安装口11与可选门盖是维护界面，不自动补断管、先排水或防漏实测。',
 'performance':'0034—0036寿命/浓度/沉积及0054效率为作者有益效果陈述，无完整试验协议/N/误差/独立验证；背景1900非本装置实验。',
 'endpoint':'袋和安装口仅取出/清理支持；完整A范围未定位微纤维最终垃圾分类/回收/封装外运去向，unknown保持。',
 'carrier_conditioning':'耐磨材料选择、取袋与0074更换网122不等于介质自身干燥；完整A范围未定位独立载体排水干燥，unknown保持。'}
page_map={n:next(i+1 for i,p in enumerate(reader.pages) if '['+str(n).zfill(4)+']' in (p.extract_text() or '')) for n in {n for ns in MAP.values() for n in ns}|{2,3,7,30}}
assert set(MAP)==set(s['features'])
bindings={'source_path':'revision_20260929/legal/cn115637570_probe_20260929_2112/CN115637570A_original.pdf','source_sha256':EXPECTED,'text_scope':'all paragraphs0001-0079, claims1-10, figures1-6; previous fulltext/drawings plus actual five-page visual completion','original_field_bindings':{f:{'accepted_observation_ids':[o['observation_id'] for o in prior['features'][f]['observations']],'printed_paragraphs':ns,'scope_judgment':J[f],'original_excerpt_bindings':[{'printed_paragraph':n,'physical_page':page_map[n],'evidence_excerpt':paras[n][:180]} for n in ns]} for f,ns in MAP.items()},'historical_original_readback_record':'original_A_complete_readback' ,'source_conflicts_preserved':['0074 filter bag accumulation then replace filter net122; original not silently corrected'],'rendered_pages':rendered,'new_visual_pages_read_20261004':[1,2,6,7,8],'previous_visual_pages_read':[3,4,5,9,10,11]}
scene={'classification':'laundry_wastewater_microfibres_with_microplastic_focus','review_status':STATUS,'publication_id':PUB,'source_path':str(PDF),'source_sha256':EXPECTED,'boundary':'本件洗衣机微纤维过滤；背景微塑料/微纤维与1900引述不是本装置试验，不把所有衣物纤维判塑料。','basis':[{'printed_paragraph':n,'physical_page':page_map[n],'evidence_excerpt':paras[n][:220],'source_role':'background_context' if n in [2,3] else 'description_of_this_invention'} for n in [2,3,7,30]]}
if '--verify' in sys.argv:
 for x,y in zip(old['samples'],m['samples']):
  if x['sample_id']!=SID:assert x==y
  else:
   for k in x:
    if k not in ['scene_material','publications','review_completeness','features']:assert x[k]==y[k]
   for f in x['features']:assert {k:v for k,v in x['features'][f].items() if k!='review_status'}=={k:v for k,v in y['features'][f].items() if k!='review_status'}
   rc=y['review_completeness'];assert rc['current_scope'][:-1]==x['review_completeness']['current_scope']
   assert {k:v for k,v in rc.items() if k not in ['full_text_rechecked','full_text_rechecked_scope',KEY,RECORD,'current_scope']}=={k:v for k,v in x['review_completeness'].items() if k not in ['full_text_rechecked','current_scope']}
 assert s['review_completeness'][RECORD]==bindings and s['scene_material']==scene
 for k in old:
  if k not in ['updated_at','samples']:assert old[k]==m[k]
 csvold=baseline('corrections/20260929_r1/data/review_coverage.csv').splitlines(keepends=True);csvnew=(R/'data/review_coverage.csv').read_bytes().splitlines(keepends=True)
 assert len(csvold)==len(csvnew) and all(x==y for x,y in zip(csvold,csvnew) if PUB.encode() not in x)
 v=module(R/'scripts/verify_and_export.py','cn115_validator');q=v.validate(m)
 assert q['observations']==168 and set(q['accepted_representative_publications'])=={PUB,'CN117702432A','CN118273060A','CN222043626U'}
 for issue in ['missing_receipt','missing_scene','wrong_hash']:
  bad=copy.deepcopy(s)
  if issue=='missing_receipt':bad['review_completeness'].pop(KEY)
  elif issue=='missing_scene':bad['scene_material']['classification']=None
  else:bad['review_completeness'][KEY]['source_sha256']='0'*64
  try:v.validate_acceptance(bad)
  except AssertionError:pass
  else:raise AssertionError(issue+' passed')
 q.update({'baseline':BASE,'target':PUB,'all_old168_observations_unchanged':True,'other13_whole_objects_unchanged':True,'all_legal_unchanged':True,'non_target_CSV_rows_exact_bytes_unchanged':True,'all13_original_field_bindings_verified':True,'original_paragraphs_checked':79,'binding_excerpt_checks':sum(map(len,MAP.values())),'original_render_hashes_checked':11,'original_visual_scope':'old3/4/5 and9/10/11 visual; new1/2/6/7/8 actual visual; cumulative11pages andall6figures','scope':'representative published A only; saved B comparison is separate, original B and current legality remain pending','semantic_negative_checks':['missing receipt','missing scene','wrong source hash'],'unknown_supports_preserved':True,'source_conflict_preserved':True,'historical_QA_unchanged':True,'reset_consumed':False,'failures_before_acceptance':[]})
 q['failures_before_acceptance']=['fitz runtime probe unavailable; no source read/write by fitz. Existing Poppler rendered exact five pages successfully, all later checks restarted.']
 print(dump(q));raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();rc=s['review_completeness']
rc[RECORD]=bindings;rc['full_text_rechecked']=True;rc['full_text_rechecked_scope']='representative_published_document_only'
rc[KEY]={'accepted':True,'publication':PUB,'scope':'representative_published_document_only','accepted_at':now,'source_path':'revision_20260929/legal/cn115637570_probe_20260929_2112/CN115637570A_original.pdf','source_sha256':EXPECTED,'source_page_count':11,'text_pages_read':list(range(1,12)),'visual_pages_read':list(range(1,12)),'description_paragraphs':[1,79],'claims':[1,10],'drawing_pages_read':list(range(9,12)),'figures_read':[1,6],'field_bindings':{f:{'review_record_key':RECORD,'binding_key':f} for f in s['features']},'previous_review_QA':str(qa_path.relative_to(H)),'previous_review_QA_sha256':sha(qa_path),'previous_feature_review_statuses':{f:v['review_status'] for f,v in s['features'].items()},'previous_scene':s['scene_material'],'prior_evidence_preserved':True,'legal_qualification_granted_by_this_acceptance':False,'does_not_accept':['family-wide completion','current legal validity','measured performance','formal statistics','final report','whole project completion']}
rc['current_scope'].append({'publication':PUB,'scope':'representative_published_document_only','acceptance_record':KEY,'at':now});s['scene_material']=scene
for p in s['publications']:
 if p['publication_id']==PUB:p['previous_review_status']=p['review_status'];p['review_status']=STATUS;p['original_source_path']='revision_20260929/legal/cn115637570_probe_20260929_2112/CN115637570A_original.pdf';p['original_source_sha256']=EXPECTED;p['technical_acceptance_record']=KEY
for f in s['features'].values():f['review_status']=STATUS
m['updated_at']=now
# Reuse only the proven unique-sample patch helper without running its generator.
import ast
source=(R/'scripts/accept_cn118_publication_20261004.py').read_text(encoding='utf8');tree=ast.parse(source);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='patch')
import difflib
exec(compile(ast.Module(body=[fn],type_ignores=[]),str(R/'scripts/accept_cn118_publication_20261004.py'),'exec'))
print('*** Begin Patch\n'+patch(M,dump(m))+'*** End Patch')
