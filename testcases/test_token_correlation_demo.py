from __future__ import annotations

from utils.assertions import Assert


def test_token_auto_inject(auth_api, client, token_manager):
    # 1) 登录提取 token，写入 TokenManager
    login = auth_api.login("admin", "123456")
    Assert.status_code(login.response, 200)
    Assert.is_true(token_manager.get())

    # 2) 访问需要 token 的接口：BaseRequest 会自动注入 Authorization Header
    result = client.request("GET", "/protected")
    Assert.status_code(result.response, 200)
