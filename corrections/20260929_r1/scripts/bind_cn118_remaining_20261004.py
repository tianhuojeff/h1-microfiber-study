"""Original capture field binding, preserving all accepted observations."""
from pathlib import Path
import ast,datetime,difflib,hashlib,json,subprocess,sys
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='6cb6d617166280b39eaa57edf14c7a4768c3c804';SID='H1-F91644784';PUB='CN118273060A';KEY='original_remaining_field_bindings_20261004'
PAGES=[];PDF=H/'patents/CN118273060A.pdf';EXPECTED='fcfde50da413b25f2b5dadcca389a44fc41a3aa682027825617ef51c309be80d'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def baseline(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=H)
def target(m):
    out=[x for x in m['samples'] if x['sample_id']==SID and x['representative_publication']==PUB];assert len(out)==1
    return out[0]
old=json.loads(baseline('corrections/20260929_r1/data/analysis_master.json'));m=json.loads(M.read_text(encoding='utf8'))
matches=[s for s in m['samples'] if s['sample_id']==SID and s['representative_publication']==PUB];assert len(matches)==1;s=matches[0]
assert sha(PDF)==EXPECTED
images=[R/'evidence'/('CN118273060A_body_20261003-'+str(i)+'.png') for i in PAGES];assert all(p.is_file() for p in images)
def patch(p,new):
    prior=p.read_text(encoding='utf8');a=json.loads(prior);b=json.loads(new)
    assert all(x==y for x,y in zip(a['samples'],b['samples']) if x['sample_id']!=SID)
    second='\n'.join('    '+line for line in dump(target(b)).strip().splitlines())
    marker='      "representative_publication": "'+PUB+'",'
    assert prior.count(marker)==1
    start=prior.rfind('\n    {',0,prior.index(marker))+1
    decoded,length=json.JSONDecoder().raw_decode(prior[start+4:])
    assert decoded==target(a)
    first=prior[start:start+4+length]
    assert prior.count(first)==prior.count(marker)==1
    if prior[start+4+length:start+5+length]==',':
        first+=',';second+=','
    body=['@@\n','-  "updated_at": '+json.dumps(a['updated_at'])+',\n','+  "updated_at": '+json.dumps(b['updated_at'])+',\n']
    before=(first+'\n').splitlines(True);after=(second+'\n').splitlines(True);started=False
    for group in difflib.SequenceMatcher(None,before,after,autojunk=False).get_grouped_opcodes(3):
        body.append('@@ '+marker+'\n' if not started else '@@\n');started=True
        for tag,a0,a1,b0,b1 in group:
            if tag=='equal':body.extend(' '+line for line in before[a0:a1])
            if tag in ['delete','replace']:body.extend('-'+line for line in before[a0:a1])
            if tag in ['insert','replace']:body.extend('+'+line for line in after[b0:b1])
    return '*** Update File: '+p.as_posix()+'\n'+''.join(body)

import re
from pypdf import PdfReader
FIELDS={
'cleaning':([165,186,189],[],'具体清洗/剥离/反洗程序未定位；可取出维护更换不补介质再生。','not_located_in_full_original_scope',[26]),
'transfer':([119,174,189],[16],'含物滤组随盖轴向移动为载体移出；未定位松散截留固体卸下后转独立容器。','not_located_in_full_original_scope',[26]),
'chamber_drainage':([88,166,174],[],'301/302为正常液路；166跨页水交叉作用措辞保持，不补维护腔排空、去向或先排空联锁。','not_located_in_full_original_scope',list(range(15,27))),
'solids_dewatering':([37,70,187],[],'滚筒离心和介质过滤对象分别；未定位截留固体压滤/离心去夹带水及含水率实测。','not_located_in_full_original_scope',[39,40,41]),
'liquid_route':([39,40,54,55,56],[17],'950可排放或再循环；951/952分脏净。泵前后、阀在第一/第二段、各出口为分别选项；95121原字对图9521冲突保留，不判零颗粒。','explicit_original_optional_routes',list(range(15,26))),
'storage':([70,135,140,144],[],'组5介质50的含物暂留边界；409盒状接合支撑件不判集渣容器；未定位独立松散固体长期干储。','in_filter_carrier_boundary_only',[26,39,40,41]),
'removal':([119,165,174,180,181,189],[16],'止动7解锁后盖4和组5轴向抽移；前侧/上侧位置各可选，不等同独立集渣盒或安全处置。','explicit_original_carrier_removal',[26]),
'state_switch':([57,60,61,62,63,174,175],[16],'机械两角锁解锁与另一优选压差/压力信号通知分开；闭塞且停机是示例，不拼强制停泵排空开盖联锁。','explicit_original_distinct_optional_states',[26,34,35]),
'seals_connections':([103,104,107,109,115,118,124,126,173],[1,5],'41经401接511促510/40密封；T1-T4界面和不同轴径向位置、螺纹或卡口各可选，编号矛盾不默修，不补防漏实测。','explicit_original_optional_connections',list(range(27,39))),
'performance':([179,180,181,184,186,190],[],'紧凑、维护/抽插便利、减力、环境影响为作者文本主张；原全文未定位量化截留/装配力协议、N、误差或独立验证。','text_claim_only',[26]),
'endpoint':([186,189],[],'维护更换与抽移明确；原技术全文及图未定位收集固体/含物滤材垃圾分类、回收、销毁或安全最终去向。','not_located_in_full_original_scope',[26]),
'carrier_conditioning':([36,165],[],'洗衣烘干功能对象非介质50；未定位使用后介质自身排水、干燥或调理程序，不由过滤或拆卸推出已干。','not_located_in_full_original_scope',[39,40,41])
}
reader=PdfReader(str(PDF));texts=[p.extract_text() or '' for p in reader.pages]
assert len(texts)==41
clean=[]
for t in texts[3:14]:
 t=re.sub(r'说\s*明\s*书\s*\d+/11\s*页\s*\d+\s*CN\s*118273060\s*A\s*\d+','',t)
 clean.append(t)
whole='\n'.join(clean)
parts=list(re.finditer(r'\[(\d{4})\]',whole));paras={}
for j,z in enumerate(parts):
 n=int(z.group(1));e=parts[j+1].start() if j+1<len(parts) else len(whole)
 assert n not in paras
 paras[n]=re.sub(r'\s+','',whole[z.end():e])
assert sorted(paras)==list(range(1,240))
def refs(ns):
 return [{'printed_paragraph':n,'physical_pages':([11,12] if n==166 else [i+1 for i,t in enumerate(texts) if ('['+str(n).zfill(4)+']') in t]),
          'evidence_excerpt':paras[n][:180], 'excerpt_is_prefix_of_original_paragraph':True,
          'source_role':'description_of_this_invention_or_optional_embodiment'} for n in ns]
image_map={}
for k,v in s['review_completeness'].items():
 if isinstance(v,dict):
  for im in v.get('rendered_pages',[]):
   assert sha(Path(im['path']))==im['sha256'];image_map[im['physical_page']]=im
assert set(range(2,42))<=set(image_map)
def make_bindings():
 return {f:{'observation_ids_preserved':[o['observation_id'] for o in s['features'][f]['observations']],
 'original_paragraph_evidence':refs(ns),'original_claims':cs,'original_figure_physical_pages':fs,
 'judgment':jud,'support_status':support,
 'reviewed_scope':'Published A description0001-0239/claims1-19/figures all27pages read Oct3; no new exhaustive visual reading claimed.',
 'availability_judgment':('unknown' if support=='not_located_in_full_original_scope' else support),
 'claim_role_note':'Claims and optional descriptions separately scoped; no counterpart/granted claim borrowing.'}
 for f,(ns,cs,jud,support,fs) in FIELDS.items()}
if '--verify' in sys.argv:
 assert [x['sample_id'] for x in old['samples']]==[x['sample_id'] for x in m['samples']]
 for x,y in zip(old['samples'],m['samples']):
  if x['sample_id']!=SID:assert x==y
  else:
   for k in x:
    if k!='review_completeness':assert x[k]==y[k]
   assert {k:v for k,v in y['review_completeness'].items() if k!=KEY}==x['review_completeness']
 for k in old:
  if k not in ['updated_at','samples']:assert old[k]==m[k]
 rc=s['review_completeness'][KEY]
 assert rc['source_sha256']==sha(PDF) and rc['bindings']==make_bindings()
 assert all('说明书' not in e['evidence_excerpt'] and 'CN118273060A' not in e['evidence_excerpt'] for f in rc['bindings'].values() for e in f['original_paragraph_evidence'])
 assert rc['bindings']['chamber_drainage']['original_paragraph_evidence'][1]['physical_pages']==[11,12]
 claim_text='\n'.join(texts[1:3]);claim_ids=[int(z) for z in re.findall(r'(?:^|\n)\s*(\d{1,2})\s*\.',claim_text)]
 assert claim_ids==list(range(1,20)) and all(c in claim_ids for f in rc['bindings'].values() for c in f['original_claims'])
 assert set(rc['bindings'])==set(s['features'])-{'capture'}
 assert rc['cumulative_original_visual_pages']==list(range(1,42))
 assert rc['cumulative_drawing_visual_pages']==list(range(15,42))
 assert not rc['new_visual_reading_claimed']
 assert (R/'data/review_coverage.csv').read_bytes()==baseline('corrections/20260929_r1/data/review_coverage.csv')
 assert sum(len(f['observations']) for z in m['samples'] for f in z['features'].values())==168
 assert all(z['sample_role']=='pending' for z in m['samples'])
 assert all(z['review_completeness']['full_text_rechecked']==x['review_completeness']['full_text_rechecked'] for x,z in zip(old['samples'],m['samples']))
 assert not m['formal_statistics_allowed'] and not m['final_report_ready']
 rel=json.loads((H/'current_release.json').read_bytes())
 assert rel['master_sha256']==sha(M) and rel['current_observations']==168
 print(dump({'verified':True,'baseline':BASE,'observations':168,'added_observations':0,
 'bindings_added':12,'all13_fields_original_bound':True,'all_old_features_and_observations_unchanged':True,
 'other13_complete_objects_unchanged':True,'all_legal_unchanged':True,'CSV_bytes_unchanged':True,
 'master_sha256':sha(M),'source_pdf_sha256':sha(PDF),'239_original_paragraph_ids_verified':True,
 'original_paragraph_excerpt_checks':sum(len(x[0]) for x in FIELDS.values()),
 'existing_original_render_hashes_verified':len(image_map),'all27_drawing_pages_previously_read':True,
 'new_visual_reading_claimed':False,'full_text_flags_not_automatically_promoted':True,
 'failure_notes':['Oversized field-read output and first displayed generator output truncated; neither applied. Compact field projection/page blocks reread fully. Preview found overescaped page-header cleanup and background paragraph2 role; generator corrected before first data apply, then real-byte QA from first item.'],
 'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
 'reset_consumed':False}));raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
s['review_completeness'][KEY]={'source_path':str(PDF),'source_sha256':sha(PDF),'at':now,
 'source_text_pages_revisited_this_transaction':[3,7,9,10,11,12,13],
 'cumulative_original_visual_pages':list(range(1,42)),'cumulative_drawing_visual_pages':list(range(15,42)),
 'new_visual_reading_claimed':False,'bindings':make_bindings(),
 'capture_prior_binding':'original_capture_binding_20261003',
 'original_field_binding_complete':True,
 'original_technical_acceptance_pending_separate_logic':True,
 'existing_conflicts_preserved':'406/516 role;52 versus512/513;medium2 versus50;pump560 versus960;route95121 versus9521',
 'previous_full_visual_receipt':'corrections/20260929_r1/QA/CN118273060A_original_body_20261003.json',
 'next_action':'Separately accept candidate technical full-text scope with scene/coverage/QA invariants; legal pending and formal statistics gates unchanged.'}
m['updated_at']=now
print('*** Begin Patch\n'+patch(M,dump(m))+'*** End Patch')

