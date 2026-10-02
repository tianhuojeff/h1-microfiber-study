"""Complete saved-text scope, no original-page or legal completion claim."""
from pathlib import Path
import ast,csv,datetime,difflib,hashlib,io,json,subprocess,sys
from local_source import read_anchors
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json';C=R/'data/review_coverage.csv'
BASE='a39d4403abd6cf4baf58bc5eceb01ac04da1d125';PUB='CN118273060A';SID='H1-F91644784'
SRC=H/'team_package_20260928/sources/CN118273060A.html';EXPECTED='3705139d2c2b2357c39e824de5ad1586fe93c2ef22a591a3fdb8a46a92b79bf5'
FIELDS=['cleaning','transfer','chamber_drainage','solids_dewatering','storage','performance','endpoint','carrier_conditioning']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
def baseline(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=H)
def target(m):
    pairs=[s for s in m['samples'] if s['sample_id']==SID and s['representative_publication']==PUB];assert len(pairs)==1
    return pairs[0]
# Load only the previously inspected pure patch function; no predecessor body.
helper=ast.parse((R/'scripts/review_cn118273060_positive_20261002.py').read_text(encoding='utf8'))
function=next(n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name=='patch')
exec(compile(ast.Module(body=[function],type_ignores=[]),'<unique-sample-patch>','exec'))
assert sha(SRC)==EXPECTED
a=read_anchors(SRC);keys=['p'+str(i).zfill(4) for i in range(1,245)]+['zh-cl'+str(i).zfill(4) for i in range(1,20)]
assert len(a)==263 and set(a)==set(keys)
old=json.loads(baseline('corrections/20260929_r1/data/analysis_master.json'));m=json.loads(M.read_text(encoding='utf8'));s=target(m)
if '--verify' in sys.argv:
    assert [z['sample_id'] for z in old['samples']]==[z['sample_id'] for z in m['samples']]
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
                    if field not in ['storage','performance']:
                        assert g['support_status']=='not_located_in_reviewed_scope' and g['observations'][0]['availability_judgment']=='unknown'
            for k in x['review_completeness']:
                if k!='current_scope':assert x['review_completeness'][k]==y['review_completeness'][k]
            assert y['review_completeness']['current_scope'][:-8]==x['review_completeness']['current_scope']
    for k in old:
        if k not in ['samples','updated_at']:assert old[k]==m[k]
    obs=[o for z in m['samples'] for f in z['features'].values() for o in f['observations']];idx={o['observation_id']:o for o in obs}
    prior=[o for z in old['samples'] for f in z['features'].values() for o in f['observations']]
    assert len(obs)==len(idx)==156 and len(prior)==148 and all(idx[o['observation_id']]==o for o in prior)
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
    rel=json.loads((H/'current_release.json').read_text(encoding='utf8'));assert rel['master_sha256']==sha(M) and rel['current_observations']==156
    assert rel['phase']=='P2' and rel['status']=='draft' and not rel['project_completion_accepted']
    assert all(z['sample_role']=='pending' and not z['review_completeness']['full_text_rechecked'] for z in m['samples'])
    assert not m['formal_statistics_allowed'] and not m['final_report_ready']
    rc=s['review_completeness']['complete_saved_text_remaining_fields_20261002'];assert rc['executor_read_anchor_ids']==keys and rc['source_sha256']==sha(SRC)
    assert not rc['original_pdf_checked'] and not rc['drawings_checked']
    assert all(s['features'][f]['observations'] for f in s['features'])
    print(dump({'verified':True,'baseline':BASE,'observations':156,'added':8,'old_148_unchanged':True,'other_13_candidates_unchanged':True,
     'old_target_6_observations_and_field_objects_unchanged':True,'all_legal_evidence_unchanged':True,'master_sha256':sha(M),
     'source_html_sha256':sha(SRC),'all_source_bytes_and_excerpts_verified':True,'CSV_verified':True,'fields':FIELDS,
     'executor_read_anchor_count':263,'executor_read_ranges':['p0001-p0244','zh-cl0001-zh-cl0019'],
     'executor_complete_saved_text_read':True,'read_method':'Four complete normalized saved-HTML blocks read directly by executor; key boundary anchors reread',
     'original_pdf_checked':False,'drawings_checked':False,'source_conflicts_preserved':rc['source_conflicts'],
     'unknown_not_zero':True,'all_14_pending':True,'full_text_complete_count':0,'formal_statistics_allowed':False,
     'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()}));raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
data=[
 ('cleaning',['p0170','p0179','p0191','p0194'],'过滤介质50上的截留物分离/清理动作',
  '完整保存263锚点范围未定位具体洗涤、刷洗、反冲洗或从介质50剥离截留物的操作程序。p0170/0191/0194是维护更换可达性与抽插操纵便利，p0179为机械锁解锁；不能由滤组可取出补成已执行清洗或完整介质再生。限定未定位，未知不填0。','not_located_in_reviewed_scope','unknown'),
 ('transfer',['p0124','p0179','p0194'],'从过滤介质50分離的松散固体向独立收集载体的转移',
  '滤组5与盖4共同抽插是已知载体移出路径（旧removal观察保持）；完整保存263锚点未定位从50卸下松散截留固体并送入独立盒、袋或接收器的步骤。不否认含物滤组移动，也不把整组抽移重写成独立固体转储。限定未定位，未知不填0。','not_located_in_reviewed_scope','unknown'),
 ('chamber_drainage',['p0093','p0171','p0179'],'维护前过滤室20游离液专门排空路径',
  'p0093入口301/出口302属于正常过滤水流。p0171含“水的交叉作用从滑动肋排放到滑动引导件上”原句，但对象/出口/维护状态未明确，保留文字不推专门腔排液；p0179锁解锁未给先排空联锁。完整保存263锚点未定位维护前独立腔排空程序、残液实测或去向；未知不填0。','not_located_in_reviewed_scope','unknown'),
 ('solids_dewatering',['p0042','p0069','p0075','p0192'],'已截留固体附着/夹带水的降低动作',
  '完整保存263锚点未定位针对已截留微塑料/纤维固体的压滤、离心或其他降低附着/夹带水动作。p0042滚筒离心率的对象是洗衣操作，p0069/0075/0192是介质过滤与分区，不能转为滤渣脱水或实测含水率。限定未定位，未知不填0。','not_located_in_reviewed_scope','unknown'),
 ('storage',['p0069','p0075','p0149','p0192'],'过滤介质50及滤组5内含物保留的边界',
  '结合本件既有capture与p0069/0075/0192，捕获载体是组5的介质50，含物可随滤组保留/移出；这只给使用中的载体暂留边界，不补独立松散固体储存盒或长期干储。p0149盒状接合元件409为接合/定心结构，不是收渣盒；未定位另行储存容器、密封长期防漏或储存时间。','same_embodiment_combination','in_filter_carrier_boundary_only'),
 ('performance',['p0183','p0185','p0186','p0191','p0195','p0197'],'维护抽插便利、密封/减力的文本主张',
  '保存文本确述便于前侧或上侧抽插、维护更换简化、气密联接与所需力减小、防错组装等作者主张；前/上侧为各可选位置，不拼唯一动作。完整263锚点未定位本案量化截留率、组装力实测、试验协议/N/误差或独立验证，不把“完全实现目的”或“力被减小”作为已测性能。','explicit','text_claim_only'),
 ('endpoint',['p0170','p0185','p0191','p0194'],'已收集固体/废弃含物介质的最终去向',
  '保存文本给滤组抽插、维护更换便利；完整263锚点未定位取出后固体/含物滤材的垃圾分类、回收设施、销毁或安全环境终点。正常滤液去向不是固体最终处置，移出更换也不证明已完成处置。限定未定位，未知不填0。','not_located_in_reviewed_scope','unknown'),
 ('carrier_conditioning',['p0007','p0041','p0075','p0170','p0191'],'过滤介质50自身排水、干燥或调理动作',
  '完整保存263锚点未定位使用后介质50自身独立排水、干燥或调理步骤。p0007/0041洗衣烘干机一般含干燥功能未将对象指定介质50；p0170/0191更换可达不等于介质干燥。材料泡沫结构、腔正常流路或含物滤组抽出不能推载体已干。限定未定位，未知不填0。','not_located_in_reviewed_scope','unknown')]
for field,quoted,obj,meaning,support,available in data:
    f=s['features'][field];assert not f['observations'] and f['support_status'] is None
    ev=[{'locator':'保存HTML #'+k,'html_anchor':k,'evidence_excerpt':a[k],'source_role':'description_embodiment',
     'subject_role':'this_invention_or_optional_embodiment','source_path':str(SRC),'source_url':'https://patents.google.com/patent/'+PUB+'/zh',
     'source_sha256':sha(SRC),'verified_at':now,'extraction_note':'Saved mirror anchor, not physical page; excerpt supplies object/boundary contrast; unlocated judgment covers all 263 directly reviewed anchors.'} for k in quoted]
    o={'observation_id':PUB+'-'+field+'-complete_saved_scope-20261002','publication_id':PUB,'grant_publication_id':None,'sample_role':'pending',
     'embodiment_id':'complete_saved_scope_distinct_objects','stage':field,'technical_feature':meaning,'object':obj,
     'start':'限定保存文本及明示对象','end':'限定范围裁定，非测得性能或安全终点','boundary':'保存HTML p0001-p0244/zh-cl0001-zh-cl0019；原PDF/附图未核，互斥可选结构不拼接',
     'operation_order':[],'support_status':support,'review_status':'complete_in_stated_saved_text_scope','availability_judgment':available,
     'claim_dependency':'19项全部读；不同从属与实施方式保持独立，未用背景或装配结构补写缺失功能',
     'evidence':ev,'interpretation':meaning,'performance_status':'text_claim_only' if field=='performance' else 'not_verified',
     'verified_at':now,'old_value':f['prior_field'],'new_value':meaning,'change_reason':'本人完整保存文本范围回读，补空字段边界裁定；原值、法律及未知门槛保持。',
     'removal_kind':None,'reviewed_anchor_ranges':['p0001-p0244','zh-cl0001-zh-cl0019']}
    f['observations'].append(o);f['review_status']='complete_saved_text_scope';f['support_status']=support
    s['review_completeness']['current_scope'].append({'publication':PUB,'anchors':keys,'field':field,'at':now})
s['review_completeness']['complete_saved_text_remaining_fields_20261002']={'source_path':str(SRC),'source_sha256':sha(SRC),
 'executor_read_anchor_ids':keys,'description_anchors':244,'claim_anchors':19,'executor_complete_saved_text_read':True,
 'read_method':'Four complete normalized saved-HTML blocks directly read; key boundary anchors reread','fields_added':FIELDS,
 'original_pdf_checked':False,'drawings_checked':False,'not_a_full_text_completion':True,'verified_at':now,
 'source_conflicts':['p0134 protrusion406/groove516 vs zh-cl0009 groove406/protrusion516; p0216/p0229 both slots',
 'p0147 sidewall52/p0174 bottomwall52 vs zh-cl0010 sidewall513/bottom512',
 'p0176 medium2 vs medium50; p0181/p0182 pump560 vs pump960; original PDF/figures needed, no silent correction']}
m['updated_at']=now
rows=list(csv.DictReader(C.read_text(encoding='utf-8-sig').splitlines()));cols=rows[0].keys()
for row in rows:
    if row['sample_id']==SID and row['publication']==PUB and row['field'] in FIELDS:
        f=s['features'][row['field']];row.update(review_status=f['review_status'],support_status=f['support_status'],observation_count='1')
buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=cols,lineterminator='\n');w.writeheader();w.writerows(rows)
print('*** Begin Patch\n'+patch(M,dump(m))+patch(C,'\ufeff'+buf.getvalue())+'*** End Patch')
