"""Original-source numbering checks only; preserves accepted features and unknown gates."""
from pathlib import Path
import ast,datetime,difflib,hashlib,json,re,subprocess,sys
from pypdf import PdfReader
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='849eeb8e885935a83a8ecc49acd4807e14465627';PUB='CN118273060A';SID='H1-F91644784';KEY='original_numbering_conflict_review_20261003'
PDF=H/'patents/CN118273060A.pdf';EXPECTED='fcfde50da413b25f2b5dadcca389a44fc41a3aa682027825617ef51c309be80d'
VISUAL=[2,10,11,12,13,14,26,33,34,35,36,37]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def baseline(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=H)
def target(m):
    out=[x for x in m['samples'] if x['sample_id']==SID and x['representative_publication']==PUB];assert len(out)==1
    return out[0]
helper=ast.parse((R/'scripts/review_cn118273060_positive_20261002.py').read_text(encoding='utf8'))
function=next(n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='patch')
exec(compile(ast.Module(body=[function],type_ignores=[]),'<unique-sample-patch>','exec'))
assert sha(PDF)==EXPECTED
reader=PdfReader(PDF);texts=[p.extract_text() for p in reader.pages];assert len(texts)==41
parts=['\n'.join(x for x in t.splitlines() if not re.match(r'^说\s*明\s*书|^CN 118273060 A$|^\d+$',x.strip())) for t in texts[3:14]]
whole='\n'.join(parts);mm=list(re.finditer(r'\[(\d{4})\]',whole));assert [int(x.group(1)) for x in mm]==list(range(1,240))
paras={int(x.group(1)):re.sub(r'\s+','',whole[x.end():mm[i+1].start() if i+1<len(mm) else len(whole)]) for i,x in enumerate(mm)}
claim=re.sub(r'\s+','',texts[1]);cl9=claim[claim.index('9.根据'):claim.index('权利要求书')]
images=[R/'evidence'/('CN118273060A_conflict_20261003-'+str(i).zfill(2)+'.png') for i in VISUAL];assert all(p.is_file() for p in images)
old=json.loads(baseline('corrections/20260929_r1/data/analysis_master.json'));m=json.loads(M.read_text(encoding='utf8'));s=target(m)
if '--verify' in sys.argv:
    assert len(old['samples'])==len(m['samples'])==14 and [z['sample_id'] for z in old['samples']]==[z['sample_id'] for z in m['samples']]
    for x,y in zip(old['samples'],m['samples']):
        if x['sample_id']!=SID:assert x==y
        else:
            for k in x:
                if k!='review_completeness':assert x[k]==y[k]
            assert {k:v for k,v in y['review_completeness'].items() if k!=KEY}==x['review_completeness']
    for k in old:
        if k not in ['samples','updated_at']:assert old[k]==m[k]
    rc=s['review_completeness'][KEY];assert rc['source_sha256']==sha(PDF) and rc['executor_visual_pages_read']==VISUAL
    assert rc['original_claim9_excerpt']==cl9 and len(rc['conflicts'])==4 and not rc['all_drawings_visually_read']
    for c in rc['conflicts']:
        for e in c['paragraph_evidence']:assert e['excerpt_normalized']==paras[e['printed_paragraph']]
    for img in rc['rendered_pages']:assert sha(Path(img['path']))==img['sha256']
    assert (R/'data/review_coverage.csv').read_bytes()==baseline('corrections/20260929_r1/data/review_coverage.csv')
    assert sum(len(f['observations']) for z in m['samples'] for f in z['features'].values())==168
    assert all(z['sample_role']=='pending' and not z['review_completeness']['full_text_rechecked'] for z in m['samples'])
    rel=json.loads((H/'current_release.json').read_text(encoding='utf8'));assert rel['master_sha256']==sha(M) and rel['current_observations']==168 and rel['phase']=='P2' and rel['status']=='draft' and not rel['project_completion_accepted']
    assert not m['formal_statistics_allowed'] and not m['final_report_ready']
    print(dump({'verified':True,'baseline':BASE,'observations':168,'added_observations':0,'all_old_168_features_unchanged':True,'other_13_candidates_unchanged':True,
    'all_legal_evidence_unchanged':True,'CSV_bytes_unchanged':True,'master_sha256':sha(M),'source_pdf_sha256':sha(PDF),
    'printed_description_paragraphs_read':[1,239],'all_claims_text_read':[1,19],'executor_text_pages_read':list(range(2,15)),
    'executor_visual_pages_read':VISUAL,'drawing_pages_visually_read':[26,33,34,35,36,37],'all_27_drawings_pages_visually_read':False,
    'four_original_numbering_conflicts_preserved':True,'all_new_original_excerpts_and_image_bytes_verified':True,'all_14_pending':True,'formal_statistics_allowed':False,
    'reset_consumed':False,'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()}));raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
rows=[
('406/516 roles',[129,130,133,211,224],[2,10,13,14],
'原权9物理2写槽406/突起516，原说明[0129]/[0130]物理10写突起406/槽516，列表[0211]/[0224]分别都写实体槽。原[0133]另述器件在滤组或插塞上的另一实施方式，须区分部件位置选项与编号/名称文本差异。图3/7″/8所选例516指前端凹槽区域，不能据此静默改权9或统一所有实施方式。'),
('side/bottom 52 vs513/512',[73,142,169,220,222],[3,8,10,12,14],
'原[0142]物理10侧壁52、[0169]物理12底壁52仍在原PDF；原权10物理3及[0073]/列表使用侧壁513/底板512。图6″/图7′/图8分别可见512或513标注，支持这些所画结构的标签，不据此把52原文默改或宣称所有版本修正。'),
('medium2 vs50',[70,171,196,216],[8,12,13],
'原[0171]物理12确写过滤介质2；原[0070]介质50，列表[0196]2为壳体组、[0216]50为过滤介质。图7″/8中50指介质；原PDF文字差异保留，不能把一般壳体组当介质功能或自动改2为50。'),
('pump560 vs960',[48,176,177,232],[6,12,14],
'原[0176]/[0177]物理12确写泵组560，前文[0048]及权18/列表[0232]为960。模块集成方式与泵前后位置各选项不能互相强合，所读6图页未确认560号身份，差异作为未决编号线索保留，不自动判新独立泵或改成960。')]
conflicts=[{'id':name,'printed_paragraphs':nums,'physical_text_pages':pages,'judgment':meaning,
'paragraph_evidence':[{'printed_paragraph':n,'excerpt_normalized':paras[n]} for n in nums]} for name,nums,pages,meaning in rows]
rc={'source_path':str(PDF),'source_sha256':sha(PDF),'at':now,'executor_text_pages_read':list(range(2,15)),
'printed_description_paragraphs_read':[1,239],'claims_text_read':[1,19],'executor_visual_pages_read':VISUAL,
'previous_cover_visual_read_receipt':'corrections/20260929_r1/QA/CN118273060A_original_source_20261003.json',
'drawing_titles_read_pages':list(range(15,42)),'drawing_pages_visually_read':[26,33,34,35,36,37],
'all_drawings_visually_read':False,'original_technical_full_review_complete':False,'original_claim9_excerpt':cl9,
'conflicts':conflicts,'rendered_pages':[{'physical_page':i,'path':str(p),'sha256':sha(p)} for i,p in zip(VISUAL,images)],
'next_drawing_visual_pages':[i for i in range(15,42) if i not in [26,33,34,35,36,37]],
'not_a_whole_project_or_legal_acceptance':True}
s['review_completeness'][KEY]=rc;m['updated_at']=now
print('*** Begin Patch\n'+patch(M,dump(m))+'*** End Patch')
