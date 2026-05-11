"""
TradingAgents 台股版 - 命令列範例
=================================

使用範例:
    python main.py                # 預設分析 2330 (台積電)
    python main.py 2454           # 分析 2454 (聯發科)
    python main.py 0050 2025-05-01

需先設定 GOOGLE_API_KEY (放在 .env 或環境變數)。
"""
import sys
from datetime import date, timedelta

from dotenv import find_dotenv, load_dotenv

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

load_dotenv(find_dotenv(usecwd=True))


def main():
    ticker = sys.argv[1] if len(sys.argv) > 1 else "2330"
    if len(sys.argv) > 2:
        analysis_date = sys.argv[2]
    else:
        analysis_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = 1

    print(f"\n[Start] 分析台股: {ticker} @ {analysis_date}")
    print(f"[LLM]   {config['deep_think_llm']} / {config['quick_think_llm']}\n")

    ta = TradingAgentsGraph(debug=True, config=config)
    state, decision = ta.propagate(ticker, analysis_date)

    print("\n" + "=" * 60)
    print("最終決策")
    print("=" * 60)
    print(decision)


if __name__ == "__main__":
    main()
