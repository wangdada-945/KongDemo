from __future__ import annotations

import json

import pytest

from utils.assertions import Assert
from utils.data_driver import data_driver
from utils.paths import DATA_DIR


def _maybe_json(s):
    if s is None:
        return None
    if isinstance(s, (dict, list)):
        return s
    if isinstance(s, str) and s.strip():
        return json.loads(s)
    return None


@pytest.mark.smoke
@data_driver(excel_file=str(DATA_DIR / "httpbin_cases.xlsx"), argnames="case")
def test_httpbin_cases_excel(httpbin_api, case: dict):
    method = str(case.get("method", "GET")).upper()
    expected = int(case.get("expected_status", 200))

    params = _maybe_json(case.get("params"))
    body = _maybe_json(case.get("json"))

    if method == "GET":
        result = httpbin_api.get(params=params)
    else:
        result = httpbin_api.post(json=body)

    Assert.status_code(result.response, expected)
