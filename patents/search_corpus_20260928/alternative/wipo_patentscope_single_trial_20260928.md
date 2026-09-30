# WIPO PATENTSCOPE 公开入口：单次替代检索试验

执行日：2026-09-28（Asia/Shanghai）  
入口：WIPO PATENTSCOPE（WIPO 官方公开专利检索服务）  
试验目标：验证该入口能否在不登录、不绕过验证码或限流的前提下，返回并保存本项目同类题名对象检索的原始候选记录。

## 检索式与入口

PATENTSCOPE 的公开帮助页说明 `EN_TI` 是 English Title 字段，并支持布尔组配；因此将原先 Google Patents 的题名对象条件改写为 PATENTSCOPE 语法：

```text
EN_TI:((laundry OR "washing machine") AND (microfiber OR microfibre OR microplastic))
```

单次请求 URL（URL 编码后的 `query` 参数）：

```text
https://patentscope.wipo.int/search/en/result.jsf?query=EN_TI%3A%28%28laundry%20OR%20%22washing%20machine%22%29%20AND%20%28microfiber%20OR%20microfibre%20OR%20microplastic%29%29
```

字段与语法来源（读取时间同日）：

- https://patentscope.wipo.int/search/en/help/querySyntaxHelp.jsf （明确举例 `EN_TI:(...)`）
- https://patentscope.wipo.int/search/en/structuredSearch.jsf （公开结构化检索页面列出 `EN_TI` 为 English Title）

## 实测结果

本轮只发出 **一次** 对上述 WIPO URL 的未认证 HTTPS GET 请求（30 秒超时，最多 3 次 HTTP 重定向；没有重试、没有改变请求头、没有登录和没有验证码处理）。请求在 TLS/传输阶段失败，PowerShell 的 `Invoke-WebRequest` 报错为：

```text
Received an unexpected EOF or 0 bytes from the transport stream.
```

服务端未返回可保存的 HTTP 状态码、响应头或响应正文。因此本次也**没有候选记录、命中数、CSV 或伪造母表**。这是一次入口连通性/可导出性失败记录，不能用于推断 WIPO 的实际检索命中或数据库覆盖范围。

## 审计边界

本试验未再尝试 WIPO 其他端点、未使用浏览器会话或账户，也没有访问 EPO/CNIPA；这些均留给后续在独立授权和冷却窗口下的单独试验。该文件本身是本轮唯一证据记录。
