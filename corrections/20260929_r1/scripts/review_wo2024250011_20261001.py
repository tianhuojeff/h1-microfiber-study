"""Bounded original-page review with unresolved source conflicts preserved."""
from pathlib import Path
import csv,datetime,difflib,hashlib,json,subprocess,sys
from local_source import read_anchors
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='7c7e3022047d72da548c875a32277173afb27bb2';PUB='WO2024250011A1';PAGES=[9,10,11,12,13,15,16,17,18,19,20]
SRC=H/'team_package_20260928/sources/WO2024250011A1.html';PDF=H/'patents/expansion_20260921/WO2024250011A1.pdf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def img(n):return R/f'evidence/WO2024250011A1_review_20261001_{n}.png'
assert sha(SRC)=='1842bd29f950f82b162f3f1b3d3d5733ac4223a5bf41a798d0be41e516495284'
assert sha(PDF)=='279c9c49d20757133f4426dea2b85d51130f5fd6b08c19a526a840d46366a4ef'
a=read_anchors(SRC);old=json.loads(subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/analysis_master.json'],cwd=H));m=json.loads(M.read_text(encoding='utf-8'))
if '--verify' in sys.argv:
    for x,y in zip(old['samples'],m['samples']):
        if x['representative_publication']!=PUB:assert x==y
        else:
            assert x['legal_evidence']==y['legal_evidence'] and x['prior_working_evidence']==y['prior_working_evidence']
            for k,v in x['features'].items():assert y['features'][k]['observations'][:len(v['observations'])]==v['observations']
    obs=[o for s in m['samples'] for f in s['features'].values() for o in f['observations']];assert len(obs)==116 and len({o['observation_id'] for o in obs})==116
    cache={}
    for o in obs:
        for e in o['evidence']:
            p=Path(e['source_path']);assert sha(p)==e['source_sha256']
            if e.get('html_anchor'):
                if str(p) not in cache:cache[str(p)]=read_anchors(p)
                assert e['evidence_excerpt'] in cache[str(p)][e['html_anchor']]
            else:assert sha(Path(e['page_image_path']))==e['page_image_sha256']
        if o.get('pdf_visual_crosscheck'):
            q=o['pdf_visual_crosscheck'];assert sha(Path(q['source_path']))==q['source_sha256'] and sha(Path(q['image_path']))==q['image_sha256']
    s=next(s for s in m['samples'] if s['representative_publication']==PUB)
    assert all(f['observations'] for f in s['features'].values()) and not s['review_completeness']['full_text_rechecked']
    assert len(s['source_conflicts_20261001'])==2 and s['source_conflicts_20261001'][0]['original_quote']=='The device of claim 23'
    for c in s['source_conflicts_20261001']:
        assert c['status']=='unresolved' and not c['automatically_corrected']
        for ref in c['page_images']:assert sha(Path(ref['path']))==ref['sha256']
    for row in csv.DictReader((R/'data/review_coverage.csv').read_text(encoding='utf-8-sig').splitlines()):
        f=next(s for s in m['samples'] if s['representative_publication']==row['publication'])['features'][row['field']]
        assert int(row['observation_count'])==len(f['observations']) and row['review_status']==f['review_status'] and row['support_status']==(f['support_status'] or '')
    rel=json.loads((H/'current_release.json').read_text(encoding='utf-8'));assert rel['master_sha256']==sha(M) and rel['current_observations']==116
    assert all(s['sample_role']=='pending' for s in m['samples']) and not m['formal_statistics_allowed'] and not m['final_report_ready'] and not rel['project_completion_accepted']
    print(dump({'verified':True,'baseline':BASE,'observations':116,'added':12,'old_104_unchanged':True,'other_13_candidates_unchanged':True,
       'legal_evidence_unchanged':True,'all_14_pending':True,'master_sha256':sha(M),'original_pdf_sha256':sha(PDF),'source_html_sha256':sha(SRC),
       'executor_visual_pages':PAGES,'readonly_reviewer_reported_pages':list(range(1,32)),
       'visual_page_sha256':{str(n):sha(img(n)) for n in PAGES},'source_conflicts_preserved':2,'full_text_complete_count':0,'CSV_verified':True,'formal_statistics_allowed':False}))
    raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();s=next(s for s in m['samples'] if s['representative_publication']==PUB)
# field, route, anchors, page, object, start, end, meaning, support, performance role
D=[
('capture','two_stage_capture',['clm-0017','p0054','p0060'],16,'衣物微纤维','洗衣水进入多级滤材','第二级内截留','独立权17明确第二级捕获微纤维，[0056]非织造垫先截留、随后纤维推出至细网留住；可记录材料/截留关系，但210/220编号与材料有原件冲突，不能无条件绑定统一编号。不是所有衣物纤维都塑料。','explicit','not_verified'),
('chamber_drainage','device_gravity_drain_boundary_unknown',['p0056','p0019'],10,'停用device100中的水','停用装置','翻起铰接装置使水排离device，液体终点unknown','[0058]明确self-drainage，停用向上翻起借重力让水离device100；图3C支持姿态，未精确指定独立腔体、专用出口或液体终点。不写完全排干/自动排空，也不把装置级沥水直接充作维护前腔游离液完全排空。','explicit_device_drainage_chamber_boundary_unresolved','not_verified'),
('solids_dewatering','solid_water_removal_unlocated',['p0051','p0056'],9,'已捕获微纤维固体夹带水','捕获固体','unknown：专用固体脱水终点未定位','本次原页及只读代理报告的技术正文/权项/图范围，未定位对已收集微纤维固体夹带水的压滤/离心脱水或含水率终点。[0035]衣物离心、[0051]滤面离心+pulse脱离及elastic band增加视觉截留不改成固体压干；[0058]device水沥出不变成滤渣含水率。','not_located_in_reviewed_scope','not_verified'),
('liquid_route','in_drum_variants',['clm-0017','p0058','p0067','p0072'],12,'洗/漂水','滚筒内壳体开孔/缝隙','经过内滤材后仍在滚筒水路；沥水后终点unknown','device100的洗漂水穿壳体开孔进入多级滤材；球式600通水缝隙和杆式800外壳840缝隙分别保留。过滤在滚筒内，未披露独立外排废水管或额外泵，概念channels/doors不补画阀路。不合并球式与固定杆式动作链。','explicit','not_verified'),
('state_switch','device100_closed_open_upright',['p0015','p0016','p0019','p0056'],19,'device100及内滤件','闭合过滤位置','打开检查/替换；停用铰接翻起重力沥水位置','图1闭合过滤、图2打开可插移滤器、图3B/3C停用翻起沥水各有披露。未明确谁翻起，不添自动控制器，不加先完全沥干才取出的强制次序；球式自滚动及杆式固定为其他可选方式。','explicit','not_verified'),
('seals_connections','ball_sibling_connectors',['clm-0004','clm-0005','clm-0006','clm-0007','p0067','p0068'],15,'球式两半壳','两半壳','可选卡扣/螺纹/铰链连接','权5/6/7分别依权4→1，是同级可选连接。球式tongue-and-groove卡扣/螺纹/铰链不视为必须全有；外壳有通水缝，不称防水密封。','explicit','not_verified'),
('seals_connections','device100_hinge_push_rivets',['clm-0022','clm-0023','p0056','p0064','p0065'],20,'device100壳体/底座/网板','铰链330与底座310；push rivets','可旋转连接及网板固定','device100铰链330与底座310、push rivets装网板有明确图文；权22依17。权23原件自引23、编号/材料冲突另存，不修成22，不把原件网板220无条件解释成nonwoven第一层；不补断管/防漏。','explicit_with_unresolved_source_conflict','not_verified'),
('seals_connections','rod_optional_fixings',['p0071','p0072','p0073','p0074'],13,'杆式800/900/1000滤件','滚筒内壁/孔位','各自可选可拆固定','杆式可调长度、铆钉/孔；另有挂钩、磁件、弹簧等不同方式。不把不同图构造拼成同一必需固定系统，不外推默认断管或漏水密封。','explicit','not_verified'),
('performance','qualitative_patent_trials',['p0051'],9,'原型滤器定性试验观察','不同PPI/长度/厚度/形状原型','视觉捕获和至少10cycles文本观察','[0051]确有专利自身试验观察：30/45PPI差别较小、4.5英寸比9英寸较好、两层、内外视觉捕获，lifespan tests至少10cycles无显著阻力。保留有试验这项事实；未见完整样本量、可复制计量协议、统计捕获率/误差或独立验证，不写完全没有试验或所有性能已实证。','explicit','patent_internal_qualitative_trials'),
('performance','design_claims_not_tested_limits',['clm-0017','p0061'],16,'尺寸/耐温/转速构型要求','原构型文本','1000rpm/45—150°F及10μm尺寸陈述','独立权17的最高1000rpm、45—150°F为要求，[0064]10μm为设计捕获尺寸陈述；本次没有相应极限测试证明，不写为已验性能极限或统计效率。','explicit','text_design_claim_not_verified_limit'),
('endpoint','replacement_not_final_disposal',['p0016','clm-0017','p0056'],18,'含纤维已用滤件/替换耗材','捕获及取出后','unknown：最终分类/清空/销毁/安全环境处置未定位','disposable inner filter与打开插移replacement filters只支持耗材替换/组件取出；在已核原页及只读代理技术全文报告范围未定位最终垃圾分类、销毁等安全终点，不能由disposable补写扔垃圾完成。','not_located_in_reviewed_scope','not_verified'),
('carrier_conditioning','whole_device_drain_not_media_dry',['p0056','p0051'],10,'滤载体自身','使用后滤介质','unknown：独立介质排水/干燥步骤未定位','[0058]是整个device停用重力沥水，未明确介质自身独立排水/干燥工序。[0051]vacuum drying属于aerogel滤材制备试验，不是使用后载体干燥；保留对象限定与未知，不填0。','not_located_in_reviewed_scope','not_verified')]
added=[]
for field,route,keys,page,obj,start,end,meaning,status,perf in D:
    evidence=[]
    for k in keys:
        text=a[k]
        if k=='p0056' and field in ['chamber_drainage','state_switch','carrier_conditioning']:
            j=text.index('A self-drainage');text=text[j:j+800]
        elif k=='p0051' and field=='performance':text=text[:1500]
        else:text=text[:600]
        evidence.append({'locator':'保存HTML #'+k+'；原PDF物理'+str(page)+'页交叉核对（非逐锚点全部同页）','html_anchor':k,'source_path':str(SRC),'source_sha256':sha(SRC),
            'source_role':'independent_claim' if k=='clm-0017' else 'dependent_claim' if k.startswith('clm') else 'description','evidence_excerpt':text})
    o={'observation_id':PUB+'-'+field+'-'+route+'-20261001','publication_id':PUB,'grant_publication_id':None,'sample_role':'pending','embodiment_id':route,'stage':field,
       'technical_feature':meaning,'object':obj,'start':start,'end':end,'boundary':'对应device100/球式/杆式各自边界；原编号冲突不自动修正','operation_order':[meaning],
       'support_status':status,'review_status':'complete_in_checked_scope','claim_dependency':'见interpretation；权23自引保留未解，不猜其真实依附',
       'evidence':evidence,'interpretation':meaning,'performance_status':perf,'verified_at':now,'old_value':s['features'][field]['support_status'],'new_value':meaning,
       'change_reason':'补九空字段并分开连接方式、定性试验与设计要求；保留旧4观察，另作原页补强',
       'pdf_visual_crosscheck':{'source_path':str(PDF),'source_sha256':sha(PDF),'physical_page':page,'image_path':str(img(page)),'image_sha256':sha(img(page)),
           'checked_at':now,'verification_method':'manual_visual_readback_original_English','scope':'执行者本次11原页；只读代理报告全31页范围另记，未冒称执行者全文视觉阅读'},
       'review_scope':'执行者9/10/11/12/13/15/16/17/18/19/20；只读代理报告正文/23权项/11图页全31物理页。负向判断仅为范围内未定位。'}
    s['features'][field]['observations'].append(o);s['features'][field]['support_status']=status;s['features'][field]['review_status']='complete_in_checked_scope';added.append(o)
# Multiple connector observations need aggregate role rather than the last row's status.
s['features']['seals_connections']['support_status']='explicit_with_unresolved_source_conflict'
def refs(pages):return [{'physical_page':n,'path':str(img(n)),'sha256':sha(img(n))} for n in pages]
s['source_conflicts_20261001']=[
 {'conflict_id':'WO2024250011A1-claim23-self-reference','status':'unresolved','original_quote':'The device of claim 23','locator':'物理17页权23；保存clm-0023也相符',
  'source_path':str(PDF),'source_sha256':sha(PDF),'page_images':refs([17]),'automatically_corrected':False,'boundary':'不改成权22、不推真实依附；后续版本需单独原件核验'},
 {'conflict_id':'WO2024250011A1-layer-number-material','status':'unresolved','original_quote':'mesh filter 220 / first stage 220 nonwoven / second stage 210 mesh',
  'locator':'物理10[0058]、11[0061]/[0065]/[0068]、19图3A和20图4','source_path':str(PDF),'source_sha256':sha(PDF),'page_images':refs([10,11,19,20]),
  'automatically_corrected':False,'boundary':'保留原编号/材料角色矛盾；权17不含210/220编号，可录其两级关系，不能生成统一编号材料表'}]
s['scene_material']={'classification':'laundry_textile_microfibres_including_synthetic_microplastic_focus','review_status':'checked_application_scope','verified_at':now,
 'evidence':'原物理10[0059]洗衣衣物/床品/毛巾；只读报告原6[0030]聚酯/尼龙/丙烯酸纤维，不将全部衣物纤维自动视为塑料。'}
s['review_completeness']['original_targeted_readback_20261001']={'checked_at':now,'pdf_sha256':sha(PDF),'executor_visual_pages':PAGES,
 'readonly_reviewer':'/root/h1_source_review','reviewer_reported_visual_pages':list(range(1,32)),'reviewer_report_received':True,'candidate_full_text_accepted':False,
 'all_fields_have_scoped_observations':True,'legacy_observation_original_crosschecks':[
  {'field':'cleaning','scope':'原9[0051]，离心/pulse，不新增重复观察','page_images':refs([9])},
  {'field':'transfer','scope':'原9[0051]滤面→separate compartment，未补管阀','page_images':refs([9])},
  {'field':'storage','scope':'保存p0066=[0069]跨原11至12首两行；backwash compartment不合并[0051]腔','page_images':refs([11,12])},
  {'field':'removal','scope':'原16权17和10[0058]/18图2补强可移组件/内核装卸界面；不是最终安全处置','page_images':refs([16,10,18])}]}
assert not s['review_completeness']['full_text_rechecked'];m['updated_at']=now
print('*** Begin Patch\n*** Update File: '+str(M).replace('\\','/'));section=0
for l in list(difflib.unified_diff(dump(old).splitlines(),dump(m).splitlines(),n=3))[2:]:
    if l.startswith('@@'):
        section+=1;print('@@       "representative_publication": "WO2024250011A1",' if section==2 else '@@')
    else:print(l)
body='# WO2024250011A1 原件九字段与冲突复核\n\n原PDF SHA '+sha(PDF)+'。执行者原页 '+','.join(map(str,PAGES))+'；只读代理全31页范围分开，全文验收仍false。\n\n'
for o in added:body+='## '+o['stage']+' / '+o['embodiment_id']+'\n\n'+o['interpretation']+'\n\n原页 '+str(o['pdf_visual_crosscheck']['physical_page'])+'；保存锚点 '+','.join(e['html_anchor'] for e in o['evidence'])+'。\n\n'
body+='原冲突：权23自引23；原[0058]mesh220与[0061]/[0065]nonwoven220/mesh210、图3A/4不一致，均保持未解。旧4条以元数据原页补强、不重复新增；新增12条，合计116。14资格pending，正式统计/终稿false。\n'
print('*** Add File: '+str(R/'evidence/WO2024250011A1_original_field_readback_20261001.md').replace('\\','/'));print('\n'.join('+'+l for l in body.splitlines()));print('*** End Patch')
