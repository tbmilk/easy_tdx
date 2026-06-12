"""执行仿真引擎单元测试。"""

from __future__ import annotations

import pandas as pd
import pytest

from easy_tdx.backtest.execution import ExecutionModel, ImmediateExecution
from easy_tdx.backtest.types import Signal


def _make_df(n: int = 20) -> pd.DataFrame:
    """构造测试用K线数据。"""
    data = {
        "datetime": [20240101 + i for i in range(n)],
        "open": [100.0 + i for i in range(n)],
        "close": [101.0 + i for i in range(n)],
        "high": [102.0 + i for i in range(n)],
        "low": [99.0 + i for i in range(n)],
        "volume": [10000] * n,
    }
    return pd.DataFrame(data)


class TestExecutionBase:
    """基类验证。"""

    def test_cannot_instantiate_abc(self) -> None:
        with pytest.raises(TypeError):
            ExecutionModel()  # type: ignore[abstract]


class TestImmediateExecution:
    """即时成交。"""

    def test_buy_signal(self) -> None:
        df = _make_df(10)
        model = ImmediateExecution()
        signal = Signal(datetime=20240101, direction="BUY", size=100)
        trades = model.execute(
            signal=signal,
            df=df,
            bar_idx=0,
            cash=20000,
            position=0,
            position_mode="fixed",
            commission=0.0003,
            min_commission=5.0,
            stamp_tax=0.001,
            slippage_model=None,
        )
        assert len(trades) == 1
        assert trades[0].direction == "BUY"
        assert trades[0].price == 101.0

    def test_sell_signal(self) -> None:
        df = _make_df(10)
        model = ImmediateExecution()
        signal = Signal(datetime=20240101, direction="SELL", size=100)
        trades = model.execute(
            signal=signal,
            df=df,
            bar_idx=0,
            cash=0,
            position=200,
            position_mode="fixed",
            commission=0.0003,
            min_commission=5.0,
            stamp_tax=0.001,
            slippage_model=None,
        )
        assert len(trades) == 1
        assert trades[0].direction == "SELL"

    def test_signal_at_last_bar(self) -> None:
        df = _make_df(10)
        model = ImmediateExecution()
        signal = Signal(datetime=20240109, direction="BUY", size=100)
        trades = model.execute(
            signal=signal,
            df=df,
            bar_idx=9,
            cash=20000,
            position=0,
            position_mode="fixed",
            commission=0.0003,
            min_commission=5.0,
            stamp_tax=0.001,
            slippage_model=None,
        )
        assert len(trades) == 0

    def test_with_slippage_model(self) -> None:
        from easy_tdx.backtest.slippage import FixedSlippage

        df = _make_df(10)
        model = ImmediateExecution()
        signal = Signal(datetime=20240101, direction="BUY", size=100)
        trades = model.execute(
            signal=signal,
            df=df,
            bar_idx=0,
            cash=20000,
            position=0,
            position_mode="fixed",
            commission=0.0003,
            min_commission=5.0,
            stamp_tax=0.001,
            slippage_model=FixedSlippage(per_share=0.01),
        )
        assert len(trades) == 1
        assert trades[0].slippage == pytest.approx(1.0)

    def test_commission_on_buy(self) -> None:
        df = _make_df(10)
        model = ImmediateExecution()
        signal = Signal(datetime=20240101, direction="BUY", size=100)
        trades = model.execute(
            signal=signal,
            df=df,
            bar_idx=0,
            cash=20000,
            position=0,
            position_mode="fixed",
            commission=0.0003,
            min_commission=5.0,
            stamp_tax=0.001,
            slippage_model=None,
        )
        assert len(trades) == 1
        assert trades[0].commission >= 5.0

    def test_stamp_tax_on_sell(self) -> None:
        df = _make_df(10)
        model = ImmediateExecution()
        signal = Signal(datetime=20240101, direction="SELL", size=100)
        trades = model.execute(
            signal=signal,
            df=df,
            bar_idx=0,
            cash=0,
            position=200,
            position_mode="fixed",
            commission=0.0003,
            min_commission=5.0,
            stamp_tax=0.001,
            slippage_model=None,
        )
        assert len(trades) == 1
        assert trades[0].commission > 10.0

    def test_full_position_buy(self) -> None:
        df = _make_df(10)
        model = ImmediateExecution()
        signal = Signal(datetime=20240101, direction="BUY", size=0)
        trades = model.execute(
            signal=signal,
            df=df,
            bar_idx=0,
            cash=20000,
            position=0,
            position_mode="full",
            commission=0.0003,
            min_commission=5.0,
            stamp_tax=0.001,
            slippage_model=None,
        )
        assert len(trades) == 1
        assert trades[0].size == 100
