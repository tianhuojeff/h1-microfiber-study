"""Bind completed original A review without duplicating or changing accepted observations."""
from pathlib import Path
import ast,datetime,difflib,hashlib,json,re,subprocess,sys
from pypdf import PdfReader
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='3faa3576021452510bfbeb275102b1f316fe7b62';SID='H1-F90159083';PUB='CN117702432A'
PDF=H/'patents/CN117702432A.pdf';EXPECTED='e22fdc6e0d024314eea78668846b860ee3cb031fa35e484cfa446e8a06070458'
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
reader=PdfReader(PDF);texts=[p.extract_text() for p in reader.pages];assert len(texts)==14
clean=[]
for text in texts[3:9]:
    lines=[x for x in text.splitlines() if not re.match(r'^说\s*明\s*书|^CN 117702432 A$|^\d+$',x.strip())]
    clean.append('\n'.join(lines))
whole='\n'.join(clean);matches=list(re.finditer(r'\[(\d{4})\]',whole));assert [int(x.group(1)) for x in matches]==list(range(1,75))
paragraphs={int(x.group(1)):re.sub(r'\s+','',whole[x.end():matches[i+1].start() if i+1<len(matches) else len(whole)]) for i,x in enumerate(matches)}
images=[R/'evidence'/('CN117702432A_original_20261003_page-'+str(i).zfill(2)+'.png') for i in range(1,15)]
assert all(p.is_file() for p in images)
old=json.loads(baseline('corrections/20260929_r1/data/analysis_master.json'));m=json.loads(M.read_text(encoding='utf8'));s=target(m)
KEY='original_published_A_full_review_20261003'
if '--verify' in sys.argv:
    assert len(old['samples'])==len(m['samples'])==14 and [x['sample_id'] for x in old['samples']]==[x['sample_id'] for x in m['samples']]
    for x,y in zip(old['samples'],m['samples']):
        if x['sample_id']!=SID:assert x==y
        else:
            for k in x:
                if k!='review_completeness':assert x[k]==y[k]
            assert {k:v for k,v in y['review_completeness'].items() if k!=KEY}==x['review_completeness']
    for k in old:
        if k not in ['samples','updated_at']:assert old[k]==m[k]
    rc=s['review_completeness'][KEY]
    assert rc['source_sha256']==sha(PDF) and rc['executor_text_pages_read']==list(range(1,15)) and rc['executor_visual_pages_read']==list(range(1,15))
    assert len(rc['original_field_bindings'])==13
    for f,binding in rc['original_field_bindings'].items():
        assert f in s['features'] and binding['accepted_observation_ids']==[o['observation_id'] for o in s['features'][f]['observations']]
        for p in binding['paragraph_evidence']:assert p['excerpt_normalized']==paragraphs[p['printed_paragraph']]
    for x in rc['rendered_pages']:assert sha(Path(x['path']))==x['sha256']
    assert (R/'data/review_coverage.csv').read_bytes()==baseline('corrections/20260929_r1/data/review_coverage.csv')
    obs=[o for z in m['samples'] for f in z['features'].values() for o in f['observations']]
    assert len(obs)==168 and all(z['sample_role']=='pending' and not z['review_completeness']['full_text_rechecked'] for z in m['samples'])
    rel=json.loads((H/'current_release.json').read_text(encoding='utf8'))
    assert rel['master_sha256']==sha(M) and rel['current_observations']==168 and rel['phase']=='P2' and rel['status']=='draft' and not rel['project_completion_accepted']
    assert not m['formal_statistics_allowed'] and not m['final_report_ready']
    print(dump({'verified':True,'baseline':BASE,'observations':168,'new_observations':0,'all_old_168_observations_and_feature_objects_unchanged':True,
    'other_13_candidates_unchanged':True,'all_legal_evidence_unchanged':True,'CSV_exact_bytes_unchanged':True,'master_sha256':sha(M),
    'original_pdf_sha256':sha(PDF),'original_pdf_pages':14,'executor_text_pages_read':list(range(1,15)),'executor_visual_pages_read':list(range(1,15)),
    'printed_description_paragraphs':[1,74],'claim_numbers':[1,10],'drawing_pages':[10,14],'figures_read':[1,2,3,4,5,6,7,8],
    'original_field_bindings_count':13,'all_binding_excerpts_and_image_bytes_verified':True,'full_text_complete_count':0,'all_14_pending':True,
    'formal_statistics_allowed':False,'reset_consumed':False,'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()}));raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
data={
'capture':([48,50,51],[7],'权1与说明书过滤网320截留至少部分微塑料；图3/6—8分选通腔，不推同时全网串联。'),
'cleaning':([54,55],[7,8],'取出滤网清理可达性明确；完整74段/全10权/8图未定位具体清洗沉积物分离方法。'),
'transfer':([49,50,54],[7,8],'含物载体可拆取，完整原件未定位松散固体卸下并向独立收集盒转移；不是判功能绝对不存在。'),
'chamber_drainage':([54,62,69],[7,8,9],'普通过滤重力出口与阀切换，不是维护前腔游离液排空；完整原件未定位专门排空。'),
'solids_dewatering':([39,49,50,54],[6,7,8],'衣物运动/烘干或过滤出水不转滤渣脱水；完整原件范围未定位固体含水降低动作。'),
'liquid_route':([42,43,48,50,69],[6,7,9],'管段夹装或末端、过滤水下水道或分支回供水均为各可选，原[0043]不补控制阀/水质保证。'),
'storage':([49,50,52],[7],'过滤腔/网内堆积暂留与堵塞后换腔，不是专用储渣盒或长期防漏干储。'),
'removal':([54,55],[7,8],'分体壳盖可取出网清理；图5爆炸仅结构可达性，不补固体卸载/最终处置/先排干顺序。'),
'state_switch':([60,61,62,63,65,66],[8,9],'权4依3依2依1给开关状态；[0063]/[0066]压力达到阈值触发，90度为例，未给控制器/压力数值/自动程度实测。图3→6→7→8分别选通腔，不作四腔同时过滤。'),
'seals_connections':([54,56,57,58],[7,8],'权9依2依1卡扣；多对卡扣/硅胶说明书可选。图5未编号环轮廓不自动认定硅胶，原[0058]称图未示保持。'),
'performance':([4,27,53,65,70,71],[4,5,7,9],'周期/寿命/精度都是本件效果主张；完整原件未定位本装置效率、寿命实验方法/N/误差。背景35%不作效率。'),
'endpoint':([43,54],[6,7,8],'[0043]液体去向不是固体处置；完整原件未定位含物固体/废网最终处置。'),
'carrier_conditioning':([39,54,55,69],[6,7,8,9],'衣物烘干/取网清理/普通水流不作网320排水干燥，完整原件未定位该介质调理。')}
bindings={}
for f,(nums,pages,result) in data.items():
    bindings[f]={'accepted_observation_ids':[o['observation_id'] for o in s['features'][f]['observations']],
    'printed_paragraphs':nums,'physical_text_pages':pages,'scope_judgment':result,
    'paragraph_evidence':[{'printed_paragraph':n,'excerpt_normalized':paragraphs[n]} for n in nums],
    'evidence_role':'Original paragraph object/claim boundary validation; an individual contrast excerpt does not prove whole-document absence.'}
rc={'source_path':str(PDF),'source_sha256':sha(PDF),'source_bytes':PDF.stat().st_size,'at':now,
'executor_text_pages_read':list(range(1,15)),'executor_visual_pages_read':list(range(1,15)),
'printed_description_paragraphs':[1,74],'claim_numbers':[1,10],'drawing_pages':[10,14],'figures_read':[1,2,3,4,5,6,7,8],
'original_published_A_technical_scope_complete':True,'full_text_acceptance_flag_unchanged':True,
'completion_scope':'All published A pages and figures personally read; no grant/current legal/family qualification or overall P2 acceptance.',
'original_field_bindings':bindings,
'figure_boundary_notes':['Figure5 physical12 has unnumbered rectangular ring-like outline below cover; description0058 says seal not shown; identity/material not independently specified.',
'Figures3/6/7/8 each illustrate different selected chamber; pressure switching description0063/0066 is not an efficiency measurement or a mandatory controller structure.'],
'rendered_pages':[{'physical_page':i+1,'path':str(p),'sha256':sha(p)} for i,p in enumerate(images)]}
s['review_completeness'][KEY]=rc;m['updated_at']=now
print('*** Begin Patch\n'+patch(M,dump(m))+'*** End Patch')
