"""
台股代號處理 & yfinance 整合工具
=================================

提供以下功能：
1. 自動為台股代號補上 .TW (上市) 或 .TWO (上櫃) 後綴
2. 常用台股代號 → 公司名稱對照
3. 包裝 yfinance，回傳台幣計價資料

支援格式範例：
- "2330"      → "2330.TW"   (自動判斷為上市)
- "2330.TW"   → "2330.TW"   (已含後綴，直接回傳)
- "00646.TWO" → "00646.TWO" (上櫃，已含後綴)
- "TSM"       → "TSM"       (英文代號 ADR，不變動)
"""
from typing import Annotated, Optional
import re
import pandas as pd
import yfinance as yf

# 常見台股代號 (上市)
TWSE_COMMON = {
    "2330": "台積電 (TSMC)",
    "2317": "鴻海 (Foxconn)",
    "2454": "聯發科 (MediaTek)",
    "2412": "中華電信",
    "2308": "台達電",
    "2882": "國泰金",
    "2881": "富邦金",
    "1301": "台塑",
    "1303": "南亞",
    "2002": "中鋼",
    "2891": "中信金",
    "2884": "玉山金",
    "3711": "日月光投控",
    "2303": "聯電",
    "2357": "華碩",
    "2382": "廣達",
    "1216": "統一",
    "2207": "和泰車",
    "2105": "正新",
    "1101": "台泥",
    "5880": "合庫金",
    "2603": "長榮海運",
    "2609": "陽明海運",
    "2615": "萬海",
    "2912": "統一超",
    "0050": "元大台灣 50 ETF",
    "0056": "元大高股息 ETF",
    "00878": "國泰永續高股息 ETF",
    "00919": "群益台灣精選高息 ETF",
    "00929": "復華台灣科技優息 ETF",
    "00940": "元大台灣價值高息 ETF",
}

# 常見台股代號 (上櫃)
TPEX_COMMON = {
    "6488": "環球晶",
    "5483": "中美晶",
    "3105": "穩懋",
    "4966": "譜瑞-KY",
    "6446": "藥華藥",
    "8069": "元太",
    "5371": "中光電",
    "6182": "合晶",
}


def normalize_taiwan_ticker(symbol: str, default_market: str = "TWSE") -> str:
    """
    將輸入的台股代號標準化為 yfinance 接受的格式。

    Args:
        symbol: 使用者輸入的代號 (例如 "2330", "2330.TW", "00646.TWO")
        default_market: 預設市場 ("TWSE" → .TW, "TPEx" → .TWO)

    Returns:
        標準化後的 yfinance 代號
    """
    if not symbol:
        return symbol

    s = symbol.strip().upper()

    # 已包含 .TW / .TWO 後綴 → 直接回傳
    if s.endswith(".TW") or s.endswith(".TWO"):
        return s

    # 純英文代號 (例如 ADR: TSM, AAPL) → 不變動
    if re.fullmatch(r"[A-Z]+", s):
        return s

    # 純數字代號 → 加上後綴
    if re.fullmatch(r"\d{4,6}", s):
        # 上櫃股票通常以特定號段開頭，但簡單起見：
        # 先依預設市場判斷；若使用者明確需要上櫃，請傳 default_market="TPEx"
        if default_market.upper() == "TPEX":
            return f"{s}.TWO"
        return f"{s}.TW"

    # 其他情況 → 維持原樣
    return s


def lookup_taiwan_company_name(symbol: str) -> Optional[str]:
    """查詢台股代號對應的公司名稱 (僅常見標的)。"""
    if not symbol:
        return None
    raw = symbol.replace(".TW", "").replace(".TWO", "").strip().upper()
    return TWSE_COMMON.get(raw) or TPEX_COMMON.get(raw)


def get_taiwan_stock_data(
    symbol: Annotated[str, "台股代號 (例如 2330 或 2330.TW)"],
    start_date: Annotated[str, "起始日期 yyyy-mm-dd"],
    end_date: Annotated[str, "結束日期 yyyy-mm-dd"],
) -> str:
    """
    抓取台股歷史價格資料，回傳 CSV 字串。

    使用 yfinance 抓取資料，支援上市 (.TW) 與上櫃 (.TWO) 標的。
    """
    norm = normalize_taiwan_ticker(symbol)
    ticker = yf.Ticker(norm)
    data = ticker.history(start=start_date, end=end_date)

    if data.empty:
        return f"找不到代號 '{symbol}' (標準化為 '{norm}') 在 {start_date} 至 {end_date} 的資料"

    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    for col in ("Open", "High", "Low", "Close", "Adj Close"):
        if col in data.columns:
            data[col] = data[col].round(2)

    company = lookup_taiwan_company_name(symbol) or "—"
    header = (
        f"# 台股資料: {norm}  ({company})\n"
        f"# 期間: {start_date} ~ {end_date}\n"
        f"# 共 {len(data)} 筆交易日\n"
        f"# 計價幣別: TWD\n\n"
    )
    return header + data.to_csv()


def get_taiwan_stock_info(symbol: str) -> dict:
    """取得台股基本面資訊 (公司名稱、產業、市值等)。"""
    norm = normalize_taiwan_ticker(symbol)
    try:
        ticker = yf.Ticker(norm)
        info = ticker.info or {}
    except Exception as e:
        return {"error": f"無法取得 {norm} 的資訊: {e}"}

    return {
        "symbol": norm,
        "company_name_zh": lookup_taiwan_company_name(symbol),
        "long_name": info.get("longName"),
        "short_name": info.get("shortName"),
        "industry": info.get("industry"),
        "sector": info.get("sector"),
        "market_cap": info.get("marketCap"),
        "currency": info.get("currency", "TWD"),
        "previous_close": info.get("previousClose"),
        "trailing_pe": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "dividend_yield": info.get("dividendYield"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
    }


def list_common_taiwan_tickers() -> list:
    """回傳常用台股代號列表 (給 UI 下拉選單使用)。"""
    items = []
    for code, name in TWSE_COMMON.items():
        items.append({"code": f"{code}.TW", "label": f"{code}  {name}"})
    for code, name in TPEX_COMMON.items():
        items.append({"code": f"{code}.TWO", "label": f"{code}  {name} (上櫃)"})
    return items
