from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import os
import requests
from requests import Response

from utils.token_manager import TokenManager


class RequestError(RuntimeError):
    pass


@dataclass
class RequestResult:
    response: Response
    json: Any | None
    text: str


class BaseRequest:
    """
    Requests 基础封装：
    - 统一 base_url / timeout / ssl / headers
    - 统一异常处理、日志（由外部传入 logger）
    - token 自动注入（来自 TokenManager）
    """

    def __init__(
        self,
        *,
        base_url: str,
        timeout: float = 15,
        verify_ssl: bool = True,
        token_manager: TokenManager | None = None,
        token_header: str = "Authorization",
        token_prefix: str = "Bearer ",
        logger=None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        # 某些环境会通过 HTTP(S)_PROXY 劫持请求导致 403/无法出网
        # 可通过环境变量 REQUESTS_TRUST_ENV=0 关闭读取代理等环境变量
        self.session.trust_env = os.getenv("REQUESTS_TRUST_ENV", "1").strip() != "0"
        self.token_manager = token_manager
        self.token_header = token_header
        self.token_prefix = token_prefix
        self.logger = logger

    def _full_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def _inject_token(self, headers: dict[str, str] | None) -> dict[str, str]:
        h = dict(headers or {})
        if self.token_manager:
            token = self.token_manager.get()
            if token:
                h[self.token_header] = f"{self.token_prefix}{token}"
        return h

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> RequestResult:
        url = self._full_url(path)
        h = self._inject_token(headers)

        try:
            if self.logger:
                self.logger.info(f"REQ {method.upper()} {url} params={params} json={json}")

            resp = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json,
                data=data,
                headers=h,
                timeout=self.timeout,
                verify=self.verify_ssl,
                **kwargs,
            )

            text = resp.text or ""
            resp_json = None
            try:
                resp_json = resp.json()
            except Exception:
                resp_json = None

            if self.logger:
                body_preview = resp_json if resp_json is not None else text
                self.logger.info(f"RESP {resp.status_code} {url} body={str(body_preview)[:500]}")

            return RequestResult(response=resp, json=resp_json, text=text)
        except requests.RequestException as e:
            if self.logger:
                self.logger.exception(f"Request failed: {method.upper()} {url}")
            raise RequestError(str(e)) from e

