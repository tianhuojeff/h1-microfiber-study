# 2026-09-28 检索截图取证：真实阻塞记录

## 目标与边界

本目录原计划取得 Google Patents 对下列冻结窄题名检索的页面截图，或在 Google 页面限流时取得一件冻结同族公开件的 Google Patents 题录／Family 页面截图：

```text
TI=((laundry OR "washing machine") (microfiber OR microfibre OR microplastic))
```

该检索式、一次即时计数 `98` 与其后原始分页保存触发 `GoogleSorry` 的既有记录，见 `../../patents/search_corpus_20260928/README.md`。本次未改变该记录、14同族样本、矩阵、报告正文或模板。

## 已存原始公开页的离线浏览器回放

由于 Google Patents 的现场请求受限，本次还对已经保存在项目中的**原始 Google Patents HTML**进行浏览器离线回放。回放时阻断所有 `http`／`https` 资源请求；源HTML没有被修改。

|拍摄时刻（Asia/Shanghai）|原始快照及哈希|页面范围|输出PNG及哈希|能证明|不能证明|
|---|---|---|---|---|---|
|2026-09-28 11:02:47|`../../team_package_20260928/sources/WO2021116933A1.html`；`85504E62B3AF33D1B91AC4D2C9C9F5F2AC0FDEA26D713DA0ABEF5D8F01F95B92`|该快照开头的题录区：公开编号 `WO2021116933A1`、题名、PCT申请号等|`google_patents_archived_public_record_WO2021116933A1_20260928.png`；`497ED4172B807083456A0D5332B59883133006A9A915335ED7F796DA84227B93`|被保存的 Google Patents 公开页快照包含该WO公开件的题录信息|不证明此刻 Google 仍显示同一页面；不证明题名检索式、98即时计数或检索命中。|
|2026-09-28 11:02:47|同上|同一快照的 `Also Published As` 国别／版本栏；画面中包含 `CN115087774A (en)` 与公布日 `2022-09-20`|`google_patents_archived_also_published_as_WO2021116933A1_20260928.png`；`4A9415DF6225981693FC60505A1F042E100AF704B08EC52C126EDC110AB24F67`|该保存快照的数据库“Also Published As”栏把WO与CN版本并列展示，可辅助说明本报告的定向同族扩展线索|不证明法律同族、权利范围、法律状态或现场数据库查询；不可写成“98条检索结果截图”。|

浏览器回放元数据（含本地文件URL、页面标题、可见文本校验、PNG字节数及哈希）存于 `capture_archived_google_patents_run_20260928.json`，其SHA-256为 `73895CA41AEC1E60D14E0BA4D9A9370B9CE9C158C8BFC6D3EF31CEDFD6CA8FA5`。

## 现场访问与停止依据

|时刻（Asia/Shanghai）|请求地址|浏览器可见结果|处理|
|---|---|---|---|
|2026-09-28 10:58:24|`https://patents.google.com/patent/WO2022084677A1/en`|页面标题为 `Sorry...`，未出现公开件题录|按任务要求遇到 GoogleSorry 后停止对 Google Patents 的后续请求；未保存或伪造“题录页”截图。|
|2026-09-28 10:59:00|`https://patentscope.wipo.int/search/en/detail.jsf?docId=WO2022084677`|HTTP 403，标题 `ERROR 403 FORBIDDEN`|没有将拒绝页冒充公开件页面。|

唯一外部搜索回退为 Bing 的一次性公开网页查询，查询词为 `laundry microfiber microfibre microplastic patent`；其页面虽真实显示该查询词和即时“84条结果”，但可见结果为与专利无关的内容。因此该 PNG **不得作为专利命中、题名字段检索或样本纳入证据**，仅保留为“Google 受限后一次非数据库回退无效”的审计记录。

## 现有文件、哈希和能证明的范围

|文件|SHA-256|页面范围／能证明|不能证明|
|---|---|---|---|
|`capture_run_20260928.json`|`8E88B96869836D613F8AA169C6D52DC8C8137DF446CEA7370B51A2A32BD2C9B6`|Google Patents 已返回 `Sorry...` 的自动化取证元数据|不证明题名检索命中、即时计数或公开件题录。|
|`capture_wipo_run_20260928.json`|`1B26BEF6138C6A9DD88AF30BC665DCE50212D6FA859620433F77631436F9249E`|WIPO PATENTSCOPE 已返回 403 的自动化取证元数据|不证明 WO2022084677 的任何题录或检索结果。|
|`bing_public_web_search_patent_terms_20260928.png`|`F7F6C2A6FE30B95CCE7E7088BE9A017522E74923649901AB69B379844C69C9FB`|Bing 页面在拍摄时显示所列公开网页查询词及其页面内容|不证明 Google Patents 的字段语法、98、题名命中、相关性、同族关系或14同族样本。|
|`capture_bing_run_20260928.json`|`10DF130BEBEFCE591D46808C46D56B1F4B25086DA954921E380207404F1EEB3D`|Bing 页面地址、HTTP 200、拍摄时刻、PNG 字节数及哈希|同上。|

## 结论

本次没有取得符合竞赛模板“检索思路截图辅助说明”要求的**现场**Google Patents 查询或公开件题录截图。原因是该域在实际访问时给出 `Sorry...`，且任务要求在此情形立即停止。两张离线回放图只能辅助说明保存的公开件题录和定向同族扩展，不能替代现场检索截图或98命中截图。若后续在解除限流的独立会话中恢复访问，应以同一检索式重新拍摄页面，并另行写入页面URL、拍摄时刻、可见检索式／结果和文件哈希。
