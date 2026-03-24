# 快速体验示例

## 准备工作

1. 获取 API Key
2. 确保账户有 USDC 余额

## Python 示例

```python
import requests

API_KEY = "your_api_key_here"
BASE_URL = "https://api.agentbridge.xyz"

def fetch_url(url: str, output_format: str = "markdown"):
    response = requests.post(
        f"{BASE_URL}/v1/fetch/dynamic",
        json={"url": url, "output_format": output_format},
        headers={"X-API-Key": API_KEY}
    )
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 402:
        print("余额不足，请充值")
        print(f"充值地址: {response.json()['topup_wallet']}")
    else:
        print(f"错误: {response.status_code}")
    
    return None

# 使用示例
result = fetch_url("https://example.com")
if result:
    print(result["data"])
    print(f"消耗: {result['_billing']['cost']} USDC")
    print(f"剩余: {result['_billing']['balance_after']} USDC")
cURL 示例
bash
curl -X POST https://api.agentbridge.xyz/v1/fetch/dynamic \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "url": "https://example.com",
    "output_format": "markdown"
  }'
充值
向以下地址发送 USDC（Base 链）：

text
0x1630c8E0833c367F39f0ca909b6b67f5159d7A00
充值后余额会自动更新。

text

---

确认 `examples/demo.md` 创建后，我们进行下一步：**优化 X 置顶推文**。