"""Current read-only trace and scoped technical-acceptance QA.
No observation edits or file writes. --export-patch emits review-derived text.
Historical one-off QA scripts retain their recorded stage invariants.
"""
from pathlib import Path
import argparse,csv,datetime,difflib,hashlib,io,json,re,sys
from local_source import read_anchors
R=Path(__file__).resolve().parents[1];H=R.parents[1]
M=R/'data/analysis_master.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def validate_acceptance(s):
 rc=s['review_completeness'];a=rc.get('publication_technical_acceptance')
 if not rc['full_text_rechecked']:
  assert not a or not a.get('accepted'), 'accepted publication must have matching technical flag'
  return False
 assert a and a.get('accepted'), 'technical flag requires explicit scoped acceptance'
 assert a['scope']=='representative_published_document_only'
 assert a['publication']==s['representative_publication']
 assert sha(H/a['source_path'])==a['source_sha256']
 assert a['source_page_count']>0
 assert a['text_pages_read']==a['visual_pages_read']==list(range(1,a['source_page_count']+1))
 assert set(a['field_bindings'])==set(s['features']) and s['scene_material']['classification']
 assert s['scene_material']['review_status']=='accepted_in_original_published_scope'
 for f,b in a['field_bindings'].items():
  v=rc[b['review_record_key']]
  assert v['source_sha256']==a['source_sha256']
  if 'original_field_bindings' in v:binding=v['original_field_bindings'][b['binding_key']]
  elif 'bindings' in v:binding=v['bindings'][b['binding_key']]
  else:assert v.get('bound_field')==f;binding=v
  ids=binding.get('accepted_observation_ids',binding.get('observation_ids_preserved',binding.get('old_observation_ids_preserved')))
  assert ids==[o['observation_id'] for o in s['features'][f]['observations']]
  assert s['features'][f]['review_status']=='accepted_in_original_published_scope'
 assert any(p['publication_id']==a['publication'] and p['review_status']=='accepted_in_original_published_scope' for p in s['publications'])
 assert a['legal_qualification_granted_by_this_acceptance'] is False
 return True
def validate(m=None,check_coverage=True):
 m=m or json.loads(M.read_bytes());ids=[];errors=[];cache={};checks=0;images=0;paths={};accepted=[]
 assert not m['formal_statistics_allowed'] and not m['final_report_ready']
 for s in m['samples']:
  assert s['sample_role']=='pending'
  if validate_acceptance(s):accepted.append(s['representative_publication'])
  for f in s['features'].values():
   for o in f['observations']:
    ids.append(o['observation_id'])
    for k in ['publication_id','embodiment_id','object','start','end','boundary','operation_order','support_status','review_status','claim_dependency','evidence','old_value','new_value','change_reason']:assert k in o
    for e in o['evidence']:
     p=Path(e['source_path']);paths[str(p)]=sha(p);assert paths[str(p)]==e['source_sha256']
     if e.get('html_anchor'):
      if str(p) not in cache:cache[str(p)]=read_anchors(p)
      assert e['evidence_excerpt'] in cache[str(p)].get(e['html_anchor'],'');checks+=1
     elif e.get('page_image_path'):
      assert sha(e['page_image_path'])==e['page_image_sha256'];images+=1
    if 'pdf_visual_crosscheck' in o:
     q=o['pdf_visual_crosscheck'];assert sha(q['source_path'])==q['source_sha256'];assert sha(q['image_path'])==q['image_sha256']
  for v in s['review_completeness'].values():
   if isinstance(v,dict):
    for im in v.get('rendered_pages',[]):assert sha(im['path'])==im['sha256']
 assert len(ids)==len(set(ids))
 if check_coverage:
  rows=list(csv.DictReader((R/'data/review_coverage.csv').read_text(encoding='utf-8-sig').splitlines()))
  expected=[(s['sample_id'],s['representative_publication'],k,f['review_status'],f['support_status'] or '',str(len(f['observations']))) for s in m['samples'] for k,f in s['features'].items()]
  assert [tuple(z[k] for k in ['sample_id','publication','field','review_status','support_status','observation_count']) for z in rows]==expected
 return {'verified':True,'verified_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
 'master_sha256':sha(M),'observations':len(ids),'full_text_complete_count':len(accepted),
 'accepted_representative_publications':accepted,'full_text_flag_scope':'representative_published_document_only',
 'html_quote_checks':checks,'pdf_image_checks':images,'source_hashes':paths,'errors':errors,
 'formal_statistics_allowed':False,'final_report_ready':False,
 'what_this_proves':'Traceability plus explicit previously read publication technical acceptance; no legal qualification, family-wide technical completion, or project completion.'}
def patch(p,new):
 prior=p.read_text(encoding='utf-8') if p.exists() else None
 if prior==new:return ''
 if prior is None:return '*** Add File: '+p.as_posix()+'\n'+''.join('+'+x+'\n' for x in new.splitlines())
 body=[]
 for line in list(difflib.unified_diff(prior.splitlines(True),new.splitlines(True),n=3))[2:]:
  body.append('@@\n' if line.startswith('@@') else line)
 return '*** Update File: '+p.as_posix()+'\n'+''.join(body)
def card(s):
 pub=s['representative_publication'];a=s['review_completeness'].get('publication_technical_acceptance')
 scope=('公布文本'+pub+'完整技术范围已独立验收；范围只限本公布文本，非同族全部成员。' if a and a.get('accepted') else '本候选技术全文尚未独立验收；逐项范围以当前读取记录为准。')
 lines=[f'# {pub} — {s["title"]}',f'样本：{s["sample_id"]}；法律角色：{s["sample_role"]}。',scope,'法律资格仍pending；正式统计、终稿和项目验收仍未放行。']
 if a:lines+=['原件：'+a['source_path']+'；SHA256 '+a['source_sha256']+'。','场景：'+str(s['scene_material']['classification'])+'；'+s['scene_material'].get('boundary','')]
 for key,f in s['features'].items():
  lines+=[f'## {f["label"]} / {key}', '当前技术范围：'+f['review_status']+'；支持：'+str(f['support_status'])+'。']
  if a:
   b=a['field_bindings'][key];v=s['review_completeness'][b['review_record_key']]
   z=v.get('original_field_bindings',v.get('bindings',{})).get(b['binding_key'],v)
   lines+=['原件绑定：'+b['review_record_key']+' / '+b['binding_key']+'。',z.get('scope_judgment',z.get('judgment',''))]
  for o in f['observations']:
   lines += ['### '+o['observation_id'],o['interpretation'],'对象：'+o['object']+'。边界：'+o['boundary']+'。']
   lines+=['- '+e['locator']+'：'+e['evidence_excerpt'] for e in o['evidence']]
 lines+=['## 仍有限制','未定位只限所列已读技术范围，unknown不转0；作者性能主张非实测验证。法律、正式统计及报告终稿仍待闭合。']
 return '\n\n'.join(lines)+'\n'
def export_patch(publications):
 m=json.loads(M.read_bytes());q=validate(m,False);out=[]
 for pub in publications:
  s=next(s for s in m['samples'] if s['representative_publication']==pub)
  out.append(patch(R/'evidence/technical_cards'/(pub+'.md'),card(s)))
 rows=io.StringIO(newline='');w=csv.writer(rows);w.writerow(['sample_id','publication','field','review_status','support_status','observation_count'])
 for s in m['samples']:
  for k,f in s['features'].items():w.writerow([s['sample_id'],s['representative_publication'],k,f['review_status'],f['support_status'],len(f['observations'])])
 out.append(patch(R/'data/review_coverage.csv','\ufeff'+rows.getvalue()))
 index=['# 当前技术复核入口','168条当前观察；公布文本技术范围验收'+str(q['full_text_complete_count'])+'件；其余范围待核。法律14pending，非正式专利统计。','|文献|已记录判断|技术范围与剩余|','|---|---:|---|']
 for s in m['samples']:
  pub=s['representative_publication'];n=sum(len(f['observations']) for f in s['features'].values());a=s['review_completeness'].get('publication_technical_acceptance')
  status=(pub+'公布文本已独立验收；资格待核' if a and a.get('accepted') else '技术全文待独立验收；资格及未填字段待核')
  index.append(f'|[{pub}](technical_cards/{pub}.md)|{n}|{status}|')
 out.append(patch(R/'evidence/技术复核入口.md','\n\n'.join(index[:2])+'\n\n'+'\n'.join(index[2:])+'\n'))
 out.append(patch(R/'QA/current_evidence_readback.json',dump(q)))
 return '*** Begin Patch\n'+''.join(out)+'*** End Patch\n'
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--export-patch',action='store_true');ap.add_argument('--publication',action='append',default=[]);a=ap.parse_args()
 if a.export_patch:
  assert a.publication, 'explicit publication scope required';print(export_patch(a.publication))
 else:print(dump(validate()))
