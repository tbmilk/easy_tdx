"""演示：从本地通达信目录读取扩展市场日线数据。

扩展市场包括：期货、港股、外盘等。
文件位于 vipdoc/ds/ 目录下，如 29#A1801.day

需要本地已安装通达信并下载过扩展市场数据。
"""

from pathlib import Path

from xmtdx.offline import detect_tdx_home, read_ex_daily_bars

home = detect_tdx_home()
if home is None:
    print("未检测到通达信安装目录，请设置 TDX_HOME 环境变量")
    raise SystemExit(1)

vipdoc = Path(home) / "vipdoc" / "ds" / "lday"

# 列出 ds 目录下可用的 .day 文件
day_files = sorted(vipdoc.glob("*.day")) if vipdoc.is_dir() else []
if not day_files:
    print(f"扩展市场目录为空或不存在: {vipdoc}")
    print("请在通达信中下载扩展市场数据后再试")
    raise SystemExit(0)

print(f"可用文件 ({len(day_files)} 个):")
for f in day_files[:10]:
    print(f"  {f.name}")
if len(day_files) > 10:
    print(f"  ... 还有 {len(day_files) - 10} 个")

# 读取第一个文件作为示例
sample = day_files[5]
"""
可用文件 (211 个):
  12#A_IXIC.day
  38#1_GDP.day
  38#1_GDPI.day
  38#1_MSR.day
  38#2_CGPI.day
  38#2_CPI.day
  38#2_PPCI.day
  38#2_PPI.day
  38#2_PPPI.day
  38#3_BCI.day
  ... 还有 201 个

读取: 38#2_CPI.day
共 250 条记录，最后 5 条:
            日期        开盘        最高        最低        收盘        结算
  2025-12-31    100.80    100.80    100.80    100.80      0.00
  2026-01-31    100.20    100.20    100.20    100.20      0.00
  2026-02-28    101.30    101.30    101.30    101.30      0.00
  2026-03-31    101.00    101.00    101.00    101.00      0.00
  2026-04-30    101.20    101.20    101.20    101.20      0.00
"""
print(f"\n读取: {sample.name}")
bars = read_ex_daily_bars(sample)

if bars:
    print(f"共 {len(bars)} 条记录，最后 5 条:")
    print(f"  {'日期':>12s}  {'开盘':>8s}  {'最高':>8s}  {'最低':>8s}  {'收盘':>8s}  {'结算':>8s}")
    for bar in bars[-5:]:
        print(
            f"  {bar.year}-{bar.month:02d}-{bar.day:02d}  "
            f"{bar.open:>8.2f}  {bar.high:>8.2f}  "
            f"{bar.low:>8.2f}  {bar.close:>8.2f}  {bar.settlement:>8.2f}"
        )
