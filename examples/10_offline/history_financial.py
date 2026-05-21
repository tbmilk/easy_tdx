"""演示：从本地通达信目录读取历史财务数据。

支持两种文件格式：
  - .dat 文件: 直接读取
  - .zip 文件: 自动解压后读取（如 gpcw20260331.zip）

文件可通过 TdxClient.get_financial_file_list() + download_file() 获取，
也可从 calc 服务器下载。

需要本地有 gpcw*.dat 或 gpcw*.zip 文件。
"""

from pathlib import Path

from xmtdx.offline import detect_tdx_home, read_history_financial

home = detect_tdx_home()
if home is None:
    print("未检测到通达信安装目录，请设置 TDX_HOME 环境变量")
    raise SystemExit(1)

# 常见的历史财务数据存放位置
candidates = [
    Path(home) / "vipdoc" / "fin",
    Path(home) / "T0002" / "fin",
    Path.home() / "Downloads",
    Path("."),
]

# 查找可用的财务数据文件
fin_files: list[Path] = []
for d in candidates:
    if d.is_dir():
        fin_files.extend(d.glob("gpcw*.dat"))
        fin_files.extend(d.glob("gpcw*.zip"))

if not fin_files:
    print("未找到历史财务数据文件 (gpcw*.dat 或 gpcw*.zip)")
    print("\n获取方式:")
    print("  1. 使用 TdxClient.get_financial_file_list() 查询可用文件")
    print("  2. 使用 TdxClient.download_file() 下载到本地")
    raise SystemExit(0)

print(f"找到 {len(fin_files)} 个财务数据文件:")
for f in fin_files:
    print(f"  {f}")

# 读取第一个文件
sample = fin_files[0]
print(f"\n读取: {sample.name}")
records = read_history_financial(sample)

if not records:
    print("未读取到数据")
    raise SystemExit(0)

print(f"共 {len(records)} 条记录")
print(f"\n前 10 条:")
print(f"  {'代码':>8s}  {'市场':>4s}  {'报告期':>10s}  {'字段数':>6s}")
for rec in records[:10]:
    print(f"  {rec.code:>8s}  {rec.market.name:>4s}  {rec.report_date:>10d}  {len(rec.fields):>6d}")

# 展示一只股票的详细数据
if records:
    rec = records[0]
    print(f"\n{rec.code} ({rec.market.name}) 报告期 {rec.report_date} 的前 20 个字段:")
    for i, val in enumerate(rec.fields[:20]):
        print(f"  字段{i + 1:3d}: {val:>15.4f}")
