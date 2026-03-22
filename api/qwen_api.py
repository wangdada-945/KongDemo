from __future__ import annotations

from api.base_api import BaseRequest, RequestResult


class QwenApi:
    """
    通义千问（DashScope）真实接口示例：
    - 使用 OpenAI 兼容模式的 Chat Completions
    - 需要环境变量 DASHSCOPE_API_KEY
    """

    def __init__(self, client: BaseRequest, api_key: str) -> None:
        self.client = client
        self.api_key = api_key

    def chat_completions(self, *, model: str, messages: list[dict], temperature: float = 0.2) -> RequestResult:
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"model": model, "messages": messages, "temperature": temperature}
        return self.client.request("POST", url, json=payload, headers=headers)

