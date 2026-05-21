"""演示：检测通达信安装目录与路径解析。

offline 模块的路径检测优先级：
  1. TDX_HOME 环境变量
  2. 平台常见路径猜测 (Windows: C:\\new_jyplug, C:\\new_tdx, D:\\... 等)

vipdoc 目录结构:
  vipdoc/
  ├── sh/lday/     上海日线    sh600000.day
  ├── sh/fzline/   上海5分钟线 sh600000.5
  ├── sh/fzline/  上海分钟线  sh600000.lc1 / .lc5
  ├── sz/lday/     深圳日线    sz000001.day
  ├── sz/fzline/   深圳5分钟线 sz000001.5
  ├── sz/fzline/  深圳分钟线  sz000001.lc1 / .lc5
  └── ds/          扩展市场    29#A1801.day
"""

import os
from pathlib import Path

from xmtdx.offline import detect_tdx_home, resolve_vipdoc
from xmtdx.offline import find_daily_bar_file, find_5min_bar_file, find_lc1_bar_file
from xmtdx import Market

# --- 检测安装目录 ---
print("=" * 60)
print("通达信安装目录检测")
print("=" * 60)

home = detect_tdx_home()
if home:
    print(f"检测到: {home}")
else:
    print("未检测到，可通过以下方式指定:")
    print(f"  set TDX_HOME=C:\\new_jyplug")

# --- 手动指定路径 ---
print(f"\n{'=' * 60}")
print("手动指定 vipdoc 路径")
print("=" * 60)

if home:
    vipdoc = resolve_vipdoc()
    print(f"vipdoc 目录: {vipdoc}")

    # 列出 vipdoc 子目录
    if vipdoc.is_dir():
        for d in sorted(vipdoc.iterdir()):
            if d.is_dir():
                files = list(d.rglob("*"))
                print(f"  {d.name}/ ({len(files)} 个文件)")
else:
    print("(需要 TDX_HOME 才能自动解析)")

# --- 文件定位示例 ---
print(f"\n{'=' * 60}")
print("通过 市场+代码 定位文件")
print("=" * 60)

if home:
    examples = [
        ("浦发银行 日线", lambda: find_daily_bar_file(Market.SH, "600000")),
        ("平安银行 日线", lambda: find_daily_bar_file(Market.SZ, "000001")),
        ("浦发银行 5分钟", lambda: find_5min_bar_file(Market.SH, "600000")),
        ("平安银行 1分钟", lambda: find_lc1_bar_file(Market.SZ, "000001")),
    ]
    for label, finder in examples:
        p = finder()
        exists = "存在" if p.is_file() else "不存在"
        print(f"  {label}: {p} ({exists})")
else:
    print("(需要 TDX_HOME)")

# --- 设置环境变量的方式 ---
print(f"\n{'=' * 60}")
print("如何设置 TDX_HOME")
print("=" * 60)
print("  Windows CMD:  set TDX_HOME=C:\\new_jyplug")
print("  Windows PS:   $env:TDX_HOME = 'C:\\new_jyplug'")
print("  Linux/macOS:  export TDX_HOME=/opt/new_tdx")
