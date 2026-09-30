"""Resolve the six historic matrix conflicts against actual local publication texts."""
from review_core import *

p='CN115700309A'
record(p,'removal','recovery_housing','回收壳体510可从洗衣机箱体10抽出，其第一腔室及过滤组件上表面承载过滤杂质；可经上侧敞口清理，也可另取出过滤组件。','含过滤杂质的回收装置','箱体内回收装置500','箱体外的回收壳体510','整机箱体边界',['抽出回收壳体','经敞口清理；可选卸下滤组件'],[('cl0010','过滤杂质收集于第一腔室中'),('p0120','用户可将回收装置500从箱体10内抽出进行清理'),('p0121',None)],'10→9→8→1—7择一；选1形成10→9→8→1，不能写成10直接依附1','C11：短版只写可抽壳体不充分；原文有明确载物、抽出和清理连接。','same_embodiment_combination','container_with_retained_material')
record(p,'liquid_route','two_chambers','带杂质污水进入第一腔室531，经过滤组件520后水入第二腔室532；杂质留在滤组件上表面。该二次过滤流路不独立证明维护前腔体排空。','带液杂质与分离水','第一腔室531','固体留第一腔；水入第二腔532','回收装置内部两腔',['污水入第一腔','穿过滤组件','水入第二腔'],[('p0117',None),('p0118',None)],'权10所属链；具体实施例说明','C07：二次固液分离与腔体维护排空分开。','same_embodiment_combination')
p='CN118273060A'
record(p,'removal','unlock_axial','止动构件解锁后，盖装置和过滤器组能沿轴线从壳体主体移动出；移出承载过滤介质的过滤器组，不能笼统归为独立集渣盒。','包含截留介质的过滤器组5','壳体3的过滤室20','壳体外取出的过滤器组','过滤模块壳体边界；未据此证明整机外接液管断开',['止动件解锁','盖与过滤器组轴向移出'],[('zh-cl0016',None),('zh-cl0001','所述过滤器组(5)包括过滤介质(50)和联接到所述过滤介质(50)的过滤器结构(51)'),('p0179',None)],'16依附前述任一项；可选16→1，不将所有前项累加','C11：团队旧表仅密封定位漏掉权16；含介质过滤组件路径应单列。','same_embodiment_combination','filter_assembly_with_retained_material')
record(p,'liquid_route','wash_pipe','过滤器前第一段951接滚筒，过滤后第二段952可接排放系统或回滚筒；这是两个可选终点，不能合成全部外排。','洗衣水/天然纤维及微塑料','第一段951','第二段952→排放系统或滚筒','模块→设备水路',['进入过滤器','处理水到第二段','择一路终点'],[('p0059',None)],'说明书优选实施方式；权17另明确排放和/或再循环','保留材料和液路选择边界。')
p='WO2022084677A1'
record(p,'chamber_drainage','fig1_ab','图1第一构型先停供液，再由104排出过滤腔101残液；完成排液后才将105移离111，进入第二构型转移滤渣。','过滤腔游离液','腔101','出口104','过滤腔边界',['停止供液','104排液','105移开111','转移滤渣'],[('p0213','Supply of the effluent is stopped and residual effluent in the filter chamber 101 is drained out of the outlet 104.'),('p0213','The filter is then put into the second configuration by moving the moveable member 105 away from the opening 111.')],'权27依附前述任一项；顺序取自图1实施方式而非拼接27—30','C11/C07：原“残留未知”更正；明确维护/切换前排液对象。')
record(p,'solids_dewatering','fig1_ab','排液后滤渣液含量降低，可在滤面等待进一步减少液体；不意味着全干。非流动态和已脱水另见权29、30，其中30依附29。','湿滤渣','排液后滤面','较少液体的滤渣','同一过滤腔内部',['排液降低液含量','必要时等待'],[('p0213','This leaves filter residue with reduced liquid content.'),('p0213','If necessary, the filter residue can be left on the filter medium 106 for a time period to further reduce liquid content.'),('clm-0030',None)],'30→29→选定前述项；图1等待为可选说明书步骤','C11：脱水对象为滤渣，不与腔体排液字段合并。')
record(p,'transfer','fig1_ab','图1b接触件108a相对滤面移动刮/推滤渣，经111进入过滤腔外的收集腔107；external指相对过滤腔，不是整机外。','滤渣','滤介质106第一面','收集腔107','过滤腔→其外收集腔，仍可能位于同一模块',['排液','打开111','刮/推入107'],[('p0213','In figure 1b, the filter residue removal apparatus 108 is operated to push residue off the surface of the filter medium 106, through the opening 111 , and into the filter residue collection chamber 107.')],'独立权1的第二构型＋图1b具体实施方式','不把独立权3旋转甩出强行加入图1b接触刮推。')
record(p,'removal','slidable_collection_option','权10及说明书p0083支持收集腔或其一部分滑出微粒过滤器；图1描述收集腔可拆以便排空，但未证明每个刮推或甩出实施例均配同样抽屉。','含滤渣收集腔或其部分','过滤模块内收集单元','过滤模块外可移出单元','微粒过滤模块边界',['滑出收集腔/部分','供排空'],[('clm-0010',None),('p0083',None)],'10依附前述任一项；抽屉为可选说明书结构','分开收集腔移出与从滤腔到收集腔的内部转移。','same_embodiment_combination','container_with_retained_material')
p='WO2024250011A1'
record(p,'cleaning','description0051','说明书[0051]明示用离心力与未具体限定的pulse使褶皱滤面微纤维脱离；脉冲来源、强度、流路和执行器未由该段给出。','褶皱滤面微纤维','褶皱滤面','脱离滤面的微纤维','滤面边界',['离心力与pulse使其脱离'],[('p0051','aspects of the present disclosure leverage the centrifugal force and a pulse to knock them off again and move the microfibers to a separate compartment where they get stored.')],'不适用：说明书[0051]；本轮已读权1—23未定位该脉冲路线限定','C11：说明书本发明方案是技术披露，不因未入权项判未知。')
record(p,'transfer','description0051','同段说明微纤维从滤面移至单独存储腔；仅能说明概念性起终点，不能补画管路阀门或称为已实现干渣输送。','微纤维','褶皱滤面','separate compartment','滤面→单独腔体，模块/整机边界未详述',['脱离滤面','转移','存储'],[('p0051','move the microfibers to a separate compartment where they get stored.')],'说明书[0051]；非权项限定','C11：撤销转移未知，但保留实现细节缺失。')
record(p,'storage','description0069','说明书[0069]另述图5滤器可设反冲洗腔收集反冲颗粒；未确认与[0051]的separate compartment为同一部件。','反冲洗颗粒','图5滤器500','backwash compartment','图5可选收集腔',['可选反冲洗颗粒捕集'],[('p0066','The filter 500 can include a backwash compartment to trap backwashed particles.')],'说明书[0069]，HTML实际锚点p0066','不同段落/部件不自动合并成单一流程。')
record(p,'removal','claim17','权17将捕获微纤维的第二级滤层置于可移除多级滤器中；属于含目标物过滤组件的取出结构，具体拆装顺序需另核。','含捕获微纤维的多级滤器','壳体内','可移除的滤器','壳体与内滤器边界',['可移除；本项未给具体动作次序'],[('clm-0017','a removable porous, multi-stage filter within the housing'),('clm-0017','wherein microfibers from the textile items are captured within the second stage of the multi-stage filter')],'独立权17','保留滤组件移出路径；不把可拆外壳当唯一依据。','same_embodiment_combination','filter_assembly_with_retained_material')

# Scanned German publication: primary PDF manually viewed, never empty OCR as negative evidence.
pub='WO2024199585A1';s=sample(pub);pdf=H/'patents'/f'{pub}.pdf'
def pdf_obs(field,emb,text,excerpt,page,locator,image_path,dependency,obj,start,end,order):
 o={'observation_id':pub+'-'+field+'-'+emb,'publication_id':pub,'grant_publication_id':None,'sample_role':'pending','embodiment_id':emb,'stage':field,'technical_feature':text,'object':obj,'start':start,'end':end,'boundary':'滤元件/截留物容器/滤液出口分别识别；不推断整机外边界','operation_order':order,'support_status':'explicit','review_status':'complete_in_stated_scope','claim_dependency':dependency,'evidence':[{'locator':locator,'evidence_excerpt':excerpt,'source_role':'claim' if '权' in locator else 'description_embodiment','subject_role':'this_invention','source_path':str(pdf),'source_url':'https://patents.google.com/patent/WO2024199585A1/de','source_sha256':sha(pdf),'physical_page':page,'page_image_path':str(image_path),'page_image_sha256':sha(image_path),'verification_method':'manual_visual_readback_original_German','verified_at':NOW}],'interpretation':text,'performance_status':'not_verified','verified_at':NOW,'old_value':s['prior_working_evidence']['fields'].get(field),'new_value':text,'change_reason':'C11/C16：空claims抽取不代表无权项；回德文原页裁定，本发明控制清理不借背景短时间措辞。'}
 f=s['features'][field];f['observations']=[x for x in f['observations'] if x['observation_id']!=o['observation_id']]+[o];f.update(review_status='partial',support_status='explicit');s['review_completeness']['current_scope'].append({'publication':pub,'physical_page':page,'field':field,'at':NOW})
pdf_obs('cleaning','claim9','权9公开控制机构调节微塑料从滤元件区域导出或回流，特别用于清理滤元件；无固定清理时长。','dass die Steuermechanik (8) eine Ableitung des Mikroplastiks aus dem Bereich des Filterelements (3) oder eine Rückströmung, insbesondere zur Reinigung des Filterelements (3) regelt.',28,'物理28页/印刷26页，权9',RUN/'evidence/WO2024199585A1_physical28.png','9→1—8中任一项','微塑料/回流','滤元件3','导出或回流清理',['控制导出或回流'])
pdf_obs('cleaning','claim14','权14公开通过模拟或数字控制机构清理滤元件；依附12或13，13再依附12。不能以背景所谓短时间作为本方案性能。','dass durch eine analoge oder digitale Steuermechanik eine Reinigung des Filterelements (3) erfolgt.',29,'物理29页/印刷27页，权14',RUN/'evidence/WO2024199585A1_physical29.png','14→12或13；13→12','滤元件3','运行状态','清理状态',['模拟/数字控制清理'])
pdf_obs('cleaning','description_pressure_pulse','说明书阀控制可给滤壁压力脉冲，使附着微塑料/颗粒脱离，属于明确清理路径；不能推出最短周期或效率。','einen Druckimpuls auf die Wandung des Filterelements zu geben',15,'物理15页/印刷13页20—26行',H/'revision_20260929/evidence/wo2024199585_pages/description-15.png','不适用：本发明实施方式','附着滤壁微塑料','滤元件壁面','脱离壁面进入截留物流',['阀控制产生压力脉冲','颗粒脱离'])
pdf_obs('removal','claim8','权8语法主体为Retentat：截留物可由容器收集并从容器取出；不是容器一定可拆取。','dass das Retentat in einem Behälter (7) auffangbar und aus dem Behälter (7) entnehmbar ist.',27,'物理27页/印刷25页，权8',H/'revision_20260929/evidence/wo2024199585_pages/claims-27.png','8→1—7中任一项','截留物本身','容器7','容器外','收集后取出'.split('后'))
s['publications'][0]['review_status']='partial_original_German_PDF_pages_15_27_28_29'
s['scene_material']={'classification':'包括洗衣或洗碗废水微塑料，并有其他流体场景','review_status':'primary_text_scope_reviewed','evidence':'物理29页权15；不把全部对象称为微纤维'}
for pub in cache:
 (RUN/'evidence'/(pub+'_anchors.json')).write_text(json.dumps(cache[pub],ensure_ascii=False,indent=2),encoding='utf-8')
M.update(updated_at=NOW,phase='P2_in_progress');P.write_text(json.dumps(M,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

a=H/'patents/training_20260927/14同族人工功能矩阵.json';b=H/'team_package_20260928/inputs/14同族人工功能矩阵.json'
A={x['publication']:x for x in json.loads(a.read_text(encoding='utf-8-sig'))};B={x['publication']:x for x in json.loads(b.read_text(encoding='utf-8-sig'))};diff=[]
mapping={'固体移出':'removal','残留':'chamber_drainage','再生/清理':'cleaning','转移':'transfer'}
for pub,row in A.items():
 for key,value in row['features'].items():
  prior=B[pub]['features'].get(key)
  if prior==value:continue
  obs=sample(pub)['features'][mapping[key]]['observations'];assert obs
  diff.append({'publication':pub,'legacy_field':key,'training_matrix_value':value,'team_matrix_value':prior,'decision':[o['technical_feature'] for o in obs],'observation_ids':[o['observation_id'] for o in obs],'status':'primary_text_decided; publication_roles_pending','source_matrix_hashes':[sha(a),sha(b)]})
assert len(diff)==6 and len({d['publication'] for d in diff})==5
(RUN/'data/matrix_conflict_decisions.json').write_text(json.dumps(diff,ensure_ascii=False,indent=2),encoding='utf-8')
checks=json.loads((RUN/'QA/correction_checklist.json').read_text(encoding='utf-8'))
for c in checks:
 if c['id']=='C11':c.update(status='six_fields_primary_text_decided; final_export_pending',evidence=['data/matrix_conflict_decisions.json','data/analysis_master.json'])
 if c['id']=='C16':c.update(status='WO2024199585A1_empty_claims_handled_by_original_pages; wider_read_completeness_pending',evidence=['evidence/WO2024199585A1_physical28.png','evidence/WO2024199585A1_physical29.png'])
(RUN/'QA/correction_checklist.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print('Six historical fields resolved; total observations',sum(len(f['observations']) for s in M['samples'] for f in s['features'].values()))
