from __future__ import annotations

from api.base_api import BaseRequest, RequestResult


class BaiduApi:
    """
    真实公网接口示例：百度首页健康检查
    - 不需要 token
    """

    def __init__(self, client: BaseRequest) -> None:
        self.client = client

    def home(self) -> RequestResult:
        # 直接使用完整 URL，避免受 base_url 环境影响
        return self.client.request("GET", "https://www.baidu.com")

