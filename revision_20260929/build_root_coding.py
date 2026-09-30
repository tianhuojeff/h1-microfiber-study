"""Materialize source-anchored manual coding of the four review counterexamples."""
from pathlib import Path
import json
from extract_patent_html import extract

BASE=Path(__file__).resolve().parent
PROJECT=BASE.parent.parent
CORPUS=json.loads((PROJECT/'h1-study/patents/training_20260927/current_corpus.json').read_text(encoding='utf-8'))
META={x['publication']:x for x in CORPUS}
KEYS=['cleaning','transfer','solids_dewatering','chamber_drainage','liquid_route','removal','state_switch','seals_connections','endpoint']
RECORDS=[]

def make(pub):
    global CURRENT,ROWS,DOC
    DOC=extract(PROJECT/'h1-study/team_package_20260928/sources'/f'{pub}.html')
    ROWS={x['id']:x for x in DOC['rows'] if x['id']}
    CURRENT={'publication':pub,'family_id':META[pub]['family_id'],'reviewed_version':pub,
             'legal_status_as_of':'unknown','analysis_date':'2026-09-29',
             'sources':[dict(source_path=DOC['source_path'],source_sha256=DOC['source_sha256'],url=META[pub]['source_url'],source_kind='saved_publication_full_text_mirror')],
             'fields':{},'sequence':[],'boundary_notes':['仅对所列公开文本技术披露编码；官方当前有效状态及授权版本仍待核。','技术结构/步骤披露不等于实施效果实证。']}
    RECORDS.append(CURRENT)

def field(key,summary,ids=(),judgment='explicit',reason=''):
    ev=[]
    for i in ids:
        row=ROWS[i]
        num=row['num']
        loc=('权利要求'+str(int(num))) if row['type']=='claim' else ('说明书['+num.lstrip('n')+']' if num else '说明书HTML段'+i)
        ev.append({'source_path':DOC['source_path'],'source_sha256':DOC['source_sha256'],'locator':loc,'html_id':i,'quote':row['text'],'evidence_type':row['type']})
    CURRENT['fields'][key]={'judgment':judgment,'summary':summary,'evidence':ev,'unknown_reason':reason,
                            'review_scope':'本版本权利要求及本记录引用的说明书段落；未引用实施例未作穷尽性否定。'}

def seq(variant,steps,ids,certainty='explicit'):
    CURRENT['sequence'].append({'variant':variant,'steps':steps,'evidence_locators':ids,'ordering_certainty':certainty})

make('CN112914464A')
field('cleaning','泵31经反冲洗管线42和入口27反冲洗主过滤设备26；不是仅有容器移除。',['p0055'])
field('transfer','反冲洗使过滤物质从过滤设备26经管线44转移至转换抽屉内的过滤物质容器；带液转移。',['p0055','p0057'])
field('solids_dewatering','可选实施例在收集容器底设置额外过滤器62及底部出口，使水流走并回导水装置，以浓缩/增稠并减少过滤物质含水量；属于收集后分离，非所有实施例必有。',['p0058'])
field('chamber_drainage','权22排空的是过滤物质容器内容物；当前所审段未落实单独的维护前腔体残液排空程序，不能将权22直接归为残液排空。',['cl0022','p0058'],'unresolved','待查其他实施例是否另有明确排空程序；收集物排空和腔内残液排空不同。')
field('liquid_route','主过滤出水经水管29、泵31，可排至流出物18或返回滚筒/抽屉；反冲洗支路送过滤物质至容器；可选二次过滤水回导水装置/水管22。',['p0053','p0054','p0055','p0058'])
field('removal','权22明示过滤物质容器移除及排空/移除后排空；权23为整体结构单元移除后机械拆分容器；权25柔性双腔袋移除；不同实施方式分别保留。',['cl0022','cl0023','cl0025','cl0026'])
CURRENT['fields']['removal'].update(removal_object=['collection_chamber','collection_bag'],integrated_or_separate='可单独容器、双腔袋或完整结构单元；非同一实施例全部并存',text_disclosed_only=True)
field('state_switch','控制器驱动泵及阀33/38，切换排水、回水和反冲洗；后续由用户按填充水平指示移除容器。',['p0054','p0055','cl0021','cl0022'])
field('seals_connections','袋的可闭合通路、内外连接件密封；权28明示袋移除后关闭通路，新袋插入前打开用于连接。',['cl0016','cl0017','cl0028'])
field('endpoint','处置、交处置公司或清洁后重复使用为公开操作方案；未给最终环境处置效果试验。',['cl0023','cl0025','cl0027'])
seq('图1反冲洗与图2可选二次过滤支路',['过滤设备26截留','阀切至反冲洗，泵使颗粒带液进入收集容器','可选额外过滤器62让水返回、过滤物质浓缩','容器移除/排空（具体整体/分体结构另选）'],['p0055','p0057','p0058','cl0022'],'inferred')
seq('权22—24分体移除方法',['从用具移除整个结构单元','机械拆分容器','处置或交处置公司，替换空过滤物质容器','结构单元插回用具'],['cl0022','cl0023','cl0024'])

make('CN115637570A')
field('cleaning','螺杆带动螺旋叶片，清除/搅动滤网沉积微纤维；刮送与清理由同一旋转动作实现，但叶片与网有间隙。',['cl0001','p0057','p0062'])
field('transfer','叶片旋进方向与水流同向，借助水流把微纤维刮送至靠近出水口的收集装置；不能写成干态螺旋输送。',['cl0001','p0057','p0059'])
field('solids_dewatering','未在已核权项和相关实施段落实专门降低收集物含水量的动作；过滤袋及出水口本身不足以证明脱水。',[],'unresolved','尚未穷尽所有实施细节；不将正常过滤等同收集物脱水。')
field('chamber_drainage','未在已核段落实取袋前腔体排空程序。',[],'unresolved','门盖取袋披露不说明取出前残液如何排空。')
field('liquid_route','进水口进入滤网内部，过滤水经筒下部与网之间排水流道至出水口；收集物受水流辅助迁移。',['cl0001','p0061','p0063'])
field('removal','权8可拆过滤袋与说明书[0078]开前门取出过滤袋/微纤维过滤器清理，共同支持文本移出路径。',['cl0008','p0082','p0083'])
CURRENT['fields']['removal'].update(removal_object=['collection_bag','filter_element'],integrated_or_separate='过滤袋位于收集装置内；也允许取出过滤器，属于不同取出对象',text_disclosed_only=True)
field('state_switch','可选传感器检测积聚量，控制器启停电机进行间歇旋转清理；不据此推断取袋时阀门联锁。',['p0071','p0072','p0073'])
field('seals_connections','前面板安装口/门盖提供取袋或过滤器通道；该段未明确密封件和水管拆接顺序。',['cl0010','p0082','p0083'])
field('endpoint','文本给取出清理安排，未在所核段说明清理后纤维最终处置方式。',['p0083'],'unresolved','取袋不自动证明不滴漏或安全处置。')
seq('螺旋水辅助刮送与前门维护',['水流进入并经过滤网','螺杆旋转，清理与送往收集装置合并','袋积累微纤维后经前门取出清理'],['p0057','p0061','p0073','p0079','p0083'],'inferred')
CURRENT['boundary_notes'].append('说明书[0074]在过滤袋积聚语境中写“更换过滤网122”，保留原文疑点，取袋结论以[0078]为直接依据。授权B版须另行比对，不能把A版权8复制为B版权8。')

make('CN222043626U')
field('cleaning','明确取盒/取网后进行人工清理的维护安排；未披露自动清网机构，具体除渣动作仍未限定。',['p0057','p0064','p0068'],'unresolved','人工清理意图明确，但主过滤表面的具体去除动作待核，不能编码自动清理。')
field('transfer','微塑料在盒内过滤网上就地拦截；取盒是维护移出，未在所核段找到从主滤面到另一独立收集位置的转移机构。',['zh-cl0001','p0053','p0055'],'unresolved','进水带颗粒入盒不等同截留后独立转移。')
field('solids_dewatering','收集盒网孔及双滤网用于过滤；当前所核段没有独立降低已收集固体含水量的操作说明。',['p0054','p0073'],'unresolved','不能仅凭滤网/网孔归为脱水。')
field('chamber_drainage','所核维护段未给拆盖取盒前排空腔内液体的程序。',[],'unresolved','正常排水通路不等同维护排空。')
field('liquid_route','洗衣机排水管→壳体第一进水口→盒第二进水口→过滤网→第二/第一出水口→排水管；另一实施例盒整体为网孔结构。',['zh-cl0001','zh-cl0009','p0044','p0053','p0066','p0073'])
field('removal','拆开盖板露出收集盒供用户取出；安装管沿滑槽装入/拆出盒体；无需拆开壳体与排水管连接即清理。',['zh-cl0007','p0053','p0064','p0071'])
CURRENT['fields']['removal'].update(removal_object=['collection_box','combined_filter_collector'],integrated_or_separate='盒可脱离壳体，但过滤网在盒内，非主滤网之外的独立集渣袋',text_disclosed_only=True)
field('state_switch','维护时拆盖、取盒；装回盒后盖板连接且密封进入过滤状态；进出水关闭或联锁顺序未明确。',['p0064','p0071','p0072'])
field('seals_connections','盖板与主壳可拆，卡扣连接；可加密封圈；盒滑槽/弹性件限位。明确无需拆壳体与排水管连接。',['zh-cl0005','p0053','p0064','p0071','p0072'])
field('endpoint','可拆盒便于统一清理，但所核段未给盒内纤维清理后的最终去向。',['p0053'],'unresolved','不能将可拆出清理扩展为环保最终处置实证。')
seq('可拆盒实施方式',['排水经盒内滤网就地拦截','拆开盖板','取出收集盒进行清理','安装管沿滑槽装入并限位','盖板连接密封恢复过滤'],['zh-cl0001','p0064','p0071','p0072'],'inferred')

make('CN115087774A')
field('cleaning','板移动收集并压实微塑料；不能据此认定主滤网再生，所核段未说明滤面清理动作。',['cl0001','cl0024'],'unresolved','压实分水与滤网清理分栏；没有将压实编码为再生。')
field('transfer','板向压缩位移动收集/挤压微塑料，返程释放或使固体与排放口对准，再排出。',['cl0001','p0059','p0065'])
field('solids_dewatering','权24驱动板穿过流出物以分离水并压缩微塑料；实施例板/腔壁可透水并挤出剩余液体。',['cl0024','p0057','p0068'])
field('chamber_drainage','说明书[0066]自动排放实施例明示板返程及其余废水排出打开排放口；这支持该阶段排出残余废水，未证明整个腔完全干燥。',['p0071'])
field('liquid_route','透水板后部排水通道208、透水后壁通道212等为可选方案；图8—9实施例入口/出口止回阀、压缩冲程泵出废水并可经管804回系统再过滤。',['cl0018','cl0019','p0057','p0074'])
field('removal','权1由板运动通过排放出口自动排出压缩微塑料，权24给分水—回程—排放；说明书另述开活板门/可拆盖取出与自动掉落方案。',['cl0001','cl0024','p0056','p0071'])
CURRENT['fields']['removal'].update(removal_object=['loose_or_compacted_solids'],integrated_or_separate='直接排出压缩固体，非取走收集盒；下游容器非本段必要限定',text_disclosed_only=True)
field('state_switch','图3入口阀开启接收流出物/排放口关闭，板压缩后返程并打开出口；图6两板与锁存器产生压缩、回程掉落、复位；图8—9止回阀方案单列。',['p0054','p0055','p0070','p0074'])
field('seals_connections','排放出口可由透水翻板或可拆卸盖关闭；入口翻板防压缩时逆向逸出，止回阀属于另一具体布置。',['cl0022','p0057','p0074'])
field('endpoint','压缩成块便于用户处置为文本陈述；所核段未确定最终处置介质/设施或环境绩效。',['p0055'],'unresolved','易处置的设计主张不是处置效果测量。')
seq('权24基本方法',['接收流出物','板由非压缩位置到压缩位置以分水并压缩','板返回非压缩位置','排放压缩微塑料'],['cl0024'])
seq('图6双板锁存方案',['透水板收集纤维并由废水出口排水','两板压缩挤出剩余液体','第一板返程，第二板锁存，固体掉落','解锁第二板复位'],['p0068','p0070'])
seq('图8—9止回阀回路',['回程抽吸流出物进腔','压缩冲程关闭入口止回阀并将废水泵出','水可经804回系统再过滤','重复循环直到滚筒排空'],['p0074'])

for record in RECORDS:
    assert set(record['fields'])==set(KEYS)
    for value in record['fields'].values():
        if value['judgment'] in ['explicit','inferred']:
            assert value['evidence']
out=BASE/'coding_group_review_cases.json'
out.write_text(json.dumps({'schema_version':'1.0','reviewer':'root','status':'technical_coding_working_version','records':RECORDS},ensure_ascii=False,indent=2),encoding='utf-8')
print(out, len(RECORDS))
