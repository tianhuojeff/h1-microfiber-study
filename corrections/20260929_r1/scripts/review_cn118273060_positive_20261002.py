"""Targeted positive source readback; no inferred whole-document absence."""
from pathlib import Path
import ast,csv,datetime,difflib,hashlib,io,json,subprocess,sys
from local_source import read_anchors
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json';C=R/'data/review_coverage.csv'
BASE='acaaf2a292d493a4d562a193f854bc3ecb6dd871';PUB='CN118273060A';SID='H1-F91644784'
SRC=H/'team_package_20260928/sources/CN118273060A.html';EXPECTED='3705139d2c2b2357c39e824de5ad1586fe93c2ef22a591a3fdb8a46a92b79bf5'
FIELDS=['capture','state_switch','seals_connections']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def baseline(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=H)
def target(m):
    pairs=[s for s in m['samples'] if s['sample_id']==SID and s['representative_publication']==PUB];assert len(pairs)==1
    return pairs[0]
helper=ast.parse((R/'scripts/review_cn115700309_performance_20261002.py').read_text(encoding='utf8'))
function=next(n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='patch')
exec(compile(ast.Module(body=[function],type_ignores=[]),'<unique-sample-patch>','exec'));original_patch=patch
def patch(p,new):
    prior=p.read_text(encoding='utf8')
    if prior==new:return ''
    if p==M:
        x=json.loads(prior);y=json.loads(new)
        assert [z['sample_id'] for z in x['samples']]==[z['sample_id'] for z in y['samples']]
        assert all(a==b for a,b in zip(x['samples'],y['samples']) if a['sample_id']!=SID)
        sample='\n'.join('    '+line for line in dump(target(x)).strip().splitlines())
        marker='      "representative_publication": "'+PUB+'",'
        assert prior.count(sample)==prior.count(marker)==1
        lower=prior[:prior.index(marker)].count('\n');upper=prior[:prior.index(sample)+len(sample)].count('\n')+1
    before=prior.splitlines(True);after=new.splitlines(True);body=[];jumped=False
    for group in difflib.SequenceMatcher(None,before,after,autojunk=False).get_grouped_opcodes(3):
        positions=[i for tag,a0,a1,_,_ in group if tag!='equal' for i in range(a0,max(a0+1,a1))]
        if p==M and any(i>=lower for i in positions):
            assert all(lower<i<upper for i in positions)
            body.append('@@ '+marker+'\n' if not jumped else '@@\n');jumped=True
        else:
            if p==M:assert all(i<lower for i in positions)
            body.append('@@\n')
        for tag,a0,a1,b0,b1 in group:
            if tag=='equal':body.extend(' '+line for line in before[a0:a1])
            if tag in ['delete','replace']:body.extend('-'+line for line in before[a0:a1])
            if tag in ['insert','replace']:body.extend('+'+line for line in after[b0:b1])
    return '*** Update File: '+p.as_posix()+'\n'+''.join(body)
assert sha(SRC)==EXPECTED
a=read_anchors(SRC);assert len(a)==263
old=json.loads(baseline('corrections/20260929_r1/data/analysis_master.json'));m=json.loads(M.read_text(encoding='utf8'));s=target(m)
read_ids=['p0004','p0005','p0006']+['p'+str(i).zfill(4) for i in range(62,70)]+['p'+str(i).zfill(4) for i in range(75,84)]+['p0192']+['p'+str(i).zfill(4) for i in range(107,125)]+['p0129','p0131','p0134','p0135','p0138','p0158','p0159','p0160','p0161','p0172','p0178','p0179','p0180']+['zh-cl'+str(i).zfill(4) for i in range(1,20)]
assert len(read_ids)==len(set(read_ids))
if '--verify' in sys.argv:
    assert len(m['samples'])==14
    for x,y in zip(old['samples'],m['samples']):
        assert x['sample_id']==y['sample_id']
        if x['sample_id']!=SID:assert x==y
        else:
            for k in x:
                if k not in ['features','review_completeness']:assert x[k]==y[k]
            for field,f in x['features'].items():
                if field not in FIELDS:assert f==y['features'][field]
                else:assert not f['observations'] and y['features'][field]['prior_field']==f['prior_field']
            assert y['review_completeness']['current_scope'][:-4]==x['review_completeness']['current_scope']
            for k in x['review_completeness']:
                if k!='current_scope':assert x['review_completeness'][k]==y['review_completeness'][k]
    obs=[o for z in m['samples'] for f in z['features'].values() for o in f['observations']];index={o['observation_id']:o for o in obs}
    assert len(obs)==len(index)==141
    prior=[o for z in old['samples'] for f in z['features'].values() for o in f['observations']]
    assert len(prior)==137 and all(index[o['observation_id']]==o for o in prior)
    cache={}
    for o in obs:
        for e in o['evidence']:
            p=Path(e['source_path']);assert sha(p)==e['source_sha256']
            if e.get('html_anchor'):
                if str(p) not in cache:cache[str(p)]=read_anchors(p)
                assert e['evidence_excerpt'] in cache[str(p)][e['html_anchor']]
            else:assert sha(Path(e['page_image_path']))==e['page_image_sha256']
    before=list(csv.DictReader(baseline('corrections/20260929_r1/data/review_coverage.csv').decode('utf-8-sig').splitlines()))
    after=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()));assert len(before)==len(after)==182
    for x,y in zip(before,after):
        if x['sample_id']!=SID or x['field'] not in FIELDS:assert x==y
        f=next(z for z in m['samples'] if z['sample_id']==y['sample_id'])['features'][y['field']]
        assert y['review_status']==f['review_status'] and y['support_status']==(f['support_status'] or '') and int(y['observation_count'])==len(f['observations'])
    rel=json.loads((H/'current_release.json').read_text(encoding='utf8'));assert rel['master_sha256']==sha(M) and rel['current_observations']==141
    assert not rel['project_completion_accepted'] and rel['phase']=='P2' and rel['status']=='draft'
    assert all(z['sample_role']=='pending' and not z['review_completeness']['full_text_rechecked'] for z in m['samples'])
    assert not m['formal_statistics_allowed'] and not m['final_report_ready']
    receipt=s['review_completeness']['saved_text_positive_fields_20261002']
    assert receipt['executor_read_anchor_ids']==read_ids
    assert sha(Path(receipt['readonly_agent_report_path']))==receipt['readonly_agent_report_sha256']
    print(dump({'verified':True,'baseline':BASE,'observations':141,'added':4,'old_137_unchanged':True,
     'other_13_candidates_unchanged':True,'all_legal_evidence_unchanged':True,'all_source_bytes_and_excerpts_verified':True,
     'source_html_sha256':sha(SRC),'master_sha256':sha(M),'CSV_verified':True,'fields':FIELDS,'executor_read_anchor_ids':read_ids,
     'executor_complete_saved_text_read':False,'readonly_agent_complete_saved_text_read':True,'original_pdf_checked':False,
     'drawings_checked':False,'numbering_conflict_preserved':['p0134 vs zh-cl0009: protrusion/groove 406/516'],
     'all_14_pending':True,'full_text_complete_count':0,'formal_statistics_allowed':False,
     'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()}));raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
data=[
 ('capture','filter_medium_and_optional_layers',['p0004','p0005','p0006','p0069','p0075','p0079','p0080','p0082','p0083','p0192','zh-cl0001','zh-cl0012','zh-cl0013','zh-cl0014'],
  '污染物留在过滤器组5的过滤介质50',
  '组5含介质50与支撑结构51、分隔脏/净区域，p0192称迫使水经过介质。多层500、开孔泡沫、聚氨酯及沿流孔径减小是可选；权12与13分别任一前项，14只依13，不拼成全必要组合。对象包括微塑料与其他污染物，不把天然纤维全判塑料；孔径/截留效果不写实测。',
  '权1基本分区；权12/13各依前项之一，权14→13，不自动绑定12'),
 ('state_switch','mechanical_two_angle_lock',['p0179','p0180','zh-cl0016'],
  '止动7控制盖4与滤组5轴向移动',
  '止动构件7锁定时阻止盖4和组5轴向移动，解锁时允许沿X-X抽插；优选旋转元件两个角位置。机械锁状态有明文，不补停泵/排空/开盖联锁或自动控制器，不要求先排干。',
  '权16依前项之一，机械止动限定；两角位置为说明书优选'),
 ('state_switch','optional_pressure_notice',['p0062','p0063','p0064','p0065','p0066','p0067','p0068'],
  '可选压力传感器组与命令面板',
  '另一优选实施方式检测压差或下游水压并向命令单元发信号；p0065—67列将堵、闭塞及闭塞且洗衣机停止信号，p0068灯/显示通知维护。只是该可选方案，不变全部构型必须自动停机；两个预设值无实测数值，不与机械锁7拼成强制联锁链。',
  '所列说明书另一优选实施方式；不冒授权项必要条件'),
 ('seals_connections','centering_seals_with_numbering_conflict',['p0107','p0108','p0109','p0112','p0113','p0114','p0117','p0120','p0124','p0129','p0131','p0134','p0178','zh-cl0001','zh-cl0005','zh-cl0009'],
  '41经401接511，封头板510/帽40及T1—T4各界面',
  '41穿401与定心511接合促510/40密封，组5与盖4可共同沿轴插入。T1内侧、T2外侧、T3盖/边缘313、T4组/盖与壳壁是不同界面；螺纹或卡口、轴向或径向等可选方式分开，不要求全部叠加，不补防漏实测。保存描述p0134突起406/槽516对权9槽406/突起516的文字矛盾，未有原PDF/图不能默改编号。',
  '权1接合；权5螺纹或卡口同级选项；权9原编号与描述冲突保留')]
for field,route,quoted,obj,meaning,dependency in data:
    f=s['features'][field]
    ev=[{'locator':'保存HTML #'+k,'html_anchor':k,'evidence_excerpt':a[k],'source_role':'claim' if k.startswith('zh-cl') else 'description_embodiment',
     'subject_role':'this_invention_or_optional_embodiment','source_path':str(SRC),'source_url':'https://patents.google.com/patent/'+PUB+'/zh',
     'source_sha256':sha(SRC),'verified_at':now,'extraction_note':'Saved mirror anchor; no original PDF/figure read, no physical-page substitution.'} for k in quoted]
    o={'observation_id':PUB+'-'+field+'-'+route+'-20261002','publication_id':PUB,'grant_publication_id':None,'sample_role':'pending',
     'embodiment_id':route,'stage':field,'technical_feature':meaning,'object':obj,'start':'原文所列状态/结构','end':'范围内技术关系，非已验证性能',
     'boundary':'只读所列保存文本锚点；互斥可选结构与独立控制路径分开','operation_order':[],
     'support_status':'explicit','review_status':'complete_in_stated_saved_text_scope','claim_dependency':dependency,'evidence':ev,
     'interpretation':meaning,'performance_status':'not_verified','verified_at':now,'old_value':f['prior_field'],'new_value':meaning,
     'change_reason':'补空字段正向定位；原值/法律/未知门槛保持，编号冲突不默修。','removal_kind':None}
    if field=='seals_connections':o['source_conflicts']=[{'description_anchor':'p0134','claim_anchor':'zh-cl0009','conflict':'406/516突起与槽对换','resolution':'unresolved; original PDF/figures pending'}]
    f['observations'].append(o);f['review_status']='partial_saved_text_targeted';f['support_status']='explicit'
    s['review_completeness']['current_scope'].append({'publication':PUB,'anchors':quoted,'field':field,'at':now})
s['review_completeness']['saved_text_positive_fields_20261002']={'source_path':str(SRC),'source_sha256':sha(SRC),'executor_read_anchor_ids':read_ids,
 'fields_added':FIELDS,'original_pdf_checked':False,'drawings_checked':False,'executor_complete_saved_text_read':False,
 'readonly_agent_report_path':str(H.parent/'work_logs/artifacts/controller-20261002/下一原件抽查/CN118273060A/只读审核.md'),
 'readonly_agent_report_sha256':'12763534b7661e5065ad5f7a56ded7981414ee7c151aa6852f98cfc6564ac620',
 'readonly_agent_read_anchors':['p0001-p0244','zh-cl0001-zh-cl0019'],'not_a_full_text_completion':True,'verified_at':now}
m['updated_at']=now
rows=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()));cols=rows[0].keys()
for row in rows:
    if row['sample_id']==SID and row['publication']==PUB and row['field'] in FIELDS:
        f=s['features'][row['field']];row.update(review_status=f['review_status'],support_status=f['support_status'],observation_count=str(len(f['observations'])))
buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=cols,lineterminator='\n');w.writeheader();w.writerows(rows)
print('*** Begin Patch\n'+patch(M,dump(m))+patch(C,'\ufeff'+buf.getvalue())+'*** End Patch')
