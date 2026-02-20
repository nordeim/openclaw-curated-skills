---
name: tuniu-hotel
description: 途牛酒店助手 - 通过 exec + curl 调用 MCP 实现酒店搜索、详情查询、预订下单。适用于用户询问某地酒店、入住日期、查看酒店详情或提交订单时使用。
version: 1.0.0
metadata: {"openclaw": {"emoji": "🏨", "category": "travel", "tags": ["途牛", "酒店", "预订", "搜索"]}}
---

# 途牛酒店助手

当用户询问酒店搜索、详情或预订时，使用此 skill 通过 exec 执行 curl 调用途牛酒店 MCP 服务。

## 适用场景

- 按城市、日期搜索酒店（第一页、翻页）
- 查看指定酒店详情、房型与报价
- 用户确认后创建酒店预订订单

## 配置要求

### 必需配置

- **TUNIU_MEMBER_KEY**：途牛开放平台会员 key，用于 `Authorization: Bearer` 请求头
- **TUNIU_API_KEY**：途牛开放平台 API key，用于 `apiKey` 请求头

用户需在[途牛开放平台](https://platform.tuniu.com)注册并获取上述密钥。

### 可选配置

- **TUNIU_MCP_URL**：MCP 服务地址，默认 `https://openapi.tuniu.cn/mcp/hotel`

### 会话说明

## 调用方式

**直接调用工具**：使用以下请求头调用 `tools/call` 即可：

- `Authorization: Bearer $TUNIU_MEMBER_KEY`
- `apiKey: $TUNIU_API_KEY`
- `Content-Type: application/json`
- `Accept: application/json, text/event-stream`

## 可用工具

**重要**：下方示例中的参数均为占位，调用时需**根据用户当前需求**填入实际值（城市、日期、酒店 ID/名称、入住人、联系方式等），勿直接照抄示例值。

### 1. 酒店搜索 (tuniu_hotel_search)

**第一页**：必填 `cityName`，可选 `checkIn`、`checkOut`（格式 YYYY-MM-DD）、`keyword`、`prices` 等。响应会返回 `queryId`、`totalPageNum`、`currentPageNum`，需保留 queryId 供翻页使用。

**翻页**：传 `queryId`（首次搜索返回）和 `pageNum`（2=第二页，3=第三页…），不再传 cityName。用户说「还有吗」「翻页」「下一页」时必须用 queryId + pageNum 再次调用。

**触发词**：某地酒店、某日入住、查酒店、搜酒店

```bash
# 第一页：cityName/checkIn/checkOut 等按用户说的城市、入住/离店日期填写（日期格式 YYYY-MM-DD）
curl -s -X POST "${TUNIU_MCP_URL:-https://openapi.tuniu.cn/mcp/hotel}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TUNIU_MEMBER_KEY" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"tuniu_hotel_search","arguments":{"cityName":"<用户指定的城市>","checkIn":"<用户指定的入住日期 YYYY-MM-DD>","checkOut":"<用户指定的离店日期 YYYY-MM-DD>"}}}'
```

```bash
# 翻页：queryId 用上轮 search 返回的值，pageNum 为 2、3、4…
curl -s -X POST "${TUNIU_MCP_URL:-https://openapi.tuniu.cn/mcp/hotel}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TUNIU_MEMBER_KEY" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"tuniu_hotel_search","arguments":{"queryId":"<上轮返回的queryId>","pageNum":2}}}'
```

### 2. 酒店详情 (tuniu_hotel_detail)

**入参**：`hotelId`（数字，与搜索结果一致）与 `hotelName` 二选一必填；可选 `checkIn`、`checkOut`（YYYY-MM-DD）、`roomNum`、`adultNum`、`childNum` 等。

当用户说「看一下」「详情」「介绍」某酒店且对话或搜索结果中已有 hotelId 或 hotelName 时，直接传入调用，无需用户再确认。

**触发词**：酒店详情、房型、看一下某某酒店、介绍这家酒店

```bash
# 按 hotelId：hotelId 从搜索结果或用户指定酒店取，日期按用户需求填
curl -s -X POST "${TUNIU_MCP_URL:-https://openapi.tuniu.cn/mcp/hotel}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TUNIU_MEMBER_KEY" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"tuniu_hotel_detail","arguments":{"hotelId":<用户/搜索结果中的 hotelId>,"checkIn":"<用户指定的入住日期 YYYY-MM-DD>","checkOut":"<用户指定的离店日期 YYYY-MM-DD>"}}}'
```

```bash
# 按 hotelName：酒店名、日期均按用户需求填
curl -s -X POST "${TUNIU_MCP_URL:-https://openapi.tuniu.cn/mcp/hotel}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TUNIU_MEMBER_KEY" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"tuniu_hotel_detail","arguments":{"hotelName":"<用户指定的酒店名称>","checkIn":"<用户指定的入住日期 YYYY-MM-DD>","checkOut":"<用户指定的离店日期 YYYY-MM-DD>"}}}'
```

### 3. 创建订单 (tuniu_hotel_create_order)

**前置条件**：必须先调用 `tuniu_hotel_detail` 获取酒店详情；从返回的 `roomTypes[].ratePlans[]` 中选取报价，拿到 `preBookParam`。本工具会自动验价，无需单独验价。

**必填参数**：hotelId（字符串）、roomId（字符串）、preBookParam、checkInDate、checkOutDate（YYYY-MM-DD）、roomCount、roomGuests、contactName、contactPhone。

**roomGuests**：数组长度等于 roomCount；每项为 `{"guests":[{"firstName":"名","lastName":"姓"}]}`，至少一位入住人。

**触发词**：预订、下单、订这家、我要订、提交订单

```bash
# hotelId、roomId、preBookParam 从最近一次 detail 结果取；日期、入住人、联系人按用户需求填
curl -s -X POST "${TUNIU_MCP_URL:-https://openapi.tuniu.cn/mcp/hotel}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TUNIU_MEMBER_KEY" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"tuniu_hotel_create_order","arguments":{"hotelId":"<detail 返回的 hotelId>","roomId":"<detail 返回的 roomId>","preBookParam":"<detail 对应报价的 preBookParam>","checkInDate":"<用户指定的入住日期 YYYY-MM-DD>","checkOutDate":"<用户指定的离店日期 YYYY-MM-DD>","roomCount":1,"roomGuests":[{"guests":[{"firstName":"<入住人名的名>","lastName":"<入住人名的姓>"}]}],"contactName":"<用户提供的联系人姓名>","contactPhone":"<用户提供的联系电话>"}}}'
```

（hotelId、roomId、preBookParam 必须来自最近一次 tuniu_hotel_detail 的返回，不可用示例值。）

## 响应处理

### 成功响应

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [{"type": "text", "text": "..."}]
  },
  "id": 2
}
```

- **本项目中** 工具结果统一放在 **`result.content[0].text`** 中。`text` 为 **JSON 字符串**，需先 `JSON.parse(result.content[0].text)` 再使用。
- 解析后为业务对象，各工具结构不同：
  - **酒店列表**（tuniu_hotel_search）：`displayHint`、`message`、`success`、`queryId`、`totalPageNum`、`currentPageNum`、`cityInfo`、`hotels`（含 hotelId、hotelName、starName、brandName、commentScore、commentDigest、lowestPrice、address、business 等）。按 `displayHint` 与列表字段整理后回复。
  - **酒店详情**（tuniu_hotel_detail）：`displayHint`、酒店基础信息、`roomTypes`（房型与报价，含 preBookParam 等）。
  - **创建订单**（tuniu_hotel_create_order）：`displayHint`、`orderId`、`confirmationNumber`、`paymentUrl`、入住/离店日期等。
- 错误时 `text` 解析后为 `{ "error": "错误信息" }`，可从 `error` 字段取提示文案。

### 错误响应

本项目中错误分两类，需分别处理：

**1. 传输/会话层错误**（无 `result`，仅有顶层 `error`，通常伴随 HTTP 4xx/5xx）：

```json
{
  "jsonrpc": "2.0",
  "error": {"code": -32000, "message": "..."},
  "id": null
}
```
- **Method Not Allowed**：GET 等非 POST 请求
- **Internal server error**（code -32603）：服务内部异常

**2. 工具层错误**（HTTP 仍为 200，有 `result`）：与成功响应结构相同，但 `result.content[0].text` 解析后为 `{ "error": "错误信息" }`，且可能带 `result.isError === true`。例如参数校验失败、报价失效、下单失败等，从 `error` 字段取文案提示用户或重试。

## 输出格式建议

- **搜索列表**：以表格或清单展示酒店名称、星级、地址、最低价格、queryId（若需翻页可提示「可以说翻页/下一页」）
- **酒店详情**：房型、报价、设施、政策等分块呈现；若有 preBookParam，可提示用户可预订
- **预订成功**：明确写出订单号/确认号、入住/离店日期、酒店与房型、联系人信息

## 使用示例

以下示例中，所有参数均从**用户表述或上一轮结果**中解析并填入，勿用固定值。

**用户**：北京 2 月 20 号入住一晚，有什么酒店？

**AI 执行**：按用户意图填参：cityName=北京、checkIn=2026-02-20、checkOut=2026-02-21，调用 tuniu_hotel_search（请求头需带 Authorization、apiKey、Content-Type、Accept）。解析 result.content[0].text，整理酒店列表回复，并保留 queryId 供翻页。

**用户**：还有吗？/ 下一页

**AI 执行**：用上一轮 search 返回的 queryId 与 pageNum=2（或 3、4…）再次调用 tuniu_hotel_search，不传 cityName。

**用户**：看一下xxx酒店的详情

**AI 执行**：从上一轮列表取xxx酒店的 hotelId（或 hotelName），连同用户之前的入住/离店日期，调用 tuniu_hotel_detail；解析详情后分块展示房型、报价、设施，并提示可预订。

**用户**：就订这个，联系人张三 13800138000

**AI 执行**：从最近一次 detail 结果取 hotelId、roomId、preBookParam；按用户提供的入住/离店日期填 checkInDate/checkOutDate；将「张三」拆为 lastName=张、firstName=三 填入 roomGuests，contactName=张三、contactPhone=13800138000。成功后回复订单号、确认号、入住信息与支付链接。

## 注意事项

1. **密钥安全**：不要在回复或日志中暴露 TUNIU_MEMBER_KEY、TUNIU_API_KEY
2. **认证**：若遇协议或认证错误，可重试或检查 TUNIU_MEMBER_KEY、TUNIU_API_KEY
3. **日期格式**：所有日期均为 YYYY-MM-DD
4. **下单前**：create_order 的 hotelId、roomId、preBookParam 必须来自最近一次 tuniu_hotel_detail 的返回；若间隔较长，建议重新调 detail 刷新报价
5. **翻页**：用户要「更多」「下一页」时必须用上一轮 search 返回的 queryId 和 pageNum（≥2）调用，不能只传城市名
