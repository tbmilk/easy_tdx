"""扩展行情异步 TCP 连接（asyncio，端口 7727）。"""

import asyncio
from types import TracebackType
from typing import TYPE_CHECKING, TypeVar

from ...codec.frame import HEADER_SIZE, decompress_body, parse_header
from ...exceptions import TdxConnectionError
from ..commands.setup import EX_SETUP_CMD
from ..models import KNOWN_EX_HOSTS

if TYPE_CHECKING:
    from ...commands.base import BaseCommand

T = TypeVar("T")

_DEFAULT_EX_PORT = 7727
_DEFAULT_TIMEOUT = 15.0


class AsyncExTdxConnection:
    """扩展行情异步 TCP 连接（asyncio，端口 7727，单包握手）。"""

    def __init__(
        self,
        host: str = KNOWN_EX_HOSTS[0],
        port: int = _DEFAULT_EX_PORT,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._io_lock = asyncio.Lock()

    async def connect(self) -> None:
        async with self._io_lock:
            if self._writer is not None and not self._writer.is_closing():
                return
            await self._connect_unlocked()

    async def close(self) -> None:
        async with self._io_lock:
            await self._close_unlocked()

    async def execute(self, cmd: "BaseCommand[T]") -> T:
        async with self._io_lock:
            if self._writer is None or self._reader is None:
                raise TdxConnectionError("未连接，请先调用 connect()")
            request = cmd.build_request()
            try:
                self._writer.write(request)
                await asyncio.wait_for(self._writer.drain(), timeout=self.timeout)
                header_buf = await self._recv_exact(HEADER_SIZE)
                header = parse_header(header_buf)
                raw_body = await self._recv_exact(header.zipsize)
            except asyncio.TimeoutError as e:
                await self._close_unlocked()
                raise TdxConnectionError(f"通信超时: {self.timeout}s") from e
            except (OSError, asyncio.IncompleteReadError) as e:
                await self._close_unlocked()
                raise TdxConnectionError(f"通信错误: {e}") from e

            body = decompress_body(header, raw_body)
            return cmd.parse_response(body)

    async def _connect_unlocked(self) -> None:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout,
            )
        except (OSError, asyncio.TimeoutError) as e:
            raise TdxConnectionError(f"无法连接 {self.host}:{self.port}: {e}") from e
        self._reader = reader
        self._writer = writer
        try:
            await self._send_setup()
        except Exception:
            await self._close_unlocked()
            raise

    async def _close_unlocked(self) -> None:
        if self._writer is not None:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except OSError:
                pass
            self._reader = None
            self._writer = None

    async def __aenter__(self) -> "AsyncExTdxConnection":
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def _send_setup(self) -> None:
        """发送单条扩展行情握手命令并丢弃响应。"""
        assert self._writer is not None
        assert self._reader is not None
        self._writer.write(EX_SETUP_CMD)
        await asyncio.wait_for(self._writer.drain(), timeout=self.timeout)
        try:
            hdr_buf = await self._recv_exact(HEADER_SIZE)
            hdr = parse_header(hdr_buf)
            if hdr.zipsize > 0:
                await self._recv_exact(hdr.zipsize)
        except (OSError, asyncio.TimeoutError, asyncio.IncompleteReadError):
            pass

    async def _recv_exact(self, n: int) -> bytes:
        assert self._reader is not None
        return await asyncio.wait_for(
            self._reader.readexactly(n),
            timeout=self.timeout,
        )
