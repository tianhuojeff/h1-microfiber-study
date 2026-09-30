from review_core import *

# Conditioning a granular filter bed is distinct from dewatering collected solids.
M['field_dictionary']['carrier_conditioning']={'label':'过滤载体排水/干燥','definition':'对象是过滤颗粒床或介质本身，非默认等同已收集微纤维的固体脱水；保留对象、时点和液路。'}
for s in M['samples']:s['features'].setdefault('carrier_conditioning',{'label':'过滤载体排水/干燥','review_status':'not_reviewed_this_revision','support_status':None,'observations':[],'prior_field':None})
p='CN115298383A'
record(p,'capture','granular_bed','纺织流出液渗滤颗粒介质30，支撑件透液，上方留自由体积；微纤维可被截留在颗粒床孔隙和上表面。','纺织微纤维','流出液','颗粒介质30','颗粒床',['渗滤截留'],[('cl0001','允许所述流出液渗滤通过所述颗粒介质(30)的通道装置(100)')],'独立权1','明确承载对象，不能把滤床颗粒与目标纤维混为一物。')
record(p,'cleaning','fluidization','气体抽吸引起上升对流使床层颗粒流化，较小纤维随气流带走，停止后床粒沉淀重成滤床。','截留微纤维与床层颗粒','颗粒床','纤维随气流离开；床粒保留再沉降','滤床边界',['抽气流化','纤维随气流离开','停抽后床粒沉淀'],[('p0077','过滤床的颗粒被设为运动和流化，而不被气流夹带。比构成过滤床的颗粒更小的纤维被夹带在上升的气流中。')],'方法14含再生阶段；p0077为气抽吸实施方式','气流搬运微纤维，非水流回洗，也非排走全部滤料。')
record(p,'transfer','downstream_collector','再生后的纤维可在下游膜滤器或旋流室收集；应用例进一步给出商业吸尘器一次性过滤袋接收微纤维。该处没有据此断言袋的最终处置方式。','再生释放的微纤维','颗粒床','下游膜/旋流收集；例示吸尘器过滤袋','过滤床→外接再生收集设备',['排水/干燥后再生','气流带出','下游收集'],[('cl0019',None),('p0132','这使得微纤维可以被排入过滤袋')],'19→14—18择一；吸尘器袋为具体应用例，不要求全部权19装置均配袋','不把公开下游收集简写为“未知转移”。','same_embodiment_combination')
record(p,'carrier_conditioning','fig9','图9在再生前先排水后干燥：下部气抽吸促进颗粒床残液排走，再以热气干燥。对象是床层/介质中液体，不能编码为已收集滤渣脱水。','颗粒床间隙残液/湿气','颗粒床30','排液系统/载湿气流','颗粒床及下部流出口',['床层排水','床层干燥','再生'],[('p0108','所述强制气体对流夹带着颗粒介质间隙中存在的大部分残余液体'),('p0110','阀门111可以排放(打开阀门)排水阶段之前和期间蓄积的流出液'),('p0112','经过排水的颗粒介质在再生之前被干燥')],'17→14—16择一；顺序取说明书图9，数字效果未验证','C07：加入载体条件化单列，避免又把不同对象塞入残留/固体脱水。','same_embodiment_combination')

p='CN116282270A'
record(p,'cleaning','rinse_spin','漂洗时滤网截留；甩干时叶轮在套管内形成低压，将截留杂质吸出并形成反冲洗。权1与权2关于传动方向的措辞相反，不能据此固定统一方向结论。','滤网上微塑料等杂质','漂洗过滤网','中空套管13','滤面→套管',['漂洗截留','甩干驱动叶轮','低压吸出'],[('zh-cl0001','同时将所述第一单元中被截留在微塑料过滤网上的固体杂质吸出，对微塑料过滤网形成反冲洗')],'独立方法权1；装置权2是另一独立项','动作链有明示；机械方向矛盾单列待图文复核。')
record(p,'transfer','cyclone','带杂质甩干水由套管切向进入旋流器，固体沿壁面到底流收集腔；水从溢流口进入净化出水管。不能把旋流分离推断成固体完全脱水。','微塑料等固体杂质及水','中空套管13','固体入5-8；水经5-1到19','套管→旋流分离器/收集腔',['切向入旋流器','固体到底流','水从溢流口流出'],[('p0055',None)],'权3→2；图示具体方法说明p0055','固液不同路径分别识别，分离不等于含水率效果。')
record(p,'removal','threaded_chamber','收集腔5-8穿过洗衣机外壁对应开孔，可从旋流器底流口拧松取出以定期清理；属含固体容器移出。','承载微塑料等固体杂质的收集腔5-8','旋流器底流口','洗衣机外部可取出的收集腔','旋流模块/洗衣机外壁接口',['拧松螺纹收集腔','取出','定期清理'],[('zh-cl0004',None),('p0036',None),('p0052','可使收集腔5-8能够方便从旋流器底流口拧松、取出')],'4→3→2；外壁/拧松步骤来自p0036/p0052','不以缺倒出记录否认取腔路径。','same_embodiment_combination','container_with_retained_material')
record(p,'state_switch','gear_direction_conflict','方法权1写竖直转为水平，装置权2写水平转为竖直；已读文字存在方向冲突，保留原词，尚未据图裁定。','传动方向','竖直或水平（文本冲突）','水平或竖直（文本冲突）','动力传动关系',['需附图/授权文本定向复核'],[('zh-cl0001','将甩干时洗衣机竖直方向的机械转动转换至水平方向'),('zh-cl0002','将洗衣机电动机水平方向的机械转动转换至竖直方向')],'两个独立项1、2分别记录','未知/冲突不能被新表强行抹平。','conflict')

p='CN117702432A'
record(p,'state_switch','alternate_chambers','阀门选择相邻过滤腔室，堵塞时切换其他腔室继续过滤；这是过滤路径选择，不等同已清除原滤面颗粒。','不同过滤腔室流路','当前连通腔室','另一个连通腔室','盒内分区',['一腔过滤','切换另一腔过滤'],[('zh-cl0001',None),('p0058','在一个过滤腔室313中的过滤网320被堵塞时，使用其他过滤网320以及过滤腔室313进行微塑料的过滤')],'独立权1；详细阀状态为4→3→2→1','防止把延长清理周期的目的误编码为主动再生。')
record(p,'removal','split_box_filter','说明书p0059明确分体盒是为取出内部过滤网320清理；结合其微塑料过滤用途，支持含目标物滤网取出，不能仍停留在“只有盖可拆”。','含截留物过滤网320','盒体310内','盒体外供清理的过滤网','过滤组件盒体边界；未确认拆盖是否需断开其进水管',['拆分盒体可接近内部','取出过滤网','清理'],[('p0059','盒体310为分体式结构，以便于取出盒体310内的零部件诸如过滤网320进行清理'),('p0058','在一个过滤腔室313中的过滤网320被堵塞时')],'权2→1仅说明盖可拆；取网操作依据p0059，非仅靠权2猜测','本轮新增纠正：旧工作结论若限于盖可拆不足，应加入已定位取网说明书。','same_embodiment_combination','filter_assembly_with_retained_material')

p='CN120500565A'
record(p,'liquid_route','claims1_2','权1和2均明示入水、第一腔、开口、第二腔过滤器及出水的顺序；“液相出口未知”不成立，但装置以外最终水路不能只由该项推断。','洗涤水','入水口','出水口','过滤器装置流路',['第一腔','开口','第二腔过滤器','出水口'],[('zh-cl0001',None)],'独立权1；独立权2为分隔壁实现方式，分别记录','纠正旧液相出口漏记；普通过滤出水不是维护排空。')
record(p,'cleaning','guide_surface','权3借引导部把开口水流导向滤器侧面，使附着颗粒分离并导向滤器底部；这是滤器内部重分布，不等同自动排出模块。','滤器侧面附着颗粒','过滤器侧面','过滤器底部','过滤器内部',['水流引导','侧面颗粒脱离','到达底部'],[('zh-cl0003',None)],'3→1或2；4→3进一步约束引导面','清理与局部转移支持，但无外排固结论。')
record(p,'removal','drawer_filter','权9抽屉容纳可拆滤器并可向前抽出；权11允许从敞开顶面取出滤器。路径为含物过滤组件取出，不把整个抽屉叫独立干渣盒。','承载颗粒的过滤器','第二腔内抽屉','抽屉上方取出的过滤器','第二腔→抽屉外/模块外',['向前抽出抽屉','从顶部移除滤器'],[('zh-cl0006','颗粒从所述左侧表面和所述右侧表面的下部分堆积'),('zh-cl0009',None),('zh-cl0011',None)],'11→9→8→7→6→1或2；9并不依附清理引导权3','不把所有分支累加；过滤器承载来自所依附权6。','same_embodiment_combination','filter_assembly_with_retained_material')
record(p,'seals_connections','drawer_drain','权10设置抽屉排放部分，权14规定底面向出水口下倾；这些是不同依附9的分支，不能由此声称取出前已完成排空或不滴水。','抽屉底面与水流','抽屉内','水出口','抽屉/出水接口',['存在排放及坡面设计，维护时序未限定'],[('zh-cl0010',None),('zh-cl0014',None)],'10→9与14→9分别记录，不相互依附','C07：结构排水倾向不等于维护前残液排空。')

p='WO2024143783A1'
o=record(p,'removal','drawer_filter','本WO保存页韩文及英文对照的权9、11分别写向前取抽屉及从敞开顶部取滤器；仅作为本WO具体文本，不把CN权项号无核复制。','可拆过滤器','第二腔抽屉内','抽屉外','第二腔/抽屉边界',['向前取出抽屉','顶部取过滤器'],[('c09','상기 드로워는 상기 제2챔버로부터 전방 방향으로 꺼낼 수 있는 세탁기용 필터 장치.'),('c11','상기 드로워의 개방된 상부를 통해 상기 필터를 상기 드로워로부터 꺼낼 수 있는 세탁기용 필터 장치.')],'11→9→8→7→6→1或2；保存页原韩文项首逐一读取','跨版本分别核对；本记录尚待原PDF韩文页交叉核验。','same_embodiment_combination','filter_assembly_with_retained_material')
o['review_status']='partial';o['evidence_language']='Korean original plus Google English translation; quote uses Korean saved text'
o=record(p,'seals_connections','claim17_wording','本WO权17原韩文为자력부재 및 마찰부재（磁力构件及摩擦构件），CN权17为磁性构件或摩擦构件；至少存在连接词差异，不能宣称全部权项逐字相同。','外部联接构件','装置外表面','安装位置','设备安装连接',['文本结构关系，无操作顺序'],[('c17','상기 결합부재는 자력부재 및 마찰부재를 포함하는 세탁기용 필터 장치.')],'17→15或16；15→1，16→2','新发现差异需原PDF/正式版本确认，不由机译保证权利范围差异。')
o['review_status']='partial';o['verification_gap']='原PDF韩文对应页与CN原PDF待交叉核验；当前不作权利范围结论'

p='WO2023047385A1'
record(p,'transfer','backflow_fig12_13','图12—13收集状态关闭入口第一阀，打开收集出口第三阀，第二阀打开反流通路；反向水流从膜背侧推颗粒到可拆收集腔34。','截留微粒及输送水','膜98前表面','收集腔34','主过滤腔→收集腔，非整机外',['阀切换到收集状态','膜背侧反流','带粒水经216进入34'],[('p0049','This reverse movement of the process fluid 24 in the upstream direction 240 pushes the captured micro-sized particles 26 from the leading surface 194 of the filter membrane 98 and through the now-opened third valve 214 and the collector outlet 216 that leads into the removable collection chamber 34.')],'独立权34含二次循环流结构；具体阀序为说明书[0051]，HTML p0049','不要混用图10抽吸疏水层的另一方案。')
record(p,'liquid_route','secondary_hydrogel','收集腔中二次水凝胶过滤器260留住微粒，水可回主流路22或回反流储液器190；两种回流可选，不能把“流出收集腔”写成排入环境。','二次过滤后的过程水','收集腔34的260','主流路22或储液器190','收集腔→机器循环水路',['二次过滤','择一回流'],[('clm-0036',None),('p0052','This filtered process fluid 126 from the removable collection chamber 34 can then be recirculated back to the fluid path 22 for later use. Alternatively, this filtered process fluid 126 can be recirculated back to the backflow reservoir 190')],'36→34或35；35需独立核查，当前可用36→34；说明书图12—13','固液分离存在；不由水凝胶二次过滤推断固体干燥率。')
record(p,'removal','removable_collection','独立权1将颗粒由微粒过滤器送至可拆收集腔；收集腔承载关系明确，可拆容器路径可纳入，但该项未给开盖/解锁/断管顺序。','含微粒收集腔','过滤系统收集位置','可移除收集单元','收集腔与过滤系统接口；整机壳体跨越方式未详述',['可拆收集腔；具体拆装时序未限定'],[('clm-0001','a secondary flow mechanism that delivers the micro-sized particles from the microparticle filter to a removable collection chamber.')],'独立权1，独立权17亦含；不挪用别件拆装动作','统一取含物容器规则，明确动作细节范围。',kind='container_with_retained_material')

for pub,rows in cache.items():
 (RUN/'evidence'/(pub+'_anchors.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
 for v in sample(pub)['publications']:
  if v['publication_id']==pub:v['review_status']='partial_claims_and_targeted_description_reviewed'
M.update(updated_at=NOW,phase='P2_in_progress')
P.write_text(json.dumps(M,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Total current observations',sum(len(f['observations']) for s in M['samples'] for f in s['features'].values()),'families with reviewed issues',sum(any(f['observations'] for f in s['features'].values()) for s in M['samples']))
