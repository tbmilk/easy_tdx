# src/easy_tdx/factor/__init__.py
"""因子研究模块。"""
from __future__ import annotations

from easy_tdx.factor.base import FACTORY_REGISTRY, Factor, register_factor
from easy_tdx.factor.engine import FactorEngine

# 导入 builtin 触发自动注册
from easy_tdx.factor.builtin import get_factor, list_factors  # noqa: F401

__all__ = [
    "Factor",
    "register_factor",
    "FACTORY_REGISTRY",
    "FactorEngine",
    "list_factors",
    "get_factor",
]
