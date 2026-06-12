"""可插拔执行仿真引擎。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from easy_tdx.backtest.types import Trade

if TYPE_CHECKING:
    from easy_tdx.backtest.slippage import SlippageModel
    from easy_tdx.backtest.types import Signal


class ExecutionModel(ABC):
    """执行仿真基类。"""

    @abstractmethod
    def execute(
        self,
        signal: Signal,
        df: pd.DataFrame,
        bar_idx: int,
        cash: float,
        position: float,
        position_mode: str,
        commission: float,
        min_commission: float,
        stamp_tax: float,
        slippage_model: SlippageModel | None,
    ) -> list[Trade]:
        """将信号转换为一笔或多笔成交。"""
        ...

    def _calc_commission(
        self,
        size: float,
        price: float,
        is_sell: bool,
        commission: float,
        min_commission: float,
        stamp_tax: float,
    ) -> float:
        """计算手续费。"""
        comm = max(size * price * commission, min_commission)
        if is_sell:
            comm += size * price * stamp_tax
        return comm

    def _calc_slippage(
        self,
        size: float,
        price: float,
        is_sell: bool,
        slippage_model: SlippageModel | None,
        df: pd.DataFrame,
    ) -> float:
        """计算滑点。"""
        if slippage_model is None:
            return 0.0
        volume = float(df["volume"].iloc[-1]) if "volume" in df.columns else 0.0
        volatility = self._estimate_volatility(df)
        return slippage_model.compute(
            price=price,
            size=size,
            volume=volume,
            volatility=volatility,
            direction="SELL" if is_sell else "BUY",
        )

    def _estimate_volatility(self, df: pd.DataFrame) -> float:
        """从收盘价估计近期年化波动率。"""
        if "close" not in df.columns or len(df) < 2:
            return 0.0
        close = df["close"].to_numpy()
        returns = np.diff(close) / close[:-1]
        if len(returns) < 2:
            return 0.0
        return float(np.std(returns)) * np.sqrt(252)

    def _calc_buy_size(
        self,
        signal_size: float,
        price: float,
        cash: float,
        position_mode: str,
        commission: float,
    ) -> float:
        """计算买入数量。"""
        if position_mode == "full" or signal_size == 0:
            max_cost = price * (1 + commission)
            max_shares = int(cash / max_cost / 100) * 100
            return float(max_shares)
        elif position_mode == "percent":
            target_value = cash * signal_size
            return float(int(target_value / price / 100) * 100)
        return signal_size

    def _get_datetime_int(self, df: pd.DataFrame, idx: int) -> int:
        """获取指定 index 的 datetime int。"""
        dt_raw = df["datetime"].iloc[idx]
        if hasattr(dt_raw, "strftime"):
            return int(dt_raw.strftime("%Y%m%d"))
        return int(dt_raw)


class ImmediateExecution(ExecutionModel):
    """即时成交（向后兼容，与现有 OrderSimulator 行为一致）。"""

    def execute(
        self,
        signal: Signal,
        df: pd.DataFrame,
        bar_idx: int,
        cash: float,
        position: float,
        position_mode: str,
        commission: float,
        min_commission: float,
        stamp_tax: float,
        slippage_model: SlippageModel | None,
    ) -> list[Trade]:
        exec_idx = bar_idx + 1
        if exec_idx >= len(df):
            return []

        price = float(df["open"].iloc[exec_idx])

        if signal.direction == "BUY":
            size = self._calc_buy_size(
                signal.size,
                price,
                cash,
                position_mode,
                commission,
            )
            if size <= 0:
                return []
            comm = self._calc_commission(
                size,
                price,
                False,
                commission,
                min_commission,
                stamp_tax,
            )
            slip = self._calc_slippage(size, price, False, slippage_model, df)
            return [
                Trade(
                    datetime=self._get_datetime_int(df, exec_idx),
                    direction="BUY",
                    size=size,
                    price=price,
                    commission=comm,
                    slippage=slip,
                )
            ]
        elif signal.direction == "SELL":
            size = signal.size if signal.size > 0 else position
            if size <= 0:
                return []
            if size > position:
                size = position
            comm = self._calc_commission(
                size,
                price,
                True,
                commission,
                min_commission,
                stamp_tax,
            )
            slip = self._calc_slippage(size, price, True, slippage_model, df)
            return [
                Trade(
                    datetime=self._get_datetime_int(df, exec_idx),
                    direction="SELL",
                    size=size,
                    price=price,
                    commission=comm,
                    slippage=slip,
                )
            ]

        return []
