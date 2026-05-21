"""演示：从本地通达信目录读取日线 K 线数据。

两种用法：
  1. 直接指定 .day 文件路径
  2. 通过 市场+代码 自动定位文件（需要设置 TDX_HOME 环境变量）

需要本地已安装通达信并下载过日线数据。
"""

from xmtdx.offline import detect_tdx_home, read_daily_bars, find_daily_bar_file
from xmtdx import Market

home = detect_tdx_home()
if home is None:
    print("未检测到通达信安装目录，请设置 TDX_HOME 环境变量")
    print("例如: set TDX_HOME=C:\\new_jyplug")
    raise SystemExit(1)

print(f"通达信目录: {home}")

# --- 方式1: 通过 市场+代码 自动定位文件 ---
filepath = find_daily_bar_file(Market.SH, "600000")
print(f"\n文件路径: {filepath}")

bars = read_daily_bars(filepath)
if not bars:
    print("未读取到数据，请确认通达信已下载该股票的日线数据")
    raise SystemExit(0)

# 最近 10 个交易日
print(f"\n浦发银行 日线 (最近 {min(10, len(bars))} 个交易日):")
print(f"{'日期':>12s}  {'开盘':>8s}  {'最高':>8s}  {'最低':>8s}  {'收盘':>8s}  {'成交量':>10s}")
for bar in bars[-10:]:
    print(
        f"{bar.year}-{bar.month:02d}-{bar.day:02d}  "
        f"{bar.open:>8.2f}  {bar.high:>8.2f}  "
        f"{bar.low:>8.2f}  {bar.close:>8.2f}  "
        f"{bar.vol:>10.0f}"
    )

# --- 方式2: 直接指定文件路径 ---
# from pathlib import Path
# bars2 = read_daily_bars(Path(r"C:\new_jyplug\vipdoc\sz\lday\sz000001.day"))
