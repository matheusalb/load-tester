"""Utility functions for testing purposes."""
from typing import Any, TypeVar

T = TypeVar("T")
def assert_values(value1: T, value2: T, msg: str) -> None:
    """Assert that two values are equal."""
    if value1 != value2:
        raise AssertionError(msg)
