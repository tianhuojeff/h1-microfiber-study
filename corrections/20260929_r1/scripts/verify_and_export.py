"""Readback validation and readable derived cards. No semantic auto-acceptance."""
from pathlib import Path
import json,hashlib,datetime,re,csv
from local_source import read_anchors
R=Path(__file__).resolve().parents[1];H=R.parents[1]
p=R/'data/analysis_master.json';m=json.loads(p.read_text(encoding='utf-8'))
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cache={};ids=[];checks=[];images=[];errors=[];paths={}
independent={'CN112914464A':{1,21,22},'CN115637570A':{1,9},'CN222043626U':{1,10},'CN115087774A':{1,23,24},'WO2021116933A1':{1,23,24},'CN115700309A':{1,8},'CN118273060A':{1,17},'WO2022084677A1':{1},'WO2024250011A1':{1,17},'CN115298383A':{1,14,20},'CN116282270A':{1,2,5},'CN117702432A':{1,10},'CN120500565A':{1,2,19},'WO2024143783A1':{1,2,19},'WO2023047385A1':{1,17,34},'WO2024199585A1':{1,12,15}}
for s in m['samples']:
 for field in s['features'].values():
  for o in field['observations']:
   ids.append(o['observation_id'])
   for key in ['publication_id','embodiment_id','object','start','end','boundary','operation_order','support_status','review_status','claim_dependency','evidence','old_value','new_value','change_reason']:
    if key not in o:errors.append([o['observation_id'],'missing',key])
   for e in o['evidence']:
    src=Path(e['source_path']);paths[str(src)]=sha(src)
    ok=paths[str(src)]==e['source_sha256']
    if not ok:errors.append([o['observation_id'],'hash_mismatch',str(src)])
    if e.get('html_anchor'):
     rows=cache.setdefault(str(src),read_anchors(src));literal=e['evidence_excerpt'] in rows.get(e['html_anchor'],'')
     if not literal:errors.append([o['observation_id'],'quote_mismatch',e['html_anchor']])
     checks.append({'id':o['observation_id'],'anchor':e['html_anchor'],'source_hash_match':ok,'literal_match':literal})
     if e['source_role']=='claim':
      num=int(re.search(r'(\d+)$',e['html_anchor']).group(1));e['source_role']='independent_claim' if num in independent[o['publication_id']] else 'dependent_claim'
      e['claim_number']=num
    else:
     img=Path(e['page_image_path']);images.append({'id':o['observation_id'],'page':e['physical_page'],'image_hash_match':sha(img)==e['page_image_sha256'],'manual_review_recorded':e.get('verification_method')=='manual_visual_readback_original_German'})
     if not images[-1]['image_hash_match']:errors.append([o['observation_id'],'image_mismatch'])
     if e['source_role']=='claim':
      num=int(re.search(r'权(\d+)',e['locator']).group(1));e['source_role']='independent_claim' if num in independent[o['publication_id']] else 'dependent_claim';e['claim_number']=num
   if 'pdf_visual_crosscheck' in o:
    q=o['pdf_visual_crosscheck'];assert sha(Path(q['source_path']))==q['source_sha256'];assert sha(Path(q['image_path']))==q['image_sha256']
assert len(ids)==len(set(ids));assert not errors,errors
assert not m['formal_statistics_allowed'] and not m['final_report_ready']
assert all(s['sample_role']=='pending' for s in m['samples'])
m['updated_at']=now;save(p,m)
qa={'verified_at':now,'master_sha256':sha(p),'observations':len(ids),'family_candidates_with_some_review':sum(any(f['observations'] for f in s['features'].values()) for s in m['samples']),'full_text_complete_count':sum(s['review_completeness']['full_text_rechecked'] for s in m['samples']),'html_quote_checks':checks,'pdf_manual_records':images,'source_hashes':paths,'errors':errors,'what_this_proves':'Source bytes, excerpts, references and minimum record structure match. Semantic findings are manually read within their stated scope; this is not full-text or legal-status completion.','formal_statistics_allowed':False}
save(R/'QA/current_evidence_readback.json',qa)

cards=R/'evidence/technical_cards';cards.mkdir(exist_ok=True)
index=['# 当前技术复核入口\n',f'更新：{now}。本轮{len(ids)}条定点判断覆盖14个候选同族；不代表14件全文复核完成。全部资格仍pending，未生成正式统计。\n','|文献|已记录判断|仍待处理|','|---|---:|---|']
for s in m['samples']:
 pub=s['representative_publication'];obs=[o for f in s['features'].values() for o in f['observations']]
 missing=[f['label'] for f in s['features'].values() if not f['observations']]
 lines=[f'# {pub} — {s["title"]}\n',f'样本：{s["sample_id"]}；角色：pending。状态来源为既有2026-09-29登记，本轮未新增当前法律核验。\n','复核范围：权项和实施方式的定点争议；未作全文穷尽否定。未填字段保留待核，不是无该功能。\n']
 for o in obs:
  lines += [f'## {o["publication_id"]} / {o["stage"]} / {o["embodiment_id"]}\n',o['interpretation']+'\n',f'支持：{o["support_status"]}；读取：{o["review_status"]}。',f'对象：{o["object"]}。起点：{o["start"]}。终点：{o["end"]}。',f'边界：{o["boundary"]}。','顺序：'+' → '.join(o['operation_order'])+'。','权项/实施方式：'+o['claim_dependency']+'。']
  for e in o['evidence']:lines += ['- '+e['locator']+'（'+e['source_role']+'）：'+e['evidence_excerpt']]
  lines+=['修订理由：'+o['change_reason']+'。\n','来源哈希：'+', '.join(dict.fromkeys(e['source_sha256'] for e in o['evidence']))+'。\n']
 lines+=['## 未完成\n','尚未单独裁定：'+'、'.join(missing)+'。这些未完成项不能自动记为否。','全文/图文穷尽复核、当前有效授权资格、正式统计与报告传播仍待完成。']
 (cards/(pub+'.md')).write_text('\n\n'.join(lines)+'\n',encoding='utf-8')
 index.append(f'|[{pub}](technical_cards/{pub}.md)|{len(obs)}|全文、资格及未填字段|')
(R/'evidence/技术复核入口.md').write_text('\n'.join(index)+'\n',encoding='utf-8')
with (R/'data/review_coverage.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['sample_id','publication','field','review_status','support_status','observation_count'])
 for s in m['samples']:
  for key,v in s['features'].items():w.writerow([s['sample_id'],s['representative_publication'],key,v['review_status'],v['support_status'],len(v['observations'])])
diff=json.loads((R/'data/matrix_conflict_decisions.json').read_text(encoding='utf-8'))
lines=['# 旧两矩阵六字段裁定\n','仅为本轮字段级技术裁定；正式数据导出和报告尚未发布。原两矩阵保留历史，不再作为当前输入。\n','|文献/旧字段|训练矩阵旧值|团队矩阵旧值|当前原文裁定|','|---|---|---|---|']
for d in diff:lines.append('|'+d['publication']+'/'+d['legacy_field']+'|'+d['training_matrix_value']+'|'+d['team_matrix_value']+'|'+'；'.join(d['decision'])+'|')
(R/'data/矩阵差异裁定.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({k:qa[k] for k in ['observations','family_candidates_with_some_review','full_text_complete_count','errors','master_sha256']},ensure_ascii=False))
