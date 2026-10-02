"""Complete original U source review; retain unknowns and all historical values."""
from pathlib import Path
import ast,csv,datetime,difflib,hashlib,io,json,subprocess,sys
from pypdf import PdfReader
from local_source import read_anchors
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json';C=R/'data/review_coverage.csv'
BASE='9750db0a6107f705fd1a33326226e0c780232858';PUB='CN222043626U';SID='H1-F93508213'
PDF=H/'patents/CN222043626U.pdf';EXPECTED='27b93dc08a6e684face981d4b2d7afedbb8dfad39b59c222d91c09132b0b08b2'
IMAGES=R/'evidence/CN222043626U_original_pages_20261002'
FIELDS=['cleaning','transfer','chamber_drainage','solids_dewatering','performance','endpoint','carrier_conditioning']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def baseline(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=H)
def target(m):
    pairs=[s for s in m['samples'] if s['sample_id']==SID and s['representative_publication']==PUB];assert len(pairs)==1
    return pairs[0]
helper=ast.parse((R/'scripts/review_cn118273060_positive_20261002.py').read_text(encoding='utf8'))
function=next(n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='patch')
exec(compile(ast.Module(body=[function],type_ignores=[]),'<changed-index-sample-patch>','exec'))
assert sha(PDF)==EXPECTED
pdf=PdfReader(PDF);assert len(pdf.pages)==14
text=[''.join((p.extract_text() or '').split()) for p in pdf.pages]
assert all(text)
images=[{'physical_page':i,'path':str(IMAGES/f'physical-{i:02d}.png'),'sha256':sha(IMAGES/f'physical-{i:02d}.png')} for i in range(1,15)]
old=json.loads(baseline('corrections/20260929_r1/data/analysis_master.json'));m=json.loads(M.read_text(encoding='utf8'));s=target(m)
if '--verify' in sys.argv:
    assert len(m['samples'])==14
    for x,y in zip(old['samples'],m['samples']):
        assert x['sample_id']==y['sample_id']
        if x['sample_id']!=SID:assert x==y
        else:
            for k in x:
                if k not in ['features','review_completeness']:assert x[k]==y[k]
            for field,f in x['features'].items():
                if field not in FIELDS:assert f==y['features'][field]
                else:assert not f['observations'] and y['features'][field]['prior_field']==f['prior_field'] and len(y['features'][field]['observations'])==1
            assert y['review_completeness']['current_scope'][:-7]==x['review_completeness']['current_scope']
            for k in x['review_completeness']:
                if k!='current_scope':assert x['review_completeness'][k]==y['review_completeness'][k]
    obs=[o for z in m['samples'] for f in z['features'].values() for o in f['observations']];index={o['observation_id']:o for o in obs}
    assert len(obs)==len(index)==148
    prior=[o for z in old['samples'] for f in z['features'].values() for o in f['observations']]
    assert len(prior)==141 and all(index[o['observation_id']]==o for o in prior)
    cache={}
    for o in obs:
        for e in o['evidence']:
            p=Path(e['source_path']);assert sha(p)==e['source_sha256']
            if e.get('html_anchor'):
                if str(p) not in cache:cache[str(p)]=read_anchors(p)
                assert e['evidence_excerpt'] in cache[str(p)][e['html_anchor']]
            else:
                assert sha(Path(e['page_image_path']))==e['page_image_sha256']
                if e.get('pdf_physical_page') and p==PDF:assert e['evidence_excerpt'] in text[e['pdf_physical_page']-1]
    before=list(csv.DictReader(baseline('corrections/20260929_r1/data/review_coverage.csv').decode('utf-8-sig').splitlines()))
    after=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()));assert len(before)==len(after)==182
    for x,y in zip(before,after):
        if x['sample_id']!=SID or x['field'] not in FIELDS:assert x==y
        f=next(z for z in m['samples'] if z['sample_id']==y['sample_id'])['features'][y['field']]
        assert y['review_status']==f['review_status'] and y['support_status']==(f['support_status'] or '') and int(y['observation_count'])==len(f['observations'])
    rel=json.loads((H/'current_release.json').read_text(encoding='utf8'));assert rel['master_sha256']==sha(M) and rel['current_observations']==148
    assert not rel['project_completion_accepted'] and rel['phase']=='P2' and rel['status']=='draft'
    assert all(z['sample_role']=='pending' and not z['review_completeness']['full_text_rechecked'] for z in m['samples'])
    assert not m['formal_statistics_allowed'] and not m['final_report_ready']
    assert all(s['features'][k]['observations'] for k in s['features'])
    assert '第一过滤网331和第二过滤网331均设置为齿状' in text[5]
    print(dump({'verified':True,'baseline':BASE,'observations':148,'added':7,'old_141_unchanged':True,
     'other_13_candidates_unchanged':True,'all_legal_evidence_unchanged':True,'all_source_bytes_and_excerpts_verified':True,
     'source_pdf_sha256':sha(PDF),'master_sha256':sha(M),'CSV_verified':True,'fields':FIELDS,'executor_visual_physical_pages':list(range(1,15)),
     'text_scope':'cover; claims1-10 physical2; paragraphs0001-0072 physical3-8; drawings1-7 physical9-14',
     'all_6_drawing_pages_visually_read':True,'rendered_pages':images,'all_13_fields_addressed_in_original_U_scope':True,
     'old_6_observations_unchanged_and_original_crosschecked':True,'source_conflict_preserved':'0055 second filter331 vs claims3 and figure3 label332; original wording not rewritten',
     'all_14_pending':True,'full_text_complete_count':0,'formal_statistics_allowed':False,
     'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()}));raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
# Excerpts are exact PDF text with whitespace removed, not invented quotations.
data=[
 ('cleaning','not_located_in_reviewed_scope',7,'[0059]','当需要将收集盒320拆出进行清洁时，可以将盖板314与主壳313拆卸开',
  '过滤网330表面截留物的清除动作',
  '原U权1—10、[0001]—[0072]及图1—7完整范围：0059/0063支持取盒/取网以清理的目的与界面，但未定位具体洗、刷、反洗或使固体脱离滤面的动作程序。开盖取盒不自动证明滤面清理再生已实现，具体清理机制保留未知，不填0。'),
 ('transfer','not_located_in_reviewed_scope',5,'[0048]','收集盒320用于收集过滤出的微塑料，以便于统一进行清理',
  '截留微塑料从330到另独立承载容器的转移',
  '原U完整范围：微塑料直接在收集盒内330截留，0048/0059的载物盒取出对应移出，未定位将固体从330剥离再转储至另一独立盒/袋/腔的起终点或动力。水进入盒过滤属于截留液路，不充作脱离后固体转移；不否认含物组件可取出。'),
 ('chamber_drainage','not_located_in_reviewed_scope',8,'[0068]','通过第二进水口321和第二出水口322实现进水过滤与排出',
  '维护前壳体或盒内游离液',
  '原U完整范围未定位维护前专门排空腔内游离液的动作、出口和终点。311/312、321/322及可选网状盒是普通过滤液路，0059开盖/取盒没有先排空条件；不能从正常出水推完全无残液。限定原件范围，保持未知。'),
 ('solids_dewatering','not_located_in_reviewed_scope',6,'[0050]','以拦截进入收集盒320的微塑料',
  '已收集微塑料附着或夹带液体',
  '原U完整范围未定位对已截留固体夹带/附着液体的挤压、离心或其他脱水步骤；0050过滤拦截及0068网孔通水不能转成滤渣已脱水。0038离心力/烘干对象为洗衣滚筒与衣物，非截留固体；残余含水率无实测支持，未知不填0。'),
 ('performance','explicit',6,'[0054]','可以减小第一过滤网331和/或第二过滤网332堵塞的速度',
  '可选齿状滤网的堵塞/清理间隔等文本效果',
  '0054/0055齿状增加接触面积、降低堵塞和延长清理间隔，以及0056大小孔双重过滤、0052/0071便利和减少漏水均为原文效果主张。完整原U未定位本装置效率/压差/清理时长/漏水/含水率实测、样本量、误差或独立验证。0002的35%为背景引用，非本机捕获率；第一网孔大于或等于第二是设计关系，非实测粒径。'),
 ('endpoint','not_located_in_reviewed_scope',5,'[0048]','以便于统一进行清理',
  '取出后截留微塑料或已用滤网的最终去向',
  '原U完整范围0048/0059/0063有统一清理及取出目的，但未定位固体交垃圾、回收、销毁或安全环境终点。0044下水道/回收供水是滤后水液体路径，不能补成截留固体后续处置；移出不等于安全最终处置，未知不填0。'),
 ('carrier_conditioning','not_located_in_reviewed_scope',7,'[0063]','以便于将其内部的过滤网330取出进行清理',
  '过滤网330/331/332自身排水或干燥',
  '原U完整范围未定位过滤介质自身独立排水、干燥或调理工序。0063取网清理和0068/0069网状承载物正常通水不足证明滤材已排干；0038洗衣烘干对象为衣物，不推滤网或滤渣干燥。保持对象限定与未知，不填0。')]
for field,status,page,para,excerpt,obj,meaning in data:
    assert excerpt in text[page-1];f=s['features'][field];assert not f['observations']
    img=images[page-1]
    e={'locator':f'原U PDF物理{page}页，说明书{page-2}/6页，{para}；未定位结论范围为权1—10/0001—0072/图1—7',
     'pdf_physical_page':page,'source_path':str(PDF),'source_sha256':sha(PDF),'source_url':'https://patentimages.storage.googleapis.com/0c/27/f7/b98ebf05098854/CN222043626U.pdf',
     'source_role':'description_embodiment','subject_role':'this_invention_or_optional_embodiment','evidence_excerpt':excerpt,
     'extraction_note':'Whitespace removed only; excerpt supplies object boundary, absence limited to the complete original U technical scope.',
     'page_image_path':img['path'],'page_image_sha256':img['sha256'],'verified_at':now}
    o={'observation_id':PUB+'-'+field+'-original_U_scope-20261002','publication_id':PUB,'grant_publication_id':PUB,'sample_role':'pending',
     'embodiment_id':'original_U_complete_scope_distinct_objects','stage':field,'technical_feature':meaning,'object':obj,
     'start':'原件明确对象/范围','end':'效果主张未验证' if field=='performance' else '该具体功能未定位，未知不填0',
     'boundary':'原U完整技术范围；不同盒/网形态可选，维护目的与具体动作分开','operation_order':[],'support_status':status,
     'review_status':'complete_in_stated_original_U_scope','availability_judgment':'unknown' if status!='explicit' else 'text_claim_only',
     'claim_dependency':'全部权1—10已读；权2→1、3→2、4→1-3之一、5/6/9→4、7/8→6、10→1-9之一，不跨从属强合并',
     'evidence':[e],'interpretation':meaning,'performance_status':'text_claim_only' if field=='performance' else 'not_verified',
     'verified_at':now,'old_value':f['prior_field'],'new_value':meaning,'change_reason':'新取得原U全文及6图页复核后补空字段；原值与未知保留，资格不放行。','removal_kind':None}
    f['observations'].append(o);f['review_status']='complete_in_original_U_scope';f['support_status']=status
    s['review_completeness']['current_scope'].append({'publication':PUB,'field':field,'physical_pages_scope':list(range(1,15)),'at':now})
s['review_completeness']['original_U_readback_20261002']={'source_path':str(PDF),'source_sha256':sha(PDF),'physical_pages_read':list(range(1,15)),
 'visual_physical_pages':list(range(1,15)),'description_paragraphs':'0001-0072','claims':'1-10','drawings':'1-7, physical9-14','rendered_pages':images,
 'all_13_fields_addressed':True,'prior_6_original_crosscheck':{'capture':'0050, claim1, figure3 physical10','liquid_route':'0043-0044 physical5',
 'storage':'0048 physical5;0068 physical8 closed/mesh alternatives','removal':'0059 physical7;0066-0067 physical7-8',
 'state_switch':'0059 physical7;0067 physical8','seals_connections':'0066-0067 physical7-8;figure7 physical14'},
 'source_conflicts':[{'paragraph':'0055','physical_page':6,'original_wording':'第一过滤网331和第二过滤网331均设置为齿状',
 'comparison':'Claim3 and figure3 identify second filter332','resolution':'Original typo preserved; do not rewrite publication or treat both filters as same part'}],
 'full_candidate_acceptance':False,'legal_current_status':'unknown','verified_at':now}
m['updated_at']=now
rows=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()));cols=rows[0].keys()
for row in rows:
    if row['sample_id']==SID and row['publication']==PUB and row['field'] in FIELDS:
        f=s['features'][row['field']];row.update(review_status=f['review_status'],support_status=f['support_status'],observation_count='1')
buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=cols,lineterminator='\n');w.writeheader();w.writerows(rows)
print('*** Begin Patch\n'+patch(M,dump(m))+patch(C,'\ufeff'+buf.getvalue())+'*** End Patch')
