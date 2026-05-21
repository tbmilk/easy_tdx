"""演示：从本地通达信目录读取分钟 K 线数据。

支持三种文件格式：
  - .5   文件: vipdoc/{sh,sz}/fzline/  (OHLC 为整数÷100)
  - .lc1 文件: vipdoc/{sh,sz}/fzline/ (OHLC 为浮点数)
  - .lc5 文件: vipdoc/{sh,sz}/fzline/ (OHLC 为浮点数)

需要本地已安装通达信并下载过分钟数据。
"""

from xmtdx.offline import (
    detect_tdx_home,
    read_5min_bars,
    read_lc_min_bars,
    find_5min_bar_file,
    find_lc1_bar_file,
    find_lc5_bar_file,
)
from xmtdx import Market

home = detect_tdx_home()
if home is None:
    print("未检测到通达信安装目录，请设置 TDX_HOME 环境变量")
    raise SystemExit(1)

"""
# --- .5 文件 (5 分钟线) ---
print("=" * 60)
print("5 分钟线 (.5 文件)")
print("=" * 60)

filepath = find_5min_bar_file(Market.SH, "600000")
bars = read_5min_bars(filepath)
if bars:
    print(f"共 {len(bars)} 条记录，最后 5 条:")
    for bar in bars[-5:]:
        print(
            f"  {bar.year}-{bar.month:02d}-{bar.day:02d} "
            f"{bar.hour:02d}:{bar.minute:02d}  "
            f"开{bar.open:>7.2f} 高{bar.high:>7.2f} "
            f"低{bar.low:>7.2f} 收{bar.close:>7.2f} 量{bar.vol:>8.0f}"
        )
else:
    print("未读取到数据")

# --- .lc1 文件 (1 分钟线) ---
print(f"\n{'=' * 60}")
print("1 分钟线 (.lc1 文件)")
print("=" * 60)

filepath = find_lc1_bar_file(Market.SH, "600000")
bars = read_lc_min_bars(filepath)
if bars:
    print(f"共 {len(bars)} 条记录，最后 5 条:")
    for bar in bars[-5:]:
        print(
            f"  {bar.year}-{bar.month:02d}-{bar.day:02d} "
            f"{bar.hour:02d}:{bar.minute:02d}  "
            f"开{bar.open:>7.2f} 高{bar.high:>7.2f} "
            f"低{bar.low:>7.2f} 收{bar.close:>7.2f} 量{bar.vol:>8.0f}"
        )
else:
    print("未读取到数据")
"""

# --- .lc5 文件 (5 分钟线) ---
print(f"\n{'=' * 60}")
print("5 分钟线 (.lc5 文件)")
print("=" * 60)

filepath = find_lc5_bar_file(Market.SZ, "002176")
bars = read_lc_min_bars(filepath)
if bars:
    print(f"共 {len(bars)} 条记录，最后 5 条:")
    for bar in bars[-5:]:
        print(
            f"  {bar.year}-{bar.month:02d}-{bar.day:02d} "
            f"{bar.hour:02d}:{bar.minute:02d}  "
            f"开{bar.open:>7.2f} 高{bar.high:>7.2f} "
            f"低{bar.low:>7.2f} 收{bar.close:>7.2f} 量{bar.vol:>8.0f}"
        )
else:
    print("未读取到数据")
