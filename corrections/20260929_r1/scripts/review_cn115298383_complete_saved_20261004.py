"""Nine bounded saved-text fields; keep original-document and legal gaps explicit."""
from pathlib import Path
import ast,datetime,difflib,hashlib,importlib.util,json,subprocess,sys
from local_source import read_anchors
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='7a14b55193e635d2272d3147467cd328c6cd7315';SID='H1-F70804819';PUB='CN115298383A';KEY='complete_saved_text_review_20261004'
SRC=H/'team_package_20260928/sources/CN115298383A.html';EXPECTED='78e6bc2d1f0f5828a42891071f7ca12c54df153e1957438f2f944c3e3e50285d'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(v):return json.dumps(v,ensure_ascii=False,indent=2)+'\n'
def target(m):
 v=[s for s in m['samples'] if s['sample_id']==SID and s['representative_publication']==PUB];assert len(v)==1;return v[0]
def base(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=H)
old=json.loads(base('corrections/20260929_r1/data/analysis_master.json'));m=json.loads(M.read_bytes());s=target(m);prev=target(old)
assert sha(SRC)==EXPECTED;a=read_anchors(SRC);keys=['p'+str(i).zfill(4) for i in range(1,135)]+['cl'+str(i).zfill(4) for i in range(1,21)];assert set(a)==set(keys)
DATA={
'chamber_drainage':(['p0110','p0111'],'explicit','fig9_drainage','支撑件20下方空间蓄积的游离流出液','下部空间','管道110及废水系统',['再生前床层排水','开启111排出下部积液'],
'图9描述排水前/期间阀111可打开排放蓄积液；0111明确残液穿床/支撑件后积聚在130下方，开111经110排出。这是再生前下部游离液排放正向路径，不能沿旧有限权项未定位。床层排水另属carrier_conditioning，非收集滤渣脱水；完全排空/剩余量未实测。'),
'solids_dewatering':(['cl0017','p0108','p0109','p0132'],'not_located_in_reviewed_scope','complete_saved_scope','已被下游收集的微纤维夹带液','下游袋/膜/旋流所收纤维','unknown',[],
'完整保存134描述/20权项未定位下游已收集微纤维另行压滤、离心或干燥减水动作。权17/0108/0109排水干燥对象是颗粒介质，0132先床层排水干燥再气流将纤维送袋；不能把介质残湿95%或床层液体体积分数<10%赋给袋中滤渣。未知不转0，结论仅保存文本。'),
'liquid_route':(['p0057','p0085','p0086','p0111','p0130'],'explicit','normal_outlet_optional_bypass','过滤流出液、可选旁路未过滤积液及排水残液','床层上方/下方','废水排放系统',['向下渗滤','110出液或可选旁路','图9开111排液'],
'正常过滤水经支撑件下方110可接废水系统/主排水上游虹吸；外部140和内部140分别是积液旁路可选变体，绕过介质的一部分水不得称已滤净。图9积液通过111/110排出；应用例重力排放。不同变体不默认同时具备，不补零颗粒或零排放。'),
'storage':(['p0077','p0120','p0132'],'explicit','downstream_collection_example','再生带出的微纤维','上升气流','下游膜/旋流或应用例一次性过滤袋',['再生释放','下游收集暂留'],
'文本明确再生下游膜过滤器/旋流室收集；应用例商业吸尘器一次性过滤袋接收纤维，可记录含物载体暂留。上游腔11储的是流出液非专门储渣盒，外壳40供积液/床膨胀，不能冒长期安全干储、防漏或所有变体内置收集袋。'),
'removal':(['p0077','p0120','p0132'],'not_located_in_reviewed_scope','complete_saved_scope','下游收集的纤维或载物袋','下游收集器','用户侧具体移出界面unknown',[],
'全保存文本有气流把纤维带出滤床进入收集器/一次性袋，但未定位用户如何取出袋、清空器或排出已收集固体的具体界面/程序。不能由一次性自动补拆袋扔垃圾；保留正向transfer/storage，移出具体程序unknown不转0。'),
'state_switch':(['p0092','p0096','p0097','p0105','p0106','p0132'],'explicit','alternative_control_variants','流出液/再生气体及床层','过滤状态','再生状态再返回过滤',['按不同变体切换阀路','床层再生','停止抽吸沉降恢复'],
'过滤与再生分态；图6两三通阀58/61和图7六通阀62是可选不同控制配置，不拼必须全部阀。应用例58关100开120、等待5h床排水干燥、120接吸尘器，130进气/110止回关闭；停抽后床粒沉降再开100关120。正文0105为20—150，权15/0034为50—150；触发百分比0106原文保留，不改为统一次数或强制全部触发。'),
'seals_connections':(['p0059','p0082','p0112','p0113','p0132'],'explicit','external_regeneration_connections','外壳开口及外接再生设备','过滤连接','气抽吸/热气设备接口',['按变体连接120或130','改变过滤/再生阀路'],
'明确外接气抽吸/吹气装置开口连接及应用例120接商业吸尘器；图9下部130抽吸、上部120热气，干燥后抽吸改接120是该独立方式。0082密封废水连接时额外通风口、开放虹吸时可无需额外口是替代条件，不默认全密封。未定位必须开盖/断管取袋、防漏实测或统一拆装方式。'),
'performance':(['p0060','p0108','p0109','p0121','p0126','p0128','p0131','p0133'],'text_claim_only','application_example_not_independent_validation','捕获效率/床层残湿/运行参数','专利参数与应用例','独立验证未核',[],
'文本有具体应用例：5kg/最多50L、沙床尺寸粒径、流量压降、100g及约100次洗涤设计，80—90%长于约50μm纤维捕获自述；不是完全无方法或参数。全文未给这些效率/残湿对应可复现实验计量协议、样本量、误差或独立验证。0108<10%为床中液体体积分数，0109>95%为介质残湿排出主张，均非收集固体含水率；保留设计/计算与性能主张区别。'),
'endpoint':(['p0012','p0077','p0120','p0132'],'explicit','optional_recycling_or_collection_route','再生收集的微纤维','下游收集器','回收材料或适当收集系统的建议处置',['再生收集','可选回收/收集系统处理'],
'0077明确收集纤维可作回收材料或作为无害废料在适当收集系统处理，是本发明建议后续路径，不能继续称只创造可能无任何去向。无害是作者用语，未有污染安全/实际回收处置效果验证；具体分类/交接/处理设施未明，不把一次性袋自动写入生活垃圾。')}
OLD4={'capture':['p0048','p0052','p0065','cl0001'],'cleaning':['p0077','cl0014'],'transfer':['p0077','p0120','p0132','cl0019'],'carrier_conditioning':['p0107','p0108','p0109','p0110','p0111','p0112','p0113','cl0017']}
def ev(k,now):
 text=a[k]
 if k=='p0077':text=text[-205:]
 elif k in ['p0109','p0110']:text=text[-205:]
 else:text=text[:260]
 return {'locator':'保存HTML #'+k,'html_anchor':k,'evidence_excerpt':text,'source_role':'claim' if k.startswith('cl') else 'description_embodiment','subject_role':'this_invention_or_optional_embodiment','source_path':str(SRC),'source_url':'https://patents.google.com/patent/'+PUB+'/zh','source_sha256':EXPECTED,'verified_at':now,'extraction_note':'Exact saved mirror anchor excerpt; HTML id is not PDF page or printed paragraph. Scope read all154 anchors; original PDF/figures not obtained/read.'}
if '--verify' in sys.argv:
 for x,y in zip(old['samples'],m['samples']):
  if x['sample_id']!=SID:assert x==y
  else:
   for k in x:
    if k not in ['features','scene_material','publications','review_completeness']:assert x[k]==y[k]
   for f in x['features']:
    if f not in DATA:assert x['features'][f]==y['features'][f]
    else:assert len(y['features'][f]['observations'])==1 and not x['features'][f]['observations'] and y['features'][f]['prior_field']==x['features'][f]['prior_field']
   rc=y['review_completeness'];assert not rc['full_text_rechecked'];assert rc[KEY]['read_anchor_ids']==keys and not rc[KEY]['original_pdf_checked'] and not rc[KEY]['drawings_checked']
   assert rc['current_scope'][:-9]==x['review_completeness']['current_scope']
   assert {k:v for k,v in rc.items() if k not in [KEY,'current_scope']}=={k:v for k,v in x['review_completeness'].items() if k!='current_scope'}
 obs=[o for z in m['samples'] for f in z['features'].values() for o in f['observations']];index={o['observation_id']:o for o in obs}
 assert len(obs)==len(index)==186
 assert all(index[o['observation_id']]==o for z in old['samples'] for f in z['features'].values() for o in f['observations'])
 assert all(x==y for x,y in zip(base('corrections/20260929_r1/data/review_coverage.csv').splitlines(),(R/'data/review_coverage.csv').read_bytes().splitlines()) if PUB.encode() not in x)
 for k in old:
  if k not in ['samples','updated_at']:assert old[k]==m[k]
 spec=importlib.util.spec_from_file_location('cn115298_saved_validator',R/'scripts/verify_and_export.py');v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;sys.path.insert(0,str(R/'scripts'));spec.loader.exec_module(v);q=v.validate(m)
 assert q['observations']==186 and q['full_text_complete_count']==6
 assert sum(not f['observations'] for z in m['samples'] for f in z['features'].values())==19
 q.update({'baseline':BASE,'target':PUB,'old177_observations_preserved':True,'other13_whole_objects_unchanged':True,'all_legal_unchanged':True,'non_target_CSV_exact_unchanged':True,'source_html_sha256':EXPECTED,'description_anchors_read':134,'claims_read':20,'all154_anchors_read':True,'added_fields':list(DATA),'old4_observations_unchanged':True,'original_PDF_checked':False,'drawings_checked':False,'full_text_flag_not_promoted':True,'true_empty_fields':19,'unknown_not_zero':True,'new_source_conflicts_preserved':s['review_completeness'][KEY]['source_conflicts'],'reset_consumed':False,'failures_before_acceptance':['First generated patch exceeded tool output budget; explicit begin/end gate prevented apply, zero master/CSV write. Removed duplicate receipt evidence, retained observation quotes, complete generator and QA restarted.']});print(dump(q));raise SystemExit
assert m==old;now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
for field,(anchors,support,emb,obj,start,end,order,meaning) in DATA.items():
 f=s['features'][field];assert not f['observations'] and f['support_status'] is None
 o={'observation_id':PUB+'-'+field+'-complete_saved_scope-20261004','publication_id':PUB,'grant_publication_id':None,'sample_role':'pending','embodiment_id':emb,'stage':field,'technical_feature':meaning,'object':obj,'start':start,'end':end,'boundary':'保存p0001—0134/cl0001—0020完整；不同图变体分别限定；原PDF/图未核','operation_order':order,'support_status':support,'review_status':'complete_in_stated_saved_text_scope','claim_dependency':'本文说明实施方式与权项分别限定，不把权17/19的多项择一依附拼成全部必需；权18错引5/6保留待原件核','evidence':[ev(k,now) for k in anchors],'interpretation':meaning,'performance_status':'text_claim_only' if field=='performance' else 'not_verified','verified_at':now,'old_value':f['prior_field'],'new_value':meaning,'change_reason':'完整保存文本补齐该空字段，保留未知与所有旧观察/实施方式边界。','removal_kind':None,'reviewed_anchor_ranges':['p0001-p0134','cl0001-cl0020']}
 if support=='not_located_in_reviewed_scope':o['availability_judgment']='unknown'
 f['observations'].append(o);f['review_status']='complete_saved_text_scope';f['support_status']=support
 s['review_completeness']['current_scope'].append({'publication':PUB,'anchors':anchors,'field':field,'at':now})
bindings={f:{'observation_ids_preserved':[o['observation_id'] for o in s['features'][f]['observations']],'scope_judgment':DATA[f][-1] if f in DATA else '既有观察保留；本轮完整保存范围补源，颗粒介质/目标纤维对象区分。','saved_anchor_ids':DATA[f][0] if f in DATA else OLD4[f],'evidence_location':'Current observation evidence; old4 original observations preserved'} for f in s['features']}
s['review_completeness'][KEY]={'source_path':str(SRC),'source_sha256':EXPECTED,'read_anchor_ids':keys,'description_anchors':134,'claim_anchors':20,'read_method':'Executor read all prepared normalized text in four complete blocks and verified every anchor against source HTML; mechanical index not used for judgments.','fields_added':list(DATA),'bindings':bindings,'original_pdf_checked':False,'drawings_checked':False,'not_a_full_original_document_acceptance':True,'verified_at':now,'source_conflicts':[{'anchors':['p0034','p0105','cl0015'],'detail':'步骤A次数前者/权15为50—150，后段20—150；不统一改写。'},{'anchors':['cl0018','cl0005','cl0006','cl0007','cl0008'],'detail':'权18所述控制装置引用权5—6，控制装置正文权7—8；保留原引用不默修。'},{'anchors':['p0070','p0128'],'detail':'前段密度单位kg/m2，应用例kg/m3；不默改原单位或实测身份。'},{'anchors':['p0106'],'detail':'渗滤率低于参考100%或优选50%原句保留，不自行修百分比触发。'},{'anchors':['p0127'],'detail':'连接点高度描述5cm、上方15cm、因此离地40cm内部不一致，原句保持待原件。'},{'anchors':['p0128','p0129'],'detail':'应用例称图5设计又引用图4短回路，保留原文出处，未看原图不判断是否绘图错误。'}]}
s['scene_material']={'classification':'洗衣/纺织处理流出液，天然和合成微纤维均包括','review_status':'complete_saved_text_scope_pending_original','publication_id':PUB,'source_path':str(SRC),'source_sha256':EXPECTED,'basis':[ev(k,now) for k in ['p0002','p0048','p0049','p0050']],'scope_note':'明确家庭/工业洗衣、染色/防水等可选纺织处理用途；天然棉毛和合成聚酯/聚酰胺/丙烯酸均包括，不把全部微纤维自动判塑料。'}
for p in s['publications']:
 if p['publication_id']==PUB:p['review_status']='complete_saved_text_scope_pending_original'
m['updated_at']=now
tree=ast.parse((R/'scripts/accept_cn118_publication_20261004.py').read_text(encoding='utf8'));fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='patch');exec(compile(ast.Module(body=[fn],type_ignores=[]),'unique_sample_patch','exec'))
print('*** Begin Patch\n'+patch(M,dump(m))+'*** End Patch')
