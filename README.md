# ODDCS-Protocol
Global Agent Gateway for Chinese Web. Pay-per-fetch, 100% Autonomous on Base Mainnet.
# ODDCS-Protocol: Global Agent Gateway for Chinese Web

An experimental bridge connecting Global AI Agents to the fragmented Chinese Internet (XHS, Zhihu, etc.) via **x402 Protocol** and **Base Mainnet**.

## 🚀 The Mission
Modern LLM Agents struggle with the "HTML Noise" and "Anti-Bot Walls" of the Chinese web. ODDCS (On-Demand Data Distillation) solves this by:
1. **Distilling**: Converting messy HTML into token-efficient Markdown.
2. **Autonomous Payment**: Utilizing the x402 protocol for sub-cent, pay-per-fetch settlements on Base.
3. **M2M Ready**: Zero API keys required. Your agent pays, your agent gets data.

## 🛠️ Architecture


- **Node**: `https://api.060504.shop` (Active)
- **Settlement**: $USDC on Base Mainnet.
- **Protocol**: x402 (HTTP 402 Payment Required integration).

## 📖 Live Example (Distillation Result)
**Input:** `https://www.xiaohongshu.com/discovery/item/...`
**Output:**
---
Source: Xiaohongshu | Author: Rango老师
Topic: UCASS University Name Change Analysis
Tokens Saved: ~90%
---
[Clean Markdown Content...]

## 🤝 Getting Started
To interact with an ODDCS node, your agent should be configured to handle HTTP 402 responses and sign transactions on the Base network. 

Detailed specs for the `x-base-node-address` header and payload structure coming soon.

---
**Build in Public. No Fake Specs. Just Data.**
