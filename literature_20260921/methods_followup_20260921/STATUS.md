# H1 计量方法补充：当前获取状态

更新时间：2026-09-21（Asia/Shanghai）。本目录仅收纳本轮最多两篇一手方法研究及其获取证据；尚未改动 H1 主入口、既有文献或 Obsidian。

|编号|一手来源|研究所补缺口|当前可用文本|PDF状态|待验收边界|
|---|---|---|---|---|---|
|F07|Shalumon, C. S.; Ratanatamskul, C. *A novel simplified method for extraction of microplastic particles from face scrub and laundry wastewater*. *Scientific Reports* 13, 14168 (2023). DOI: [10.1038/s41598-023-41457-y](https://doi.org/10.1038/s41598-023-41457-y)|真实宿舍洗衣废水、流程空白、显微FTIR识别；明确核对加标回收的基质|Europe PMC 官方公开全文 XML：`F07_Shalumon2023_fulltext.xml`，并有离线纯文本 `F07_Shalumon2023_fulltext.txt`；来源：<https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10465532/fullTextXML>|**未取得出版PDF**。此前 Nature PDF 请求为反爬 HTML，PMC PDF直链为 HTTP 403；本轮未重试。XML不是PDF，未计入PDF。|加标回收为面部磨砂样品中的PE质量回收，不能写成洗衣废水微纤维端到端回收；XML/在线HTML无固定出版PDF页码，研究卡以原文小节、图表定位。
|F08|Lant, N. J. et al. *Microfiber release from real soiled consumer laundry and the impact of fabric care products and washing conditions*. *PLOS ONE* 15(6), e0233332 (2020). DOI: [10.1371/journal.pone.0233332](https://doi.org/10.1371/journal.pone.0233332)|真实消费者混合污衣废水、全流路干质量与纤维识别子样的不可互换性|官方JATS全文：`F08_Lant2020_real_soiled_laundry.jats.xml`；PLOS来源：<https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0233332>|**已取得并完成全文卡/证据验收**：`F08_Lant2020_real_soiled_laundry.pdf`，PDF头/18页/哈希、JATS全文、pp.4–8渲染和研究卡均已核验。|已逐页记录流程空白、加标回收、称量/计数和材质识别的实际报告范围；未报告项目仍保持“未报告”，不补写为零或已验证。

## F08 文件核验

- PDF 头：`%PDF-1.6`
- 页数：18（`pdfinfo`）
- SHA-256：`CA1300E2B78C39EF8C4537D383B35C6FDE9154CE719C239112AFF7CD2D4033E3`
- 文件大小：2,543,254 bytes

## 未纳入“下载完成”的响应

- Nature PDF 请求返回网页反爬内容，未保存为 F07 PDF。
- PLOS 的 `type=manuscript` 响应为合法 JATS XML，已按其真实格式保存，未伪装为PDF。
- F07 通过 Europe PMC 的 `fullTextXML` 公开接口取得合法 JATS XML；它是可离线核查的公开全文，不是出版PDF。
- F07 原 XML 链接的作者更正已作为独立官方XML/纯文本保存；更正范围仅为引言的 `500 nm`→`500 μm`，详见 `F07_2024作者更正_影响核验.md`。
