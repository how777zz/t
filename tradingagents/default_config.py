import os

_TRADINGAGENTS_HOME = os.path.join(os.path.expanduser("~"), ".tradingagents")

# ============================================================
# Taiwan Stock Edition - Powered by Google Gemini
# 預設使用 Google Gemini 2.5，並以繁體中文輸出分析報告
# ============================================================

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", os.path.join(_TRADINGAGENTS_HOME, "logs")),
    "data_cache_dir": os.getenv("TRADINGAGENTS_CACHE_DIR", os.path.join(_TRADINGAGENTS_HOME, "cache")),
    "memory_log_path": os.getenv("TRADINGAGENTS_MEMORY_LOG_PATH", os.path.join(_TRADINGAGENTS_HOME, "memory", "trading_memory.md")),
    # Optional cap on the number of resolved memory log entries.
    "memory_log_max_entries": None,

    # ----- LLM 設定 (預設 Google Gemini) -----
    "llm_provider": "google",
    "deep_think_llm": "gemini-2.5-pro",       # 深度思考 (辯論、研究員、風險評估)
    "quick_think_llm": "gemini-2.5-flash",    # 快速思考 (分析師資料整理)
    "backend_url": None,

    # Gemini thinking level: "high" / "medium" / "low" / "minimal"
    "google_thinking_level": "medium",
    "openai_reasoning_effort": None,
    "anthropic_effort": None,

    # Checkpoint
    "checkpoint_enabled": False,

    # ----- 輸出語言 -----
    # 分析師報告與最終決策以繁體中文輸出
    # (內部 agent 辯論仍以英文進行，以維持推理品質)
    "output_language": "Traditional Chinese (繁體中文)",

    # ----- 辯論設定 -----
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,

    # ----- 資料來源 (預設 yfinance, 支援 .TW / .TWO 後綴抓台股) -----
    "data_vendors": {
        "core_stock_apis": "yfinance",
        "technical_indicators": "yfinance",
        "fundamental_data": "yfinance",
        "news_data": "yfinance",
    },
    "tool_vendors": {},

    # ----- 台股專用設定 -----
    # 自動補全代號:輸入「2330」會自動加上 .TW 後綴變成 2330.TW
    "taiwan_stock_auto_suffix": True,
    # 預設市場別: "TWSE" (上市) 或 "TPEx" (上櫃)
    "taiwan_default_market": "TWSE",
}
