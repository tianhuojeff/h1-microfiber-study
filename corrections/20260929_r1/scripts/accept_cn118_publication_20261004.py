"""Original capture field binding, preserving all accepted observations."""
from pathlib import Path
import ast,datetime,difflib,hashlib,json,subprocess,sys
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='2e568c70565cb1daa47d17510a6bba2b76579cd8';SID='H1-F91644784';PUB='CN118273060A';KEY='publication_technical_acceptance'
PAGES=[];PDF=H/'patents/CN118273060A.pdf';EXPECTED='fcfde50da413b25f2b5dadcca389a44fc41a3aa682027825617ef51c309be80d'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
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

import re,copy,importlib.util
from pypdf import PdfReader
RECORD='original_remaining_field_bindings_20261004';STATUS='accepted_in_original_published_scope'
record=s['review_completeness'][RECORD]
body_record=s['review_completeness']['original_remaining_body_visual_20261003']
assert body_record['cumulative_original_visual_pages']==list(range(1,42)) and body_record['cumulative_drawing_visual_pages']==list(range(15,42))
assert body_record['all_original_pages_visually_read'] and body_record['all_drawings_visually_read']
text_record=s['review_completeness']['original_numbering_conflict_review_20261003']
assert text_record['claims_text_read']==[1,19] and text_record['printed_description_paragraphs_read']==[1,239]
assert record['source_sha256']==sha(PDF) and set(record['bindings'])==set(s['features'])-{'capture'}
for f,b in record['bindings'].items():
 assert b['observation_ids_preserved']==[o['observation_id'] for o in s['features'][f]['observations']]
capture=s['review_completeness']['original_capture_binding_20261003']
assert capture['old_observation_ids_preserved']==[o['observation_id'] for o in s['features']['capture']['observations']]
for v in s['review_completeness'].values():
 if isinstance(v,dict):
  for im in v.get('rendered_pages',[]):assert sha(im['path'])==im['sha256']
previous_qa=R/'QA/CN118273060A_remaining_original_bindings_20261004.json';pq=json.loads(previous_qa.read_bytes())
assert pq['verified'] and pq['all13_fields_original_bound'] and pq['existing_original_render_hashes_verified']==40
reader=PdfReader(str(PDF));assert len(reader.pages)==41
body='\n'.join(re.sub(r'说\s*明\s*书\s*\d+/11\s*页\s*\d+\s*CN\s*118273060\s*A\s*\d+','',p.extract_text() or '') for p in reader.pages[3:14])
par=list(re.finditer(r'\[(\d{4})\]',body));paras={int(z.group(1)):re.sub(r'\s+','',body[z.end():(par[j+1].start() if j+1<len(par) else len(body))]) for j,z in enumerate(par)}
assert sorted(paras)==list(range(1,240))
scene={'classification':'laundry_water_mixed_synthetic_natural_fibres_including_microplastics',
 'review_status':STATUS,'publication_id':PUB,'source_path':str(PDF),'source_sha256':sha(PDF),
 'boundary':'本件明确洗衣滚筒出水，合成纤维及天然棉/麻/毛织物均为对象；微塑料属于污染物之一，不把所有天然或衣物纤维自动判塑料。',
 'basis':[{'printed_paragraph':n,'physical_page':4,'evidence_excerpt':paras[n][:220],
 'source_role':'description_of_this_invention_or_optional_use'} for n in [3,4,5]]}
def import_current_validator():
 spec=importlib.util.spec_from_file_location('h1_current_acceptance_validator',R/'scripts/verify_and_export.py')
 mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod
 sys.path.insert(0,str(R/'scripts'));spec.loader.exec_module(mod);return mod
if '--verify' in sys.argv:
 for x,y in zip(old['samples'],m['samples']):
  if x['sample_id']!=SID:assert x==y
  else:
   for k in x:
    if k not in ['scene_material','publications','review_completeness','features']:assert x[k]==y[k]
   for f in x['features']:
    assert x['features'][f]['observations']==y['features'][f]['observations']
    assert {k:v for k,v in y['features'][f].items() if k!='review_status'}=={k:v for k,v in x['features'][f].items() if k!='review_status'}
   rc=y['review_completeness'];assert rc['full_text_rechecked'] and rc[KEY]['scope']=='representative_published_document_only'
   assert rc['current_scope'][:-1]==x['review_completeness']['current_scope']
   assert {k:v for k,v in rc.items() if k not in ['full_text_rechecked','full_text_rechecked_scope',KEY,'current_scope']}=={k:v for k,v in x['review_completeness'].items() if k not in ['full_text_rechecked','current_scope']}
 assert s['scene_material']==scene
 new_csv=(R/'data/review_coverage.csv').read_bytes().splitlines(keepends=True)
 old_csv=baseline('corrections/20260929_r1/data/review_coverage.csv').splitlines(keepends=True)
 assert len(new_csv)==len(old_csv)
 assert all(x==y for x,y in zip(old_csv,new_csv) if PUB.encode() not in x)
 for k in old:
  if k not in ['updated_at','samples']:assert old[k]==m[k]
 v=import_current_validator();q=v.validate(m)
 assert q['observations']==168 and q['full_text_complete_count']==2 and set(q['accepted_representative_publications'])=={PUB,'CN117702432A'}
 bad=copy.deepcopy(s);bad['review_completeness'].pop(KEY)
 try:v.validate_acceptance(bad)
 except AssertionError:pass
 else:raise AssertionError('flag without receipt was accepted')
 bad=copy.deepcopy(s);bad['scene_material']['classification']=None
 try:v.validate_acceptance(bad)
 except AssertionError:pass
 else:raise AssertionError('missing scene was accepted')
 bad=copy.deepcopy(s);bad['review_completeness'][KEY]['source_sha256']='0'*64
 try:v.validate_acceptance(bad)
 except AssertionError:pass
 else:raise AssertionError('wrong original source hash accepted')
 q.update({'baseline':BASE,'target':PUB,'all_old168_observations_unchanged':True,'other13_whole_objects_unchanged':True,
 'all_legal_unchanged':True,'only13_target_feature_review_statuses_changed':True,'original_PDF_pages_figures_fields':'41pages/27drawingpages/13fields',
 'scope':'representative published A only; not family/granted scope/current status','semantic_gate_tests':'pending legal accepted; missing receipt/scene/wrong original hash rejected',
 'old_invariant':'Before independent publication acceptance all full-text flags false',
 'new_invariant':'A true flag requires explicit complete published-document receipt, original field bindings and scene; other samples untouched. Legal/official statistics remain independent.',
 'historical_QA_and_oneoff_scripts_unchanged':True,'non_target_CSV_rows_exact_bytes_unchanged':True,'reset_consumed':False,
 'failures_before_acceptance':[]})
 print(dump(q));raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
oldrc=s['review_completeness'];oldstatuses={f:v['review_status'] for f,v in s['features'].items()}
oldrc['full_text_rechecked']=True;oldrc['full_text_rechecked_scope']='representative_published_document_only'
oldrc[KEY]={'accepted':True,'publication':PUB,'scope':'representative_published_document_only','accepted_at':now,
 'source_path':'patents/CN118273060A.pdf','source_sha256':sha(PDF),'source_page_count':41,
 'text_pages_read':list(range(1,42)),'visual_pages_read':list(range(1,42)),'description_paragraphs':[1,239],'claims':[1,19],'drawing_pages_read':list(range(15,42)),
 'field_bindings':{f:{'review_record_key':('original_capture_binding_20261003' if f=='capture' else RECORD),'binding_key':f} for f in s['features']},
 'previous_review_QA':str(previous_qa.relative_to(H)),'previous_review_QA_sha256':sha(previous_qa),
 'previous_feature_review_statuses':oldstatuses,'previous_scene':s['scene_material'],
 'prior_evidence_preserved':True,'legal_qualification_granted_by_this_acceptance':False,
 'does_not_accept':['family member completeness','current legal status','measured performance','formal statistics','final report','whole project completion']}
oldrc['current_scope'].append({'publication':PUB,'scope':'representative_published_document_only','acceptance_record':KEY,'at':now})
s['scene_material']=scene
for p in s['publications']:
 if p['publication_id']==PUB:
  p['previous_review_status']=p['review_status'];p['review_status']=STATUS
  p['original_source_path']='patents/CN118273060A.pdf';p['original_source_sha256']=sha(PDF)
  p['technical_acceptance_record']=KEY
for f in s['features'].values():f['review_status']=STATUS
m['updated_at']=now
print('*** Begin Patch\n'+patch(M,dump(m))+'*** End Patch')
