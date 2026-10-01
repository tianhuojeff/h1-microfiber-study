"""Saved-text effect claims are not measured results; emit patches, never replace historical evidence."""
from pathlib import Path
import csv, datetime, difflib, hashlib, io, json, subprocess, sys
from local_source import read_anchors
H=Path(__file__).resolve().parents[3]; R=H/'corrections/20260929_r1'
M=R/'data/analysis_master.json'; C=R/'data/review_coverage.csv'
BASE='73669dc0d0c6094d87333bd0f4c1e315253999bc'; PUB='CN115700309A'
SRC=H/'team_package_20260928/sources/CN115700309A.html'
EXPECTED='38adeb9c51ddfdc9acf91a091a12cb2ec8ad16e78b346d0df3e5df27970066e5'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o): return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def baseline(path): return subprocess.check_output(['git','show',BASE+':'+path],cwd=H)
def patch(path,new):
    old=path.read_text(encoding='utf8')
    if old==new: return ''
    if path==M:
        b=json.loads(old); c=json.loads(new)
        assert [x['sample_id'] for x in b['samples']]==[x['sample_id'] for x in c['samples']]
        for x,y in zip(b['samples'],c['samples']):
            if x['representative_publication']!=PUB: assert x==y
        prior=target(b)
        marker='      "representative_publication": "'+PUB+'",'
        sample_text='\n'.join('    '+line for line in dump(prior).strip().splitlines())
        assert old.count(sample_text)==1 and old.count(marker)==1
        lower=old[:old.index(marker)].count('\n')
        upper=old[:old.index(sample_text)+len(sample_text)].count('\n')+1
    before=old.splitlines(True); after=new.splitlines(True); body=[]
    for group in difflib.SequenceMatcher(None,before,after,autojunk=False).get_grouped_opcodes(3):
        i0,i1=group[0][1],group[-1][2]
        if path==M and i0>lower and i1<=upper:
            body.append('@@ '+marker+'\n')
        else:
            if path==M: assert all(i<lower for tag,a0,a1,_,_ in group if tag!='equal' for i in range(a0,max(a0+1,a1)))
            body.append('@@\n')
        for tag,a0,a1,b0,b1 in group:
            if tag=='equal': body.extend(' '+line for line in before[a0:a1])
            elif tag=='delete': body.extend('-'+line for line in before[a0:a1])
            elif tag=='insert': body.extend('+'+line for line in after[b0:b1])
            elif tag=='replace':
                body.extend('-'+line for line in before[a0:a1]);body.extend('+'+line for line in after[b0:b1])
    return '*** Update File: '+path.as_posix()+'\n'+''.join(body)
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
                if k not in ['performance']: assert f==y['features'][k]
                else:
                    assert not f['observations'] and f['support_status'] is None
                    assert y['features'][k]['prior_field']==f['prior_field']
                    assert len(y['features'][k]['observations'])==1 and y['features'][k]['support_status']=='explicit'
            assert y['review_completeness']['current_scope'][:-1]==x['review_completeness']['current_scope']
    obs=[o for s0 in m['samples'] for f in s0['features'].values() for o in f['observations']]
    assert len(obs)==135 and len({o['observation_id'] for o in obs})==135
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
        if x['publication']!=PUB or x['field'] not in ['performance']: assert x==y
    rel=json.loads((H/'current_release.json').read_text(encoding='utf8'))
    assert rel['master_sha256']==sha(M) and rel['current_observations']==135
    assert all(z['sample_role']=='pending' and not z['review_completeness']['full_text_rechecked'] for z in m['samples'])
    assert not m['formal_statistics_allowed'] and not m['final_report_ready'] and not rel['project_completion_accepted']
    assert s['review_completeness']['saved_text_performance_claims_20261002']['original_pdf_checked'] is False
    print(dump({'verified':True,'baseline':BASE,'observations':135,'added':1,'old_134_unchanged':True,
      'other_13_candidates_unchanged':True,'all_legal_evidence_unchanged':True,'all_14_pending':True,
      'master_sha256':sha(M),'source_html_sha256':sha(SRC),'CSV_verified':True,'full_text_complete_count':0,
      'original_pdf_checked':False,'fields':['performance'],'formal_statistics_allowed':False}))
    raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();s=target(m)
data=[
 ('performance','embodiment4_effect_claims_unverified',['p0187','p0190','p0195','p0211','p0212'],'实施例四末次漂洗空气压排效果主张与控制参数取值建议','原文无残液、避免细菌、减少启停、延长泵寿命的陈述','本范围实测/独立验证未知；保持文本主张',
 ['末次漂洗先停泵进气再开泵压排','原文主张无残留及泵寿命等效果；与中间漂洗允许不排净区分','参数可预先大量实验得出是建议，没有在这些锚点给实际试验记录'],
 '实施例四p0187/0212的完全排出、无污水残留、避免细菌滋生及延长循环泵寿命是文本效果主张，不转成残液量、菌数或寿命实测。p0190/0195写t1/t2与ΔH可预先通过大量实验得出，是取值建议，不能冒实际实验已执行、N/误差/测量方法或独立验证。p0211中间漂洗/洗涤可不排净，主张只保留末次漂洗边界。本次仅五锚点范围，不能断言整件完全没有其他数据；缺测量/独立可比证据在此范围保留未知。')]

for field,route,keys,obj,start,end,order,meaning in data:
    f=s['features'][field]; assert not f['observations']
    evidence=[{'locator':'保存HTML #'+k,'html_anchor':k,'evidence_excerpt':a[k],
      'source_role':'description_embodiment','subject_role':'this_invention_or_optional_embodiment',
      'source_path':str(SRC),'source_url':'https://patents.google.com/patent/'+PUB+'/zh','source_sha256':sha(SRC),
      'verified_at':now,'extraction_note':'Saved mirror, whitespace normalized; no original PDF checked.'} for k in keys]
    o={'observation_id':PUB+'-'+field+'-'+route+'-20261002','publication_id':PUB,'grant_publication_id':None,
      'sample_role':'pending','embodiment_id':route,'stage':field,'technical_feature':meaning,'object':obj,'start':start,'end':end,
      'boundary':'实施例四末次漂洗效果主张；本条五锚点不替代全文性能核验','operation_order':order,'support_status':'explicit',
      'review_status':'complete_in_stated_saved_text_scope','claim_dependency':'不适用：本条以所列说明书锚点为据，不并入授权独立项',
      'evidence':evidence,'interpretation':meaning,'performance_status':'not_verified','verified_at':now,
      'old_value':f['prior_field'],'new_value':meaning,'change_reason':'补此前空字段正向定位，限定保存文本；原件/法律资格缺口保持。',
      'removal_kind':None}
    f['observations'].append(o); f['review_status']='partial_saved_text_targeted'; f['support_status']='explicit'
    s['review_completeness']['current_scope'].append({'publication':PUB,'anchors':keys,'field':field,'at':now})
s['review_completeness']['saved_text_performance_claims_20261002']={'source_path':str(SRC),'source_sha256':sha(SRC),
  'read_anchors':['p0187','p0190','p0195','p0211','p0212'],'fields_added':['performance'],
  'original_pdf_checked':False,'not_a_full_text_completion':True,'verified_at':now}
m['updated_at']=now
rows=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()));fields=rows[0].keys()
for row in rows:
    if row['publication']==PUB and row['field'] in ['performance']:
        f=s['features'][row['field']];row.update(review_status=f['review_status'],support_status=f['support_status'],observation_count='1')
buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
print('*** Begin Patch\n'+patch(M,dump(m))+patch(C,'\ufeff'+buf.getvalue())+'*** End Patch')
