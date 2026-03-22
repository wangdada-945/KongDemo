from __future__ import annotations

import threading


class TokenManager:
    """
    token 自动管理（线程安全）：
    - 登录后写入 token
    - 发请求时自动从这里取 token 注入 Header
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._token: str | None = None

    def set(self, token: str | None) -> None:
        with self._lock:
            self._token = token

    def get(self) -> str | None:
        with self._lock:
            return self._token

    def clear(self) -> None:
        self.set(None)
