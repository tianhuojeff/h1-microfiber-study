"""Record individually read primary-text findings for C04-C06/C08."""
from pathlib import Path
import json,hashlib,datetime
from local_source import read_anchors
RUN=Path(__file__).resolve().parents[1];H=RUN.parents[1]
P=RUN/'data/analysis_master.json';M=json.loads(P.read_text(encoding='utf-8'))
NOW=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sample(pub):return next(s for s in M['samples'] if any(p['publication_id']==pub for p in s['publications']))
cache={}
def record(pub,field,emb,feature,obj,start,end,boundary,order,refs,dependency,reason,support='explicit',kind=None):
 s=sample(pub);src=H/'team_package_20260928/sources'/(pub+'.html')
 rows=cache.setdefault(pub,read_anchors(src));ev=[]
 for anchor,excerpt in refs:
  assert anchor in rows,(pub,anchor)
  excerpt=excerpt or rows[anchor]
  assert excerpt in rows[anchor],(pub,anchor,excerpt)
  ev.append({'locator':'HTML #'+anchor,'html_anchor':anchor,'evidence_excerpt':excerpt,
   'source_role':'claim' if 'cl' in anchor else 'description_embodiment','subject_role':'this_invention_or_optional_embodiment',
   'source_path':str(src),'source_url':next(p['source_url'] for p in s['publications'] if p['publication_id']==pub),'source_sha256':sha(src),
   'verified_at':NOW,'extraction_note':'Saved patent-publication mirror; whitespace normalized, no semantic paraphrase in excerpt.'})
 o={'observation_id':pub+'-'+field+'-'+emb,'publication_id':pub,'grant_publication_id':None,'sample_role':s['sample_role'],
 'embodiment_id':emb,'stage':field,'technical_feature':feature,'object':obj,'start':start,'end':end,'boundary':boundary,
 'operation_order':order,'support_status':support,'review_status':'complete_in_stated_scope','claim_dependency':dependency,
 'evidence':ev,'interpretation':feature,'performance_status':'not_verified','verified_at':NOW,
 'old_value':s['prior_working_evidence']['fields'].get(field),'new_value':feature,'change_reason':reason,'removal_kind':kind}
 f=s['features'][field];f['observations']=[x for x in f['observations'] if x['observation_id']!=o['observation_id']]+[o]
 f['review_status']='partial';f['support_status']=support
 s['review_completeness']['current_scope'].append({'publication':pub,'anchors':[a for a,_ in refs],'field':field,'at':NOW})
 return o

p='CN112914464A'
record(p,'removal','method22','过滤物质容器从家庭用具移除并排空或移除以排空；无需散装倒出实測才承认该技术路径。','含过滤物质的容器','家庭用具内结构单元','家庭用具外供排空的容器','家庭用具边界',['移除容器','排空或移除以供排空'],[('cl0022',None),('cl0001','所述用于过滤物质的接收器具有过滤物质容器')],'22引用1所述家庭用具','C04：原文直接公开取出容器路径，撤销因无实測而排除。',kind='container_with_retained_material')
record(p,'endpoint','method23','权23在移除整个结构单元后机械拆分容器，再处置或交处置公司；这是公开方法而非真实处置效果证明。','拆分容器','已移出家庭用具的整个结构单元','拆分容器交付处置','整机外结构单元到容器；后续处理效果未知',['移出整个结构单元','机械拆分容器','处置或交公司'],[('cl0023',None)],'23→22；22引用1','C04：处置叙述存在但不能升级为最终环境去向实证。')
record(p,'seals_connections','method24','权24另列拆分容器的替换与结构单元插回；权23和24分别依附22，不能写成23→24的强制连续链。','容器及结构单元','已拆分容器','替换后结构单元插回家庭用具','容器/结构单元/整机三级',['容器替换','结构单元插回'],[('cl0024',None)],'24→22；并非24→23','纠正历史sequence把权22—24无条件串行的风险。')
record(p,'cleaning','fig1','泵31经反冲洗管线42进入过滤器26，使积聚物脱离；阀与泵由控制器46驱动。','过滤物质','过滤器26','管线44','滤面/过滤器边界',['阀33切换','泵反冲洗'],[('p0055','因此，过滤设备26可被反冲洗，或者积聚在其中的过滤物质可从其中移除')],'不适用：说明书图1','本发明实施方式支持清理，非仅凭背景反冲洗关键词。')
record(p,'transfer','fig1_fig2','反冲洗后的过滤物质经44进入抽屉20的收集容器63；容器是集中收集处，并非其内生成颗粒。','带液过滤物质','过滤器26','抽屉20中的容器63','过滤器→收集容器，仍属整机',['反冲洗脱离','管线44输送','容器63收集'],[('p0055','所述过滤物质可通过过滤物质管线44朝向转换抽屉20输送'),('p0057','所述过滤物质65不在过滤物质容器63中产生，而是仅收集在其中以用于集中处置')],'不适用：相邻图1—2说明','原文可连接滤器与收集容器，不把带液转移说成干固体排放。','same_embodiment_combination')
record(p,'solids_dewatering','fig2_optional62','可选底部过滤器62使容器内过滤物质集中/增稠，水流回导水装置；该可选路线支持降低夹带液的技术披露，不支持干燥率。','收集的湿过滤物质','容器63内','水较少的集中物','容器底部额外过滤器62',['收集','可选二次分水'],[('p0058','该额外的过滤器62是有利的'),('p0058','较多关注过滤物质的进一步集中或增稠'),('p0058','所述水能够流回到导水装置中，例如流入水管线22中')],'不适用：图2可选实施方式','C07：分水浓缩不再与维护排空、最终处置混同。')
record(p,'liquid_route','fig2_optional62','可选过滤器62分离的水回到导水装置，例如22；不等同排入环境。','分离水','容器63底部过滤器62','导水装置或水管线22','收集容器→机器水路',['过滤','回流'],[('p0058','所述水能够流回到导水装置中，例如流入水管线22中')],'不适用：可选说明书实施方式','独立记录液体终点。')

p='CN115637570A'
record(p,'cleaning','claim1','螺旋叶片126以同水流旋进方向将过滤网122上的微纤维刮入收集装置127；清理与转移由该动作耦合。','微纤维','过滤网122','收集装置127','滤面→收集装置',['螺旋叶片旋进刮送'],[('cl0001','用于将所述过滤网(122)上的微纤维刮入到所述微纤维收集装置(127)中')],'独立权利要求1','C05：先确认袋内物料来源，不能只记录袋可拆。')
record(p,'transfer','claim1','叶片刮送方向与筒体水流同向，目标为靠近出水口的收集装置127；这是模块内部转移。','微纤维','网122','装置127','过滤模块内部',['刮离并沿轴向收集'],[('cl0001','所述螺旋叶片(126)的旋进方向与所述过滤器筒体(121)内水流的流动方向相同')],'独立权利要求1','区分转入收集装置与最终取袋。')
record(p,'storage','optional_bag','可拆过滤袋位于微纤维收集装置127，说明书明确袋中微纤维积累；不把其后更换过滤网122的疑似混写改成未见的更换袋原句。','微纤维','装置127','过滤袋','集污装置内可拆承载物',['收集积累'],[('cl0008',None),('p0079','当过滤袋中的微纤维累积的较多时，可以更换过滤网122')],'8→1','C05：承载关系可定位；保留p0079文字歧义，不自改原文。','same_embodiment_combination')
record(p,'removal','front_door_bag','前面板门盖可打开，用户取出过滤袋清理；同时原文另列整体过滤器取出选项。按取袋和取过滤组件分开，不强求公开倒出散装固体动作。','承载微纤维的过滤袋','过滤器中的收集装置127','前面板门盖外可取出的袋','过滤模块与洗衣机前面板维护口',['打开门盖','取出过滤袋','清理'],[('p0078',None),('p0079','当过滤袋中的微纤维累积的较多时'),('p0083',None)],'权8→1支持袋结构；p0083为洗衣机可选门盖实施方式，不是权8全部限定','C05：同一描述的袋承载与取出操作有依据；散料倒出未知不否定袋移出。','same_embodiment_combination','container_with_retained_material')
record(p,'seals_connections','front_door_bag','维护入口是前面板安装口11及可选门盖，取袋或取整个过滤器为两个选择；原文此处未确认维护前排水或断管。','门盖、过滤袋/过滤器','前面板安装口','可接近取出位置','机壳前面板',['打开门盖','择一取出袋或过滤器'],[('p0082',None),('p0083',None)],'说明书；权10→9→选定1—8之一不能变成全部并列限定','保留可选支路，不编造排液/断管流程。')

p='CN222043626U'
record(p,'capture','collection_box','微塑料由收集盒320内过滤网330截留；盒及网共同构成含物料承载单元，不能只看盖可拆。','洗衣废水中的微塑料及相近尺寸杂质','收集盒入口','盒内过滤网330','收集盒内部',['水进入盒','滤网截留'],[('zh-cl0001',None),('p0056','与微塑料尺寸相近的其他杂质也可以被过滤并拦截')],'独立权利要求1','C06：把目标物、滤网、盒体关系写清。')
record(p,'removal','box_lid','拆开盖板314与主壳313，露出收集盒320供用户取出清洁；原文明确盒用于收集微塑料，无需拆壳体与排水管。','含截留物的收集盒及盒内过滤网','主壳313内','主壳外可取出的收集盒320','过滤模块主壳边界',['拆盖板','露出盒','取出盒清洁'],[('p0053','收集盒320用于收集过滤出的微塑料'),('p0053','无需将壳体310与排水管200拆卸'),('p0064','可以将盖板314与主壳313拆卸开，以露出收集盒320供用户取出')],'权4可选依附1—3；本判断具体操作以p0053/p0064说明书为据','C06：拆盖不是独立充分证据；盒内承载与实际取盒语句共同支持。','same_embodiment_combination','container_with_retained_material')
record(p,'seals_connections','sliding_pipe','安装管324沿主壳滑槽滑動以装拆盒体；主壳与外部排水管保持连接。内部安装管的拆开与外部管路拆卸不能混为一项。','盒体安装管324','滑槽内','滑槽外','收集盒安装接口；非壳体—外排水管接口',['拆盖后可接近盒','安装管沿滑槽移动'],[('zh-cl0007',None),('p0071','安装管324能够在滑槽313a内滑动，以将盒体323装入或者拆出主壳313'),('p0053','无需将壳体310与排水管200拆卸')],'7→6→4→1/2/3择一（2→1；3→2→1），非把所有分支累加','维护边界具体化；无漏水属效果主张，未作实际验证。','same_embodiment_combination')
record(p,'liquid_route','drain_line','洗衣机排水管水经壳体、盒内过滤网后继续排出；说明书例示排入下水道。此为过滤流路，不是取盒前排空。','过滤后的水','收集盒第二出水口','排水管/例示下水道','过滤模块→设备排水',['过滤','随排水管流出'],[('p0052',None),('p0044','诸如通过排水口排到下水道中')],'说明书图1—2所述流路','C07：普通出水不误填维护排空。','same_embodiment_combination')

for pub,anchor in [('CN115087774A','cl0024'),('WO2021116933A1','clm-0024')]:
 record(pub,'solids_dewatering','method24','方法24逐项规定接收流出物、板向压缩位置运动以分水并压缩含微塑料物、板返回、排出压缩微塑料；分水与压实同阶段。','湿微塑料材料','含水流出物','压缩含微塑料材料','压实腔内部固液分离',['接收','分水并压缩','板返回','排固'],[(anchor,None)],'本版本方法24引用本版本1—23所述类型；CN与WO分别读取','C08：确认各自项号和文字，不互换版本；含水率及效果未核验。')
 claim1='cl0001' if pub.startswith('CN') else 'clm-0001'
 record(pub,'removal','claim1','至少一个板将压缩微塑料移向排放出口，并以板的移动使其自动排出压实器；不等于整个洗衣流程全自动。','压缩微塑料','压实器腔','压实器排放出口外','压实器模块边界；不自动扩为洗衣机机壳外',['板移动','经出口排固'],[(claim1,None)],'独立权利要求1','明确直接排固对象和边界；不等同最终安全处置。',kind='direct_solid_discharge')
 claim18='cl0018' if pub.startswith('CN') else 'clm-0018'
 record(pub,'chamber_drainage','claim18','腔室设置废水出口将水排出；该权项未独立限定为拆装前排空动作。','腔室废水','腔室','废水出口','腔室边界，外部终点由实施方式另定',['从腔室排出废水'],[(claim18,None)],'18依附前述任一项，所选链需在具体方案中确定','C07/C08：记录腔体排液功能，不把普通出口说成维护排空。')
 prefix='cl' if pub.startswith('CN') else 'clm-'
 record(pub,'seals_connections','claim19','入口与出口止回阀依附具有废水出口的权18，不能当作权1所有装置必含特征。','入口、废水出口止回阀','流路接口','单向流约束','压实腔与流路接口',['止回配合运行，具体时序未由该项单独给出'],[(prefix+'0019',None),(prefix+'0018',None)],'19→18→选定前述项','纠正从属层级；不把结构信息当滴漏实证。')

record('CN115087774A','liquid_route','fig3d','图3d透水板204后的水经排水通道208离开腔体；另有图3e透水后壁211/通道212，两个选项单独记录。','压缩分离水','板204后侧','通道208','压实腔→排水通道',['压缩时透水','通道排出'],[('p0057','在此实施例中，水通过排水通道208从板204后方的腔室后部逸出，如图3d中所展示')],'说明书图3d；权15/16/17只是另有可透材料从属分支','分水、液体终点与部件版本分开，不混合图3d/3e。')
record('WO2021116933A1','liquid_route','fig3d','WO图3d同样采用板204后侧通道208；原文还说明较大网孔可能使纤维随水带出而需要回到过滤阶段。不能承诺全部分水直接安全排放。','分离水及可能夹带微纤维','透水结构','通道208；粗网情形需回过滤阶段','压实模块→液路，终点取决于实施方式',['透水','依网孔条件处理出水'],[('p0039','In this embodiment, water escapes from the rear of the chamber behind the plate 204 through a drainage channel 208 as shown in Figure 3d.'),('p0039','the water removed by this mesh will contain a significant proportion of microfibers and therefore will need to be returned to the filtration stage for separation.')],'说明书图3d及网孔条件说明；不并入独立权1','保留不同网孔下液路条件，避免“全部去除”效果宣称。')

for pub in cache:
 s=sample(pub);s['scene_material']={'classification':'明确包括洗衣微纤维或微塑料','review_status':'primary_text_scope_reviewed','scope_note':'压实器还适用其他流出物，不把所有用途自动称为洗衣；CN222043626U亦可截留其他相近尺寸杂质。'}
 for v in s['publications']:
  if v['publication_id']==pub:v['review_status']='claims_read_and_targeted_description_reviewed'
 (RUN/'evidence'/(pub+'_anchors.json')).write_text(json.dumps(cache[pub],ensure_ascii=False,indent=2),encoding='utf-8')

for pub,page in [('CN115087774A',3),('WO2021116933A1',21)]:
 s=sample(pub);pdf=H/'team_package_20260928/sources'/(pub+'.pdf');png=RUN/'evidence'/f'{pub}_physical{page}.png'
 for o in s['features']['solids_dewatering']['observations']:
  if o['publication_id']==pub and o['embodiment_id']=='method24':o['pdf_visual_crosscheck']={'source_path':str(pdf),'source_sha256':sha(pdf),'physical_page':page,'claim':24,'image_path':str(png),'image_sha256':sha(png),'visually_read':True,'verified_at':NOW}
M.update(updated_at=NOW,phase='P2_in_progress');P.write_text(json.dumps(M,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
checks=json.loads((RUN/'QA/correction_checklist.json').read_text(encoding='utf-8'))
for c in checks:
 if c['id'] in ['C04','C05','C06','C08']:
  c.update(status='primary_text_issue_resolved; whole-report propagation pending',evidence=['data/analysis_master.json','evidence/priority_review_cards.md'],verified_at=NOW)
 if c['id']=='C07':c.update(status='dictionary_done; all-sample_recode_pending',evidence=['data/field_dictionary.md'])
(RUN/'QA/correction_checklist.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# C04—C06、C08 优先原文复核\n',f'核验时间：{NOW}。当前样本角色均为pending；以下是技术披露裁定，不是现时有效资格结论。全部专利全范围复核尚未完成。\n']
for s in M['samples']:
 obs=[o for f in s['features'].values() for o in f['observations']]
 if not obs:continue
 lines+=['## '+s['representative_publication']+'\n']
 for o in obs:
  lines+=['### '+o['publication_id']+' / '+o['stage']+' / '+o['embodiment_id']+'\n',o['technical_feature']+'\n',f"对象：{o['object']}；起点：{o['start']}；终点：{o['end']}。边界：{o['boundary']}。",'顺序：'+' → '.join(o['operation_order'])+'。','依据关系：'+o['claim_dependency']+'。支持：'+o['support_status']+'。']
  for e in o['evidence']:lines+=['- '+e['locator']+'：'+e['evidence_excerpt']]
  lines+=['修订理由：'+o['change_reason']+'\n']
lines+=['## 原页核验补充\n','CN115087774A权24位于本地21页PDF的物理第3页；WO2021116933A1权24位于本地34页PDF的物理第21页，已分别目视核对。WO物理第22页实际是图1，不能沿用旧卡的笼统页码范围当作权24定位。','\nCN115637570A的p0079在谈袋内积累后写“更换过滤网122”，此处不擅自改写为更换袋。取袋动作另由p0083直接支持。','\nCN112914464A权23与24各自依附22；不可把权23处置分支和24替换分支自动写成一条必经流程。']
(RUN/'evidence/priority_review_cards.md').write_text('\n\n'.join(lines)+'\n',encoding='utf-8')
print('Saved',sum(len(f['observations']) for s in M['samples'] for f in s['features'].values()),'source-bound observations; 4 family candidates, 5 publication texts; no final statistics.')
