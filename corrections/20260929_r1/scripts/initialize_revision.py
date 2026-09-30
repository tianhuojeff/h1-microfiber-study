"""One-time P0/P1 migration. Does not promote inherited findings to accepted facts."""
from pathlib import Path
import json,hashlib,re,csv,datetime

ROOT=Path(__file__).resolve().parents[4]
H=ROOT/'h1-study'
RUN=Path(__file__).resolve().parents[1]
NOW=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

spec=H/'H1_现有任务纠偏执行命令与长期规则.md'
old=H/'revision_20260929/master_technical_coding_v1.json'
corpus=read(H/'patents/training_20260927/current_corpus.json')
legalp=H/'revision_20260929/legal/official_status_register_20260929.json'
legal={r['sample']:r for r in read(legalp)['records']}
previous=read(old)
target=RUN/'data/analysis_master.json'
if target.exists(): raise SystemExit('Migration refused: current master already exists')

definitions={
 'capture':('截留位置与承载物','物料实际留在滤面、滤材、腔体或可拆容器何处；进出水口不能代替截留关系'),
 'cleaning':('清理／脱离','使截留物离开原截留位置的动作；压实或阀切换不自动等于滤面清理'),
 'transfer':('转移','物料起点、终点、驱动力；液体流动和部件可拆本身不足证明固体转移'),
 'chamber_drainage':('腔体排液','腔内游离液的出口、终点和阶段；与普通过滤出水分开'),
 'solids_dewatering':('固体脱水','针对收集物夹带或附着水的结构；不等于含水率实测或完全干燥'),
 'liquid_route':('液体路径','普通出水、回流、二次过滤、维护排空逐路区分，不默认排入环境'),
 'storage':('暂存','物料停留载体及其与过滤区域关系；不推断密闭或长期无泄漏'),
 'removal':('移出','直接排固／取含物容器／取含物过滤组件分开，标明越过的边界'),
 'state_switch':('操作与驱动','状态、触发、动力及有依据的顺序；局部自动不等于全链自动'),
 'seals_connections':('维护接口','开盖、解锁、旋拧、抽出、断管的具体关系，不虚构时间和便利性'),
 'performance':('实际性能','文本主张、实际数据、可比验证分开；未核验不能填零'),
 'endpoint':('后续处置','只记录原文处置动作／主张；移出装置不等于安全最终处置已验证')}

samples=[]
for rec in previous['records']:
 pub=rec['publication'];meta=next(r for r in corpus if r['publication']==pub)
 members=[r for r in corpus if r['family_id']==meta['family_id']]
 sources=[]
 for member in members:
  p=H/'team_package_20260928/sources'/(member['publication']+'.html')
  sources.append({'publication_id':member['publication'],'source_path':str(p),'source_url':member['source_url'],'source_sha256':sha(p) if p.exists() else None,'local_exists':p.exists(),'historical_corpus_sha256':member['html_sha256'],'text_role':'application_publication' if not member['publication'].endswith('U') else 'utility_model_grant_publication','review_status':'not_reviewed_this_revision'})
 samples.append({'sample_id':'H1-F'+meta['family_id'],'family_key':meta['family_id'],
 'family_definition':{'basis':'历史Google Patents family ID归并','verification_status':'provisional; priority/application member relationships require targeted confirmation','source':'patents/training_20260927/current_corpus.json'},
 'representative_publication':pub,'title':meta['title'],'sample_role':'pending',
 'role_reason':'具体相关授权文本与截至核验时点的有效资格未闭合；保留技术复核，不计入已核有效核心数',
 'grant_publication_id':legal[pub].get('grant_no'),'legal_evidence':legal[pub],
 'legal_evidence_source':{'path':str(legalp),'sha256':sha(legalp),'imported_at':NOW,'new_online_query_performed':False},
 'scene_material':{'classification':None,'review_status':'pending_primary_text'},
 'publications':sources,'prior_working_evidence':rec,'prior_acceptance':'historical literal checks only; not current semantic acceptance',
 'features':{key:{'label':label,'review_status':'not_reviewed_this_revision','support_status':None,'observations':[],'prior_field':rec['fields'].get(key)} for key,(label,_) in definitions.items()},
 'routes':[],'review_completeness':{'full_text_rechecked':False,'current_scope':[]}})

master={'schema_version':'H1-2.0','run_id':'20260929_r1','status':'draft','phase':'P1_initial_complete',
 'created_at':NOW,'updated_at':NOW,'spec_sha256':sha(spec),'single_source_of_current_analysis':True,
 'historical_baseline':{'families':14,'publications':16,'denominator_frozen':False},
 'formal_statistics_allowed':False,'final_report_ready':False,
 'eligibility_note':'14条pending是当前工作状态，不是14件无效；当前已确认核心数不能用来假装完成资格审查。',
 'support_status_values':['explicit','same_embodiment_combination','not_located_in_reviewed_scope','conflict','not_applicable'],
 'review_status_values':['complete_in_stated_scope','partial','not_acquired','extraction_failed','not_reviewed_this_revision'],
 'unreviewed_support_status':None,'unknown_policy':'No automatic zero coding; review completeness and technical support are independent.',
 'imported_master':{'path':str(old),'sha256':sha(old),'records':len(previous['records'])},
 'field_dictionary':{k:{'label':v[0],'definition':v[1]} for k,v in definitions.items()},'samples':samples}
save(target,master)
with (RUN/'data/sample_status.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['sample_id','publication','family_key','sample_role','grant_lead','current_status','reason'])
 for s in samples:w.writerow([s['sample_id'],s['representative_publication'],s['family_key'],s['sample_role'],s['grant_publication_id'],s['legal_evidence']['status_as_of'],s['role_reason']])

lines=['# P1 技术字段与资格初筛\n','当前14条均pending；允许P2技术复核，禁止称为已核有效核心集或固定统计分母。\n','|字段|判定对象与边界|','|---|---|']
lines += [f'|{label}|{definition}|' for label,definition in definitions.values()]
lines += ['\n## 统一纳入与证据规则\n','移出分直接排固、含目标物容器取出、含目标物过滤组件取出；单独盖板可拆仅支持维护可达性。每条判断记录实际公开号、实施方式、从属链、原句、释义、来源哈希、物料起终点、边界及顺序。不同实施方式不合成一套方案。','\n技术状态为明示／同一实施方式组合／已读范围未定位／冲突／不适用；未读的支持状态为null，读取状态单列。说明书与从属项可支持技术披露，不自动并入授权权利要求。','\n场景区分明确洗衣微纤维或微塑料、洗衣绒毛或滤渣但材质未明、非洗衣技术对照；不得凭题名或代表号自动归类。','\n法律信息来自既有核验记录，本轮迁移未新增在线查询。A/B/U后缀、同族代表表和Google状态标签都不证明当前有效。P3继续缺失状态与具体授权文本。','\n唯一当前主表：data/analysis_master.json。旧记录完整嵌入prior_working_evidence以留痕；当前observations必须经本轮原文核读才写入。sample_status.csv为主表派生初筛视图。']
(RUN/'data/field_dictionary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

checks=[]
for line in spec.read_text(encoding='utf-8-sig').splitlines():
 if re.match(r'\| C\d\d \|',line):
  parts=[s.strip() for s in line.strip('|').split('|')]
  checks.append({'id':parts[0],'problem':parts[1],'required_action':parts[2],'acceptance':parts[3],'status':'pending','evidence':[]})
save(RUN/'QA/correction_checklist.json',checks)

baseline=read(RUN/'baseline_manifest.json')
entries=baseline.get('files',baseline.get('entries',[]))
backups_ok=all(Path(r['backup']).exists() and sha(Path(r['backup']))==r['sha256'] for r in entries)
assert len(entries)==43 and backups_ok
old_agents=(RUN/'baseline/AGENTS.md').read_text(encoding='utf-8-sig')
new_agents=(ROOT/'AGENTS.md').read_text(encoding='utf-8-sig')
rest=old_agents.split('\n',1)[1]
rules=spec.read_text(encoding='utf-8-sig').split('## H1 参赛报告：当前有效规则',1)[1].split('```',1)[0]
rule_lines=[l for l in rules.splitlines() if re.match(r'\d+\. ',l)]
h1_agents=(H/'AGENTS.md').read_text(encoding='utf-8-sig')
qa={'checked_at':NOW,'baseline_files':len(entries),'backup_hashes_match':backups_ok,'root_previous_content_preserved':rest in new_agents,'rules_count':len(rule_lines),'all_twenty_rules_present':len(rule_lines)==20 and all(l in h1_agents for l in rule_lines),'original_spec_hash_matches':sha(spec)==sha(Path('C:/Users/tianhuo/Downloads/H1_现有任务纠偏执行命令与长期规则.md')),'current_master_records':len(samples),'current_publications':sum(len(s['publications']) for s in samples),'pending':len(samples),'formal_statistics_allowed':False}
assert qa['root_previous_content_preserved'] and qa['all_twenty_rules_present'] and qa['original_spec_hash_matches']
assert qa['current_publications']==len(corpus) and all(s['publications'] for s in samples)
save(RUN/'QA/P0_P1_acceptance.json',qa)
release=read(H/'current_release.json');release.update({'phase':'P2','updated_at':NOW,'analysis_master':'corrections/20260929_r1/data/analysis_master.json'});save(H/'current_release.json',release)
print(json.dumps(qa,ensure_ascii=False))
