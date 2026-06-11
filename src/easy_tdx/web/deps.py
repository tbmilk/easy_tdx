"""Dependency injection for Web API routers."""

from __future__ import annotations

import typing
from typing import TYPE_CHECKING

from fastapi import Request

if TYPE_CHECKING:
    from easy_tdx.client import AsyncTdxClient


def get_client(request: Request) -> AsyncTdxClient:
    """从 app.state 获取共享的 AsyncTdxClient 实例。"""
    return typing.cast(AsyncTdxClient, request.app.state.tdx_client)
