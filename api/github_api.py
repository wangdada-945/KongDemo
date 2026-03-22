from __future__ import annotations

from api.base_api import BaseRequest, RequestResult


class GithubApi:
    """
    GitHub REST API v3 封装示例（按需扩展）：
    - https://docs.github.com/en/rest
    """

    def __init__(self, client: BaseRequest) -> None:
        self.client = client

    def get_rate_limit(self) -> RequestResult:
        return self.client.request("GET", "/rate_limit")

    def get_authenticated_user(self) -> RequestResult:
        return self.client.request("GET", "/user")

    def list_user_repos(self, username: str, *, per_page: int = 10) -> RequestResult:
        return self.client.request("GET", f"/users/{username}/repos", params={"per_page": per_page})

