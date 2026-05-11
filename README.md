# TradingAgents 台股版 🇹🇼📈

> 由 **Google Gemini** 驅動的多代理人台股 AI 分析系統，附帶 **Streamlit Web App** 介面。
> 改編自 [TauricResearch / TradingAgents](https://github.com/TauricResearch/TradingAgents)，專為台灣股市最佳化。

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36%2B-red)]()
[![Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-4285F4)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-green)]()

---

## ✨ 特色

- 🇹🇼 **台股代號自動補全**：直接輸入 `2330`，系統自動轉成 `2330.TW`，也支援上櫃 `.TWO`
- 🤖 **預設 Google Gemini**：使用 Gemini 2.5 Pro / Flash，免費額度即可體驗
- 🈵 **繁體中文輸出**：所有分析師報告、最終決策皆為繁中
- 📊 **免費資料來源**：透過 yfinance 抓取台股日線、基本面、新聞
- 🌐 **內建 Web App**：Streamlit 介面，1 行指令即可啟動
- ☁️ **可一鍵部署**：支援 Streamlit Cloud / Docker / 任意雲端

## 🖼️ 介面預覽

啟動後會看到：

| 標的概覽 | AI 分析 |
| --- | --- |
| 公司資料、近 3 個月走勢、本益比、殖利率 | 多代理人辯論結果、最終投資決策、可下載 Markdown 報告 |

## 🚀 快速開始

### 1. 安裝環境

```bash
git clone https://github.com/<your-account>/TradingAgents-Taiwan.git
cd TradingAgents-Taiwan

# 建議使用 Python 3.10+
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. 設定 API Key

到 <https://aistudio.google.com/apikey> 申請 **免費的 Gemini API Key**，然後：

```bash
cp .env.example .env
# 編輯 .env，填入：
# GOOGLE_API_KEY=你的_KEY
```

或者，啟動 Web App 後直接在側邊欄輸入也可以。

### 3. 啟動 Web App

```bash
streamlit run app.py
```

打開瀏覽器到 <http://localhost:8501>，輸入台股代號（如 `2330`、`0050`、`2454`）按下 **🚀 開始分析** 即可。

### 4. (選用) 命令列模式

```bash
python main.py
```

`main.py` 預設分析 `2330`，可自行修改。

---

## 📂 專案結構

```
TradingAgents-Taiwan/
├── app.py                       ← Streamlit Web App 入口
├── main.py                      ← 命令列範例
├── requirements.txt
├── .env.example                 ← API Key 範本
├── .streamlit/
│   ├── config.toml              ← Streamlit 主題設定
│   └── secrets.toml.example     ← Streamlit Cloud secrets 範本
├── tradingagents/
│   ├── default_config.py        ← 預設用 Gemini + 繁中輸出
│   ├── dataflows/
│   │   ├── taiwan_stock.py      ← 🆕 台股代號處理 (.TW / .TWO)
│   │   ├── y_finance.py         ← 已修改：自動補台股後綴
│   │   ├── yfinance_news.py     ← 已修改：自動補台股後綴
│   │   └── stockstats_utils.py  ← 已修改：自動補台股後綴
│   ├── agents/                  ← 各分析師、研究員、交易員、風險委員
│   ├── graph/                   ← LangGraph 流程編排
│   └── llm_clients/             ← LLM 供應商抽象層
└── cli/                         ← 互動式 CLI (原作者)
```

## 🇹🇼 台股代號規則

| 你輸入的     | 系統實際抓取的 | 說明 |
| ------------ | -------------- | ---- |
| `2330`       | `2330.TW`      | 自動加上市後綴 |
| `0050`       | `0050.TW`      | ETF 也支援 |
| `6488.TWO`   | `6488.TWO`     | 已含上櫃後綴，原樣 |
| `TSM`        | `TSM`          | ADR / 美股不變動 |

如要查詢上櫃股票，建議直接輸入完整代號（例如 `6488.TWO`）。

### 內建常用標的清單

- **權值股**：2330 台積電、2317 鴻海、2454 聯發科、2412 中華電…
- **金控**：2882 國泰金、2881 富邦金、2891 中信金…
- **熱門 ETF**：0050、0056、00878、00919、00929、00940…
- **航運**：2603 長榮、2609 陽明、2615 萬海

完整清單見 [`tradingagents/dataflows/taiwan_stock.py`](tradingagents/dataflows/taiwan_stock.py)。

## ⚙️ 系統架構

```
┌──────────────┐
│  Streamlit   │  ← 使用者輸入代號 + 日期
└──────┬───────┘
       │
       ▼
┌────────────────────────────────────────────────────┐
│  TradingAgentsGraph  (LangGraph)                   │
│                                                    │
│  ① 分析師團隊  (Market / News / Social / Fund.)   │
│         ↓                                          │
│  ② 多空研究員辯論  (Bull vs Bear)                  │
│         ↓                                          │
│  ③ 交易員 → 擬定執行計畫                            │
│         ↓                                          │
│  ④ 風險委員會  (保守 / 中立 / 積極)                 │
│         ↓                                          │
│  ⑤ 投資組合經理 → 最終決策                          │
└────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│  繁中報告    │
│  + Markdown  │
└──────────────┘
```

## ☁️ 部署到 Streamlit Cloud

1. Fork 或 Push 本專案到你自己的 GitHub
2. 到 <https://share.streamlit.io> 連結 GitHub repo
3. 主檔案路徑填 `app.py`
4. 在 **Settings → Secrets** 貼上：
   ```toml
   GOOGLE_API_KEY = "你的_KEY"
   ```
5. Deploy 完成 🎉

## 🐳 Docker 部署

```bash
docker build -t trading-tw .
docker run -p 8501:8501 -e GOOGLE_API_KEY=你的_KEY trading-tw streamlit run app.py
```

## 🔑 可選：切換其他 LLM

預設使用 Google Gemini。若想換成 OpenAI / Anthropic，只需在 `app.py` 或 `default_config.py` 修改：

```python
config["llm_provider"] = "openai"        # 或 "anthropic", "deepseek", ...
config["deep_think_llm"] = "gpt-4o"
config["quick_think_llm"] = "gpt-4o-mini"
```

並在 `.env` 補上對應 API Key。

## 📜 授權

本專案遵循上游 TradingAgents 的 **Apache 2.0** License。

## 🙏 鳴謝

- 上游框架：[TauricResearch / TradingAgents](https://github.com/TauricResearch/TradingAgents)
- 資料來源：[yfinance](https://github.com/ranaroussi/yfinance)
- LLM：[Google Gemini](https://ai.google.dev/)

## ⚠️ 免責聲明

> 本系統僅供 **學術研究、技術示範** 之用。
> AI 分析結果 **不構成投資建議**，任何投資決策請自行評估、自負盈虧。
> 台股交易涉及匯率、交易稅、手續費等成本，本系統未必納入完整模型。
