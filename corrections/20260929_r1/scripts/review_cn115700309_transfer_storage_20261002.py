"""Two positive saved-text fields; emit patches, never replace historical evidence."""
from pathlib import Path
import csv, datetime, difflib, hashlib, io, json, subprocess, sys
from local_source import read_anchors
H=Path(__file__).resolve().parents[3]; R=H/'corrections/20260929_r1'
M=R/'data/analysis_master.json'; C=R/'data/review_coverage.csv'
BASE='2c506f042e9f1873b4df21e195c143f61ea35dbd'; PUB='CN115700309A'
SRC=H/'team_package_20260928/sources/CN115700309A.html'
EXPECTED='38adeb9c51ddfdc9acf91a091a12cb2ec8ad16e78b346d0df3e5df27970066e5'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o): return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def baseline(path): return subprocess.check_output(['git','show',BASE+':'+path],cwd=H)
def patch(path,new):
    old=path.read_text(encoding='utf8'); lines=list(difflib.unified_diff(old.splitlines(True),new.splitlines(True),n=3))
    if lines: return '*** Update File: '+path.as_posix()+'\n'+''.join('@@\n' if line.startswith('@@') else line for line in lines[2:])
    return ''
assert sha(SRC)==EXPECTED
a=read_anchors(SRC); old=json.loads(baseline('corrections/20260929_r1/data/analysis_master.json'))
m=json.loads(M.read_text(encoding='utf8')); target=lambda z:next(s for s in z['samples'] if s['representative_publication']==PUB)
if '--verify' in sys.argv:
    s=target(m); prev=target(old)
    assert len(m['samples'])==14
    for x,y in zip(old['samples'],m['samples']):
        if x['representative_publication']!=PUB: assert x==y
        else:
            for k in x:
                if k not in ['features','review_completeness']: assert x[k]==y[k]
            for k,f in x['features'].items():
                if k not in ['transfer','storage']: assert f==y['features'][k]
                else:
                    assert not f['observations'] and f['support_status'] is None
                    assert y['features'][k]['prior_field']==f['prior_field']
                    assert len(y['features'][k]['observations'])==1 and y['features'][k]['support_status']=='explicit'
            assert y['review_completeness']['current_scope'][:-2]==x['review_completeness']['current_scope']
    obs=[o for s0 in m['samples'] for f in s0['features'].values() for o in f['observations']]
    assert len(obs)==131 and len({o['observation_id'] for o in obs})==131
    oldobs={o['observation_id']:o for s0 in old['samples'] for f in s0['features'].values() for o in f['observations']}
    assert all(next(o for o in obs if o['observation_id']==key)==v for key,v in oldobs.items())
    cache={}
    for o in obs:
        for e in o['evidence']:
            p=Path(e['source_path']); assert sha(p)==e['source_sha256']
            if e.get('html_anchor'):
                if str(p) not in cache: cache[str(p)]=read_anchors(p)
                assert e['evidence_excerpt'] in cache[str(p)][e['html_anchor']]
            else: assert sha(Path(e['page_image_path']))==e['page_image_sha256']
    for row in csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()):
        f=next(z for z in m['samples'] if z['representative_publication']==row['publication'])['features'][row['field']]
        assert row['review_status']==f['review_status'] and row['support_status']==(f['support_status'] or '')
        assert int(row['observation_count'])==len(f['observations'])
    before=list(csv.DictReader(baseline('corrections/20260929_r1/data/review_coverage.csv').decode('utf-8-sig').splitlines()))
    after=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()))
    for x,y in zip(before,after):
        if x['publication']!=PUB or x['field'] not in ['transfer','storage']: assert x==y
    rel=json.loads((H/'current_release.json').read_text(encoding='utf8'))
    assert rel['master_sha256']==sha(M) and rel['current_observations']==131
    assert all(z['sample_role']=='pending' and not z['review_completeness']['full_text_rechecked'] for z in m['samples'])
    assert not m['formal_statistics_allowed'] and not m['final_report_ready'] and not rel['project_completion_accepted']
    assert s['review_completeness']['saved_text_transfer_storage_20261002']['original_pdf_checked'] is False
    print(dump({'verified':True,'baseline':BASE,'observations':131,'added':2,'old_129_unchanged':True,
      'other_13_candidates_unchanged':True,'all_legal_evidence_unchanged':True,'all_14_pending':True,
      'master_sha256':sha(M),'source_html_sha256':sha(SRC),'CSV_verified':True,'full_text_complete_count':0,
      'original_pdf_checked':False,'fields':['transfer','storage'],'formal_statistics_allowed':False}))
    raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();s=target(m)
data=[
 ('transfer','embodiment1_waterborne_impurity',['p0073','p0109','p0111','p0113','p0127'],'滤面脱离的过滤杂质501及其携带水','过滤腔610中含杂质污水','经6103/670/排污管路240进入回收500',
  ['排污支路导通，含501污水经6103离腔','经过670：501与水通过，680被拦截','沿240进入500；普通排污可转网或保持静止'],
  '实施例一将剥离杂质501以水携带经排污口6103、670、240迁移至500，明确是固体随水迁移而非只写液体流动。670回收清洗粒680，允许501与水通过；680下一轮回浮复用不能冒称目标固体501回收。p0113关回水阀/开污阀保证带出，p0127排污可转或不转，不把此线强合并成每轮先末次漂洗空气压排、必旋转或干固体输送。'),
 ('storage','embodiment1_recovery_first_chamber',['p0117','p0118','p0119'],'已分离过滤杂质501','回收装置500第一腔531携杂质污水','第一腔531中过滤组件520上表面留存',
  ['含杂质污水进入531','水穿520进532，501留520上表面','供用户收集处理'],
  '实施例一进一步回收装置500把501留在第一腔531内520上表面，清水在第二腔532，支持处理前暂留。回收组件不同于主滤620，670另收680清洗颗粒，不能把它当滤渣存储器。p0117—0119仅支持此承载位置与用户收集意图，不推储存时长/容量、防漏密闭、长期干储或实际最终处置。')]

for field,route,keys,obj,start,end,order,meaning in data:
    f=s['features'][field]; assert not f['observations']
    evidence=[{'locator':'保存HTML #'+k,'html_anchor':k,'evidence_excerpt':a[k],
      'source_role':'description_embodiment','subject_role':'this_invention_or_optional_embodiment',
      'source_path':str(SRC),'source_url':'https://patents.google.com/patent/'+PUB+'/zh','source_sha256':sha(SRC),
      'verified_at':now,'extraction_note':'Saved mirror, whitespace normalized; no original PDF checked.'} for k in keys]
    o={'observation_id':PUB+'-'+field+'-'+route+'-20261002','publication_id':PUB,'grant_publication_id':None,
      'sample_role':'pending','embodiment_id':route,'stage':field,'technical_feature':meaning,'object':obj,'start':start,'end':end,
      'boundary':'实施例一主过滤模块及进一步回收模块分列；非最终处置边界','operation_order':order,'support_status':'explicit',
      'review_status':'complete_in_stated_saved_text_scope','claim_dependency':'不适用：本条以所列说明书锚点为据，不并入授权独立项',
      'evidence':evidence,'interpretation':meaning,'performance_status':'not_verified','verified_at':now,
      'old_value':f['prior_field'],'new_value':meaning,'change_reason':'补此前空字段正向定位，限定保存文本；原件/法律资格缺口保持。',
      'removal_kind':None}
    f['observations'].append(o); f['review_status']='partial_saved_text_targeted'; f['support_status']='explicit'
    s['review_completeness']['current_scope'].append({'publication':PUB,'anchors':keys,'field':field,'at':now})
s['review_completeness']['saved_text_transfer_storage_20261002']={'source_path':str(SRC),'source_sha256':sha(SRC),
  'read_anchors':['p0063','p0064','p0065','p0066','p0067','p0068','p0069','p0070','p0071','p0072','p0073','p0085','p0109','p0111','p0113','p0117','p0118','p0119','p0125','p0126','p0129','cl0001','cl0010'],'fields_added':['transfer','storage'],
  'original_pdf_checked':False,'not_a_full_text_completion':True,'verified_at':now}
m['updated_at']=now
rows=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()));fields=rows[0].keys()
for row in rows:
    if row['publication']==PUB and row['field'] in ['transfer','storage']:
        f=s['features'][row['field']];row.update(review_status=f['review_status'],support_status=f['support_status'],observation_count='1')
buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
print('*** Begin Patch\n'+patch(M,dump(m))+patch(C,'\ufeff'+buf.getvalue())+'*** End Patch')
