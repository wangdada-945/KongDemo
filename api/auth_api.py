from __future__ import annotations

from api.base_api import BaseRequest, RequestResult
from utils.extract import extract_jsonpath
from utils.token_manager import TokenManager


class AuthApi:
    def __init__(self, client: BaseRequest, token_manager: TokenManager) -> None:
        self.client = client
        self.token_manager = token_manager

    def login(self, username: str, password: str) -> RequestResult:
        result = self.client.request("POST", "/login", json={"username": username, "password": password})
        if result.json:
            token = extract_jsonpath(result.json, "$.token")
            if token:
                self.token_manager.set(str(token))
        return result

