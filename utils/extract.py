from __future__ import annotations

from typing import Any

from jsonpath_ng.ext import parse


def extract_jsonpath(data: Any, expr: str) -> Any:
    """
    用 JSONPath 从响应 JSON 中提取值。
    - expr 示例：'$.token' / '$.data[0].id'
    - 找到多个 match 时，默认返回第一个
    """
    jsonpath_expr = parse(expr)
    matches = [m.value for m in jsonpath_expr.find(data)]
    if not matches:
        return None
    return matches[0]
