"""Complete explicit published-A scope acceptance without changing old observations."""
from pathlib import Path
import ast,datetime,difflib,hashlib,importlib.util,json,re,subprocess,sys
from pypdf import PdfReader
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='c089d5344d2e1a98f0cf094f1735b915994f0771';SID='H1-F72658993';PUB='CN112914464A'
KEY='original_remaining6_bindings_20261004';A='publication_technical_acceptance';STATUS='accepted_in_original_published_scope'
PDF=H/'patents/verification/20260928_cn112914464a_ep3832001b1/CN112914464A.pdf';EXPECTED='d784ea097857f7d3799ea36e49d7e3d89c1ec1501a2adb9cdb6aefa61e97460c'
NEW=[1,2,3,4,5,7,8,9,10,11,12,13,14,15]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(v):return json.dumps(v,ensure_ascii=False,indent=2)+'\n'
def target(m):
 v=[s for s in m['samples'] if s['sample_id']==SID and s['representative_publication']==PUB];assert len(v)==1;return v[0]
def base(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=H)
old=json.loads(base('corrections/20260929_r1/data/analysis_master.json'));m=json.loads(M.read_bytes());s=target(m);prev=target(old)
assert sha(PDF)==EXPECTED
reader=PdfReader(str(PDF));assert len(reader.pages)==23
texts=[p.extract_text() or '' for p in reader.pages]
body='\n'.join(re.sub(r'说\s*明\s*书\s*\d+/11\s*页\s*\d+\s*CN\s*112914464\s*A\s*\d+','',t) for t in texts[4:15]);body=re.sub(r'\s+','',body)
marks=list(re.finditer(r'\[(\d{4})\]',body));paras={int(z.group(1)):body[z.end():(marks[j+1].start() if j+1<len(marks) else len(body))] for j,z in enumerate(marks)}
assert sorted(paras)==list(range(1,65))
MAP={'capture':[33],'chamber_drainage':[38,40],'storage':[37],'state_switch':[34,35,40,50,62,63,64],'performance':[27,38],'carrier_conditioning':[38,40,60]}
J={'capture':'图1过滤器26从排出或循环洗衣水中截留衣物磨损颗粒，尤其塑料微纤维；非所有衣物颗粒均塑料。',
'chamber_drainage':'全原A权1—29、说明0001—0064及图1—12范围未定位维护前专门排空某腔游离液动作；可选62正常分水及容器排空不自动等于该程序，保留unknown。',
'storage':'图2闭合容器63接收并集中暂留滤物65，入口68；独立袋体/刚性结构单元是其他可选方式，不能全部拼为统一储存结构。',
'state_switch':'图1泵31/阀33、38路由，满位信号提示移出；0050明确可继续使用并非强制停机。图11/12头677旋转180度是另一独立分配实施方式，不拼为同一动作链。',
'performance':'0027至少5/10等洗涤周期及30/40为容量设计陈述；0038集中增稠、较少水为目的。全本件未定位相应独立测试方法/N/误差或实测含水率，保留原文本主张语义。',
'carrier_conditioning':'0038可选滤纸/非织造材料弃置或保留；0060袋体清洁/替换不等于过滤介质自身排水干燥。全原件范围未定位独立介质调理步骤，unknown不转0。'}
prior=prev['review_completeness'];old7=prior['original_old7_bindings_20261004'];draw=prior['original_A_readback']['all_drawing_pages_visually_read']
assert prior['original_A_readback']['physical_pages_read']==list(range(1,24)) and set(old7['original_field_bindings'])|set(MAP)==set(s['features'])
for im in draw+old7['rendered_pages']:assert sha(im['path'])==im['sha256']
imgs=[{'physical_page':i,'path':str(R/'evidence'/f'{PUB}_accept_20261004-{i}.png'),'sha256':sha(R/'evidence'/f'{PUB}_accept_20261004-{i}.png')} for i in NEW]
assert set(NEW+[6]+[im['physical_page'] for im in draw])==set(range(1,24))
record={'source_path':str(PDF.relative_to(H)),'source_sha256':EXPECTED,'new_visual_pages_read':NEW,'previous_visual_page6_record':'original_old7_bindings_20261004','previous_full_text_and_drawing_record':'original_A_readback','cumulative_text_pages':list(range(1,24)),'cumulative_visual_pages':list(range(1,24)),'rendered_pages':imgs,'original_field_bindings':{}}
for f,ns in MAP.items():
 quotes=[{'printed_paragraph':n,'physical_page':next(i+1 for i,t in enumerate(texts) if '['+str(n).zfill(4)+']' in re.sub(r'\s+','',t)),'evidence_excerpt':paras[n][:260]} for n in ns]
 record['original_field_bindings'][f]={'observation_ids_preserved':[o['observation_id'] for o in prev['features'][f]['observations']],'scope_judgment':J[f],'original_excerpt_bindings':quotes}
scene={'classification':'明确包括洗衣微纤维或微塑料','review_status':STATUS,'publication_id':PUB,'source_path':str(PDF.relative_to(H)),'source_sha256':EXPECTED,'scope_note':'本件洗衣机/洗干一体机排出或循环洗衣水，过滤衣物磨损颗粒，尤其塑料纤维或微塑料；本件未把所有衣物颗粒自动等同塑料。','basis':[{'printed_paragraph':n,'physical_page':5 if n in [1,6] else 11,'evidence_excerpt':paras[n][:260]} for n in [1,6,33]]}
if '--verify' in sys.argv:
 for x,y in zip(old['samples'],m['samples']):
  if x['sample_id']!=SID:assert x==y
  else:
   for k in x:
    if k not in ['scene_material','publications','review_completeness','features']:assert x[k]==y[k]
   for f in x['features']:
    assert x['features'][f]['observations']==y['features'][f]['observations']
    assert {k:v for k,v in x['features'][f].items() if k!='review_status'}=={k:v for k,v in y['features'][f].items() if k!='review_status'}
   rc=y['review_completeness'];assert rc[KEY]==record and rc['full_text_rechecked']
   assert {k:v for k,v in rc.items() if k not in [KEY,A,'full_text_rechecked','full_text_rechecked_scope','current_scope']}=={k:v for k,v in x['review_completeness'].items() if k not in ['full_text_rechecked','current_scope']}
   assert rc['current_scope'][:-1]==x['review_completeness']['current_scope']
 assert s['scene_material']==scene
 assert all(x==y for x,y in zip(base('corrections/20260929_r1/data/review_coverage.csv').splitlines(),(R/'data/review_coverage.csv').read_bytes().splitlines()) if PUB.encode() not in x)
 for k in old:
  if k not in ['samples','updated_at']:assert old[k]==m[k]
 spec=importlib.util.spec_from_file_location('cn112_accept_validator',R/'scripts/verify_and_export.py');v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;sys.path.insert(0,str(R/'scripts'));spec.loader.exec_module(v);q=v.validate(m)
 assert q['observations']==177 and q['full_text_complete_count']==6
 q.update({'baseline':BASE,'target':PUB,'old177_observations_preserved':True,'other13_whole_objects_unchanged':True,'all_legal_unchanged':True,'non_target_CSV_exact_unchanged':True,'original_PDF_sha256':EXPECTED,'new_visual_pages':NEW,'reused_visual_page6':True,'reused_drawing_pages':list(range(16,24)),'all23_visual_and_text_pages_read':True,'all13_original_fields_bound':True,'new_original_excerpt_bindings':sum(map(len,MAP.values())),'scene_old_cross_candidate_note_replaced_with_this_publication_basis':True,'acceptance_scope':'representative published A only; not family/granted scope/current legal status','reset_consumed':False,'failures_before_acceptance':[]});print(dump(q));raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();rc=s['review_completeness'];rc[KEY]=record
rc[A]={'accepted':True,'publication':PUB,'scope':'representative_published_document_only','accepted_at':now,'source_path':str(PDF.relative_to(H)),'source_sha256':EXPECTED,'source_page_count':23,'text_pages_read':list(range(1,24)),'visual_pages_read':list(range(1,24)),'claims':[1,29],'description_paragraphs':[1,64],'drawing_pages_read':list(range(16,24)),'field_bindings':{f:{'review_record_key':KEY if f in MAP else 'original_old7_bindings_20261004','binding_key':f} for f in s['features']},'previous_scene':s['scene_material'],'previous_feature_review_statuses':{f:v['review_status'] for f,v in s['features'].items()},'legal_qualification_granted_by_this_acceptance':False,'does_not_accept':['family member completeness','current legal status','measured performance','formal statistics','final report','whole P2/project completion']}
rc['full_text_rechecked']=True;rc['full_text_rechecked_scope']='representative_published_document_only';rc['current_scope'].append({'publication':PUB,'scope':'representative_published_document_only','acceptance_record':A,'at':now})
s['scene_material']=scene
for p in s['publications']:
 if p['publication_id']==PUB:p.update({'previous_review_status':p['review_status'],'review_status':STATUS,'original_source_path':str(PDF.relative_to(H)),'original_source_sha256':EXPECTED,'technical_acceptance_record':A})
for f in s['features'].values():f['review_status']=STATUS
m['updated_at']=now
tree=ast.parse((R/'scripts/accept_cn118_publication_20261004.py').read_text(encoding='utf8'));fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='patch');exec(compile(ast.Module(body=[fn],type_ignores=[]),'unique_sample_patch','exec'))
print('*** Begin Patch\n'+patch(M,dump(m))+'*** End Patch')
