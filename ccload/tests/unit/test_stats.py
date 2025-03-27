""""Unit tests for the stats methods."""
from typing import Any

import pytest

from ccload.core.load_tester_features import _calculate_statistics


def test_calculate_statistics_empty() -> None:
    """Test the calculation of statistics with no results."""
    results: list = []
    total_time = 0
    stats = _calculate_statistics(results, total_time)

    if stats["total_requests"] != 0:
        raise AssertionError
    if stats["successful_requests"] != 0:
        raise AssertionError
    if stats["failed_requests"] != 0:
        raise AssertionError
    if stats["requests_per_second"] != 0:
        raise AssertionError

def test_calculate_statistics_success() -> None:
    """Test statistics calculation with successful results."""
    # Mock successful results
    results = [
        {"status": 200, "request_time": 0.1, "ttfb": 0.05, "ttlb": 0.08},
        {"status": 200, "request_time": 0.2, "ttfb": 0.10, "ttlb": 0.15},
    ]
    total_time = 0.3

    stats = _calculate_statistics(results, total_time)

    if stats["total_requests"] != 2:  # noqa: PLR2004
        raise AssertionError
    if stats["successful_requests"] != 2:  # noqa: PLR2004
        raise AssertionError
    if stats["failed_requests"] != 0:
        raise AssertionError
    if stats["request_time_min"] != pytest.approx(0.1, 0.01):
        raise AssertionError
    if stats["request_time_max"] != pytest.approx(0.2, 0.01):
        raise AssertionError
    if stats["request_time_mean"] != pytest.approx(0.15, 0.01):
        raise AssertionError
    if stats["requests_per_second"] != pytest.approx(6.67, 0.01):
        raise AssertionError


def test_calculate_statistics_failures() -> None:
    """Test statistics calculation with failures."""
    # Mix of successful, failed, and exception results
    results: list[dict[str, Any] | Exception] = [
        {"status": 200, "request_time": 0.1, "ttfb": 0.05, "ttlb": 0.08},
        {"status": 500, "request_time": 0.2, "ttfb": 0.10, "ttlb": 0.15},
        Exception("Connection error"),
    ]
    total_time = 0.3

    stats = _calculate_statistics(results, total_time)

    if stats["total_requests"] != 3:  # noqa: PLR2004
        raise AssertionError
    if stats["successful_requests"] != 1:
        raise AssertionError
    if stats["failed_requests"] != 2:  # 500 status + exception  # noqa: PLR2004
        raise AssertionError
