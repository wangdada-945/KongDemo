from __future__ import annotations

import os
from typing import Generator

import pytest

from api.base_api import BaseRequest
from api.auth_api import AuthApi
from api.baidu_api import BaiduApi
from api.github_api import GithubApi
from api.httpbin_api import HttpbinApi
from api.qwen_api import QwenApi
from utils.config import Config
from utils.logger import setup_logger
from utils.paths import ensure_dirs
from utils.mock_server import start_mock_server
from utils.token_manager import TokenManager


@pytest.fixture(scope="session")
def config() -> Config:
    ensure_dirs()
    return Config()


@pytest.fixture(scope="session")
def logger(config: Config):
    return setup_logger("autotest", config.log_level, config.log_file)


@pytest.fixture(scope="session")
def token_manager() -> TokenManager:
    return TokenManager()


@pytest.fixture(scope="session")
def mock_server(logger):
    """
    默认启用本地 Mock Server，避免外网不可用导致用例失败。
    如需跑真实环境：设置 USE_LOCAL_SERVER=0 并在 config/config.yaml 配好 base_url。
    """
    use_local = os.getenv("USE_LOCAL_SERVER", "1").strip() != "0"
    if not use_local:
        yield None
        return

    server, stop = start_mock_server()
    logger.info(f"Mock server started at {server.base_url}")
    yield server
    stop()


@pytest.fixture(scope="session")
def client(config: Config, token_manager: TokenManager, logger, mock_server) -> BaseRequest:
    base_url = mock_server.base_url if mock_server else config.env.base_url
    return BaseRequest(
        base_url=base_url,
        timeout=config.env.timeout,
        verify_ssl=config.env.verify_ssl,
        token_manager=token_manager,
        token_header=config.auth_token_header,
        token_prefix=config.auth_token_prefix,
        logger=logger,
    )


@pytest.fixture(scope="session")
def httpbin_api(client: BaseRequest) -> HttpbinApi:
    return HttpbinApi(client)


@pytest.fixture(scope="session")
def auth_api(client: BaseRequest, token_manager: TokenManager) -> AuthApi:
    return AuthApi(client, token_manager)


@pytest.fixture(scope="session")
def github_token(token_manager: TokenManager):
    """
    GitHub Token 注入（可选）：
    - 环境变量：GITHUB_TOKEN
    - 不会写入任何文件；仅写入内存 TokenManager，供 BaseRequest 自动注入 Authorization
    """
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        token_manager.set(token)
    return token or None


@pytest.fixture(scope="session")
def github_api(client: BaseRequest, github_token) -> GithubApi:
    return GithubApi(client)


@pytest.fixture(scope="session")
def baidu_api(client: BaseRequest) -> BaiduApi:
    return BaiduApi(client)


@pytest.fixture(scope="session")
def qwen_api_key() -> str | None:
    return os.getenv("DASHSCOPE_API_KEY", "").strip() or None


@pytest.fixture(scope="session")
def qwen_api(client: BaseRequest, qwen_api_key) -> QwenApi | None:
    if not qwen_api_key:
        return None
    return QwenApi(client, qwen_api_key)


@pytest.fixture(autouse=True)
def _show_env(config: Config) -> Generator[None, None, None]:
    """
    让用例报告里更容易看到当前环境（可按需删掉）。
    """
    os.environ.setdefault("ENV", config.env.name)
    yield

