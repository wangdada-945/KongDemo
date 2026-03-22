from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from utils.data_loader import load_excel_cases, load_json


def data_driver(
    *,
    json_file: str | None = None,
    excel_file: str | None = None,
    excel_sheet: str = "Sheet1",
    key: str | None = None,
    argnames: str = "case",
    ids_key: str | None = "name",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    数据驱动装饰器（JSON / Excel）：

    JSON 约定：
    - 文件内容可为 list[dict] 或 dict
    - 若为 dict，需通过 key 指定取哪一段（例如 "cases"）

    Excel 约定：
    - 第一行表头
    - 返回 list[dict]
    """

    if bool(json_file) == bool(excel_file):
        raise ValueError("Provide exactly one of json_file or excel_file")

    def _decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if json_file:
            raw = load_json(Path(json_file))
            data = raw[key] if (key and isinstance(raw, dict)) else raw
            if not isinstance(data, list):
                raise TypeError("JSON test data must be a list (or dict[key] -> list)")
            cases = data
        else:
            cases = load_excel_cases(Path(excel_file), sheet_name=excel_sheet)  # type: ignore[arg-type]

        def _ids(v: Any) -> str | None:
            if not ids_key:
                return None
            if isinstance(v, dict) and ids_key in v and v[ids_key] is not None:
                return str(v[ids_key])
            return None

        return pytest.mark.parametrize(argnames, cases, ids=_ids)(func)

    return _decorator

