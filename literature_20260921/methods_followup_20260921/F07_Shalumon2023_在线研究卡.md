# F07 · 洗衣废水提取、流程空白与“回收率基质错配”

## 题录与获取状态

- Shalumon, C. S.; Ratanatamskul, C. (2023). *A novel simplified method for extraction of microplastic particles from face scrub and laundry wastewater*. **Scientific Reports**, 13, 14168. DOI: [10.1038/s41598-023-41457-y](https://doi.org/10.1038/s41598-023-41457-y).
- 一手来源：Nature 文章页 <https://www.nature.com/articles/s41598-023-41457-y>；PMC 收录页 <https://pmc.ncbi.nlm.nih.gov/articles/PMC10465532/>。
- 本轮阅读证据：Europe PMC 官方 `fullTextXML` 公开接口取得的 JATS 全文 `F07_Shalumon2023_fulltext.xml`，并已生成离线纯文本 `F07_Shalumon2023_fulltext.txt`。XML内题名、DOI、PMID/PMCID和 CC BY 4.0 许可与上述题录一致。Nature PDF 请求返回反爬网页，PMC 官方PDF直链 HTTP 403；没有有效出版PDF、页数或PDF哈希，故不伪造 PDF 验收。XML没有固定出版PDF页码，以下以原文小节和图号精确定位。

## 这篇实际测了什么

作者从泰国朱拉隆功大学宿舍洗衣运行期间收集三次共5 L废水并混合为代表样；取10 mL混匀洗衣废水加20 mL丙酮，倒入50 mL去离子水后，以0.2 μm玻璃纤维滤膜真空过滤，继而以 micro-FTIR 做尺寸与聚合物识别（原文 *Sample preparation and wastewater collection*、*Extraction method development*、*Characterization and quantification*；Fig. 1）。

## 可迁移步骤及证据

|H1 缺口|原文实际做法|原文定位|可迁移边界|
|---|---|---|---|
|真实洗衣废水的混匀、提取与识别|5 L洗衣废水由三次采样混合；分析前混匀。10 mL分样依次经丙酮、水相和0.2 μm玻璃纤维滤膜；以 micro-FTIR 比库判定聚合物并测尺寸。|*Sample preparation and wastewater collection*；*Extraction method development*；*Characterization and quantification*；Fig. 1|H1 可以保留“全量/分样”标签、混匀动作、玻璃器皿和FTIR识别链。10 mL是为避免滤面过密的作者选择，不能自动扩大到全流量估计；0.2 μm是收集膜孔径，不是识别或定量限。|
|背景污染控制|使用清洁玻璃容器和工具，避免塑料器具；器皿以超纯水洗净；穿棉衣/实验服；样品置玻璃培养皿并以铝箔覆盖；分析中运行空白，并从实验值扣除。|*Quality control/quality analysis*|可迁移为最小污染防控动作和“空白数值单列后才校正”的顺序。本文没有在该小节给出空白的计数、质量、材质组成或批次频率，故不能为H1提供空白校正数值或替代空气/装置/流程空白。|
|加标回收的定义|将20 mg、平均242 ± 74.9 μm的预提取PE加到**面部磨砂样品**；空白是不加MP的磨砂样。回收率 = 提取质量 / 20 mg；各实验双份。|*Extraction method development*；*Validation of the extraction protocol*；Fig. 2–3|可迁移“空白基质 + 已知投加量 + 提取量/投加量 + 重复”的报告骨架。它只能说明该文面部磨砂PE质量提取的验证，**不验证洗衣废水微纤维、不同聚合物/尺寸、计数或FTIR识别的端到端回收**。|
|真实洗衣样的结果类型|在洗衣废水上做方法与传统过滤的比较，报告提取后纤维颜色、尺寸分布并以 micro-FTIR 分析。|*Applicability of extraction method for microfiber extraction from laundry wastewater*；Fig. 6–7|H1 可将“方法可用于真实样识别”与“端到端定量回收”分开写。该文没有给出真实洗衣样的加标纤维回收率、质量/根数质量衡算、方法LOD或LOQ。|

## 对 H1 计量链的直接结论

1. 真实基质能否做出可读的 µFTIR 纤维谱，不等于该基质的加标回收已经验证；F07 的回收率来自不同的面部磨砂 PE 质量试验。
2. H1 的加标必须至少按目标材质/尺寸组在**真实洗衣废水或经证明等效的基质**中完成，并分别报告质量回收、计数回收和实际进入鉴别子样的比例。
3. F07 的“运行空白并扣除”是污染控制步骤，不提供H1可借用的背景数值。H1要保存未校正原始值、每类空白和校正公式；负校正值不应在原始表中截断。
4. 本文没有报告可转用的数值 LOD/LOQ。H1 仍需用本实验空白分布、加标回收和预设尺寸/材质规则分别建立报告限或定量能力。

## 不应带入 H1 的结果

- 约94.1 ± 1.65%的作者方法回收率只适用于所述20 mg PE面部磨砂试验；不能写入真实洗衣微纤维回收率。
- 该文的10 mL分样、0.2 μm膜孔径、ATR/FPA设置都不等同于H1的LOD/LOQ，且不证明对小于任一可见/可判读尺寸的纤维没有遗漏。

## 本地全文核验

- XML：89,902 bytes，SHA-256 `E5FB72C6344815EB5ACB225AA0EF609DDAA3A21CCF714FC7AB74E9B14B91B268`。
- 纯文本提取：31,323 bytes，SHA-256 `F03E1E490F647CDAB6F12CAF445B1AA003A7C9D8FD75FC250D7CF353802AADFC`。文本保留原文标题和段落顺序，供离线检索；图像、版面和出版PDF页码不在其中。

## 关联作者更正

原论文 XML 关联一份作者更正：DOI [10.1038/s41598-024-63484-z](https://doi.org/10.1038/s41598-024-63484-z)，PMCID `PMC11153549`。更正仅把引言中个人护理产品微珠的 `500 nm` 改为 `500 μm`；没有列出或修改洗衣废水提取、空白、加标回收、µFTIR、LOD/LOQ或结果结论。完整一手核验见 [F07 2024 作者更正影响核验](F07_2024作者更正_影响核验.md)。
