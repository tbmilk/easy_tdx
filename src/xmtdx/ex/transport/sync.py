"""扩展行情同步 TCP 连接（端口 7727）。"""

import socket
import time
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


def ping_ex_host(
    host: str,
    port: int = _DEFAULT_EX_PORT,
    timeout: float = 5.0,
) -> float | None:
    """测量扩展行情服务器延迟（秒）。失败返回 None。"""
    t0 = time.monotonic()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        sock.sendall(EX_SETUP_CMD)
        hdr_buf = _recv_exact_sock(sock, HEADER_SIZE)
        hdr = parse_header(hdr_buf)
        if hdr.zipsize > 0:
            _recv_exact_sock(sock, hdr.zipsize)
        return time.monotonic() - t0
    except OSError:
        return None
    finally:
        try:
            sock.close()
        except OSError:
            pass


def ping_ex_all(
    hosts: list[str] | None = None,
    port: int = _DEFAULT_EX_PORT,
    timeout: float = 5.0,
) -> list[tuple[str, float]]:
    """并发测量多台扩展行情服务器延迟，按延迟排序返回。"""
    import concurrent.futures

    if hosts is None:
        hosts = KNOWN_EX_HOSTS
    results: list[tuple[str, float]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(hosts)) as pool:
        futures = {pool.submit(ping_ex_host, h, port, timeout): h for h in hosts}
        for fut in concurrent.futures.as_completed(futures):
            host = futures[fut]
            latency = fut.result()
            if latency is not None:
                results.append((host, latency))
    results.sort(key=lambda t: t[1])
    return results


def _recv_exact_sock(sock: socket.socket, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise TdxConnectionError("连接被服务器关闭")
        buf.extend(chunk)
    return bytes(buf)


class ExTdxConnection:
    """扩展行情同步 TCP 连接（端口 7727，单包握手）。"""

    def __init__(
        self,
        host: str = KNOWN_EX_HOSTS[0],
        port: int = _DEFAULT_EX_PORT,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self._sock: socket.socket | None = None

    def connect(self) -> None:
        """建立 TCP 连接并完成扩展行情握手。"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            sock.connect((self.host, self.port))
        except OSError as e:
            sock.close()
            raise TdxConnectionError(f"无法连接 {self.host}:{self.port}: {e}") from e
        self._sock = sock
        try:
            self._send_setup()
        except Exception:
            try:
                sock.close()
            except OSError:
                pass
            self._sock = None
            raise

    def close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None

    def execute(self, cmd: "BaseCommand[T]") -> T:
        """执行一条命令：发送请求，接收并解压响应，返回解析结果。"""
        if self._sock is None:
            raise TdxConnectionError("未连接，请先调用 connect()")
        request = cmd.build_request()
        try:
            self._sock.sendall(request)
            header_buf = self._recv_exact(HEADER_SIZE)
            header = parse_header(header_buf)
            raw_body = self._recv_exact(header.zipsize)
        except OSError as e:
            raise TdxConnectionError(f"通信错误: {e}") from e
        body = decompress_body(header, raw_body)
        return cmd.parse_response(body)

    def __enter__(self) -> "ExTdxConnection":
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    def _send_setup(self) -> None:
        """发送单条扩展行情握手命令并丢弃响应。"""
        assert self._sock is not None
        self._sock.sendall(EX_SETUP_CMD)
        try:
            hdr_buf = self._recv_exact(HEADER_SIZE)
            hdr = parse_header(hdr_buf)
            if hdr.zipsize > 0:
                self._recv_exact(hdr.zipsize)
        except OSError:
            pass

    def _recv_exact(self, n: int) -> bytes:
        assert self._sock is not None
        return _recv_exact_sock(self._sock, n)
