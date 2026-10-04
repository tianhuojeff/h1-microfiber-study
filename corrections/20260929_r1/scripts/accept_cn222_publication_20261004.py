"""Explicit original-U acceptance; old observations and legal state preserved."""
from pathlib import Path
import copy,datetime,hashlib,importlib.util,json,re,subprocess,sys
from pypdf import PdfReader
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='99c14f61e00644dd275330fa1532713953ac635d';SID='H1-F93508213';PUB='CN222043626U'
KEY='publication_technical_acceptance';RECORD='original_U_field_bindings_20261004';STATUS='accepted_in_original_published_scope'
PDF=H/'patents/CN222043626U.pdf';EXPECTED='27b93dc08a6e684face981d4b2d7afedbb8dfad39b59c222d91c09132b0b08b2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(v):return json.dumps(v,ensure_ascii=False,indent=2)+'\n'
def baseline(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=H)
def target(m):
 hits=[s for s in m['samples'] if s['sample_id']==SID and s['representative_publication']==PUB];assert len(hits)==1;return hits[0]
def module(path,name):
 sp=importlib.util.spec_from_file_location(name,path);v=importlib.util.module_from_spec(sp);sys.modules[name]=v;sys.path.insert(0,str(R/'scripts'));sp.loader.exec_module(v);return v
old=json.loads(baseline('corrections/20260929_r1/data/analysis_master.json'));m=json.loads(M.read_bytes());s=target(m);prior=target(old)
assert sha(PDF)==EXPECTED
reader=PdfReader(str(PDF));assert len(reader.pages)==14
body='\n'.join(re.sub(r'说\s*明\s*书\s*\d+/6\s*页\s*\d+\s*CN\s*222043626\s*U\s*\d+','',p.extract_text() or '') for p in reader.pages[2:8])
markers=list(re.finditer(r'\[(\d{4})\]',body));paras={int(z.group(1)):re.sub(r'\s+','',body[z.end():(markers[j+1].start() if j+1<len(markers) else len(body))]) for j,z in enumerate(markers)}
assert sorted(paras)==list(range(1,73))
read=prior['review_completeness']['original_U_readback_20261002'];assert read['physical_pages_read']==read['visual_physical_pages']==list(range(1,15))
assert read['all_13_fields_addressed'] and read['source_sha256']==EXPECTED
for im in read['rendered_pages']:assert sha(im['path'])==im['sha256']
qa_path=R/'QA/CN222043626U_original_review_20261002.json';pq=json.loads(qa_path.read_bytes())
assert pq['verified'] and pq['all_13_fields_addressed_in_original_U_scope'] and pq['all_6_drawing_pages_visually_read'] and pq['old_6_observations_unchanged_and_original_crosschecked']
MAP={'capture':[50],'cleaning':[59,63],'transfer':[48],'chamber_drainage':[59,68],'solids_dewatering':[38,50],'liquid_route':[43,44],'storage':[48,68],'removal':[59,66,67],'state_switch':[59,67],'seals_connections':[66,67],'performance':[54,55,56,71],'endpoint':[44,48,59],'carrier_conditioning':[38,63,68]}
J={
 'capture':'盒内330过滤网截留微塑料；另相近尺寸杂质可同时截留。图3两网及孔径可选关系不推实测效率。',
 'cleaning':'开盖或可选盒门可取出盒/网以清洗，仅支持维护可达及清洗目的；没有具体刷洗、反洗或孔再生程序。',
 'transfer':'微塑料随盒320取出以统一清理；本公布全文未定位松散固体另转独立容器的专用动作。',
 'chamber_drainage':'开盖取盒与正常过水均已披露；全文0001—0072、权1—10及图1—7未定位维护前独立排空腔游离液的动作，unknown保持。',
 'solids_dewatering':'0038脱水/烘干对象是衣物；过滤及盒内收集不能当滤渣脱水。本原件完整范围未定位收集固体脱水，unknown保持。',
 'liquid_route':'接排水管中间或末端为替代安装位置；过滤出水入下水道或可选支路回机体给水，不合并必需双终点。',
 'storage':'320盒暂存微塑料以统一清理；0068闭合进出盒与网状盒为可选分支，不推所有盒密闭、干储或长期防漏。',
 'removal':'拆314取盒，或安装管324沿313a滑动并经319弹性限位拆装。内部安装管不等于外接排水管；不推默认断外管。',
 'state_switch':'开盖维护、装盒合盖密封恢复过滤明确；滑管弹性限位复位是结构分支，不推强制先排干或自动控制。',
 'seals_connections':'324滑动、313a导向和319弹性限位定位；可选盖密封圈/卡扣另行披露，不推实测防漏或强制断外管。',
 'performance':'齿状增面积/减堵、延长周期及便于清洗是作者文字主张，孔径为设计关系；无可复制性能试验/N/误差/独立验证。0055第二网331原编号冲突保留，不默改。',
 'endpoint':'0044下水道/回机体对象是液体；0048/0059统一清理与取盒不证明固体安全终点。原件完整范围未定位滤渣最终分类、回收或销毁，unknown保持。',
 'carrier_conditioning':'衣物脱水/烘干与取网清洗不同于滤介质自身排水或干燥；本原件完整范围未定位该独立工序，unknown保持。'}
page_map={n:next(i+1 for i,p in enumerate(reader.pages) if '['+str(n).zfill(4)+']' in (p.extract_text() or '')) for n in {n for ns in MAP.values() for n in ns}|{4,43,44,45,51}}
assert set(MAP)==set(s['features'])
bindings={'source_path':'patents/CN222043626U.pdf','source_sha256':EXPECTED,'text_scope':'all paragraphs0001-0072, claims1-10, figures1-7; full14visual receipt retained','original_field_bindings':{f:{'accepted_observation_ids':[o['observation_id'] for o in prior['features'][f]['observations']],'printed_paragraphs':ns,'scope_judgment':J[f],'original_excerpt_bindings':[{'printed_paragraph':n,'physical_page':page_map[n],'evidence_excerpt':paras[n][:180]} for n in ns]} for f,ns in MAP.items()},'historical_original_readback_record':'original_U_readback_20261002','source_conflicts_preserved':read['source_conflicts']}
scene={'classification':'laundry_drainage_microplastics_with_optional_other_impurities_and_uses','review_status':STATUS,'publication_id':PUB,'source_path':str(PDF),'source_sha256':EXPECTED,'boundary':'本件洗衣机排水微塑料过滤收集；还可处理相近尺寸杂质或可选清洁池出水，不把所有杂质/所有用途自动称洗衣微塑料。背景35%来源比例不是本装置实测。','basis':[{'printed_paragraph':n,'physical_page':page_map[n],'evidence_excerpt':paras[n][:220],'source_role':'description_of_this_invention_or_optional_use'} for n in [4,43,44,45,51]]}
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
 v=module(R/'scripts/verify_and_export.py','cn222_validator');q=v.validate(m)
 assert q['observations']==168 and set(q['accepted_representative_publications'])=={PUB,'CN117702432A','CN118273060A'}
 for issue in ['missing_receipt','missing_scene','wrong_hash']:
  bad=copy.deepcopy(s)
  if issue=='missing_receipt':bad['review_completeness'].pop(KEY)
  elif issue=='missing_scene':bad['scene_material']['classification']=None
  else:bad['review_completeness'][KEY]['source_sha256']='0'*64
  try:v.validate_acceptance(bad)
  except AssertionError:pass
  else:raise AssertionError(issue+' passed')
 q.update({'baseline':BASE,'target':PUB,'all_old168_observations_unchanged':True,'other13_whole_objects_unchanged':True,'all_legal_unchanged':True,'non_target_CSV_rows_exact_bytes_unchanged':True,'all13_original_field_bindings_verified':True,'original_paragraphs_checked':72,'binding_excerpt_checks':sum(map(len,MAP.values())),'original_render_hashes_checked':14,'original_visual_scope':'all14 pages/all6drawingpages/figures1-7 previously actually read; no new all-page visual claim','scope':'representative published U only; granted publication is not current legal validity','semantic_negative_checks':['missing receipt','missing scene','wrong source hash'],'unknown_supports_preserved':True,'source_conflict_preserved':True,'historical_QA_unchanged':True,'reset_consumed':False,'failures_before_acceptance':[]})
 q['failures_before_acceptance']=['Uncommitted scene boundary mistakenly used 0035 as paragraph for background35percent; corrected to background35percent with no paragraph claim, complete QA restarted. A subsequent QA timestamp patch mismatched and applied zero files; reread actual bytes before repair.']
 print(dump(q));raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();rc=s['review_completeness']
rc[RECORD]=bindings;rc['full_text_rechecked']=True;rc['full_text_rechecked_scope']='representative_published_document_only'
rc[KEY]={'accepted':True,'publication':PUB,'scope':'representative_published_document_only','accepted_at':now,'source_path':'patents/CN222043626U.pdf','source_sha256':EXPECTED,'source_page_count':14,'text_pages_read':list(range(1,15)),'visual_pages_read':list(range(1,15)),'description_paragraphs':[1,72],'claims':[1,10],'drawing_pages_read':list(range(9,15)),'figures_read':[1,7],'field_bindings':{f:{'review_record_key':RECORD,'binding_key':f} for f in s['features']},'previous_review_QA':str(qa_path.relative_to(H)),'previous_review_QA_sha256':sha(qa_path),'previous_feature_review_statuses':{f:v['review_status'] for f,v in s['features'].items()},'previous_scene':s['scene_material'],'prior_evidence_preserved':True,'legal_qualification_granted_by_this_acceptance':False,'does_not_accept':['family-wide completion','current legal validity','measured performance','formal statistics','final report','whole project completion']}
rc['current_scope'].append({'publication':PUB,'scope':'representative_published_document_only','acceptance_record':KEY,'at':now});s['scene_material']=scene
for p in s['publications']:
 if p['publication_id']==PUB:p['previous_review_status']=p['review_status'];p['review_status']=STATUS;p['original_source_path']='patents/CN222043626U.pdf';p['original_source_sha256']=EXPECTED;p['technical_acceptance_record']=KEY
for f in s['features'].values():f['review_status']=STATUS
m['updated_at']=now
# Reuse only the proven unique-sample patch helper without running its generator.
import ast
source=(R/'scripts/accept_cn118_publication_20261004.py').read_text(encoding='utf8');tree=ast.parse(source);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='patch')
import difflib
exec(compile(ast.Module(body=[fn],type_ignores=[]),str(R/'scripts/accept_cn118_publication_20261004.py'),'exec'))
print('*** Begin Patch\n'+patch(M,dump(m))+'*** End Patch')
