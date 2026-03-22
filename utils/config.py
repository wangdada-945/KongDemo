from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import yaml

from utils.paths import CONFIG_DIR


@dataclass(frozen=True)
class EnvConfig:
    name: str
    base_url: str
    timeout: float
    verify_ssl: bool


class Config:
    """
    配置管理：
    - 默认读取 `config/config.yaml`
    - 通过环境变量 ENV 切换环境：dev/test/prod（默认 dev）
    """

    def __init__(self, config_path: str | None = None) -> None:
        self._config_path = config_path or str(CONFIG_DIR / "config.yaml")
        self._raw = self._load_yaml(self._config_path)

        self.env_name = os.getenv("ENV", "dev").strip() or "dev"
        envs = self._raw.get("environments", {})
        if self.env_name not in envs:
            raise KeyError(f"ENV={self.env_name!r} not found in environments")

        env_raw = envs[self.env_name]
        self.env = EnvConfig(
            name=self.env_name,
            base_url=str(env_raw["base_url"]).rstrip("/"),
            timeout=float(env_raw.get("timeout", 15)),
            verify_ssl=bool(env_raw.get("verify_ssl", True)),
        )

    @property
    def auth_token_header(self) -> str:
        return str(self._raw.get("auth", {}).get("token_header", "Authorization"))

    @property
    def auth_token_prefix(self) -> str:
        return str(self._raw.get("auth", {}).get("token_prefix", "Bearer "))

    @property
    def log_level(self) -> str:
        return str(self._raw.get("logging", {}).get("level", "INFO"))

    @property
    def log_file(self) -> str:
        return str(self._raw.get("logging", {}).get("file", "reports/run.log"))

    @staticmethod
    def _load_yaml(path: str) -> dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            raise TypeError("config yaml must be a mapping")
        return data
