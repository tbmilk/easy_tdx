"""演示：从本地通达信目录读取股本变迁数据。

股本变迁文件包含分红、送股、配股、扩缩股等历史记录。
数据使用 XOR 加密存储，读取时会自动解密。

需要本地已安装通达信。
"""

from pathlib import Path

from xmtdx.offline import detect_tdx_home, read_gbbq

home = detect_tdx_home()
if home is None:
    print("未检测到通达信安装目录，请设置 TDX_HOME 环境变量")
    raise SystemExit(1)

gbbq_path = Path(home) / "T0002" / "hq_cache" / "gbbq"
if not gbbq_path.is_file():
    # 尝试其他可能的路径
    gbbq_path = Path(home) / "T0002" / "gbbq"

if not gbbq_path.is_file():
    print(f"股本变迁文件不存在")
    print(f"  尝试过: {Path(home) / 'T0002' / 'hq_cache' / 'gbbq'}")
    print(f"  尝试过: {Path(home) / 'T0002' / 'gbbq'}")
    print("请在通达信中确认 gbbq 文件的位置")
    raise SystemExit(0)

print(f"读取: {gbbq_path}")
records = read_gbbq(gbbq_path)

if not records:
    print("未读取到数据")
    raise SystemExit(0)

print(f"共 {len(records)} 条股本变迁记录\n")

# 按代码分组统计
from collections import Counter

code_counts = Counter(r.code for r in records)
print(f"涉及 {len(code_counts)} 只股票")

# 显示前 20 条记录
print(f"\n前 20 条记录:")
print(f"  {'市场':>4s}  {'代码':>8s}  {'日期':>10s}  {'类别':>4s}  {'红利/盘前流通':>12s}  {'配股价/前总股本':>14s}")
for rec in records[:20]:
    print(
        f"  {rec.market:>4d}  {rec.code:>8s}  {rec.datetime:>10d}  "
        f"{rec.category:>4d}  {rec.hongli_panqianliutong:>12.4f}  "
        f"{rec.peigujia_qianzongguben:>14.4f}"
    )
