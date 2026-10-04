"""Complete the remaining five fields in the actually read published A scope."""
from pathlib import Path
import ast,datetime,difflib,hashlib,importlib.util,json,re,subprocess,sys
from pypdf import PdfReader
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='4745469e7aa8cd73d5b05c5e55c9f09d4adbd8ed';SID='H1-F86813332';PUB='CN116282270A';KEY='original_complete_bindings_20261004'
REL='team_package_20260928/sources/CN116282270A.pdf';PDF=H/REL;EXPECTED='27a8dd557b3b5d1b9c66fe52ba0d2e5ea4b8efc627f4b1318553d7323fce9186'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(v):return json.dumps(v,ensure_ascii=False,indent=2)+'\n'
def target(m):
 z=[s for s in m['samples'] if s['sample_id']==SID and s['representative_publication']==PUB];assert len(z)==1;return z[0]
old=json.loads(subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/analysis_master.json'],cwd=H));m=json.loads(M.read_bytes());s=target(m)
assert sha(PDF)==EXPECTED;r=PdfReader(str(PDF));assert len(r.pages)==13;texts=[p.extract_text() or '' for p in r.pages]
body=re.sub(r'\s+','',re.sub(r'说\s*明\s*书\s*\d+/5\s*页\s*\d+\s*CN\s*116282270\s*A\s*\d+','','\n'.join(texts[3:8])))
marks=list(re.finditer(r'\[(\d{4})\]',body));paras={int(z.group(1)):body[z.end():(marks[j+1].start() if j+1<len(marks) else len(body))] for j,z in enumerate(marks)};assert sorted(paras)==list(range(1,52))
def im(n):
 if n==2 or n in [9,10,11]:return R/('evidence/CN116282270A_physical'+str(n)+'.png')
 if n==7:return R/'evidence/CN116282270A_capture_20261004-7.png'
 return R/('evidence/CN116282270A_remaining_20261004-'+str(n)+'.png')
images=[{'physical_page':n,'path':str(im(n)),'sha256':sha(im(n))} for n in range(1,14)]
def ev(n,p,q=None):
 quote=q or paras[p];assert quote in paras[p]
 return {'locator':f'原PDF物理{n} [ {p:04d} ]','printed_paragraph':p,'physical_page':n,'evidence_excerpt':quote,'source_path':str(PDF),'source_sha256':EXPECTED,'source_role':'description_of_this_invention','subject_role':'this_invention_or_optional_embodiment','page_image_path':str(im(n)),'page_image_sha256':sha(im(n))}
defs={
 'chamber_drainage':('not_located_in_reviewed_scope','原公布A全5权项/51段/图1—9范围，未定位维护前排空过滤腔、套管或收集腔游离液的专门动作。漂洗20出水、旋流5-1→19正常出水不等同维护排空；旋拧取腔未披露先排净顺序，unknown非0。',[(5,23),(6,33),(8,50)],'腔内游离液体'),
 'solids_dewatering':('not_located_in_reviewed_scope','原公布A明确旋流固液分离并把固体送入5-8，但完整范围未定位针对已收集固体降低附着/夹带水的独立压榨、离心压干或含水率控制。洗衣机脱水甩干是动力阶段，旋流分离不自动等于固体脱水；无含水率实测，unknown非0。',[(6,27),(8,50)],'进入5-8的微塑料等固体及夹带液'),
 'performance':('explicit','[0030—0034]的无需额外能耗、小巧/易维护、自动反冲洗、高效去除与避免外排均为专利作者效果陈述；原公布A全部说明书/权项/图未定位实测方法、样本量、去除率或能耗比较数据。不得宣称这些效果已实证、完全零排放或跨样本性能排名。',[(6,30),(6,31),(6,32),(6,34)],'作者性能效果陈述与实测边界'),
 'endpoint':('not_located_in_reviewed_scope','[0033]/[0047]明确外部拆卸、定期收集/清理收集腔；原公布A完整技术范围未定位收集后的垃圾分类、回收设施、销毁等具体最终去向。取腔收集的正向维护路径保留，不以缺终点否认移出，也不推安全处置已经完成。',[(6,33),(7,47)],'取出的含微塑料收集腔与后续固体'),
 'carrier_conditioning':('not_located_in_reviewed_scope','原公布A全技术范围未定位滤网18自身使用后排水/干燥调理步骤；[0009]/[0032]低压反冲洗是剥离滤面固体，洗衣机脱水不是过滤介质干燥。保持限定未定位与unknown，不填0。',[(4,9),(6,32)],'过滤网18自身水分与调理')
}
maps={'capture':[(7,48)],'cleaning':[(4,9),(7,49)],'transfer':[(6,27),(8,50)],'chamber_drainage':defs['chamber_drainage'][2],'solids_dewatering':defs['solids_dewatering'][2],'liquid_route':[(5,23),(7,48),(8,50)],'storage':[(5,18),(5,22)],'removal':[(5,24),(6,33),(7,47)],'state_switch':[(4,9),(5,14),(7,48),(7,49)],'seals_connections':[(5,24),(7,47)],'performance':defs['performance'][2],'endpoint':defs['endpoint'][2],'carrier_conditioning':defs['carrier_conditioning'][2]}
def obs(k,now):
 status,meaning,locs,obj=defs[k]
 return {'observation_id':PUB+'-'+k+'-complete_original-20261004','publication_id':PUB,'grant_publication_id':None,'sample_role':'pending','embodiment_id':'published_A_complete_scope','stage':k,'technical_feature':meaning,'object':obj,'start':'已披露过滤/旋流/收集路径','end':'原A范围裁定，不补未披露终点','boundary':'原公布A物理1—13/权1—5/[0001]—[0051]/图1—9；不跨B或同族','operation_order':['区分漂洗过滤、甩干反洗旋流、外部旋拧维护','限定原件完整范围，不把液路或衣物脱水混成目标功能'],'support_status':status,'review_status':'complete_in_original_published_scope','claim_dependency':'权1方法/权2组件分别独立；权3→2、4→3、权5择用2/3/4，不拼方向相反独立项','evidence':[ev(n,p) for n,p in locs],'interpretation':meaning,'performance_status':'text_claim_only' if k=='performance' else 'not_verified','verified_at':now,'old_value':target(old)['features'][k]['support_status'],'new_value':meaning,'change_reason':'实际补读剩余原页和全部附图范围后闭合五空格，不从局部推负向','review_scope':'公布A完整原件范围，未知不转0，原方向冲突保留'}
def record(sample):
 bindings={k:{'accepted_observation_ids':[o['observation_id'] for o in sample['features'][k]['observations']],'evidence':[ev(n,p) for n,p in locs],'scope_judgment':defs[k][1] if k in defs else '原件绑定既有观察，原支持/未知/方向冲突不改写'} for k,locs in maps.items()}
 return {'source_path':str(PDF),'source_sha256':EXPECTED,'new_text_pages':[3,4,5,6],'new_visual_pages':[1,3,4,5,6,8,12,13],'previous_text_pages':[1,2,7,8],'previous_visual_pages':[2,7,9,10,11],'historical_drawings_reused':[9,10,11],'cumulative_text_pages':list(range(1,14)),'cumulative_visual_pages':list(range(1,14)),'rendered_pages':images,'bindings':bindings,'scope':'51原段/5权项/5图页9图；明确未定位仅该版本；方向冲突保留'}
if '--verify' in sys.argv:
 for x,y in zip(old['samples'],m['samples']):
  if x['sample_id']!=SID:assert x==y
  else:
   for k in x:
    if k not in ['features','review_completeness','scene_material','publications']:assert x[k]==y[k]
   for k,fx in x['features'].items():
    fy=y['features'][k]
    for a in fx:
     if a not in ['review_status','support_status','observations']:assert fx[a]==fy[a]
    if k in defs:assert len(fy['observations'])==1 and fy['observations'][0]==obs(k,fy['observations'][0]['verified_at']) and fy['support_status']==defs[k][0]
    else:assert fx['observations']==fy['observations'] and fx['support_status']==fy['support_status']
   rcx=x['review_completeness'];rcy=y['review_completeness']
   for k in rcx:
    if k!='full_text_rechecked':assert rcx[k]==rcy[k]
   assert rcy[KEY]==record(y)
 sp=importlib.util.spec_from_file_location('cn116_complete_validator',R/'scripts/verify_and_export.py');v=importlib.util.module_from_spec(sp);sys.modules[sp.name]=v;sys.path.insert(0,str(R/'scripts'));sp.loader.exec_module(v);q=v.validate(m)
 assert q['observations']==177 and q['full_text_complete_count']==5
 prior=subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/review_coverage.csv'],cwd=H).splitlines(keepends=True);current=(R/'data/review_coverage.csv').read_bytes().splitlines(keepends=True);assert all(a==b for a,b in zip(prior,current) if PUB.encode() not in a)
 q.update({'baseline':BASE,'target':PUB,'old172_observations_exactly_preserved':True,'other13_whole_objects_unchanged':True,'only_five_empty_features_new_observations':True,'old_direction_conflict_preserved':True,'legal14_pending_unchanged':True,'non_target_CSV_exact_bytes':True,'original_pdf_sha256':EXPECTED,'13_bindings_and_all_image_bytes_checked':True,'new_text_pages':[3,4,5,6],'new_visual_pages':[1,3,4,5,6,8,12,13],'historical_9_10_11_reused':True,'true_unfilled_fields':28,'reset_consumed':False})
 print(dump(q));raise SystemExit
assert m==old;now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
for k in defs:
 f=s['features'][k];assert not f['observations'];f['observations']=[obs(k,now)];f['support_status']=defs[k][0]
for f in s['features'].values():f['review_status']='accepted_in_original_published_scope'
rc=s['review_completeness'];rc[KEY]=record(s);rc['full_text_rechecked']=True
rc['publication_technical_acceptance']={'accepted':True,'publication':PUB,'scope':'representative_published_document_only','accepted_at':now,'source_path':REL,'source_sha256':EXPECTED,'source_page_count':13,'text_pages_read':list(range(1,14)),'visual_pages_read':list(range(1,14)),'field_bindings':{k:{'review_record_key':KEY,'binding_key':k} for k in maps},'legal_qualification_granted_by_this_acceptance':False,'unresolved_original_direction_conflict_preserved':True,'does_not_accept':['current legal validity','family/B technical completeness','measured performance','whole P2 or project completion']}
s['scene_material']['review_status']='accepted_in_original_published_scope'
for p in s['publications']:p['review_status']='accepted_in_original_published_scope'
m['updated_at']=now
tree=ast.parse((R/'scripts/accept_cn118_publication_20261004.py').read_text(encoding='utf8'));fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='patch');exec(compile(ast.Module(body=[fn],type_ignores=[]),'unique_sample_patch','exec'))
print('*** Begin Patch\n'+patch(M,dump(m))+'*** End Patch')
