"""
TradingAgents 台股版 - Streamlit Web App
==========================================

執行方式:
    streamlit run app.py

需先設定 GOOGLE_API_KEY (放在 .env 或環境變數)。
"""
import os
import sys
import io
import contextlib
import traceback
from datetime import date, timedelta, datetime

import streamlit as st
from dotenv import load_dotenv, find_dotenv

# 載入 .env (若有)
load_dotenv(find_dotenv(usecwd=True))

# ----- 頁面設定 -----
st.set_page_config(
    page_title="TradingAgents 台股 AI 分析",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----- CSS 微調 -----
st.markdown(
    """
    <style>
        .main .block-container { padding-top: 1.5rem; }
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { font-size: 1.0rem; }
        .report-card {
            background: #fafafa; border: 1px solid #e6e6e6; border-radius: 8px;
            padding: 1rem 1.25rem; margin-bottom: 1rem;
        }
        .recommend-buy { color: #16a34a; font-weight: 700; }
        .recommend-sell { color: #dc2626; font-weight: 700; }
        .recommend-hold { color: #ca8a04; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----- Header -----
st.title("📈 TradingAgents - 台股 AI 多代理人分析")
st.caption(
    "由 Google Gemini 驅動的多代理人股票分析系統 · 基於 TradingAgents 框架 · "
    "使用 yfinance 抓取台股資料 (.TW / .TWO)"
)

# ============================================================
# Sidebar - 設定
# ============================================================
with st.sidebar:
    st.header("⚙️ 分析設定")

    # API Key
    api_key_input = st.text_input(
        "Google API Key",
        value=os.getenv("GOOGLE_API_KEY", ""),
        type="password",
        help="到 https://aistudio.google.com/apikey 申請免費 Gemini API Key",
    )
    if api_key_input:
        os.environ["GOOGLE_API_KEY"] = api_key_input

    st.divider()

    # 預載常見台股
    try:
        from tradingagents.dataflows.taiwan_stock import list_common_taiwan_tickers
        common_list = list_common_taiwan_tickers()
    except Exception:
        common_list = []

    # 股票代號
    st.subheader("📊 股票標的")
    pick_mode = st.radio(
        "選擇方式",
        ["從常用清單", "手動輸入代號"],
        horizontal=True,
    )

    if pick_mode == "從常用清單" and common_list:
        labels = [c["label"] for c in common_list]
        codes = [c["code"] for c in common_list]
        idx = st.selectbox("常用台股", range(len(labels)), format_func=lambda i: labels[i])
        ticker = codes[idx]
    else:
        ticker_raw = st.text_input(
            "輸入台股代號",
            value="2330",
            help="可輸入 4-6 碼數字 (例如 2330)，或直接含後綴 (2330.TW / 6488.TWO)",
        )
        ticker = ticker_raw.strip().upper()

    st.text(f"使用代號: {ticker}")

    # 日期
    st.subheader("📅 分析日期")
    analysis_date = st.date_input(
        "分析基準日",
        value=date.today() - timedelta(days=1),
        max_value=date.today(),
        help="基於該日期之前的資料進行分析",
    )

    st.divider()

    # 模型
    st.subheader("🤖 AI 模型")
    deep_model = st.selectbox(
        "深度思考模型 (辯論/研究)",
        ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"],
        index=0,
    )
    quick_model = st.selectbox(
        "快速思考模型 (資料整理)",
        ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"],
        index=0,
    )
    thinking_level = st.select_slider(
        "Gemini 思考強度",
        options=["minimal", "low", "medium", "high"],
        value="medium",
    )

    st.divider()

    # Analysts
    st.subheader("👥 分析師團隊")
    selected_analysts = st.multiselect(
        "選擇要啟用的分析師",
        options=["market", "social", "news", "fundamentals"],
        default=["market", "news", "fundamentals"],
        format_func=lambda x: {
            "market": "📈 市場/技術分析師",
            "social": "💬 社群輿情分析師",
            "news": "📰 新聞分析師",
            "fundamentals": "📊 基本面分析師",
        }[x],
    )

    debate_rounds = st.slider("辯論回合數", 1, 3, 1)
    risk_rounds = st.slider("風險討論回合數", 1, 3, 1)

    st.divider()
    run_button = st.button("🚀 開始分析", type="primary", use_container_width=True)

# ============================================================
# 主內容區
# ============================================================
tab_overview, tab_analysis, tab_about = st.tabs(["📊 標的概覽", "🤖 AI 分析", "ℹ️ 關於"])

# ----- Tab 1: 標的概覽 -----
with tab_overview:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("基本資料")
        try:
            from tradingagents.dataflows.taiwan_stock import get_taiwan_stock_info, lookup_taiwan_company_name
            info = get_taiwan_stock_info(ticker)
            zh_name = lookup_taiwan_company_name(ticker) or "—"
            st.metric("代號", info.get("symbol", ticker))
            st.metric("中文名", zh_name)
            st.metric("英文名", info.get("long_name") or info.get("short_name") or "—")
            st.metric("產業", info.get("industry") or "—")
            mc = info.get("market_cap")
            if mc:
                st.metric("市值", f"NT$ {mc/1e8:,.0f} 億")
            pc = info.get("previous_close")
            if pc:
                st.metric("前一日收盤", f"NT$ {pc:.2f}")
            pe = info.get("trailing_pe")
            if pe:
                st.metric("本益比 (TTM)", f"{pe:.2f}")
            dy = info.get("dividend_yield")
            if dy:
                st.metric("股息殖利率", f"{dy*100:.2f}%" if dy < 1 else f"{dy:.2f}%")
        except Exception as e:
            st.warning(f"無法取得 {ticker} 基本資料：{e}")

    with col2:
        st.subheader("近 60 日股價走勢")
        try:
            import yfinance as yf
            from tradingagents.dataflows.taiwan_stock import normalize_taiwan_ticker
            norm = normalize_taiwan_ticker(ticker)
            t = yf.Ticker(norm)
            hist = t.history(period="3mo")
            if not hist.empty:
                st.line_chart(hist["Close"], height=320)
                st.caption(f"資料來源: yfinance ({norm})")
                with st.expander("📋 原始資料 (最近 10 筆)"):
                    st.dataframe(hist.tail(10), use_container_width=True)
            else:
                st.info("查無資料，請確認代號")
        except Exception as e:
            st.error(f"無法取得股價: {e}")

# ----- Tab 2: AI 分析 -----
with tab_analysis:
    st.subheader(f"🤖 多代理人分析 — {ticker}")

    if not run_button:
        st.info(
            "👈 請在左側設定參數後按 **「開始分析」**。\n\n"
            "系統會啟動以下流程：\n"
            "1. 各分析師收集資料 (技術面/基本面/新聞/輿情)\n"
            "2. 多空研究員辯論\n"
            "3. 風險管理委員會討論\n"
            "4. 投資組合經理整合並輸出最終決策\n\n"
            "⏱️ 預估時間：依模型與辯論回合數，約 2~10 分鐘"
        )
    else:
        # 驗證 API Key
        if not os.getenv("GOOGLE_API_KEY"):
            st.error("❌ 請先在側邊欄輸入 Google API Key")
            st.stop()

        if not selected_analysts:
            st.error("❌ 請至少選擇一位分析師")
            st.stop()

        # 組合 config
        try:
            from tradingagents.default_config import DEFAULT_CONFIG
            from tradingagents.graph.trading_graph import TradingAgentsGraph

            config = DEFAULT_CONFIG.copy()
            config["llm_provider"] = "google"
            config["deep_think_llm"] = deep_model
            config["quick_think_llm"] = quick_model
            config["google_thinking_level"] = thinking_level
            config["max_debate_rounds"] = debate_rounds
            config["max_risk_discuss_rounds"] = risk_rounds
            config["output_language"] = "Traditional Chinese (繁體中文)"

            with st.status("🔄 正在初始化分析系統...", expanded=False) as status:
                ta = TradingAgentsGraph(
                    selected_analysts=selected_analysts,
                    debug=False,
                    config=config,
                )
                status.update(label="✅ 系統已就緒，開始分析…", state="running")

                progress_box = st.empty()
                progress_box.info(f"⏳ 分析中:  **{ticker}**  @  **{analysis_date.strftime('%Y-%m-%d')}**")

                # 執行分析
                state, decision = ta.propagate(ticker, analysis_date.strftime("%Y-%m-%d"))
                status.update(label="✅ 分析完成", state="complete")

            st.success("🎉 分析完成！結果如下")

            # 最終決策
            st.markdown("### 🎯 最終投資決策")
            st.markdown(f"<div class='report-card'>{decision}</div>", unsafe_allow_html=True)

            # 各分析師報告
            report_keys = [
                ("market_report", "📈 市場/技術分析"),
                ("sentiment_report", "💬 社群輿情分析"),
                ("news_report", "📰 新聞分析"),
                ("fundamentals_report", "📊 基本面分析"),
                ("investment_plan", "🎓 研究員投資計畫"),
                ("trader_investment_plan", "💼 交易員執行計畫"),
                ("final_trade_decision", "⚖️ 風險委員會最終裁決"),
            ]
            st.markdown("### 📚 詳細報告")
            for key, title in report_keys:
                content = state.get(key) if isinstance(state, dict) else None
                if content:
                    with st.expander(title, expanded=False):
                        st.markdown(content)

            # 下載報告
            full_report = f"# TradingAgents 台股分析報告\n\n"
            full_report += f"- **股票代號**: {ticker}\n"
            full_report += f"- **分析日期**: {analysis_date.strftime('%Y-%m-%d')}\n"
            full_report += f"- **分析師**: {', '.join(selected_analysts)}\n"
            full_report += f"- **模型**: {deep_model} / {quick_model}\n"
            full_report += f"- **產生時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            full_report += f"## 🎯 最終決策\n\n{decision}\n\n"
            for key, title in report_keys:
                content = state.get(key) if isinstance(state, dict) else None
                if content:
                    full_report += f"## {title}\n\n{content}\n\n"

            st.download_button(
                "💾 下載完整報告 (Markdown)",
                data=full_report,
                file_name=f"TradingAgents_{ticker}_{analysis_date.strftime('%Y%m%d')}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        except Exception as e:
            st.error(f"❌ 分析過程發生錯誤: {e}")
            with st.expander("🐛 詳細錯誤訊息"):
                st.code(traceback.format_exc())

# ----- Tab 3: 關於 -----
with tab_about:
    st.markdown(
        """
        ### 關於本專案

        本專案改編自 [TradingAgents](https://github.com/TauricResearch/TradingAgents)
        多代理人金融交易框架，**專為台灣股市最佳化**：

        - 🇹🇼 **台股代號自動補全**：輸入 `2330` 自動轉成 `2330.TW`
        - 🤖 **預設使用 Google Gemini**：透過 Gemini 2.5 系列模型運作
        - 🈵 **繁體中文報告**：所有分析師輸出中文，方便閱讀
        - 📊 **yfinance 免費資料**：無需額外申請台股資料 API

        ### 技術架構

        - **分析師團隊** (Analysts)：市場/技術、新聞、社群、基本面
        - **多空研究員** (Researchers)：Bull vs Bear 辯論
        - **交易員** (Trader)：根據研究員結論擬定交易計畫
        - **風險委員會** (Risk Mgmt)：保守 / 中立 / 積極 三方討論
        - **投資組合經理** (Portfolio Manager)：最終決策

        ### 免責聲明

        > ⚠️ 本系統僅供 **學術研究與技術示範**，不構成投資建議。
        > 任何依本系統判斷產生之損益，使用者需自行承擔。
        """
    )

# ----- Footer -----
st.markdown("---")
st.caption("Powered by TradingAgents · Google Gemini · yfinance · Streamlit")
