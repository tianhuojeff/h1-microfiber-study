"""One positive capture field from original A, preserving old evidence and direction conflict."""
from pathlib import Path
import ast,datetime,difflib,hashlib,importlib.util,json,re,subprocess,sys
from pypdf import PdfReader
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='d3ba1fd63cc20cd5dfe6733859b48dc40a0ae02b';SID='H1-F86813332';PUB='CN116282270A';KEY='original_seals_readback_20261004'
PDF=H/'team_package_20260928/sources/CN116282270A.pdf';EXPECTED='27a8dd557b3b5d1b9c66fe52ba0d2e5ea4b8efc627f4b1318553d7323fce9186'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(v):return json.dumps(v,ensure_ascii=False,indent=2)+'\n'
def target(m):
 v=[s for s in m['samples'] if s['sample_id']==SID and s['representative_publication']==PUB];assert len(v)==1;return v[0]
old=json.loads(subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/analysis_master.json'],cwd=H));m=json.loads(M.read_bytes());s=target(m)
assert sha(PDF)==EXPECTED;r=PdfReader(str(PDF));assert len(r.pages)==13;texts=[p.extract_text() or '' for p in r.pages]
body=re.sub(r'\s+','',re.sub(r'说\s*明\s*书\s*\d+/5\s*页\s*\d+\s*CN\s*116282270\s*A\s*\d+','','\n'.join(texts[3:8])))
marks=list(re.finditer(r'\[(\d{4})\]',body));paras={int(z.group(1)):body[z.end():(marks[j+1].start() if j+1<len(marks) else len(body))] for j,z in enumerate(marks)};assert sorted(paras)==list(range(1,52))
claim_quote='所述收集腔采用分体式螺纹连接结构'
assert claim_quote in re.sub(r'\s+','',texts[1])
storage_quote='旋流器底流出口安装一个带有螺纹的微塑料收集腔5‑8'
assert storage_quote in paras[47]
image7=R/'evidence/CN116282270A_capture_20261004-7.png';image2=R/'evidence/CN116282270A_physical2.png';image10=R/'evidence/CN116282270A_physical10.png'
images=[{'physical_page':n,'path':str(p),'sha256':sha(p)} for n,p in [(2,image2),(7,image7),(10,image10)]]
meaning='收集腔5-8采用分体式螺纹连接，位于旋流器底流且穿洗衣机外壁对应孔，可拧松取出定期清理；接口支持可拆维护，不推另有必需密封圈、默认断全部管路或实测无泄漏。'
oid=PUB+'-seals_connections-threaded_chamber58-20261004'
record={'source_path':str(PDF),'source_sha256':EXPECTED,'executor_text_pages_read':[1,2,7,8],'executor_visual_pages_read':[2,7,10],'rendered_pages':images,'printed_paragraphs_used':[47],'claims_used':[4],'figures_used':[3,4],'reviewed_field':'seals_connections','full_candidate_acceptance':False,'unread_this_round':'other physical pages/remaining five empty fields; previous direction-conflict review unchanged','previous_scene':target(old)['scene_material']}
scene=target(old)['scene_material']
def observation(now):return {'observation_id':oid,'publication_id':PUB,'grant_publication_id':None,'sample_role':'pending','embodiment_id':'cyclone_retention58','stage':'seals_connections','technical_feature':meaning,'object':'带固体的收集腔5-8及底流接口','start':'收集腔与底流连接','end':'螺纹拧松后可取腔','boundary':'分体螺纹维护界面，非实测密封性','operation_order':['螺纹连接安装收集腔','可从底流口拧松','通过对应外壁孔取出以清理'],'support_status':'explicit','review_status':'complete_in_targeted_original_scope','claim_dependency':'权4→3→独立组件权2；不拼方法权1的传动方向或额外密封要求','evidence':[{'locator':'原PDF物理7 [0047]底流收集腔与防回流挡筒','source_path':str(PDF),'source_sha256':EXPECTED,'source_role':'description_of_this_invention','evidence_excerpt':storage_quote,'page_image_path':str(image7),'page_image_sha256':sha(image7),'printed_paragraph':47},{'locator':'原PDF物理2 从属权4分体螺纹','source_path':str(PDF),'source_sha256':EXPECTED,'source_role':'dependent_claim','evidence_excerpt':claim_quote,'page_image_path':str(image2),'page_image_sha256':sha(image2),'claim_number':4}],'interpretation':meaning,'performance_status':'not_verified','verified_at':now,'old_value':target(old)['features']['seals_connections']['support_status'],'new_value':meaning,'change_reason':'原A正向螺纹维护接口字段补空；保留旧传动方向冲突及全部法律门槛','review_scope':'本轮原A物理1/2/7/8文字、2/7/10视觉，仅连接接口锚点；非全文完成'}
if '--verify' in sys.argv:
 for x,y in zip(old['samples'],m['samples']):
  if x['sample_id']!=SID:assert x==y
  else:
   for k in x:
    if k not in ['features','review_completeness','scene_material']:assert x[k]==y[k]
   for f in x['features']:
    if f!='seals_connections':assert x['features'][f]==y['features'][f]
   assert not x['features']['seals_connections']['observations'] and len(y['features']['seals_connections']['observations'])==1
   added=y['features']['seals_connections']['observations'][0];assert added==observation(added['verified_at'])
   assert y['scene_material']==scene and y['review_completeness'][KEY]==record
   assert {k:v for k,v in y['review_completeness'].items() if k!=KEY}==x['review_completeness']
 sp=importlib.util.spec_from_file_location('cn116_current_validator',R/'scripts/verify_and_export.py');v=importlib.util.module_from_spec(sp);sys.modules[sp.name]=v;sys.path.insert(0,str(R/'scripts'));sp.loader.exec_module(v);q=v.validate(m)
 assert q['observations']==172 and q['full_text_complete_count']==4 and not s['review_completeness']['full_text_rechecked']
 oldcsv=subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/review_coverage.csv'],cwd=H).splitlines(keepends=True);newcsv=(R/'data/review_coverage.csv').read_bytes().splitlines(keepends=True)
 assert all(x==y for x,y in zip(oldcsv,newcsv) if not (PUB.encode() in x and b',seals_connections,' in x))
 q.update({'baseline':BASE,'target':PUB,'old171_observations_unchanged':True,'new_observations':1,'other13_whole_objects_unchanged':True,'only_seals_feature_changed':True,'all_legal_and_direction_conflict_unchanged':True,'non_target_CSV_rows_exact_bytes':True,'original_quote_checks':2,'original_source_sha256':EXPECTED,'executor_text_pages_read':[1,2,7,8],'executor_visual_pages_read':[2,7,10],'not_full_candidate_acceptance':True,'reset_consumed':False,'failures_before_apply':[]})
 print(dump(q));raise SystemExit
assert m==old;now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();f=s['features']['seals_connections'];assert not f['observations'];f['observations'].append(observation(now));f['support_status']='explicit';f['review_status']='complete_in_targeted_original_scope';s['review_completeness'][KEY]=record;s['scene_material']=scene;m['updated_at']=now
tree=ast.parse((R/'scripts/accept_cn118_publication_20261004.py').read_text(encoding='utf8'));fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='patch');exec(compile(ast.Module(body=[fn],type_ignores=[]),'unique_sample_patch','exec'))
print('*** Begin Patch\n'+patch(M,dump(m))+'*** End Patch')
