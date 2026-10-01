"""Manual capture/flow/control decisions. Emits patches; --verify reads only."""
from pathlib import Path
import json,hashlib,subprocess,datetime,difflib,sys,csv
from local_source import read_anchors
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';P=R/'data/analysis_master.json'
BASE='aa08b3a6ab5b6360114aefbedce5f1ad3a8a5d3e';PUB='CN115637570A'
HTML=H/'team_package_20260928/sources/CN115637570A.html'
PDF=H/'revision_20260929/legal/cn115637570_probe_20260929_2112/CN115637570A_original.pdf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dumps(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
assert sha(PDF)=='ce0112648ae509c464bb45ab3fb639cbc98f53b3a3f4f146a80abc48de43d456'
old=json.loads(subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/analysis_master.json'],cwd=H))
m=json.loads(P.read_text(encoding='utf-8'));s=next(s for s in m['samples'] if s['representative_publication']==PUB)
a=read_anchors(HTML)
if '--verify' in sys.argv:
    for b,c in zip(old['samples'],m['samples']):
        if b['representative_publication']!=PUB:assert b==c
        else:
            assert b['legal_evidence']==c['legal_evidence'] and b['prior_working_evidence']==c['prior_working_evidence']
            for k,v in b['features'].items():assert c['features'][k]['observations'][:len(v['observations'])]==v['observations']
    obs=[o for z in m['samples'] for f in z['features'].values() for o in f['observations']]
    assert len(obs)==86 and len({o['observation_id'] for o in obs})==86
    for o in obs:
        for e in o['evidence']:
            src=Path(e['source_path']);assert sha(src)==e['source_sha256']
            if e.get('html_anchor'):assert e['evidence_excerpt'] in read_anchors(src)[e['html_anchor']]
            else:assert sha(Path(e['page_image_path']))==e['page_image_sha256']
        if o.get('pdf_visual_crosscheck'):
            q=o['pdf_visual_crosscheck'];assert sha(Path(q['source_path']))==q['source_sha256'] and sha(Path(q['image_path']))==q['image_sha256']
    rows=list(csv.DictReader((R/'data/review_coverage.csv').read_text(encoding='utf-8-sig').splitlines()))
    for row in rows:
        f=next(z for z in m['samples'] if z['representative_publication']==row['publication'])['features'][row['field']]
        assert int(row['observation_count'])==len(f['observations']) and row['support_status']==(f['support_status'] or '') and row['review_status']==f['review_status']
    rel=json.loads((H/'current_release.json').read_text(encoding='utf-8'))
    assert rel['master_sha256']==sha(P) and rel['current_observations']==86
    assert all(z['sample_role']=='pending' for z in m['samples']) and not m['formal_statistics_allowed'] and not rel['project_completion_accepted']
    print(dumps({'verified':True,'master_sha256':sha(P),'observations':86,'old_81_observations_unchanged':True,'all_other_samples_unchanged':True,'CSV_verified':True,'source_pdf_sha256':sha(PDF),'all_14_pending':True,'full_text_complete_count':0}))
    raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
decisions=[
('capture','tubular_claim3',['cl0003','p0060'],10,'筒状过滤网122内的微纤维','权3→2→1；图3/4/5','筒状网沿轴线周向设置，螺杆在网内，上部叶片与网的间隙大于下部；原权3的构造不能被半筒图6替代。'),
('capture','open_upper_claim4',['cl0004','p0064','p0066'],11,'下部半筒网122截留微纤维','权4→3→2→1；图2/6','权4及[0059]—[0061]上部沿轴线敞开，图6为半筒形；保留下部过滤载体和上部较大流动空间，不能与完整筒状权3当成相同几何。'),
('capture','local_inlet_open_claim5',['cl0005','p0067'],10,'进水口附近网区域的微纤维','权5→3→2→1；不依附权4','权5只使靠上部进水口的部分沿轴线敞开；不是权4全上部敞开的同一限定，二者为不同从属分支。原件未给孔径或量化分级截留数据。'),
('liquid_route','normal_lower_drain_channel',['p0061','p0063'],10,'滤后水','[0056]/[0058]图3运行流路','进水123连网内，过滤后经下部滤网与筒体下壁之间的排水流道到出口124；这是正常滤后水流，不是专用维护腔排空、固体脱水或过滤袋已排干。'),
('state_switch','optional_sensor_motor',['p0071','p0072','p0073','p0074'],9,'沉积微纤维量及电机131','说明书[0066]—[0069]；不加到独立权1','可选传感器/控制器按微纤维较多启动电机，较少停机，可间歇转动；列举不同传感器或组合，没有统一阈值或已验证自动完全清空状态。')]
added=[]
for field,emb,keys,fig,obj,dependency,meaning in decisions:
    img=R/f'evidence/CN115637570A_20261001-{fig:02}.png'
    o={'observation_id':PUB+'-'+field+'-'+emb+'-20261001','publication_id':PUB,'grant_publication_id':None,'sample_role':'pending','embodiment_id':emb,'stage':field,
       'technical_feature':meaning,'object':obj,'start':'进水/滤网或传感器','end':'对应滤网/正常出水或电机动作','boundary':'过滤器筒体121各自实施方式',
       'operation_order':['按相应原文的构造/运行路径读取'],'support_status':'explicit','review_status':'complete_in_stated_scope','claim_dependency':dependency,
       'evidence':[{'locator':'HTML #'+k+'；原PDF权页2/说明书物理6—7页','html_anchor':k,'source_path':str(HTML),'source_sha256':sha(HTML),
            'source_role':'dependent_claim' if k.startswith('cl') else 'description','evidence_excerpt':a[k]} for k in keys],
       'interpretation':meaning,'performance_status':'not_verified','verified_at':now,'old_value':None,'new_value':meaning,'change_reason':'原A权页/实施方式/图页定向复核；保留分支区别和未读字段',
       'pdf_visual_crosscheck':{'source_path':str(PDF),'source_sha256':sha(PDF),'physical_page':fig,'image_path':str(img),'image_sha256':sha(img),'checked_at':now,'verification_method':'manual_visual_readback_original_Chinese','scope':'原PDF物理2、6—7页和9—11图页；未宣称全文读取'}}
    s['features'][field]['observations'].append(o);s['features'][field]['support_status']='explicit';s['features'][field]['review_status']='partial';added.append(o)
s['review_completeness']['original_A_targeted_readback']={'checked_at':now,'source_path':str(PDF),'source_sha256':sha(PDF),'text_physical_pages_read':[2,6,7],'drawing_pages_read':[9,10,11],'full_text_rechecked':False,'new_fields':['capture','liquid_route','state_switch']}
m['updated_at']=now
print('*** Begin Patch\n*** Update File: '+str(P).replace('\\','/'))
print('\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(dumps(old).splitlines(),dumps(m).splitlines(),n=20))[2:]))
card=R/'evidence/CN115637570A_targeted_readback_20261001.md'
body='# CN115637570A 原A定向补查\n\n原PDF物理2页权项、6—7页实施方式与9—11页图1—6已读取。不是全文验收；相关B文本/资格pending。\n\n'
for o in added:body+='## '+o['stage']+' / '+o['embodiment_id']+'\n\n'+o['interpretation']+'\n\n'+o['claim_dependency']+'；定位：'+', '.join(e['html_anchor'] for e in o['evidence'])+'；图页：'+str(o['pdf_visual_crosscheck']['physical_page'])+'。\n\n'
body+='原PDF SHA '+sha(PDF)+'。其余未读字段不转0。\n'
print('*** Add File: '+str(card).replace('\\','/'));print('\n'.join('+'+l for l in body.splitlines()));print('*** End Patch')
