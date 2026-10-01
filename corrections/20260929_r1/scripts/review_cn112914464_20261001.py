"""Patch-only manual source decisions; verification is read-only."""
from pathlib import Path
import csv, datetime, hashlib, io, json, re, subprocess, sys
from pypdf import PdfReader
from local_source import read_anchors
H=Path(__file__).resolve().parents[3]; R=H/'corrections/20260929_r1'; M=R/'data/analysis_master.json'
BASE='3d5fa332149271b34fc3b9dc535b09102eda6d82'
PUB='CN112914464A'
HTML=H/'team_package_20260928/sources/CN112914464A.html'
PDF=H/'patents/verification/20260928_cn112914464a_ep3832001b1/CN112914464A.pdf'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dumps(o): return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
assert sha(PDF)=='d784ea097857f7d3799ea36e49d7e3d89c1ec1501a2adb9cdb6aefa61e97460c'
assert sha(HTML)=='e53dd8bddd8608d606f271527410ed07fa59d452c9f5b1b2036f55745e457c18'
a=read_anchors(HTML); pdf=PdfReader(PDF); assert len(pdf.pages)==23
PAGES={'p0053':'11','p0057':'11','cl0001':'2','p0058':'11—12','p0060':'12','cl0022':'3','p0054':'11','p0055':'11','cl0020':'3','cl0021':'3','p0026':'8—9','p0082':'15','p0083':'15','p0084':'15','p0030':'9','p0080':'15'}
text=[p.extract_text() for p in pdf.pages]
images=[{'physical_page':i,'path':str(R/f'evidence/CN112914464A_20261001-{i}.png'),
    'sha256':sha(R/f'evidence/CN112914464A_20261001-{i}.png')} for i in range(16,24)]
old=json.loads(subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/analysis_master.json'],cwd=H))
m=json.loads(M.read_text(encoding='utf-8')); s=next(s for s in m['samples'] if s['representative_publication']==PUB)
if '--verify' in sys.argv:
    for before,after in zip(old['samples'],m['samples']):
        if before['representative_publication']!=PUB: assert before==after
        else:
            assert before['legal_evidence']==after['legal_evidence']
            assert before['prior_working_evidence']==after['prior_working_evidence']
            for field,v in before['features'].items(): assert after['features'][field]['observations'][:len(v['observations'])]==v['observations']
    count=0; ids=[]
    for sample in m['samples']:
        assert sample['sample_role']=='pending'
        for field in sample['features'].values():
            for obs in field['observations']:
                count+=1; ids.append(obs['observation_id'])
                for e in obs['evidence']:
                    if obs['observation_id'].startswith(PUB) and obs['observation_id'].endswith('-20261001'):
                        assert '原PDF物理'+PAGES[e['html_anchor']]+'页' in e['locator']
                    src=Path(e['source_path']); assert sha(src)==e['source_sha256']
                    if e.get('html_anchor'): assert e['evidence_excerpt'] in read_anchors(src)[e['html_anchor']]
                    else: assert sha(Path(e['page_image_path']))==e['page_image_sha256']
                if obs.get('pdf_visual_crosscheck'):
                    cross=obs['pdf_visual_crosscheck']; assert sha(Path(cross['source_path']))==cross['source_sha256']
                    assert sha(Path(cross['image_path']))==cross['image_sha256']
    assert count==81 and len(ids)==len(set(ids))
    assert all(v['observations'] for v in s['features'].values())
    rows=list(csv.DictReader((R/'data/review_coverage.csv').read_text(encoding='utf-8-sig').splitlines()))
    for row in rows:
        sample=next(z for z in m['samples'] if z['representative_publication']==row['publication'])
        field=sample['features'][row['field']]
        assert int(row['observation_count'])==len(field['observations'])
        assert row['review_status']==field['review_status'] and row['support_status']==(field['support_status'] or '')
    assert not m['formal_statistics_allowed'] and not m['final_report_ready']
    release=json.loads((H/'current_release.json').read_text(encoding='utf-8'))
    assert release['master_sha256']==sha(M) and release['current_observations']==81 and not release['project_completion_accepted']
    print(dumps({'verified':True,'observations':81,'new_observations':8,'master_sha256':sha(M),
        'source_pdf_sha256':sha(PDF),'drawing_pages':images,'all_other_samples_unchanged':True,
        'old_73_observations_unchanged':True,'all_14_pending':True,'all_13_fields_addressed':True,'full_candidate_acceptance':False}))
    raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
# Every tuple is a manually read, separate embodiment or scoped negative. No guessed 0.
decisions=[
('capture','fig1_fine_filter26','explicit',['p0053'],11,16,'洗衣磨损纤维/塑料微纤维','滚筒贮槽出口23','精细过滤器26','运行水回路',['出口24进滤器26','滤后29到泵31'],'图1方案在排放或循环水中用精细过滤器26截留衣物磨损微塑料/纤维；可选多级或按衣物种类旁通，不宣称所有工况必经过滤。'),
('storage','fig2_closed_container63','explicit',['p0057','cl0001'],11,17,'已从主滤器脱离的过滤物质65','过滤物质入口68','封闭容器63','转换抽屉20/结构单元49',['物质经入口68进入','在63内集中储存'],'图2的过滤物质65由主滤器26转来并在朝外闭合的容器63内与壁接触；不是在容器中首次产生。图3一体单元、图4可分离容器、图8单袋及图9双腔袋各为不同构造，不拼成同一必经流程。'),
('chamber_drainage','dedicated_maintenance_emptying_not_located','not_located_in_reviewed_scope',['p0058','p0060','cl0022'],12,17,'过滤物质接收腔的自由液体','容器63','未定位独立快速排空/隔离机构','原A29项、[0001]—[0064]与图1—12',['可选62正常滤水/浓缩','移除后排空或处置另述'],'可选62使水流走用于浓缩，权22的过滤物质排空及图2处置均不等同维护前专用自由液体排空。完整原A范围未定位独立维护快速排空/确认已无残液；不得据此说容器不排水或行业不存在。'),
('state_switch','fig1_pump_valves','explicit',['p0054','p0055'],11,16,'循环/排水/反洗水及滤物','泵31和阀33/38','返回支路/出口18/反洗入口27','图1运行流路',['控制器46致动','阀33选择支路','反洗42到27','滤物44到抽屉'],'图1泵31、阀33/38由控制器46致动；正常排水、返滚筒/抽屉及反洗42→27是不同阀支路。不能把它与图11/12的180°分配器拼成共同控制链。'),
('state_switch','level_indication_not_mandatory_stop','explicit',['cl0020','cl0021','p0026','p0060'],12,17,'容器填充水平/用户提示','传感器51/61','控制器/使用者','图2及一般阈值提示构造',['检测空/满或阈值','控制器指示','使用者决定更换'],'权20→1及权21方法要求检测/提示，图2传感器51/61与控制器46配合；说明书还允许满后继续运行而不再收集，不得升级为强制停机、安全联锁或证实零再排放。'),
('state_switch','fig11_12_rotary_head677','explicit',['p0082','p0083','p0084'],15,23,'洗涤剂655/过滤物质665','分配器头677','出口658或入口668','图11/12单容器隔膜664方案',['图11移出洗涤剂','分配器旋转180°','堵住658','图12输入过滤物质'],'图11/12中分配器头677旋转180°，由洗涤剂排出切换为过滤物质输入，并由密封件678堵住洗涤剂出口658。空气入口679在洗涤剂排出阶段通气，不是固体主动干燥；与图2可选滤器62不自动合并。'),
('performance','capacity_design_not_test','explicit',['p0030','p0058'],9,17,'过滤物质容量/含水量','设计性叙述','无可比实测终点','原A完整文本范围',['容量匹配若干洗涤过程','可选浓缩减体积'],'[0027]至少5/10次等是容量匹配设计，[0038]较干/增稠为可选62的目的说明。全文未见这些方案的可比效率、压差、残余含水率、重复样本与测试条件，不能作为实测性能排序。'),
('carrier_conditioning','separate_carrier_drying_not_located','not_located_in_reviewed_scope',['p0058','p0060','p0080'],12,22,'过滤载体/滤纸或无纺布','可选额外过滤器62','可保留或随滤物处置并换新','原A完整文本范围',['滤水浓缩滤物','载体可保留或处置替换'],'可选62用滤纸/无纺布且可随过滤物质丢弃或保留；p0080说袋状容器可清洁/换袋，不能偷换为载体已干燥。完整原A未定位维护时独立载体排水/干燥机构；滤物减少含水与载体调理分开。')]
added=[]
for field,emb,status,keys,page,fig,obj,start,end,boundary,order,meaning in decisions:
    evidence=[{'locator':f'HTML #{k}; 原PDF物理{PAGES[k]}页及图页{fig}','html_anchor':k,'source_path':str(HTML),'source_sha256':sha(HTML),
        'source_role':'description' if k.startswith('p') else ('independent_claim' if k in ['cl0001','cl0021','cl0022'] else 'dependent_claim'),
        'evidence_excerpt':a[k]} for k in keys]
    img=next(x for x in images if x['physical_page']==fig)
    o={'observation_id':PUB+'-'+field+'-'+emb+'-20261001','publication_id':PUB,'grant_publication_id':None,'sample_role':'pending',
        'embodiment_id':emb,'stage':field,'technical_feature':meaning,'object':obj,'start':start,'end':end,'boundary':boundary,
        'operation_order':order,'support_status':status,'review_status':'complete_in_stated_scope','claim_dependency':'说明书各自构造；权1/21/22及各从属分支不跨支拼接',
        'evidence':evidence,'interpretation':meaning,'performance_status':'text_claim_only' if field=='performance' else 'not_verified',
        'verified_at':now,'old_value':s['features'][field]['support_status'],'new_value':meaning,'change_reason':'原A23页全文与8附图页复核后补未填字段；不放行法律资格',
        'pdf_visual_crosscheck':{'source_path':str(PDF),'source_sha256':sha(PDF),'physical_page':fig,'image_path':img['path'],'image_sha256':img['sha256'],
            'checked_at':now,'verification_method':'manual_visual_readback_original_Chinese','scope':'已目视该原图页并对照完整原A文本；文字证据逐项以HTML锚点保留'},
        'review_scope':'原A23页；封面、权1—29、[0001]—[0064]与图1—12；相关授权成员未完成同轮全文确认'}
    s['features'][field]['observations'].append(o);s['features'][field]['review_status']='complete_in_original_A_scope';s['features'][field]['support_status']=status
    added.append(o)
s['review_completeness']['original_A_readback']={'checked_at':now,'source_path':str(PDF),'source_sha256':sha(PDF),'physical_pages_read':list(range(1,24)),
    'text_scope':'封面、权1—29及[0001]—[0064]','all_drawing_pages_visually_read':images,'all_13_fields_addressed':True,
    'limitation':'仅原A技术文本范围；相关授权成员及资格未闭合，不计已核有效核心，不宣称整套P2完成'}
# Retain broad candidate flag until all relevant text/version/family scope is accepted.
assert s['review_completeness']['full_text_rechecked'] is False
m['updated_at']=now
def block(key,val):
    lines=json.dumps(val,ensure_ascii=False,indent=2).splitlines()
    return ['      '+json.dumps(key)+': '+lines[0]]+['      '+l for l in lines[1:-1]]+['      '+lines[-1]+',']
prior=next(s for s in old['samples'] if s['representative_publication']==PUB)
patch='*** Begin Patch\n*** Update File: '+str(M).replace('\\','/')+'\n@@\n-  "updated_at": '+json.dumps(old['updated_at'])+',\n+  "updated_at": '+json.dumps(now)+',\n'
for key in ['features','review_completeness']:
    before=block(key,prior[key]);after=block(key,s[key])
    if key=='review_completeness': before[-1]=before[-1].rstrip(',');after[-1]=after[-1].rstrip(',')
    patch+='@@\n'+''.join('-'+l+'\n' for l in before)+''.join('+'+l+'\n' for l in after)
cardpath=R/'evidence/technical_cards/CN112914464A.md'
oldcard=cardpath.read_text(encoding='utf-8');newcard=oldcard+'\n## 2026-10-01 原A完整原件补查\n\n'
for o in added:
    newcard+=f'### {o["stage"]} / {o["embodiment_id"]}\n\n{o["interpretation"]}\n\n支持：{o["support_status"]}。原件：物理图页{o["pdf_visual_crosscheck"]["physical_page"]}；锚点：'+', '.join(e['html_anchor'] for e in o['evidence'])+'。\n\n'
newcard+='原A23页文本与8幅图页均已读；全13字段在此范围有裁定。旧“尚未单独裁定”是2026-09-29历史，本次以上述补查覆盖这6个字段；相关授权成员、法律资格仍待核，全文候选验收标记仍false。\n'
patch+='*** Update File: '+str(cardpath).replace('\\','/')+'\n@@\n'+''.join(' '+l+'\n' for l in oldcard.splitlines()[-3:])+''.join('+'+l+'\n' for l in newcard[len(oldcard):].splitlines())
patch+='*** Add File: '+str(R/'evidence/CN112914464A_original_A_readback_20261001.json').replace('\\','/')+'\n'+''.join('+'+l+'\n' for l in dumps(s['review_completeness']['original_A_readback']).splitlines())
print(patch+'*** End Patch')
