"""Bind seven existing observations to original A paragraphs/claims; no completion promotion."""
from pathlib import Path
import ast,datetime,difflib,hashlib,importlib.util,json,re,subprocess,sys
from pypdf import PdfReader
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='443d67f87e2df1ff7a9bd5ce51282a3c31c76698';SID='H1-F72658993';PUB='CN112914464A';KEY='original_old7_bindings_20261004'
PDF=H/'patents/verification/20260928_cn112914464a_ep3832001b1/CN112914464A.pdf';EXPECTED='d784ea097857f7d3799ea36e49d7e3d89c1ec1501a2adb9cdb6aefa61e97460c'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(v):return json.dumps(v,ensure_ascii=False,indent=2)+'\n'
def target(m):
 v=[s for s in m['samples'] if s['sample_id']==SID and s['representative_publication']==PUB];assert len(v)==1;return v[0]
old=json.loads(subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/analysis_master.json'],cwd=H));m=json.loads(M.read_bytes());s=target(m)
assert sha(PDF)==EXPECTED
r=PdfReader(str(PDF));assert len(r.pages)==23
texts=[p.extract_text() or '' for p in r.pages]
body='\n'.join(re.sub(r'说\s*明\s*书\s*\d+/11\s*页\s*\d+\s*CN\s*112914464\s*A\s*\d+','',t) for t in texts[4:15])
body=re.sub(r'\s+','',body)
marks=list(re.finditer(r'\[(\d{4})\]',body));paras={int(z.group(1)):body[z.end():(marks[j+1].start() if j+1<len(marks) else len(body))] for j,z in enumerate(marks)}
assert sorted(paras)==list(range(1,65))
cltext='\n'.join(re.sub(r'权\s*利\s*要\s*求\s*书\s*\d+/3\s*页\s*\d+\s*CN\s*112914464\s*A\s*\d+','',t) for t in texts[1:4]);cm=list(re.finditer(r'(?m)^\s*(\d{1,2})\.',cltext));claims={int(z.group(1)):re.sub(r'\s+','',cltext[z.end():(cm[j+1].start() if j+1<len(cm) else len(cltext))]) for j,z in enumerate(cm)}
assert sorted(claims)==list(range(1,30))
MAP={'cleaning':([35],[]),'transfer':([35,37],[]),'solids_dewatering':([38],[]),'liquid_route':([38],[]),'removal':([40],[22]),'seals_connections':([],[24]),'endpoint':([],[23])}
J={'cleaning':'图1泵31经42到27反冲洗剥离，控制器46致动；非其他图分配器共同链。','transfer':'图1滤物经44转入抽屉20并在图2容器63集中收集，未在容器内首次产生。','solids_dewatering':'图2可选额外62使水流走以集中/增稠滤物，原文目的为较少水，不给含水率实测。','liquid_route':'可选62分离水回导水装置，例如22；不是据此认定固体排环境或净水零颗粒。','removal':'权22移出并排空/移出以排空，图2正文40另处置滤物再用容器；不同对象路径保留。','seals_connections':'权24直接依附22：拆分容器替换、结构单元插回；与权23同级，不拼23→24强制链。','endpoint':'权23直接依附22：先移整个结构单元再机械拆容器，处置或交处置公司；是公开技术建议，不是实际安全处置效果。'}
rc=target(old)['review_completeness']['original_A_readback'];assert rc['physical_pages_read']==list(range(1,24)) and rc['all_13_fields_addressed']
for im in rc['all_drawing_pages_visually_read']:assert sha(im['path'])==im['sha256']
numbering=R/'evidence/CN112914464A_numbering_20261004-6.png';assert numbering.is_file()
bindings={'source_path':str(PDF.relative_to(H)),'source_sha256':EXPECTED,'executor_text_pages_revisited':[3,4,6,11,12],'previous_complete_text_and_all_drawings_receipt':'original_A_readback','full_candidate_acceptance':False,'original_field_bindings':{},'rendered_pages':[{'physical_page':6,'path':str(numbering),'sha256':sha(numbering)}],'new_visual_page_read':6,'extraction_boundary':'0009 printed intact on physical6; PDF extracted [0 linebreak009], whitespace-normalized parser restored only extraction token, original bytes unchanged'}
for f,(ns,cs) in MAP.items():
 quotes=[{'printed_paragraph':n,'physical_page':next(i+1 for i,t in enumerate(texts) if '['+str(n).zfill(4)+']' in t),'evidence_excerpt':paras[n][:220]} for n in ns]
 quotes += [{'claim':n,'physical_pages':[3,4] if n==23 else [3] if n==22 else [4],'evidence_excerpt':claims[n],'dependency':'direct claim22' if n in [23,24] else 'method using claim1'} for n in cs]
 bindings['original_field_bindings'][f]={'observation_ids_preserved':[o['observation_id'] for o in target(old)['features'][f]['observations']],'scope_judgment':J[f],'original_excerpt_bindings':quotes}
if '--verify' in sys.argv:
 for x,y in zip(old['samples'],m['samples']):
  if x['sample_id']!=SID:assert x==y
  else:
   for k in x:
    if k!='review_completeness':assert x[k]==y[k]
   assert {k:v for k,v in y['review_completeness'].items() if k!=KEY}==x['review_completeness']
   assert y['review_completeness'][KEY]==bindings
 assert subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/review_coverage.csv'],cwd=H)==(R/'data/review_coverage.csv').read_bytes()
 sp=importlib.util.spec_from_file_location('cn112_binding_validator',R/'scripts/verify_and_export.py');v=importlib.util.module_from_spec(sp);sys.modules[sp.name]=v;sys.path.insert(0,str(R/'scripts'));sp.loader.exec_module(v);q=v.validate(m)
 assert q['observations']==168 and q['full_text_complete_count']==4 and not s['review_completeness']['full_text_rechecked']
 q.update({'baseline':BASE,'target':PUB,'old168_observations_and_all_features_unchanged':True,'other13_whole_objects_unchanged':True,'all_legal_scene_publication_unchanged':True,'CSV_exact_bytes_unchanged':True,'original_PDF_sha256':EXPECTED,'fields':list(MAP),'original_paragraphs':64,'original_claims':29,'binding_excerpt_checks':sum(len(ns)+len(cs) for ns,cs in MAP.values()),'existing_drawing_hashes_checked':8,'executor_text_pages_revisited':[3,4,11,12],'full_text_flag_not_promoted':True,'reset_consumed':False,'failures_before_apply':['Combined source output exceeded display budget; reread precise source pages in two complete blocks before binding.']})
 q['executor_text_pages_revisited']=[3,4,6,11,12]
 q['new_visual_page_read']=6
 q['failures_before_apply'].append('Strict four-digit token parser missed0009 due extracted linebreak [0 newline009]; generator failed before master patch. Physical6 render visually confirms printed0009, parser normalized whitespace and entire QA restarted.')
 print(dump(q));raise SystemExit
assert m==old;s['review_completeness'][KEY]=bindings;m['updated_at']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
tree=ast.parse((R/'scripts/accept_cn118_publication_20261004.py').read_text(encoding='utf8'));fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='patch');exec(compile(ast.Module(body=[fn],type_ignores=[]),'unique_sample_patch','exec'))
print('*** Begin Patch\n'+patch(M,dump(m))+'*** End Patch')
