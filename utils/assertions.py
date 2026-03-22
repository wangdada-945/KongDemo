from __future__ import annotations

from typing import Any


class Assert:
    @staticmethod
    def equal(actual: Any, expected: Any, msg: str | None = None) -> None:
        assert actual == expected, msg or f"Expect {expected!r}, got {actual!r}"

    @staticmethod
    def contains(container: Any, member: Any, msg: str | None = None) -> None:
        assert member in container, msg or f"Expect {member!r} in {container!r}"

    @staticmethod
    def is_true(value: Any, msg: str | None = None) -> None:
        assert bool(value) is True, msg or f"Expect truthy, got {value!r}"

    @staticmethod
    def status_code(resp, expected: int) -> None:
        actual = getattr(resp, "status_code", None)
        assert actual == expected, f"Expect status_code={expected}, got {actual}"
