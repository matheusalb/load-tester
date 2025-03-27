""""Unit tests for the core module."""
import asyncio
from collections.abc import Callable
from unittest.mock import MagicMock, patch

import pytest

from ccload.core.load_tester_features import load_tester


@patch("ccload.core.load_tester_features.aiohttp.ClientSession")
def test_structure(
    mock_session_cls: MagicMock,
    mock_client_session_factory: Callable[[int], MagicMock],
    test_url: str,
) -> None:
    """Test the structure of the returned statistics."""
    key_columns = [
        "total_requests","successful_requests","failed_requests",
        "request_time_min","request_time_max","request_time_mean",
        "ttfb_min","ttfb_max","ttfb_mean","ttlb_min","ttlb_max",
        "ttlb_mean","requests_per_second",
    ]

    mock_session_cls.return_value = mock_client_session_factory(200)

    stats = asyncio.run(load_tester(test_url, 1, 1))
    if set(stats.keys()) != set(key_columns):
        raise AssertionError

@patch("ccload.core.load_tester_features.aiohttp.ClientSession")
def test_successful_requests(
    mock_session_cls: MagicMock,
    mock_client_session_factory: Callable[[int], MagicMock],
    test_url: str,
) -> None:
    """Test the successful requests."""
    mock_session_cls.return_value = mock_client_session_factory(200)

    stats = asyncio.run(load_tester(test_url, 1, 1))
    if stats["successful_requests"] != 1:
        raise AssertionError
    if stats["failed_requests"] != 0:
        raise AssertionError
    if stats["total_requests"] != 1:
        raise AssertionError

@patch("ccload.core.load_tester_features.aiohttp.ClientSession")
def test_failed_request(
    mock_session_cls: MagicMock,
    mock_client_session_factory: Callable[[int], MagicMock],
    test_url: str,
) -> None:
    """Test the failed requests."""
    mock_session_cls.return_value = mock_client_session_factory(500)

    stats = asyncio.run(load_tester(test_url, 1, 1))
    if stats["successful_requests"] != 0:
        raise AssertionError
    if stats["failed_requests"] != 1:
        raise AssertionError
    if stats["total_requests"] != 1:
        raise AssertionError

@patch("ccload.core.load_tester_features.aiohttp.ClientSession")
def test_multiple_requests(
    mock_session_cls: MagicMock,
    mock_client_session_factory: Callable[[int], MagicMock],
    test_url: str,
) -> None:
    """Test the multiple requests."""
    mock_session_cls.return_value = mock_client_session_factory(200)

    n_request = 10
    stats = asyncio.run(load_tester(test_url, n_request, 1))
    if stats["successful_requests"] != n_request:
        raise AssertionError
    if stats["failed_requests"] != 0:
        raise AssertionError
    if stats["total_requests"] != n_request:
        raise AssertionError

@pytest.mark.parametrize("concurrency", [1, 5, 10])
@patch("ccload.core.load_tester_features.aiohttp.ClientSession")
def test_concurrency(
    mock_session_cls: MagicMock,
    mock_client_session_factory: Callable[[int], MagicMock],
    concurrency: int,
    test_url: str,
) -> None:
    """Test the concurrency."""
    mock_session_cls.return_value = mock_client_session_factory(200)

    n_request = 10
    stats = asyncio.run(load_tester(test_url, n_request, concurrency))
    if stats["successful_requests"] != n_request:
        raise AssertionError
    if stats["failed_requests"] != 0:
        raise AssertionError
    if stats["total_requests"] != n_request:
        raise AssertionError
