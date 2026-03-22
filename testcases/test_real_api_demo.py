from __future__ import annotations

import pytest

from api.base_api import RequestError
from utils.assertions import Assert


@pytest.mark.smoke
def test_baidu_homepage(baidu_api):
    try:
        r = baidu_api.home()
    except RequestError as e:
        pytest.skip(f"Network/DNS not available for baidu: {e}")
    Assert.status_code(r.response, 200)
    # 公网页面内容可能因地区/策略变化，这里做更稳的“可用性”断言
    text = (r.text or "").lower()
    Assert.is_true(("baidu" in text) or ("baidu.com" in text))


@pytest.mark.smoke
def test_qwen_chat_completion(qwen_api, qwen_api_key):
    if not qwen_api or not qwen_api_key:
        pytest.skip("Set DASHSCOPE_API_KEY to run Qwen real API test")

    try:
        r = qwen_api.chat_completions(
            model="qwen-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'pong'."},
            ],
            temperature=0.0,
        )
    except RequestError as e:
        pytest.skip(f"Network not available for Qwen: {e}")
    Assert.status_code(r.response, 200)
    Assert.is_true(r.json)
    # OpenAI 兼容响应一般包含 choices
    Assert.is_true("choices" in r.json)

