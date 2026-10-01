"""Saved A/B mirror comparison; emit authored patches, read-only QA mode."""
from pathlib import Path
import copy,datetime,difflib,hashlib,json,subprocess,sys,zipfile
from local_source import read_anchors,Anchors
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1';M=R/'data/analysis_master.json'
BASE='6293443625854f63e131e2425d40816067171f2a';PUB='CN115637570A'
A=H/'team_package_20260928/sources/CN115637570A.html';Z=R/'sources/CN115637570B_raw_html_20261001.zip'
J=R/'data/CN115637570_AB_version_comparison_20261001.json';Q=R/'QA/CN115637570_AB_version_comparison_20261001.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'
a=read_anchors(A)
with zipfile.ZipFile(Z) as z:
    assert z.testzip() is None and z.namelist()==['CN115637570B.html'];raw=z.read('CN115637570B.html')
assert hashlib.sha256(raw).hexdigest()=='76d837f030c713c373857d60db89e55c7b679d46f5aee61504f0a490d50ddcff'
p=Anchors();p.feed(raw.decode('utf-8'));b={r['anchor']:r['text'] for r in p.rows}
assert b==json.loads((R/'sources/CN115637570B_anchors_20261001.json').read_text(encoding='utf-8'))['anchors']
old=json.loads(subprocess.check_output(['git','show',BASE+':corrections/20260929_r1/data/analysis_master.json'],cwd=H));m=json.loads(M.read_text(encoding='utf-8'))
if '--verify' in sys.argv:
    comparison=json.loads(J.read_text(encoding='utf-8'))
    for src,key in [(a,'A_claims'),(b,'B_claims')]:
        assert comparison[key]=={k:v for k,v in src.items() if 'cl' in k}
    assert comparison['A_source_sha256']==sha(A) and comparison['B_archive_sha256']==sha(Z)
    before=copy.deepcopy(old);after=copy.deepcopy(m)
    assert before['updated_at']!=after['updated_at'];after['updated_at']=before['updated_at']
    target=next(s for s in after['samples'] if s['representative_publication']==PUB)
    review=target['review_completeness'].pop('saved_AB_version_comparison')
    assert review['report_sha256']==sha(J) and not review['original_B_pdf_read']
    assert before==after
    assert len([o for s in m['samples'] for f in s['features'].values() for o in f['observations']])==91
    rel=json.loads((H/'current_release.json').read_text(encoding='utf-8'));assert rel['master_sha256']==sha(M) and not rel['project_completion_accepted']
    assert all(s['sample_role']=='pending' for s in m['samples']) and not m['formal_statistics_allowed']
    assert comparison['description_differences']==[{ 'anchor':k,'A':a[k],'B':b[k]} for k in a if k.startswith('p') and a[k]!=b[k]]
    print(dump({'verified':True,'baseline':BASE,'master_sha256':sha(M),'comparison_sha256':sha(J),'observations_unchanged':91,
        'all_14_legal_evidence_unchanged':True,'other_13_candidates_unchanged':True,'original_B_pdf_read':False,'formal_statistics_allowed':False}))
    raise SystemExit
assert m==old
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
c={'checked_at':now,'scope':'保存A/B镜像正文84锚点与各10项；A已有原PDF核对，B原PDF仍缺，不作授权范围法律意见',
   'A_source_path':str(A),'A_source_sha256':sha(A),'B_archive_path':str(Z),'B_archive_sha256':sha(Z),'B_response_sha256':hashlib.sha256(raw).hexdigest(),
   'A_claims':{k:v for k,v in a.items() if 'cl' in k},'B_claims':{k:v for k,v in b.items() if 'cl' in k},
   'description_differences':[{'anchor':k,'A':a[k],'B':b[k]} for k in a if k.startswith('p') and a[k]!=b[k]],
   'decisions':[
    {'A_anchors':['cl0001','cl0002','cl0003','cl0008'],'B_anchors':['zh-cl0001'],'finding':'保存B权1同时写入上部进水/下部出水、筒状周向网和螺杆在网内、上下不等间隙及可拆袋。A权1未包含这些全部限制；分别在A权2、权3、权8，不能把A独立项当B独立项。'},
    {'A_anchors':['cl0004','cl0005'],'B_anchors':['zh-cl0001'],'finding':'A权4全上部敞开和权5进水处局部敞开为不同从属分支；保存B的10项没有对应敞开条款，描述p0024—p0028/p0064—p0068仍保留。描述保留不等于这些条款仍作为B的独立或从属权项。'},
    {'A_anchors':['cl0006','p0071','p0072','p0073'],'B_anchors':['zh-cl0002','zh-cl0003','zh-cl0004'],'finding':'B权2驱动电机依附权1，权3传感器/控制器依附权2，权4间歇驱动依附权3；A权6为电机，传感器/间歇驱动位于说明书。这条依附链不能与B权1必要结构混写。'},
    {'A_anchors':['cl0007','cl0008'],'B_anchors':['zh-cl0001','zh-cl0005','zh-cl0006','zh-cl0007'],'finding':'B权5另限制袋在收集装置内侧壁周向设置；可拆袋已写B权1。B权6耐磨依权1—5任一，权7不锈钢依权6；与A权7耐磨/优选不锈钢和权8可拆袋的编号不同。'},
    {'A_anchors':['cl0009','cl0010','p0083'],'B_anchors':['zh-cl0008','zh-cl0009','zh-cl0010'],'finding':'B权8洗衣机依权1—7任一，权9前面板安装口/对应可拆收集装置依权8，权10对应门盖依权9；A权9/10为洗衣机/安装口，门盖位于A说明书。不能引用A权10证明B权10的门盖条款。'},
    {'A_anchors':['p0079'],'B_anchors':['p0079'],'finding':'保存A/B该段均写更换过滤网122；不擅改成更换袋。另有p0083取袋清理，仍不提供最终处置/脱水测试。'}],
   'limitations':['B来源是保存聚合镜像，原PDF/图和当前法律资格仍pending','未把镜像Active当有效','不新增样本或重复计数同族观察','全体91条原观察/法律证据保持原值','文字版本对照不自动成为正式统计或法律保护范围结论']}
s=next(x for x in m['samples'] if x['representative_publication']==PUB)
s['review_completeness']['saved_AB_version_comparison']={'checked_at':now,'report_path':str(J),'report_sha256':hashlib.sha256(dump(c).encode()).hexdigest(),'B_claims_read':list(range(1,11)), 'B_description_anchors_read':list(k for k in b if k.startswith('p')),'original_B_pdf_read':False,'qualification_pending':True}
m['updated_at']=now
print('*** Begin Patch')
print('*** Add File: '+str(J).replace('\\','/'));print('\n'.join('+'+l for l in dump(c).splitlines()))
print('*** Update File: '+str(M).replace('\\','/'))
for l in list(difflib.unified_diff(dump(old).splitlines(),dump(m).splitlines(),n=3))[2:]:print('@@' if l.startswith('@@') else l)
body='# CN115637570 A/B 保存文本版本复核\n\n'+c['scope']+'。不新增观察、不改变资格。\n\n'
for i,d in enumerate(c['decisions'],1):body+=str(i)+'. '+d['finding']+' 定位：A '+','.join(d['A_anchors'])+'；B '+','.join(d['B_anchors'])+'。\n\n'
body+='说明书逐锚点差异 '+str(len(c['description_differences']))+' 处，完整原句和20项权项见 ../data/'+J.name+'。B原PDF与附图待核，不凭保存文字声明整个候选全文验收。\n'
print('*** Add File: '+str(R/'evidence/CN115637570_AB_version_readback_20261001.md').replace('\\','/'));print('\n'.join('+'+l for l in body.splitlines()));print('*** End Patch')
