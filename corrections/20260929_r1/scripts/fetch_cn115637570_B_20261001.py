"""Fetch a public original response into a binary ZIP; authored text is emitted as a patch."""
from pathlib import Path
import datetime,hashlib,json,re,sys,urllib.request,zipfile
from local_source import Anchors
H=Path(__file__).resolve().parents[3];R=H/'corrections/20260929_r1'
url='https://patents.google.com/patent/CN115637570B/zh'
target=R/'sources/CN115637570B_raw_html_20261001.zip'
def digest(data):return hashlib.sha256(data).hexdigest()
def parse(data):
    parser=Anchors();parser.feed(data.decode('utf-8'))
    return {r['anchor']:r['text'] for r in parser.rows}
if '--verify' in sys.argv:
    manifest=json.loads((R/'sources/CN115637570B_source_manifest_20261001.json').read_text(encoding='utf-8'))
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        raw=archive.read('CN115637570B.html')
    assert digest(raw)==manifest['response_sha256'] and digest(target.read_bytes())==manifest['archive_sha256']
    snapshot=json.loads((R/'sources/CN115637570B_anchors_20261001.json').read_text(encoding='utf-8'))
    assert parse(raw)==snapshot['anchors']
    assert len([k for k in snapshot['anchors'] if k.startswith('cl') or '-cl' in k])==10
    assert not manifest['original_pdf_saved'] and not manifest['current_validity_verified']
    print(json.dumps({'verified':True,'archive_sha256':manifest['archive_sha256'],'original_response_sha256':digest(raw),'anchors':len(snapshot['anchors']),'claims':10,'original_pdf_saved':False,'all_qualification_pending':True},ensure_ascii=False))
    raise SystemExit
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
response=urllib.request.urlopen(url,timeout=30)
raw=response.read();text=raw.decode('utf-8');raw_digest=digest(raw)
target.parent.mkdir(exist_ok=True)
assert not target.exists(), 'Do not overwrite original response'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as archive:
    archive.writestr('CN115637570B.html',raw)
anchors=parse(raw)
pdf_links=re.findall(r'<meta\s+name="citation_pdf_url"\s+content="([^"]+)"',text)
manifest={'retrieved_at':now,'retrieval_url':url,'response_final_url':response.url,'response_status':response.status,
    'response_bytes':len(raw),'response_sha256':raw_digest,'archive_path':str(target),'archive_member':'CN115637570B.html','archive_sha256':digest(target.read_bytes()),
    'source_role':'Google Patents grant-version HTML mirror; original response preserved byte-for-byte in ZIP',
    'citation_pdf_links':pdf_links,'original_pdf_saved':False,'current_validity_verified':False,'qualification':'pending',
    'actual_queries':['"CN115637570B" filetype:pdf','"CN115637570B" 专利 pdf'],
    'search_scope':'定向真实查询；搜索页与GP返回未提供可下载B PDF链接，不能视为PDF不存在',
    'search_result_count':None,'genuine_search_screenshot_saved':False,'no_login_or_account_changes':True,
    'earlier_shell_attempt':'首次只读提取命令PowerShell正则引号解析错误；整段零执行，无网络请求/文件改动。随后改为此独立脚本从请求开始重跑。',
    'supports':'保存B镜像文本版本，待原PDF对照；既有CNIPA原ZIP B公告事实独立保留',
    'does_not_support':'现时有效、年费、终止事件、原PDF/图页、正式统计或整套P2完成'}
snapshot={'source_archive':str(target),'source_sha256':raw_digest,'retrieved_at':now,'source_role':'literal normalized anchor projection of saved HTML mirror','anchors':anchors}
print('*** Begin Patch')
for path,value in [(R/'sources/CN115637570B_source_manifest_20261001.json',manifest),(R/'sources/CN115637570B_anchors_20261001.json',snapshot)]:
    print('*** Add File: '+str(path).replace('\\','/'))
    print('\n'.join('+'+line for line in json.dumps(value,ensure_ascii=False,indent=2).splitlines()))
print('*** End Patch')
