from __future__ import annotations

from utils.assertions import Assert
from utils.data_driver import data_driver
from utils.paths import DATA_DIR


@data_driver(json_file=str(DATA_DIR / "httpbin_cases.json"), key="cases", argnames="case")
def test_httpbin_cases(httpbin_api, case: dict):
    method = str(case.get("method", "GET")).upper()
    expected = int(case.get("expected_status", 200))

    if method == "GET":
        result = httpbin_api.get(params=case.get("params"))
    else:
        result = httpbin_api.post(json=case.get("json"))

    Assert.status_code(result.response, expected)
    Assert.is_true(result.text)
