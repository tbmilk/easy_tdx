"""缠论分析路由。"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from easy_tdx.web.deps import get_client
from easy_tdx.web.schemas import ChanlunRequest

router = APIRouter(tags=["chanlun"])


def _market(market: str) -> Any:
    from easy_tdx.models.enums import Market

    return Market[market.upper()]


def _category(category: str) -> Any:
    from easy_tdx.models.enums import KlineCategory

    try:
        return KlineCategory(int(category))
    except (ValueError, TypeError):
        return KlineCategory[category.upper()]


@router.post("/chanlun/analyze")
async def chanlun_analyze(
    req: ChanlunRequest,
    client: Any = Depends(get_client),
) -> dict[str, Any]:
    """执行缠论分析。

    自动从 TDX 服务器获取 K 线数据，运行完整缠论计算管道，
    返回笔、中枢、线段、买卖点、背驰等分析结果。
    """
    from easy_tdx.chanlun import ChanlunAnalyser

    # 1. Fetch kline data
    df = await client.get_security_bars(
        _market(req.market), req.code, _category(req.category), req.start, req.count
    )

    # 2. Run chanlun analysis
    symbol = f"{req.market}{req.code}"
    frequency_map: dict[str, str] = {
        "MIN_1": "1min",
        "MIN_5": "5min",
        "MIN_15": "15min",
        "MIN_30": "30min",
        "MIN_60": "60min",
        "DAY": "daily",
        "WEEK": "weekly",
        "MONTH": "monthly",
        "YEAR": "yearly",
    }
    freq = frequency_map.get(req.category.upper(), req.category)
    analyser = ChanlunAnalyser(code=symbol, frequency=freq)
    result = analyser.process_klines(df)

    return result.to_dict()
