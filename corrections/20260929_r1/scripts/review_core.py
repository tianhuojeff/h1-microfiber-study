"""Record individually read primary-text findings for C04-C06/C08."""
from pathlib import Path
import json,hashlib,datetime
from local_source import read_anchors
RUN=Path(__file__).resolve().parents[1];H=RUN.parents[1]
P=RUN/'data/analysis_master.json';M=json.loads(P.read_text(encoding='utf-8'))
NOW=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sample(pub):return next(s for s in M['samples'] if any(p['publication_id']==pub for p in s['publications']))
cache={}
def record(pub,field,emb,feature,obj,start,end,boundary,order,refs,dependency,reason,support='explicit',kind=None):
 s=sample(pub);src=H/'team_package_20260928/sources'/(pub+'.html')
 rows=cache.setdefault(pub,read_anchors(src));ev=[]
 for anchor,excerpt in refs:
  assert anchor in rows,(pub,anchor)
  excerpt=excerpt or rows[anchor]
  assert excerpt in rows[anchor],(pub,anchor,excerpt)
  ev.append({'locator':'HTML #'+anchor,'html_anchor':anchor,'evidence_excerpt':excerpt,
   'source_role':'claim' if 'cl' in anchor or anchor.startswith('c') else 'description_embodiment','subject_role':'this_invention_or_optional_embodiment',
   'source_path':str(src),'source_url':next(p['source_url'] for p in s['publications'] if p['publication_id']==pub),'source_sha256':sha(src),
   'verified_at':NOW,'extraction_note':'Saved patent-publication mirror; whitespace normalized, no semantic paraphrase in excerpt.'})
 o={'observation_id':pub+'-'+field+'-'+emb,'publication_id':pub,'grant_publication_id':None,'sample_role':s['sample_role'],
 'embodiment_id':emb,'stage':field,'technical_feature':feature,'object':obj,'start':start,'end':end,'boundary':boundary,
 'operation_order':order,'support_status':support,'review_status':'complete_in_stated_scope','claim_dependency':dependency,
 'evidence':ev,'interpretation':feature,'performance_status':'not_verified','verified_at':NOW,
 'old_value':s['prior_working_evidence']['fields'].get(field),'new_value':feature,'change_reason':reason,'removal_kind':kind}
 f=s['features'][field];f['observations']=[x for x in f['observations'] if x['observation_id']!=o['observation_id']]+[o]
 f['review_status']='partial';f['support_status']=support
 s['review_completeness']['current_scope'].append({'publication':pub,'anchors':[a for a,_ in refs],'field':field,'at':NOW})
 return o
