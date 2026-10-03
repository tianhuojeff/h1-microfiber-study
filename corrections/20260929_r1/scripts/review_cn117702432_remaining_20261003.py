"""CN117 complete saved HTML scope; no physical page or eligibility completion claim."""
from pathlib import Path
import ast,csv,datetime,difflib,hashlib,io,json,subprocess,sys
from local_source import read_anchors
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json';C=R/'data/review_coverage.csv'
BASE='bf95975fac9c8a6ba3aa8568fe8a477a49103030';PUB='CN117702432A';SID='H1-F90159083'
SRC=H/'team_package_20260928/sources/CN117702432A.html';EXPECTED='9fa4ff02688811243b49ac3fee8c9c6f5f4966f7dd72f06e01d7663c07714438'
FIELDS=['cleaning','transfer','chamber_drainage','solids_dewatering','storage','performance','endpoint','carrier_conditioning']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def baseline(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=H)
def target(m):
    out=[s for s in m['samples'] if s['sample_id']==SID and s['representative_publication']==PUB];assert len(out)==1
    return out[0]
helper=ast.parse((R/'scripts/review_cn118273060_positive_20261002.py').read_text(encoding='utf8'))
function=next(n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='patch')
exec(compile(ast.Module(body=[function],type_ignores=[]),'<unique-sample-patch>','exec'))
a=read_anchors(SRC);keys=['p'+str(i).zfill(4) for i in range(1,80)]+['zh-cl'+str(i).zfill(4) for i in range(1,11)]
assert sha(SRC)==EXPECTED and len(a)==89 and set(a)==set(keys)
old=json.loads(baseline('corrections/20260929_r1/data/analysis_master.json'));m=json.loads(M.read_text(encoding='utf8'));s=target(m)
if '--verify' in sys.argv:
    assert len(m['samples'])==len(old['samples'])==14 and [z['sample_id'] for z in m['samples']]==[z['sample_id'] for z in old['samples']]
    for x,y in zip(old['samples'],m['samples']):
        if x['sample_id']!=SID:assert x==y
        else:
            for k in x:
                if k not in ['features','review_completeness']:assert x[k]==y[k]
            for field,f in x['features'].items():
                g=y['features'][field]
                if field not in FIELDS:assert f==g
                else:
                    assert not f['observations'] and f['prior_field']==g['prior_field'] and len(g['observations'])==1
                    if field not in ['cleaning','storage','performance']:
                        assert g['support_status']=='not_located_in_reviewed_scope' and g['observations'][0]['availability_judgment']=='unknown'
            for k in x['review_completeness']:
                if k!='current_scope':assert x['review_completeness'][k]==y['review_completeness'][k]
            assert y['review_completeness']['current_scope'][:-8]==x['review_completeness']['current_scope']
    for k in old:
        if k not in ['samples','updated_at']:assert old[k]==m[k]
    obs=[o for z in m['samples'] for f in z['features'].values() for o in f['observations']];idx={o['observation_id']:o for o in obs}
    prior=[o for z in old['samples'] for f in z['features'].values() for o in f['observations']]
    assert len(obs)==len(idx)==167 and len(prior)==159 and all(idx[o['observation_id']]==o for o in prior)
    cache={}
    for o in obs:
        for e in o['evidence']:
            p=Path(e['source_path']);assert sha(p)==e['source_sha256']
            if e.get('html_anchor'):
                if str(p) not in cache:cache[str(p)]=read_anchors(p)
                assert e['evidence_excerpt'] in cache[str(p)][e['html_anchor']]
            else:assert sha(Path(e['page_image_path']))==e['page_image_sha256']
    before=list(csv.DictReader(baseline('corrections/20260929_r1/data/review_coverage.csv').decode('utf-8-sig').splitlines()))
    after=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()));assert len(before)==len(after)==182
    for x,y in zip(before,after):
        if x['sample_id']!=SID or x['field'] not in FIELDS:assert x==y
        f=next(z for z in m['samples'] if z['sample_id']==y['sample_id'])['features'][y['field']]
        assert y['review_status']==f['review_status'] and y['support_status']==(f['support_status'] or '') and int(y['observation_count'])==len(f['observations'])
    rel=json.loads((H/'current_release.json').read_text(encoding='utf8'));assert rel['current_observations']==167 and rel['master_sha256']==sha(M)
    assert rel['phase']=='P2' and rel['status']=='draft' and not rel['project_completion_accepted']
    assert all(z['sample_role']=='pending' and not z['review_completeness']['full_text_rechecked'] for z in m['samples'])
    assert not m['formal_statistics_allowed'] and not m['final_report_ready']
    rc=s['review_completeness']['complete_saved_text_remaining_fields_20261003']
    assert rc['executor_read_anchor_ids']==keys and rc['source_sha256']==sha(SRC) and not rc['original_pdf_checked'] and not rc['drawings_checked']
    assert all(s['features'][f]['observations'] for f in s['features'])
    print(dump({'verified':True,'baseline':BASE,'observations':167,'added':8,'old_159_unchanged':True,'other_13_candidates_unchanged':True,
    'old_target_5_observations_and_fields_unchanged':True,'all_legal_evidence_unchanged':True,'master_sha256':sha(M),'source_html_sha256':sha(SRC),
    'all_source_bytes_and_excerpts_verified':True,'CSV_verified':True,'fields':FIELDS,'executor_read_anchor_count':89,
    'executor_read_ranges':['p0001-p0079','zh-cl0001-zh-cl0010'],'executor_complete_saved_text_read':True,
    'read_method':'Two complete description blocks and all claims read directly by executor; no missing normalized anchors',
    'original_pdf_checked':False,'drawings_checked':False,'unknown_not_zero':True,'all_14_pending':True,'full_text_complete_count':0,
    'formal_statistics_allowed':False,'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()}));raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
data=[
('cleaning',['p0058','p0059','p0060','p0076'],'过滤网320清理可达性与清理方法的区别',
 'p0059明确分体盒体方便取出过滤网320进行清理，p0060有安装滑槽；这是清理可达性正向披露。完整保存89锚点未定位实际洗刷、反冲洗、剥离沉积物操作程序或清理后网孔再生测试。切换其他腔延长清理周期不等于原网已自清洁；保留旧字段原值，以本次正向清理用途纠偏，不将可达性冒充完整清洗工序。','explicit','cleaning_access_only_no_method'),
('transfer',['p0054','p0055','p0059'],'从过滤网分离松散固体并送至独立收集载体',
 '过滤腔/网320内堆积与取出滤网清理已披露，旧removal保持。完整保存89锚点未定位把截留松散固体从网面卸下并向专用收集盒、袋或处理位置转储的动作、接口或顺序；不否认含物载体移出，不把水流导向或拆取滤网改成独立固体转移。限定保存全文未定位，未知不填0。','not_located_in_reviewed_scope','unknown'),
('chamber_drainage',['p0053','p0059','p0067','p0074'],'维护前过滤腔313游离液排空',
 'p0059底壁或侧壁出口以及p0074重力过网出水都是正常过滤液流；p0067阀转动选通另一腔。完整保存89锚点未定位维护前专门腔排空、排空联锁、残液实测或独立维护排液路线，不能从底部出口与可拆盖推先排干再开盖。限定未定位，未知不填0。','not_located_in_reviewed_scope','unknown'),
('solids_dewatering',['p0044','p0054','p0055','p0059'],'已截留固体夹带水的降低动作',
 '完整保存89锚点未定位针对滤网320截留微塑料的压实、离心、压滤或降低附着/夹带水动作。p0044滚筒运动/烘干对象为衣物，正常出口水流对象为过滤水，不能推滤渣脱水、沥干或实测含水率。限定未定位，未知不填0。','not_located_in_reviewed_scope','unknown'),
('storage',['p0054','p0055','p0057'],'被选通腔313及过滤网320内截留物暂留',
 'p0054明确某腔微塑料堆积过多使压力升高；p0055对应网实现过滤与收集，p0057堵塞后其他腔启用。可记截留物在使用中的腔/滤网上暂留，不能把未选通腔直接改专用储渣盒或长期密封干储。完整保存89锚点未定位独立固体储存容器、容量、储存期限或防漏实测。','same_embodiment_combination','in_filter_carrier_boundary_only'),
('performance',['p0007','p0030','p0058','p0068','p0070','p0075','p0076'],'延长清理周期和寿命等文本效果主张',
 '本件明确作者主张腔切换延长清理周期/寿命、减少清理损伤、提高过滤精度；p0070四腔四级为示例，p0075孔径大小关系为结构限定。完整保存89锚点未定位本案量化捕获率、使用寿命/周期实测、阈值数值或试验协议/N/误差/独立验证。背景35%为海洋来源报告，不能作本装置效率；文本效果主张与已测性能分开。','explicit','text_claim_only'),
('endpoint',['p0048','p0055','p0059'],'截留固体或含物废滤件的后续处置',
 'p0059给取出滤网进行清理；完整保存89锚点未定位截留固体/废弃含物滤件取出后的垃圾分类、回收设施、销毁或安全环境终点。p0048下水道排放或回本体供水再利用的对象是经过过滤的水，不是固体最终处置；不把可清理/拆取写成处置已完成。限定未定位，未知不填0。','not_located_in_reviewed_scope','unknown'),
('carrier_conditioning',['p0044','p0059','p0060','p0074'],'过滤网320自身排水或干燥工序',
 '完整保存89锚点未定位使用后过滤网320自身独立排水、干燥或调理步骤。p0044衣物烘干不是滤网干燥，p0059取出清理/正常水流与p0060安装滑槽也不证明载体已排干。限定未定位，未知不填0。','not_located_in_reviewed_scope','unknown')]
for field,quoted,obj,meaning,support,available in data:
    f=s['features'][field];assert not f['observations'] and f['support_status'] is None
    ev=[{'locator':'保存HTML #'+k,'html_anchor':k,'evidence_excerpt':a[k],'source_role':'description_embodiment' if k not in ['p0044'] else 'general_washing_context',
    'subject_role':'this_invention_or_object_boundary','source_path':str(SRC),'source_url':'https://patents.google.com/patent/'+PUB+'/zh',
    'source_sha256':sha(SRC),'verified_at':now,'extraction_note':'Saved HTML anchor, not physical page; contrast excerpts do not individually prove absence; unlocated judgment covers all 89 read anchors.'} for k in quoted]
    f['observations'].append({'observation_id':PUB+'-'+field+'-complete_saved_scope-20261003','publication_id':PUB,'grant_publication_id':None,'sample_role':'pending',
    'embodiment_id':'saved_scope_distinct_filter_and_washing_objects','stage':field,'technical_feature':meaning,'object':obj,'start':'保存全文及明示对象限定',
    'end':'限定范围裁定，非测得性能或安全终点','boundary':'p0001-p0079/zh-cl0001-zh-cl0010；原PDF图未核；示例和不同选项不作全部必需',
    'operation_order':[],'support_status':support,'review_status':'complete_in_stated_saved_text_scope','availability_judgment':available,
    'claim_dependency':'全10项权利要求已读，各从属关系保留；未把正常过滤出水或衣物处理补成固体/载体功能',
    'evidence':ev,'interpretation':meaning,'performance_status':'text_claim_only' if field=='performance' else 'not_verified','verified_at':now,
    'old_value':f['prior_field'],'new_value':meaning,'change_reason':'完整保存文本范围补空字段及对象边界，旧值保留，未知非0。',
    'removal_kind':None,'reviewed_anchor_ranges':['p0001-p0079','zh-cl0001-zh-cl0010']})
    f['review_status']='complete_saved_text_scope';f['support_status']=support
    s['review_completeness']['current_scope'].append({'publication':PUB,'anchors':keys,'field':field,'at':now})
s['review_completeness']['complete_saved_text_remaining_fields_20261003']={'source_path':str(SRC),'source_sha256':sha(SRC),
'executor_read_anchor_ids':keys,'description_anchors':79,'claim_anchors':10,'executor_complete_saved_text_read':True,
'read_method':'Two complete description blocks and all claims directly read','fields_added':FIELDS,
'original_pdf_checked':False,'drawings_checked':False,'not_a_full_text_completion':True,'verified_at':now}
m['updated_at']=now
rows=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()));cols=rows[0].keys()
for row in rows:
    if row['sample_id']==SID and row['publication']==PUB and row['field'] in FIELDS:
        f=s['features'][row['field']];row.update(review_status=f['review_status'],support_status=f['support_status'],observation_count='1')
buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=cols,lineterminator='\n');w.writeheader();w.writerows(rows)
print('*** Begin Patch\n'+patch(M,dump(m))+patch(C,'\ufeff'+buf.getvalue())+'*** End Patch')
