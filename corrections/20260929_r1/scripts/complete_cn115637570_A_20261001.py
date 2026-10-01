"""Complete original-A scope from manually read pages; emit patches, never write."""
from pathlib import Path
import csv,datetime,difflib,hashlib,json,subprocess,sys
from local_source import read_anchors
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='8b232772e25bfd45bb869efc315186732d175161';PUB='CN115637570A'
SOURCE=H/'team_package_20260928/sources/CN115637570A.html'
PDF=H/'revision_20260929/legal/cn115637570_probe_20260929_2112/CN115637570A_original.pdf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dumps(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
assert sha(PDF)=='ce0112648ae509c464bb45ab3fb639cbc98f53b3a3f4f146a80abc48de43d456'
assert sha(SOURCE)=='7e2731e82b601fb6f16d2c30e96f538c1b9f3533de4406e515402e2b4c3336c1'
a=read_anchors(SOURCE);original=json.loads(subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/analysis_master.json'],cwd=H))
m=json.loads(M.read_text(encoding='utf-8'));s=next(z for z in m['samples'] if z['representative_publication']==PUB)
if '--verify' in sys.argv:
    for old,new in zip(original['samples'],m['samples']):
        if old['representative_publication']!=PUB:assert old==new
        else:
            assert old['legal_evidence']==new['legal_evidence'] and old['prior_working_evidence']==new['prior_working_evidence']
            for k,v in old['features'].items():assert new['features'][k]['observations'][:len(v['observations'])]==v['observations']
    obs=[o for z in m['samples'] for f in z['features'].values() for o in f['observations']]
    assert len(obs)==91 and len({o['observation_id'] for o in obs})==91
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
    assert all(f['observations'] and f['review_status']=='complete_in_original_A_scope' for f in s['features'].values())
    assert s['review_completeness']['full_text_rechecked'] is False
    rows=list(csv.DictReader((R/'data/review_coverage.csv').read_text(encoding='utf-8-sig').splitlines()))
    for row in rows:
        f=next(z for z in m['samples'] if z['representative_publication']==row['publication'])['features'][row['field']]
        assert int(row['observation_count'])==len(f['observations']) and row['review_status']==f['review_status'] and row['support_status']==(f['support_status'] or '')
    rel=json.loads((H/'current_release.json').read_text(encoding='utf-8'))
    assert rel['master_sha256']==sha(M) and rel['current_observations']==91 and not rel['project_completion_accepted']
    assert all(z['sample_role']=='pending' for z in m['samples']) and not m['formal_statistics_allowed'] and not m['final_report_ready']
    print(dumps({'verified':True,'master_sha256':sha(M),'observations':91,'new_observations':5,'old_86_observations_unchanged':True,
        'other_13_candidates_unchanged':True,'source_pdf_sha256':sha(PDF),'original_A_complete_readback':s['review_completeness']['original_A_complete_readback'],
        'all_14_pending':True,'CSV_verified':True,'formal_statistics_allowed':False,'full_text_complete_count':0}))
    raise SystemExit
assert m==original
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
decisions=[
('chamber_drainage','dedicated_maintenance_emptying_unlocated',['p0063','p0079','p0083'],10,'收集腔自由液体','正常滤后下部排水','未定位维护前独立排空','过滤器121与收集装置127','正常下部排水属于运行液路，开门取袋/滤器属于人工维护；原A权1—10、[0001]—[0079]及图1—6未定位维护前专用腔排空、残液确认或干式拆卸机构。不把正常出水推为腔内已无残水。'),
('solids_dewatering','no_dedicated_solids_dewatering_in_A',['p0057','p0063','p0079'],9,'刮下并携水转移的微纤维','滤网122','收集装置127/可选袋','完整原A范围','原A描述刮离与借水输送、可选袋收集，未定位对收集固体的独立压榨、离心、加热干燥、含水率控制或脱水终点。正常滤后水流不自动等同固体主动脱水，未知不转零。'),
('performance','qualitative_benefits_without_tests',['p0037','p0038','p0039'],4,'微纤维沉积/寿命与收集效率','构造和运动机理','文本目的与有益效果','原A全文','[0034]—[0036]宣称延长寿命、稀释浓度及延缓沉积，[0054]提到提高收集效率；均为文本作用说明。全文未提供可比较测试条件、数值效率/寿命、压差曲线或重复样本，不能当实测性能。背景引述每衣1900多纤维也不是本装置试验。'),
('endpoint','final_disposal_after_cleaning_unlocated',['cl0008','cl0010','p0079','p0083'],9,'已收集微纤维或取出的袋','127/过滤袋','未定位最终处置路径','完整原A维护叙述范围','权8可拆袋、权10安装口和[0078]开门取袋说明便于清理；未定位取出后微纤维的家庭垃圾、专业回收、封装外运或其他最终处置，不把取出直接编码为闭合处置终点。'),
('carrier_conditioning','carrier_drainage_drying_unlocated',['cl0007','p0075','p0076','p0079','p0083'],11,'过滤载体122/可选袋','过滤/清理状态','未定位载体独立排水干燥','完整原A范围','耐磨/不锈钢、锰钢合金或碳化硅是材料选择，不能据此断定载体已干燥。[0074]原文更换过滤网122不改成更换袋；开门取袋另由[0078]支持。全文未定位维护中独立载体排水/干燥步骤、结构或终点。')]
pages={'p0063':'6 [0058]','p0079':'7 [0074]','p0083':'7 [0078]','p0057':'6 [0052]','p0037':'4 [0034]','p0038':'4—5 [0035]','p0039':'5 [0036]','cl0008':'2 权8','cl0010':'2 权10','cl0007':'2 权7','p0075':'7 [0070]','p0076':'7 [0071]'}
added=[]
for field,emb,keys,fig,obj,start,end,boundary,meaning in decisions:
    img=R/(f'evidence/CN115637570A_full_A_20261001-{fig:02}.png' if fig==4 else f'evidence/CN115637570A_20261001-{fig:02}.png')
    status='explicit' if field=='performance' else 'not_located_in_reviewed_scope'
    o={'observation_id':PUB+'-'+field+'-'+emb+'-20261001-fullA','publication_id':PUB,'grant_publication_id':None,'sample_role':'pending',
       'embodiment_id':emb,'stage':field,'technical_feature':meaning,'object':obj,'start':start,'end':end,'boundary':boundary,
       'operation_order':['原A完整范围逐项检读','与已披露正常流路/人工拆卸分开'],'support_status':status,'review_status':'complete_in_stated_scope',
       'claim_dependency':'原A各权项/说明书限定各自保留；未新增独立项功能',
       'evidence':[{'locator':'HTML #'+k+'；原PDF物理'+pages[k],'html_anchor':k,'source_path':str(SOURCE),'source_sha256':sha(SOURCE),
           'source_role':'dependent_claim' if k.startswith('cl') else 'description','evidence_excerpt':a[k]} for k in keys],
       'interpretation':meaning,'performance_status':'text_claim_only' if field=='performance' else 'not_verified','verified_at':now,
       'old_value':s['features'][field]['support_status'],'new_value':meaning,'change_reason':'补完整原A剩余页并裁定五个未填字段；未读B与资格独立保留',
       'pdf_visual_crosscheck':{'source_path':str(PDF),'source_sha256':sha(PDF),'physical_page':fig,'image_path':str(img),'image_sha256':sha(img),
           'checked_at':now,'verification_method':'manual_visual_readback_original_Chinese','scope':'原A全文与原图；未定位仅针对该版本，不代表同族全文或行业不存在'},
       'review_scope':'原A物理1—11；权1—10、[0001]—[0079]及图1—6；原B未读'}
    s['features'][field]['observations'].append(o);s['features'][field]['support_status']=status;added.append(o)
for f in s['features'].values():f['review_status']='complete_in_original_A_scope'
s['scene_material']={'classification':'laundry_wastewater_microfibres_with_microplastic_focus','review_status':'complete_in_original_A_scope','verified_at':now,
    'basis':[{'anchor':k,'excerpt':a[k],'source_sha256':sha(SOURCE),'physical_page':3} for k in ['p0004','p0005']],
    'boundary':'背景谈小于5mm微塑料/微纤维与洗衣废水；不把所有衣物纤维都视为塑料，1900背景引述不是本装置性能测试。'}
s['review_completeness']['original_A_complete_readback']={'checked_at':now,'source_path':str(PDF),'source_sha256':sha(PDF),
    'physical_pages_read':list(range(1,12)),'claims_read':'1—10','description_read':'[0001]—[0079]','drawing_pages_visually_read':[9,10,11],
    'new_remaining_text_pages_read':[1,3,4,5,8],'all_13_fields_addressed_in_A_scope':True,'related_B_full_text_read':False,'qualification_pending':True}
assert s['review_completeness']['full_text_rechecked'] is False
s['publications'][0]['review_status']='complete_original_A_scope_related_B_pending'
m['updated_at']=now
print('*** Begin Patch\n*** Update File: '+str(M).replace('\\','/'))
diff=list(difflib.unified_diff(dumps(original).splitlines(),dumps(m).splitlines(),n=3))[2:]
section=0
for line in diff:
    if line.startswith('@@'):
        section+=1
        print('@@       "representative_publication": "CN115637570A",' if section==2 else '@@')
    else:print(line)
path=R/'evidence/CN115637570A_complete_A_readback_20261001.md'
body='# CN115637570A 原A完整范围复核\n\n原A11页、10项、[0001]—[0079]及图1—6已读；全13字段有范围内裁定。原B全文/资格仍pending，不作正式统计。\n\n'
for o in added:body+='## '+o['stage']+'\n\n'+o['interpretation']+'\n\n定位：'+', '.join(e['locator'] for e in o['evidence'])+'。\n\n'
body+='原A PDF SHA '+sha(PDF)+'。原86观察逐项保留；下一项为相关B原件获取与版本差异复核。\n'
print('*** Add File: '+str(path).replace('\\','/'));print('\n'.join('+'+l for l in body.splitlines()));print('*** End Patch')
