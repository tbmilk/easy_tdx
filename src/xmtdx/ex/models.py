"""扩展行情数据模型与常量。"""

from dataclasses import dataclass, field

# 扩展行情服务器（端口 7727），来源: pytdx_backup/util/best_ip.py
KNOWN_EX_HOSTS: list[str] = [
    "106.14.95.149",
    "112.74.214.43",
    "119.147.86.171",
    "119.97.185.5",
    "120.24.0.77",
    "47.92.127.181",
    "59.175.238.38",
    "61.152.107.141",
    "61.152.107.171",
    "47.107.75.159",
    "120.25.218.6",
    "43.139.173.246",
    "159.75.90.107",
    "106.52.170.195",
    "139.9.191.175",
    "175.24.47.69",
    "150.158.9.199",
    "150.158.20.127",
    "49.235.119.116",
    "49.234.13.160",
    "116.205.143.214",
    "124.71.223.19",
    "113.45.175.47",
    "123.60.173.210",
    "118.89.69.202",
]

# 已知扩展行情市场代码
KNOWN_EX_MARKETS: dict[int, str] = {
    0: "深圳",
    1: "上海",
    28: "郑州商品",
    29: "大连商品",
    30: "上海期货",
    31: "香港主板",
    47: "中金所",
    48: "香港创业板",
    49: "香港基金",
    71: "沪港通",
    74: "外盘",
}

_DEFAULT_EX_PORT = 7727


@dataclass
class ExMarketInfo:
    """市场定义（GetMarkets 返回）。"""

    market: int
    category: int
    name: str
    short_name: str
    _raw: bytes = field(default=b"", repr=False, compare=False)


@dataclass
class ExInstrumentInfo:
    """合约/证券信息（GetInstrumentInfo 返回）。"""

    category: int
    market: int
    code: str
    name: str
    desc: str
    _raw: bytes = field(default=b"", repr=False, compare=False)


@dataclass
class ExInstrumentQuote:
    """五档行情（GetInstrumentQuote 返回）。"""

    market: int
    code: str
    pre_close: float
    open: float
    high: float
    low: float
    price: float
    kaicang: int
    zongliang: int
    xianliang: int
    neipan: int
    waipan: int
    chicang: int
    bid1: float
    bid2: float
    bid3: float
    bid4: float
    bid5: float
    bid_vol1: int
    bid_vol2: int
    bid_vol3: int
    bid_vol4: int
    bid_vol5: int
    ask1: float
    ask2: float
    ask3: float
    ask4: float
    ask5: float
    ask_vol1: int
    ask_vol2: int
    ask_vol3: int
    ask_vol4: int
    ask_vol5: int
    _raw: bytes = field(default=b"", repr=False, compare=False)


@dataclass
class ExInstrumentBar:
    """K线数据（GetInstrumentBars / GetHistoryInstrumentBarsRange 返回）。"""

    open: float
    high: float
    low: float
    close: float
    position: int
    trade: int
    amount: float
    year: int
    month: int
    day: int
    hour: int
    minute: int
    _raw: bytes = field(default=b"", repr=False, compare=False)


@dataclass
class ExMinuteBar:
    """分时数据（GetMinuteTimeData / GetHistoryMinuteTimeData 返回）。"""

    hour: int
    minute: int
    price: float
    avg_price: float
    volume: int
    open_interest: int
    _raw: bytes = field(default=b"", repr=False, compare=False)


@dataclass
class ExTransactionRecord:
    """逐笔成交记录（GetTransactionData / GetHistoryTransactionData 返回）。"""

    hour: int
    minute: int
    second: int
    price: int
    volume: int
    zengcang: int
    nature: int
    _raw: bytes = field(default=b"", repr=False, compare=False)
