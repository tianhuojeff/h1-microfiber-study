"""Scoped embodiment-four chamber drainage, saved HTML only."""
from pathlib import Path
import csv,datetime,difflib,hashlib,io,json,subprocess,sys
from local_source import read_anchors
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json';C=R/'data/review_coverage.csv'
BASE='c719ea6197414fc5d629f35ce89f80e708aed79f';PUB='CN115700309A';FIELD='chamber_drainage'
SRC=H/'team_package_20260928/sources/CN115700309A.html';EXPECTED='38adeb9c51ddfdc9acf91a091a12cb2ec8ad16e78b346d0df3e5df27970066e5'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def gitdata(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=H)
def patch(p,t):
    d=list(difflib.unified_diff(p.read_text(encoding='utf8').splitlines(True),t.splitlines(True),n=3))
    return '*** Update File: '+p.as_posix()+'\n'+''.join('@@\n' if x.startswith('@@') else x for x in d[2:]) if d else ''
assert sha(SRC)==EXPECTED
a=read_anchors(SRC);old=json.loads(gitdata('corrections/20260929_r1/data/analysis_master.json'));m=json.loads(M.read_text(encoding='utf8'))
def target(z):return next(s for s in z['samples'] if s['representative_publication']==PUB)
if '--verify' in sys.argv:
    for x,y in zip(old['samples'],m['samples']):
        if x['representative_publication']!=PUB:assert x==y
        else:
            for k in x:
                if k not in ['features','review_completeness']:assert x[k]==y[k]
            for k,v in x['features'].items():
                if k!=FIELD:assert v==y['features'][k]
                else:assert not v['observations'] and len(y['features'][k]['observations'])==1 and v['prior_field']==y['features'][k]['prior_field']
            assert y['review_completeness']['current_scope'][:-1]==x['review_completeness']['current_scope']
    obs=[o for s in m['samples'] for f in s['features'].values() for o in f['observations']]
    assert len(obs)==127 and len({o['observation_id'] for o in obs})==127
    cache={}
    for o in obs:
        for e in o['evidence']:
            p=Path(e['source_path']);assert sha(p)==e['source_sha256']
            if e.get('html_anchor'):
                if str(p) not in cache:cache[str(p)]=read_anchors(p)
                assert e['evidence_excerpt'] in cache[str(p)][e['html_anchor']]
            else:assert sha(Path(e['page_image_path']))==e['page_image_sha256']
    for row in csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()):
        f=next(s for s in m['samples'] if s['representative_publication']==row['publication'])['features'][row['field']]
        assert row['review_status']==f['review_status'] and row['support_status']==(f['support_status'] or '') and int(row['observation_count'])==len(f['observations'])
    rel=json.loads((H/'current_release.json').read_text(encoding='utf8'));assert rel['current_observations']==127 and rel['master_sha256']==sha(M)
    assert all(s['sample_role']=='pending' and not s['review_completeness']['full_text_rechecked'] for s in m['samples'])
    assert not m['formal_statistics_allowed'] and not m['final_report_ready'] and not rel['project_completion_accepted']
    print(dump({'verified':True,'baseline':BASE,'observations':127,'added':1,'old_126_unchanged':True,
      'other_13_candidates_unchanged':True,'all_legal_evidence_unchanged':True,'all_14_pending':True,'master_sha256':sha(M),
      'source_html_sha256':sha(SRC),'field':FIELD,'executor_read_anchors':'p0177—p0196,p0200,p0205,p0211,p0212',
      'original_pdf_checked':False,'full_text_complete_count':0,'CSV_verified':True,'formal_statistics_allowed':False}));raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();s=target(m);f=s['features'][FIELD];assert not f['observations']
keys=['p0182','p0183','p0185','p0186','p0187','p0188','p0189','p0192','p0196','p0200','p0205','p0211','p0212']
meaning='实施例四在停泵后利用管路水重力回落形成空气，过滤腔610因回水阀231及排污阀241关闭仍存水；滤机构旋转剥屑后，启泵并开排污阀把管路空气压入过滤腔，含线屑污水经排污口6103排出。第二条件切断循环进水以免重新灌满；可切换外排管路或关闭泵。时间t1/t2与水位H1/H2为替代条件，最后漂洗停启泵排净与中间漂洗/洗涤可持续泵冲洗分开。完全排出、无残留及寿命延长是文本效果主张，未实测；对象是腔游离污水，不能改成滤渣压干/含水率。'
o={'observation_id':PUB+'-'+FIELD+'-embodiment4_air_pressure-20261002','publication_id':PUB,'grant_publication_id':None,
 'sample_role':'pending','embodiment_id':'embodiment4_air_pressure','stage':FIELD,'technical_feature':meaning,
 'object':'过滤腔610内携带线屑的游离污水','start':'过滤腔610闭阀保留的水','end':'排污口6103→排污管路240（本次不追加最终终点）',
 'boundary':'过滤腔边界→排污管路；非固体脱水或最终处置边界','operation_order':['停泵后管路水回落形成空气，闭阀使过滤腔留水','滤机构转动剥屑入水','第一条件达到：启泵并开排污阀，空气压入并排出含屑污水','第二条件达到：切断循环进水，避免重注；时间或水位条件分开'],
 'support_status':'explicit','review_status':'complete_in_stated_saved_text_scope','claim_dependency':'不适用：实施例四所列保存说明书锚点，不自动并入独立权项',
 'evidence':[{'locator':'保存HTML #'+k,'html_anchor':k,'evidence_excerpt':a[k],'source_role':'description_embodiment',
   'subject_role':'this_invention_or_optional_embodiment','source_path':str(SRC),'source_url':'https://patents.google.com/patent/'+PUB+'/zh',
   'source_sha256':sha(SRC),'verified_at':now} for k in keys],
 'interpretation':meaning,'performance_status':'text_claim_not_measured','verified_at':now,'old_value':f['prior_field'],
 'new_value':meaning,'change_reason':'此前空字段补正向腔排液，保存文本定向范围；未知不转零、实施例分支不合并。','removal_kind':None}
f['observations'].append(o);f['review_status']='partial_saved_text_targeted';f['support_status']='explicit'
s['review_completeness']['current_scope'].append({'publication':PUB,'field':FIELD,'anchors':keys,'at':now})
s['review_completeness']['saved_text_drainage_20261002']={'read_anchors':['p'+str(n).zfill(4) for n in range(177,197)]+['p0200','p0205','p0211','p0212'],'original_pdf_checked':False,'full_text_read_claimed':False,'verified_at':now}
m['updated_at']=now
rows=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()));names=rows[0].keys()
for row in rows:
    if row['publication']==PUB and row['field']==FIELD:row.update(review_status=f['review_status'],support_status='explicit',observation_count='1')
buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=names,lineterminator='\n');w.writeheader();w.writerows(rows)
print('*** Begin Patch\n'+patch(M,dump(m))+patch(C,'\ufeff'+buf.getvalue())+'*** End Patch')
