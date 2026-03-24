# 工作原理

## 架构图

```
┌─────────────┐     ┌──────────────┐     ┌──────────┐     ┌─────────┐
│  AI 代理    │────▶│ AgentBridge  │────▶│ ReqCast  │────▶│ Base 链 │
│             │     │              │     │          │     │  USDC   │
└─────────────┘     └──────────────┘     └──────────┘     └─────────┘
       │                    │                   │                │
       │  x402 协议请求      │  认证回调          │  执行支付       │ 结算完成
       └────────────────────┴───────────────────┴────────────────┘
```

## 组件说明

### 1. AI 代理
任何能够发起 HTTP 请求的 AI 代理（如 LangChain、AutoGPT 等），在需要支付时调用 AgentBridge 接口。

### 2. AgentBridge（本层）
- 接收 AI 代理的支付请求
- 验证 API Key 余额
- 转发请求至 ReqCast
- 接收回调并更新使用记录

### 3. ReqCast
- x402 协议的链上执行层
- 负责构造交易、签名、广播
- 向 AgentBridge 发送回调确认

### 4. Base 链 + USDC
- Base 链提供低成本 L2 结算
- USDC 作为支付代币，稳定币无波动

## 数据流

1. AI 代理发送请求到 AgentBridge（携带 API Key）
2. AgentBridge 验证余额是否足够
3. 如余额不足，返回 402 状态码及充值地址
4. 如余额充足，转发请求到 ReqCast
5. ReqCast 执行链上 USDC 转账
6. ReqCast 回调 AgentBridge 确认支付完成
7. AgentBridge 扣除费用，返回结果给 AI 代理

## 定价模式

| 模式 | 价格 (USDC) | 说明 |
|------|-------------|------|
| static | 0.003 | 静态页面抓取 |
| dynamic | 0.005 | 需要 Playwright 的动态页面 |

## API 接口

### POST /v1/fetch/dynamic

抓取网页内容，自动判断 static/dynamic 模式并扣费。

**请求头：**
```
X-API-Key: your_api_key_here
```

**请求体：**
```json
{
  "url": "https://example.com",
  "output_format": "markdown"
}
```

**成功响应（200）：**
```json
{
  "status": "success",
  "data": "网页内容...",
  "_billing": {
    "mode": "static",
    "cost": 0.003,
    "balance_after": 0.091
  }
}
```

**余额不足响应（402）：**
```json
{
  "error": "余额不足",
  "balance": 0.002,
  "mode": "static",
  "cost": 0.003,
  "topup_wallet": "0x1630c8E0833c367F39f0ca909b6b67f5159d7A00",
  "chain": "Base",
  "token": "USDC"
}
```

## 充值方式

向收款地址发送 USDC（Base 链）：
```
0x1630c8E0833c367F39f0ca909b6b67f5159d7A00
```

充值后余额自动更新。