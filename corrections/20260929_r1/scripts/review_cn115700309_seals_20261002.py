"""Positive saved-text embodiment3 seals and connection structures; emit patches, never replace historical evidence."""
from pathlib import Path
import csv, datetime, difflib, hashlib, io, json, subprocess, sys
from local_source import read_anchors
H=Path(__file__).resolve().parents[3]; R=H/'corrections/20260929_r1'
M=R/'data/analysis_master.json'; C=R/'data/review_coverage.csv'
BASE='77ace912ef5a92eff2aecbfc616b40ac051f4bda'; PUB='CN115700309A'
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
                if k not in ['seals_connections']: assert f==y['features'][k]
                else:
                    assert not f['observations'] and f['support_status'] is None
                    assert y['features'][k]['prior_field']==f['prior_field']
                    assert len(y['features'][k]['observations'])==1 and y['features'][k]['support_status']=='explicit'
            assert y['review_completeness']['current_scope'][:-1]==x['review_completeness']['current_scope']
    obs=[o for s0 in m['samples'] for f in s0['features'].values() for o in f['observations']]
    assert len(obs)==134 and len({o['observation_id'] for o in obs})==134
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
        if x['publication']!=PUB or x['field'] not in ['seals_connections']: assert x==y
    rel=json.loads((H/'current_release.json').read_text(encoding='utf8'))
    assert rel['master_sha256']==sha(M) and rel['current_observations']==134
    assert all(z['sample_role']=='pending' and not z['review_completeness']['full_text_rechecked'] for z in m['samples'])
    assert not m['formal_statistics_allowed'] and not m['final_report_ready'] and not rel['project_completion_accepted']
    assert s['review_completeness']['saved_text_seals_connections_20261002']['original_pdf_checked'] is False
    print(dump({'verified':True,'baseline':BASE,'observations':134,'added':1,'old_133_unchanged':True,
      'other_13_candidates_unchanged':True,'all_legal_evidence_unchanged':True,'all_14_pending':True,
      'master_sha256':sha(M),'source_html_sha256':sha(SRC),'CSV_verified':True,'full_text_complete_count':0,
      'original_pdf_checked':False,'fields':['seals_connections'],'formal_statistics_allowed':False}))
    raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();s=target(m)
data=[
 ('seals_connections','embodiment3_outlet_bearing_flange',['p0137','p0138','p0139','p0140','p0141','p0142','p0149','p0150','p0151','p0152'],'620出水接头621与密封支撑部611、轴承631及法兰650','过滤水出口6102外延密封支撑611','出水接头转动密封及650/651接回水管路',
 ['621插入611，第一轴承631支撑转动','第一密封641封堵621与611间隙；第二密封642是进一步方案','法兰650插接定位并由螺钉固定，连接部651连接回水管路'],
 '实施例三作为实施例一进一步限定，p0137—0142明确621/611可转动密封、第一轴承631及第一密封641；第二密封642为进一步方案，不能当所有构型必需双密封。p0149—0152给650法兰、651回水连接、优选插接652及螺钉固定，属于连接结构而非用户拆管开盖维护流程。p0139保护轴承及避免未滤水旁路为文本目的/效果，未有防漏实测；不从螺钉和插接自动补维护步骤、无水环境已验证或长期密封保证。')]

for field,route,keys,obj,start,end,order,meaning in data:
    f=s['features'][field]; assert not f['observations']
    evidence=[{'locator':'保存HTML #'+k,'html_anchor':k,'evidence_excerpt':a[k],
      'source_role':'description_embodiment','subject_role':'this_invention_or_optional_embodiment',
      'source_path':str(SRC),'source_url':'https://patents.google.com/patent/'+PUB+'/zh','source_sha256':sha(SRC),
      'verified_at':now,'extraction_note':'Saved mirror, whitespace normalized; no original PDF checked.'} for k in keys]
    o={'observation_id':PUB+'-'+field+'-'+route+'-20261002','publication_id':PUB,'grant_publication_id':None,
      'sample_role':'pending','embodiment_id':route,'stage':field,'technical_feature':meaning,'object':obj,'start':start,'end':end,
      'boundary':'实施例三出水连接进一步限定，第二密封及插接保留可选/优选层级；不推维护顺序','operation_order':order,'support_status':'explicit',
      'review_status':'complete_in_stated_saved_text_scope','claim_dependency':'不适用：本条以所列说明书锚点为据，不并入授权独立项',
      'evidence':evidence,'interpretation':meaning,'performance_status':'not_verified','verified_at':now,
      'old_value':f['prior_field'],'new_value':meaning,'change_reason':'补此前空字段正向定位，限定保存文本；原件/法律资格缺口保持。',
      'removal_kind':None}
    f['observations'].append(o); f['review_status']='partial_saved_text_targeted'; f['support_status']='explicit'
    s['review_completeness']['current_scope'].append({'publication':PUB,'anchors':keys,'field':field,'at':now})
s['review_completeness']['saved_text_seals_connections_20261002']={'source_path':str(SRC),'source_sha256':sha(SRC),
  'read_anchors':['p0136', 'p0137', 'p0138', 'p0139', 'p0140', 'p0141', 'p0142', 'p0143', 'p0144', 'p0145', 'p0146', 'p0147', 'p0148', 'p0149', 'p0150', 'p0151', 'p0152', 'p0153', 'p0154', 'p0155', 'p0156'],'fields_added':['seals_connections'],
  'original_pdf_checked':False,'not_a_full_text_completion':True,'verified_at':now}
m['updated_at']=now
rows=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()));fields=rows[0].keys()
for row in rows:
    if row['publication']==PUB and row['field'] in ['seals_connections']:
        f=s['features'][row['field']];row.update(review_status=f['review_status'],support_status=f['support_status'],observation_count='1')
buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
print('*** Begin Patch\n'+patch(M,dump(m))+patch(C,'\ufeff'+buf.getvalue())+'*** End Patch')
