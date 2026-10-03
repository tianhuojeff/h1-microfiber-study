"""Bounded original drawing review; no new observations or inferred route unification."""
from pathlib import Path
import ast,datetime,difflib,hashlib,json,re,subprocess,sys
from pypdf import PdfReader
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='d9bc591661e43519cdb5567fca490462c8426504';PUB='CN118273060A';SID='H1-F91644784';KEY='original_routes_drawing_review_20261003'
PDF=H/'patents/CN118273060A.pdf';EXPECTED='fcfde50da413b25f2b5dadcca389a44fc41a3aa682027825617ef51c309be80d';PAGES=list(range(15,26))
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
texts=[p.extract_text() for p in PdfReader(PDF).pages];assert len(texts)==41
parts=['\n'.join(x for x in t.splitlines() if not re.match(r'^说\s*明\s*书|^CN 118273060 A$|^\d+$',x.strip())) for t in texts[3:14]]
whole='\n'.join(parts);mm=list(re.finditer(r'\[(\d{4})\]',whole));assert [int(x.group(1)) for x in mm]==list(range(1,240))
paras={int(x.group(1)):re.sub(r'\s+','',whole[x.end():mm[i+1].start() if i+1<len(mm) else len(whole)]) for i,x in enumerate(mm)}
images=[R/'evidence'/('CN118273060A_routes_20261003-'+str(i)+'.png') for i in PAGES];assert all(p.is_file() for p in images)
old=json.loads(baseline('corrections/20260929_r1/data/analysis_master.json'));m=json.loads(M.read_text(encoding='utf8'));s=target(m)
if '--verify' in sys.argv:
    assert [z['sample_id'] for z in old['samples']]==[z['sample_id'] for z in m['samples']]
    for x,y in zip(old['samples'],m['samples']):
        if x['sample_id']!=SID:assert x==y
        else:
            for k in x:
                if k!='review_completeness':assert x[k]==y[k]
            assert {k:v for k,v in y['review_completeness'].items() if k!=KEY}==x['review_completeness']
    for k in old:
        if k not in ['samples','updated_at']:assert old[k]==m[k]
    rc=s['review_completeness'][KEY];assert rc['source_sha256']==sha(PDF) and rc['executor_visual_pages_read_this_transaction']==PAGES
    assert rc['cumulative_drawing_visual_pages']==list(range(15,27))+list(range(33,38))
    assert rc['remaining_drawing_visual_pages']==list(range(27,33))+list(range(38,42))
    for e in rc['paragraph_evidence']:assert e['excerpt_normalized']==paras[e['printed_paragraph']]
    for img in rc['rendered_pages']:assert sha(Path(img['path']))==img['sha256']
    assert (R/'data/review_coverage.csv').read_bytes()==baseline('corrections/20260929_r1/data/review_coverage.csv')
    assert sum(len(f['observations']) for z in m['samples'] for f in z['features'].values())==168
    assert all(z['sample_role']=='pending' and not z['review_completeness']['full_text_rechecked'] for z in m['samples'])
    rel=json.loads((H/'current_release.json').read_text(encoding='utf8'));assert rel['master_sha256']==sha(M) and rel['current_observations']==168 and rel['phase']=='P2' and rel['status']=='draft' and not rel['project_completion_accepted']
    assert not m['formal_statistics_allowed'] and not m['final_report_ready']
    print(dump({'verified':True,'baseline':BASE,'observations':168,'added_observations':0,'all_old_168_features_unchanged':True,'other_13_candidates_unchanged':True,'all_legal_evidence_unchanged':True,'CSV_bytes_unchanged':True,'master_sha256':sha(M),'source_pdf_sha256':sha(PDF),'executor_visual_pages_read_this_transaction':PAGES,'cumulative_drawing_visual_pages':rc['cumulative_drawing_visual_pages'],'remaining_drawing_visual_pages':rc['remaining_drawing_visual_pages'],'all_27_drawing_pages_read':False,'all_paragraph_excerpts_and_render_bytes_verified':True,'embodiments_not_combined':True,'all_14_pending':True,'formal_statistics_allowed':False,'reset_consumed':False,'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()}));raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
cumulative=sorted(set(PAGES+[26,33,34,35,36,37]))
rc={'source_path':str(PDF),'source_sha256':sha(PDF),'at':now,'executor_visual_pages_read_this_transaction':PAGES,
'drawing_sheet_numbers_this_transaction':list(range(1,12)),
'figure_titles_this_transaction':['1'+chr(i) for i in range(ord('a'),ord('u')+1)]+['2prime'],
'cumulative_drawing_visual_pages':cumulative,'remaining_drawing_visual_pages':[i for i in range(15,42) if i not in cumulative],
'all_drawings_visually_read':False,'original_technical_full_review_complete':False,
'figure_observations':[
{'pages':[15,16,17,18,19,20,21],'figures':'1a-1n','judgment':'分别画出过滤器1在900外/内及靠近970的不同布局，950/951/952、960与部分955的位置各不相同；图1a外置与图1b内置不合成同时必需两过滤器。'},
{'pages':[22,23,24,25],'figures':'1o-1u','judgment':'图1o-1u继续给出滤组与泵/阀前后及分支的独立路线变型；图1p/1s可见9521、9522分支标签。说明[0053]/[0055]还使用95121/9522，图和文字标签照原保留，不默修或据此新增维护排腔液。'},
{'pages':[25],'figures':'2prime','judgment':'图2′装配外观可见壳体组2、外壳3、闭合盖4和7；外观线条不证明排干、固体脱水、密封实测或内部流向。'}],
'route_boundary':'按[0045]-[0056]保持外/内、泵上/下游、阀位第一/第二管段及排出/再循环各可选布局独立。图示连线配合文字理解，不补未标箭头、强制先后、所有方案同一链或处理后水质/零排放。',
'paragraph_evidence':[{'printed_paragraph':n,'excerpt_normalized':paras[n]} for n in range(39,57)],
'rendered_pages':[{'physical_page':i,'path':str(p),'sha256':sha(p)} for i,p in zip(PAGES,images)],'not_a_whole_project_or_legal_acceptance':True}
s['review_completeness'][KEY]=rc;m['updated_at']=now
print('*** Begin Patch\n'+patch(M,dump(m))+'*** End Patch')

