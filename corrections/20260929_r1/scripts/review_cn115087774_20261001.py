"""Original A scoped review; keep prior CN/WO observations and legal gates."""
from pathlib import Path
import csv,datetime,difflib,hashlib,json,subprocess,sys
from local_source import read_anchors
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='43cb2f6bfa6868f987498b2aad235de65becf8d7';PUB='CN115087774A';PAGES=[8,10,13,17,19,20,21]
SRC=H/'team_package_20260928/sources/CN115087774A.html';PDF=H/'team_package_20260928/sources/CN115087774A.pdf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def img(n):return R/f'evidence/CN115087774A_review_20261001_{n}.png'
assert sha(SRC)=='ac305984da6b9842eb21bad93569a11859686992ed1c6f2e6efd90fbc9364bb2'
assert sha(PDF)=='5a1649bc0de1a541dda8a360b3e259142da20a713b187e6c7b4d06501de3004c'
a=read_anchors(SRC);old=json.loads(subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/analysis_master.json'],cwd=H));m=json.loads(M.read_text(encoding='utf-8'))
if '--verify' in sys.argv:
    for x,y in zip(old['samples'],m['samples']):
        if x['representative_publication']!=PUB:assert x==y
        else:
            assert x['legal_evidence']==y['legal_evidence'] and x['prior_working_evidence']==y['prior_working_evidence']
            for k,v in x['features'].items():assert y['features'][k]['observations'][:len(v['observations'])]==v['observations']
    obs=[o for s in m['samples'] for f in s['features'].values() for o in f['observations']];assert len(obs)==124 and len({o['observation_id'] for o in obs})==124
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
    assert len(s['source_conflicts_20261001'])==3 and all(c['status']=='unresolved' and not c['automatically_corrected'] for c in s['source_conflicts_20261001'])
    for row in csv.DictReader((R/'data/review_coverage.csv').read_text(encoding='utf-8-sig').splitlines()):
        f=next(s for s in m['samples'] if s['representative_publication']==row['publication'])['features'][row['field']]
        assert int(row['observation_count'])==len(f['observations']) and row['review_status']==f['review_status'] and row['support_status']==(f['support_status'] or '')
    rel=json.loads((H/'current_release.json').read_text(encoding='utf-8'));assert rel['master_sha256']==sha(M) and rel['current_observations']==124
    assert all(s['sample_role']=='pending' for s in m['samples']) and not m['formal_statistics_allowed'] and not m['final_report_ready'] and not rel['project_completion_accepted']
    print(dump({'verified':True,'baseline':BASE,'observations':124,'added':8,'old_116_unchanged':True,'other_13_candidates_unchanged':True,
      'legal_evidence_unchanged':True,'all_14_pending':True,'master_sha256':sha(M),'original_pdf_sha256':sha(PDF),'source_html_sha256':sha(SRC),
      'executor_original_text_pages':list(range(2,12)),'executor_visual_pages':PAGES,'visual_page_sha256':{str(n):sha(img(n)) for n in PAGES},
      'reviewer_reported_text_pages':list(range(1,22)),'reviewer_reported_visual_pages':[2,7,8,9,10]+list(range(12,22)),
      'unresolved_original_wording_or_numbering':3,'full_text_complete_count':0,'CSV_verified':True,'formal_statistics_allowed':False}))
    raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();s=next(s for s in m['samples'] if s['representative_publication']==PUB)
# field, route, anchors, visual page, object/start/end, scoped conclusion, support
D=[
('capture','permeable_plate_or_wall',['cl0015','cl0016','cl0017','p0057','p0068'],8,'流出物微塑料纤维','腔201含固液流出物','可渗透板面/腔壁截留并形成压缩固体','原A从属权15/16的板或壁可渗透、权17网状物；[0052]板/后壁/翻板分别可渗透，图7另为无孔板+下壁网705，保留不同实施方式，不能把板面可渗透设成所有形式的必要结构。孔径与比例为设计/文本陈述，非实测。','explicit'),
('cleaning','plate_face_pellet_release',['p0055','p0072'],10,'压实板面上的固体块','板面附着压实物','抽回板/重力释放固体块','[0050]抽回板释放固体块；[0067]图6d改变板/腔相对姿态使颗粒更易从第一板面重力释放，可如实记录板面脱块。未由此证明网孔被清洗再生、完整清洗程序或堵塞恢复实测；背景网过滤器手清/水冲不是本发明机制。','partial_explicit_plate_release_not_mesh_regeneration'),
('transfer','plate_driven_solid_to_outlet',['cl0001','p0059','p0065','p0069','p0070'],17,'积聚纤维及压实颗粒','腔内板面/板间','对准出口206并经重力或机构排出','权1板运动将压缩微塑料移动到出口并自动排放。[0054]往返冲程、图4双独立驱动板、图5/6偏置锁存板为各自实现，不串成同一必需机构。记录固体而不是只描述排水；对准与释放的原文步骤见各锚点。','explicit'),
('storage','intermittent_chamber_retention',['p0054','p0055'],13,'含纤维流出物与压实固体','入口202间歇灌入','腔201内暂存/压实后出口206排放','[0049]/[0050]腔内间歇接收、入口阀填后关闭，压缩前出料口关闭使流出物不逸出；可记录循环中的腔内暂存。原A未由此披露独立长期储渣箱、密封防漏贮存或自动装袋，不把压缩腔改名最终收集桶。','explicit_temporary_chamber_retention'),
('state_switch','separate_compression_cycles',['cl0024','p0054','p0055','p0069','p0070','p0075','p0076'],21,'板/进出阀/锁存翻板','非压缩接收位置','压缩→板返回→颗粒排放/复位','权24接收→板前进分水压缩→板返回→排放。图3入口填后关/出口压缩时关；图6偏置锁存第二板/释放复位；图7末端翻板由推杆开再关闭；图8/10抽屉可手动驱动、或其他驱动自动操作，各分支独立。不能写全装置必须自动控制器或唯一停机清渣顺序。','explicit'),
('performance','unverified_efficiency_and_dryness_claims',['p0052','p0055','p0058','p0068'],8,'孔径/去除比例/固体含水状态','设计和作用文字','99.4%等文本陈述，完整测试条件unknown','[0053]80um网可阻止99.4%的25um微纤维，是原文比例但未附计量方法、工况、重复样本或误差；[0050]/[0063]去所有液体/有效干燥也无含水率测定。背景98%水处理/99%理论和一次性套筒重量不能移成本装置实测；不补实验或填0。','explicit_text_claim_test_support_unlocated'),
('endpoint','household_collection_or_recycling',['p0052','p0053'],8,'压实微纤维颗粒/盘','板排出或用户取得后的固体','文本指向家用垃圾收集或转移回收设施','原[0047]明确颗粒形式便于通过家用垃圾收集处置；[0048]续段给例如转移回收设施。下游处置方向是正向披露，不能判未定位；但未提供分类标准、设施接收条件、封装运输验证或真实完成记录，不据目的文字宣称安全处置已实际闭合。','explicit_downstream_route_not_verified_completion'),
('carrier_conditioning','independent_carrier_drying_unlocated',['p0057','p0068','p0072'],10,'板/网载体自身','压缩运行/脱块后的载体','unknown：独立载体排水干燥工序未定位','完整原A权1—24、[0001]—[0071]文本及本次图页范围未定位载体自身独立排水/干燥步骤和终点。网让水通过是运行液路；[0063]干燥对象是压实微塑料固体，不能挪到过滤载体；[0067]板面脱块不等于介质调理。','not_located_in_reviewed_scope')]
added=[]
for field,route,keys,page,obj,start,end,meaning,status in D:
    o={'observation_id':PUB+'-'+field+'-'+route+'-20261001','publication_id':PUB,'grant_publication_id':None,'sample_role':'pending','embodiment_id':route,'stage':field,
       'technical_feature':meaning,'object':obj,'start':start,'end':end,'boundary':'原CN A本发明各实施方式分别保留；历史WO同族观察不覆盖或复计','operation_order':[meaning],
       'support_status':status,'review_status':'complete_in_checked_original_A_scope','claim_dependency':'独立权1/方法24与所引从属项分别保留；各分支见interpretation',
       'evidence':[{'locator':'保存HTML #'+k+'；原PDF交叉页见下（各锚点不一定同页）','html_anchor':k,'source_path':str(SRC),'source_sha256':sha(SRC),
          'source_role':'independent_claim' if k=='cl0001' else 'method_claim' if k=='cl0024' else 'dependent_claim' if k.startswith('cl') else 'description',
          'evidence_excerpt':a[k][:650]} for k in keys],
       'interpretation':meaning,'performance_status':'text_claim_test_support_unlocated' if field=='performance' else 'not_verified','verified_at':now,
       'old_value':s['features'][field]['support_status'],'new_value':meaning,'change_reason':'补八空字段；不重复旧CN/WO十观察，不把本发明处置正向文本当未披露',
       'pdf_visual_crosscheck':{'source_path':str(PDF),'source_sha256':sha(PDF),'physical_page':page,'image_path':str(img(page)),'image_sha256':sha(img(page)),
          'checked_at':now,'verification_method':'original_Chinese_text_readback_and_manual_visual_pages','scope':'执行者原文字2—11及视觉8/10/13/17/19/20/21；未冒称全部10图页均由执行者视觉读完'},
       'review_scope':'原A24权项/[0001]—[0071]文字完整读取及本次7页目视；关联授权文本/资格独立待核。'}
    s['features'][field]['observations'].append(o);s['features'][field]['support_status']=status;s['features'][field]['review_status']='complete_in_checked_original_A_scope';added.append(o)
s['scene_material']={'classification':'laundry_and_other_microplastic_effluent_compaction','review_status':'checked_original_A_scope','verified_at':now,
    'evidence':'原[0001]/[0044]/[0045]洗衣及其他设备、工业/废水/道路径流；本发明对象含微纤维的微塑料，不把全部流出物都只含塑料。'}
s['review_completeness']['original_targeted_readback_20261001']={'checked_at':now,'pdf_sha256':sha(PDF),'executor_text_pages':list(range(2,12)),
    'claims_read':'1—24','description_read':'[0001]—[0071]','executor_visual_pages':PAGES,'all_fields_have_scoped_observations':True,
    'candidate_full_text_accepted':False,'related_grant_text_pending':True,'note':'旧10条CN/WO证据和法律保持；执行者未目视原12/14/15/16/18图页，不能宣称个人全图阅读。'}
s['review_completeness']['original_targeted_readback_20261001']['readonly_reviewer']='/root/h1_source_review'
s['review_completeness']['original_targeted_readback_20261001']['reviewer_reported_text_pages']=list(range(1,22))
s['review_completeness']['original_targeted_readback_20261001']['reviewer_reported_visual_pages']=[2,7,8,9,10]+list(range(12,22))
s['source_conflicts_20261001']=[
 {'conflict_id':'CN115087774A-description0059-outlet-number','locator':'原物理9 [0059]','original_quote':'废水209通过废水出口207','status':'unresolved','automatically_corrected':False,
  'source_path':str(PDF),'source_sha256':sha(PDF),'boundary':'207通常为压实颗粒，液路正向锚点用[0052]/[0068]/[0069]明确208；不默修原编号'},
 {'conflict_id':'CN115087774A-description0060-drive-number','locator':'原物理9 [0060]','original_quote':'适当致动驱动单元204a和204b','status':'unresolved','automatically_corrected':False,
  'source_path':str(PDF),'source_sha256':sha(PDF),'boundary':'204a/b通常是板，205a/b是驱动；不默修原编号'},
 {'conflict_id':'CN115087774A-description0070-compressed-object','locator':'原物理10 [0070]','original_quote':'抵靠着翻板702压缩所述水','status':'unresolved','automatically_corrected':False,
  'source_path':str(PDF),'source_sha256':sha(PDF),'page_image_path':str(img(10)),'page_image_sha256':sha(img(10)),
  'boundary':'保留原文对象表述；不自行改成压缩固体。图3基础版本[0050]同出口放固体与分离流体，不推广每个版本液固独立出口'}]
assert not s['review_completeness']['full_text_rechecked'];m['updated_at']=now
print('*** Begin Patch\n*** Update File: '+str(M).replace('\\','/'));section=0
for l in list(difflib.unified_diff(dump(old).splitlines(),dump(m).splitlines(),n=3))[2:]:
    if l.startswith('@@'):
        section+=1;print('@@       "representative_publication": "CN115087774A",' if section==2 else '@@')
    else:print(l)
body='# CN115087774A 原A八字段复核\n\n原PDF SHA '+sha(PDF)+'。原文字2—11全部24权项/71段已读，执行者7原页目视范围明确；候选全文验收仍false。\n\n'
for o in added:body+='## '+o['stage']+'\n\n'+o['interpretation']+'\n\n保存锚点 '+','.join(e['html_anchor'] for e in o['evidence'])+'；视觉交叉原页 '+str(o['pdf_visual_crosscheck']['physical_page'])+'。\n\n'
body+='原[0059]废水出口207、[0060]驱动单元204a/b、[0070]压缩所述水三处原编号/对象问题均未自动修正；基础[0050]同出口放固液，不推广所有版本均独立出水。只读代理报告21页文本及2/7—10/12—21目视（全部图），不写成全21页视觉阅读。新增8条合计124；旧116、其他13对象、全部法律原值保持。14pending，正式统计/终稿未放行。\n'
print('*** Add File: '+str(R/'evidence/CN115087774A_original_field_readback_20261001.md').replace('\\','/'));print('\n'.join('+'+l for l in body.splitlines()));print('*** End Patch')
