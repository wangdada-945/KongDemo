from __future__ import annotations

from api.base_api import BaseRequest, RequestResult


class HttpbinApi:
    """
    示例接口封装（Page Object / API Object 风格）：
    - 你可以按业务域拆分更多 Api 类放在 api/ 下
    """

    def __init__(self, client: BaseRequest) -> None:
        self.client = client

    def get(self, *, params: dict | None = None) -> RequestResult:
        return self.client.request("GET", "/get", params=params)

    def post(self, *, json: dict | None = None) -> RequestResult:
        return self.client.request("POST", "/post", json=json)

