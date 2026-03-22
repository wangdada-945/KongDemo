from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    xlsx = data_dir / "httpbin_cases.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"

    ws.append(["name", "method", "params", "json", "expected_status"])
    ws.append(["get_with_params", "GET", '{"q":"hello"}', None, 200])
    ws.append(["post_with_json", "POST", None, '{"a":1,"b":"x"}', 200])

    wb.save(str(xlsx))
    print(f"Generated: {xlsx}")


if __name__ == "__main__":
    main()

