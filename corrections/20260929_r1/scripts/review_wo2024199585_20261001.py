"""Encode bounded original-page review; print patches, verify actual disk bytes."""
from pathlib import Path
import csv,copy,datetime,difflib,hashlib,json,re,subprocess,sys
from local_source import read_anchors
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='0eaa7f6a2b4d7748b8ee48f0ae931c3fcd3617af';PUB='WO2024199585A1'
SRC=H/'team_package_20260928/sources/WO2024199585A1.html';PDF=H/'patents/WO2024199585A1.pdf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
ROUTE_TERMS={
 'capture':('流体中微塑料/固体','入口4含颗粒流体','滤件3内部中央retentate；滤液侧向穿过滤面5',['入口含颗粒流体进入','固体在滤件内富集，液体侧向穿过滤面']),
 'transfer':('富集固体携液retentate','滤件内部/中央底部','出口14至容器7',['中央固体富集','经14排出或抽吸','容器7收集']),
 'chamber_drainage':('维护前腔内游离液','unknown：未定位专用维护排空起点','unknown：未定位排空终点',['区分正常13/14出口和虹吸液位调节','专用维护前腔排空未定位']),
 'solids_dewatering':('retentate附着/残余液','收集或直接送往下游的retentate','可选离心分离附着液；可选压机去残余液，含水率终点unknown',['可选送进一步技术处理','离心或额外压机去附着/残余液；不串成强制连续工艺']),
 'liquid_route':('滤液与携液retentate分别','滤件侧向滤液；内部retentate','13可回水/废水循环；14收集路径',['滤液13和retentate14分路','可选反流用滤液和/或新水']),
 'storage':('retentate固体携液混合物','出口14','容器7积存且物料可取出',['容器收集retentate','可从容器取出物料']),
 'state_switch':('retentate/滤液阀与可选传感器','过滤运行/retentate阀控制状态','可选脉冲清洗或保持滤液阀开的retentate排放状态',['方式A：retentate阀关→滤液阀短关再开→retentate阀开','方式B：滤液阀保持开时开retentate阀','可选压差负荷触发，不拼为必要顺序']),
 'seals_connections':('预腔/壳体/滤件法兰连接','各对应接口','法兰形成所述密接；维护拆卸步骤unknown',['法兰固定所述接口','不据连接推断拆卸顺序或实测漏率']),
 'performance':('专利内塑料绒状纤维试验/作者效果陈述','原20页分别叙述的试验条件','原21页三组质量占比与另列效果陈述',['两段试验条件分开保留','三份样本分别识别','内部数值与作者97/80/约5效果分列']),
 'endpoint':('取出或直接外送的retentate','收集/排出后物料','可选下游技术处理；最终安全处置unknown',['收集/取出','可选进一步过滤/离心/压机','最终垃圾分类/销毁/安全环境终点未定位']),
 'carrier_conditioning':('过滤载体自身','可取出/洗涤滤件','unknown：未定位载体自身排水或干燥终点',['独立取出/洗涤有披露','自身独立排水/干燥未定位'])}
assert sha(SRC)=='90ad20901b829d34f9429e698989cf50fabc2cfbd053cd3a82ce5a88607954be'
assert sha(PDF)=='c600b753900e1ab6eff7e59455b5b76fcca177294a64b877bc6600d0e3f3e40c'
a=read_anchors(SRC);old=json.loads(subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/analysis_master.json'],cwd=H));m=json.loads(M.read_text(encoding='utf-8'))
if '--verify' in sys.argv:
    for x,y in zip(old['samples'],m['samples']):
        if x['representative_publication']!=PUB:assert x==y
        else:
            assert x['legal_evidence']==y['legal_evidence'] and x['prior_working_evidence']==y['prior_working_evidence']
            for k,v in x['features'].items():assert y['features'][k]['observations'][:len(v['observations'])]==v['observations']
    obs=[o for s in m['samples'] for f in s['features'].values() for o in f['observations']]
    assert len(obs)==104 and len({o['observation_id'] for o in obs})==104
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
    for row in csv.DictReader((R/'data/review_coverage.csv').read_text(encoding='utf-8-sig').splitlines()):
        f=next(s for s in m['samples'] if s['representative_publication']==row['publication'])['features'][row['field']]
        assert int(row['observation_count'])==len(f['observations']) and row['review_status']==f['review_status'] and row['support_status']==(f['support_status'] or '')
    rel=json.loads((H/'current_release.json').read_text(encoding='utf-8'));assert rel['master_sha256']==sha(M) and rel['current_observations']==104
    assert all(s['sample_role']=='pending' for s in m['samples']) and not m['formal_statistics_allowed'] and not m['final_report_ready'] and not rel['project_completion_accepted']
    print(dump({'verified':True,'baseline':BASE,'observations':104,'added':13,'old_91_unchanged':True,'other_13_candidates_unchanged':True,
        'legal_evidence_unchanged':True,'all_14_pending':True,'master_sha256':sha(M),'original_pdf_sha256':sha(PDF),
        'new_visual_pages':[10,14,16,17,20,21,23,26,27,30,32],'read_only_reviewer_reported_pages':list(range(1,40)),
        'source_html_sha256':sha(SRC),'visual_page_sha256':{str(n):sha(R/f'evidence/WO2024199585A1_review_20261001_{n}.png') for n in [10,14,16,17,20,21,23,26,27,30,32]},
        'full_text_complete_count':0,'CSV_verified':True,'formal_statistics_allowed':False}))
    raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();s=next(s for s in m['samples'] if s['representative_publication']==PUB)
# field, unique route, German mirror anchors, original primary page, scoped interpretation, support, performance role
decisions=[
('capture','lateral_mesh_central_concentration',['clm-0001','clm-0006','p0027'],26,'锥形/鳃状网孔滤件使液体侧向通过滤面，固体在内部中央富集；权6网孔20—500μm、优选50—100μm为结构尺寸，原页27证实单位μm，不沿镜像OCR的pm误码，也不等同实测截留粒径。权6从属权1—5任一。','explicit','not_verified'),
('transfer','retentate_outlet_14',['clm-0001','p0068','p0069'],23,'滤件内部/中央底部富集固体随retentate经出口14排出或抽吸至容器7；不是只转移液体。图3物理32页显示14与侧向滤液13分路；图文对应各自实施方式，不凭箭头推断最终处理。','explicit','not_verified'),
('chamber_drainage','maintenance_emptying_unlocated',['clm-0001','clm-0011','p0068'],30,'在本次原页复核及只读代理报告的说明书/权项范围，未定位维护前排空腔内游离液的专门动作。正常出口13、携液retentate出口14和虹吸调液位不自动等同维护排空；限定未定位，不转0或行业不存在。','not_located_in_reviewed_scope','not_verified'),
('solids_dewatering','optional_downstream_centrifuge_press',['p0038'],14,'说明书物理14/印12行1—10明确可将retentate转至下游离心机去附着液，另可进入压机压缩并去残余液；是本发明可选后续处理，未写成本机内置模块或权1必要结构。未给固体含水率、脱水终点或该下游处理实测结果。','explicit','not_verified'),
('liquid_route','filtrate_and_retentate_separate',['clm-0001','p0038','p0044','p0069'],32,'滤液侧向经13可回fluid/水或废水循环；retentate经14到收集路径。可选清洗使用滤液和/或新水反流；不自动判排环境、零颗粒或零排放。约5%是收集容器液体体积效果陈述，不是固体含水率。','explicit','not_verified'),
('storage','retentate_container',['clm-0008','p0038'],14,'容器7可收集retentate且固体可从容器取出；图1物理30页示意外部容器。物料可取出不等于容器必须可拆，更不证明密闭长期防漏。权8依权1—7任一。','explicit','not_verified'),
('state_switch','optional_valve_modes_and_sensor',['clm-0001','p0045','p0046','p0048'],16,'权1模拟/数字控制周期或连续retentate排放。说明书可选方式A：retentate阀关→滤液阀短关再开产生脉冲→retentate阀开排出；方式B允许滤液阀保持开而开retentate阀，压力脉冲明确optional，不合为唯一必要顺序。间隔13—86s、持续0.6—6.5s可调更长更短；物理17页另可选压差负荷触发，不是强制停机。','explicit','not_verified'),
('seals_connections','flange_connection_not_maintenance_sequence',['clm-0010','p0049','p0069'],17,'原页17/印15行14—25及从属权10用法兰在入口/壳体/滤件/预腔连接，说明dichte Verbindung；图3见法兰9。单双/多件构造各保留，不据法兰自行生成必需断管、旋拧或开盖维护顺序，未核防漏实测。权10依权2—9任一。','explicit','not_verified'),
('performance','patent_internal_protocols',['p0059','p0060','p0061'],20,'专利内有真实叙述的试验方法：虹吸、双自动阀、螺旋预腔；一段为0.1g/L塑料绒状纤维、过滤10L、5/10L清洗并重复5次，间试冲洗/手洗。另段写20L自来水+0.5g纤维+5mL洗涤剂，充水排气、5/10L清洗后停止；两段参数原样分开，不擅修成同浓度。样本为全量浓缩液、1L滤液、滤内残余MR≤1L再悬浮，吸滤/圆滤纸分离质量组分。不是独立外部验证。','explicit','patent_internal_method'),
('performance','patent_internal_mass_fractions',['p0061','p0062'],21,'N=43绒状纤维试验，浓缩液颗粒占比64.1±24.1%，滤件内残留Retentat(MR)33.2±24.4%，滤液逸出2.7±3.2%；Retentat这里承接第三份滤内残余样本，不是外置容器质量占比。±含义原文未明确，不填SD/SE；不据本件数值生成跨样本可比或独立验证结论。','explicit','patent_internal_data_not_independently_verified'),
('performance','author_effect_claims_separate',['p0047','p0062'],21,'作者写最高97%分离、外容器可留超过80%，并称短清洗可将容器液体体积减至约5%；这些效果陈述与43次平均质量占比分栏保留，不把80%替代平均64.1%，不把5%当含水率，也不标成独立外部实测。','explicit','text_claim_separate_from_patent_internal_data'),
('endpoint','downstream_processing_final_disposal_unlocated',['p0038','clm-0008'],14,'可以记录收集/取出后可选离心、进一步过滤或压机技术处理；最终垃圾分类、销毁或安全环境处置终点，在本次复核及代理报告范围未定位。下游技术处理不等于最终安全处置闭合。','partial_explicit_final_disposal_unlocated','not_verified'),
('carrier_conditioning','media_drain_dry_unlocated',['clm-0005','p0044','p0059','p0060'],27,'权5滤件独立可取出和/或洗涤、试验间手洗、试验前充水排气均有文本；在本次原页和代理报告范围未定位过滤载体自身独立排水/干燥步骤或终点。反流清洗不推为介质干燥；限定未定位，unknown不转0。','not_located_in_reviewed_scope','not_verified')]
def excerpt(k,field):
    text=a[k]
    if k=='p0038' and field in ['solids_dewatering','endpoint']:
        start=text.index('Es ist aber auch möglich');return text[start:start+650]
    # Quotes remain literal substrings; exclude duplicated machine English where possible.
    english=re.search(r' (?:Furthermore|The |In the |In all |It has |For example|Before |After |A siphon|[0-9]+\. (?:Bionic|Device|Method|Use))',text)
    if english:text=text[:english.start()]
    return text[:1000]
added=[]
for field,route,keys,page,meaning,status,perf in decisions:
    image=R/f'evidence/WO2024199585A1_review_20261001_{page}.png'
    o={'observation_id':PUB+'-'+field+'-'+route+'-20261001','publication_id':PUB,'grant_publication_id':None,'sample_role':'pending',
       'embodiment_id':route,'stage':field,'technical_feature':meaning,'object':ROUTE_TERMS[field][0],
       'start':ROUTE_TERMS[field][1],'end':ROUTE_TERMS[field][2],'boundary':'原A1与各可选/从属方式分开；法律资格待核',
       'operation_order':ROUTE_TERMS[field][3],'support_status':status,'review_status':'complete_in_checked_scope',
       'claim_dependency':'独立权1控制retentate排放；所引从属权号和可选说明书分别保留，见interpretation',
       'evidence':[{'locator':'保存德文HTML #'+k+'；原德文PDF见页图交叉检查','html_anchor':k,'source_path':str(SRC),'source_sha256':sha(SRC),
          'source_role':'independent_claim' if k=='clm-0001' else 'dependent_claim' if k.startswith('clm') else 'description',
          'evidence_excerpt':excerpt(k,field)} for k in keys],
       'interpretation':meaning,'performance_status':perf,'verified_at':now,'old_value':s['features'][field]['support_status'],'new_value':meaning,
       'change_reason':'补本件11个空字段，性能方法/内部数值/作者效果分离；旧4条保持，未重读同轮清洗条目',
       'pdf_visual_crosscheck':{'source_path':str(PDF),'source_sha256':sha(PDF),'physical_page':page,'printed_page':page-2 if page<30 else 'drawing',
          'image_path':str(image),'image_sha256':sha(image),'checked_at':now,'verification_method':'manual_visual_readback_original_German',
          'scope':'执行者本次11原页；补充全页范围来自/root/h1_source_review只读原件报告，不冒称执行者39页全视觉阅读'},
       'review_scope':'本次原页10/14/16/17/20/21/23/26/27/30/32；历史15/27/28/29；只读代理报告全39页。负向判断为限定范围未定位。'}
    s['features'][field]['observations'].append(o);s['features'][field]['support_status']=status;s['features'][field]['review_status']='complete_in_checked_scope';added.append(o)
s['scene_material']={'classification':'microplastic_separation_including_laundry_dishwasher_wastewater','review_status':'checked_original_application_scope','verified_at':now,
   'basis':[{'anchor':'clm-0015','excerpt':a['clm-0015'],'source_sha256':sha(SRC),'physical_page':29}],
   'boundary':'用途包括洗衣/洗碗废水，但不是仅限洗衣；实验塑料绒状纤维不能自动外推所有材料或实水表现。'}
s['review_completeness']['original_targeted_readback_20261001']={'checked_at':now,'pdf_sha256':sha(PDF),'executor_visual_pages':[10,14,16,17,20,21,23,26,27,30,32],
   'read_only_reviewer':'/root/h1_source_review','reviewer_reported_visual_pages':list(range(1,40)),'reviewer_report_received':True,
   'all_fields_have_scoped_observations':True,'candidate_full_text_accepted':False,'related_grant_text_pending':True,
   'scan_pdf_text_extraction_empty':True,'note':'扫描件抽取为空不是缺披露；原图、保存德文原句与人工复核交叉。'}
assert not s['review_completeness']['full_text_rechecked'];m['updated_at']=now
print('*** Begin Patch\n*** Update File: '+str(M).replace('\\','/'))
section=0
for l in list(difflib.unified_diff(dump(old).splitlines(),dump(m).splitlines(),n=3))[2:]:
    if l.startswith('@@'):
        section+=1;print('@@       "representative_publication": "WO2024199585A1",' if section==2 else '@@')
    else:print(l)
body='# WO2024199585A1 原件字段复核\n\n原PDF SHA '+sha(PDF)+'。执行者新增视觉原页10/14/16/17/20/21/23/26/27/30/32，历史15/27/28/29；只读代理报告39页全文，范围分开记录。\n\n'
for o in added:body+='## '+o['stage']+' / '+o['embodiment_id']+'\n\n'+o['interpretation']+'\n\n原PDF物理页 '+str(o['pdf_visual_crosscheck']['physical_page'])+'；保存德文锚点 '+','.join(e['html_anchor'] for e in o['evidence'])+'。\n\n'
body+='新增13条/11空字段，合计104条；旧91与其他13对象/法律保持。全部pending、正式统计和终稿未放行，全文验收标记仍false。\n'
print('*** Add File: '+str(R/'evidence/WO2024199585A1_original_field_readback_20261001.md').replace('\\','/'));print('\n'.join('+'+l for l in body.splitlines()));print('*** End Patch')
