# getConversations

获取当前用户的会话列表

## 密钥配置

请在 `references/secrets/config.sh` 中配置：
- `BASE_URL`
- `AGENT_ID`
- `AGENT_SECRET`

## 基本信息

- baseUrl: `{BASE_URL}/findu-imutils/api/v1/im`
- endpoint: `/conversations`
- method: GET
- contentType: application/json

## 鉴权 Headers

签名算法: `HMAC-SHA256(secret, Method&Path&AgentKey&Timestamp)`

| 参数名 | 来源 | 描述 |
|--------|------|------|
| X-Agent-Id | `config.sh` 的 `AGENT_ID` | 代理ID |
| X-Timestamp | 当前时间戳 (秒) | 请求时间戳 |
| X-Agent-Signature | HMAC-SHA256签名 | 签名 |

## 请求参数 (Query)

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| count | number | 否 | 获取会话数量，默认100 |

## curl 示例

```bash
source references/secrets/config.sh

TIMESTAMP=$(date +%s)
SIGNATURE=$(echo -n "GET&/findu-imutils/api/v1/im/conversations&${AGENT_ID}&${TIMESTAMP}" | openssl dgst -sha256 -hmac "${AGENT_SECRET}" | awk '{print $2}')

curl -X GET "${BASE_URL}/findu-imutils/api/v1/im/conversations?count=100" \
  -H "X-Agent-Id: ${AGENT_ID}" \
  -H "X-Timestamp: ${TIMESTAMP}" \
  -H "X-Agent-Signature: ${SIGNATURE}"
```

## 响应示例

成功:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "conversationId": "conv_001",
      "peerId": "用户ID",
      "peerName": "张三",
      "un5,
      "lastMessage": "readCount": 好的",
      "lastTimestamp": 1700000000
    }
  ]
}
```
