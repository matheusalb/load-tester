"""Unit tests for the stats methods."""

import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar
from unittest.mock import MagicMock, patch

from ccload.script.request_script import (
    RequestScript,
    script_load_tester,
)
from tests.unit.utils import assert_values


def test_request_parse(
    mock_data: dict, create_temp_script: Callable[[dict | list[dict]], Path],
) -> None:
    """Test the RequestScript class."""
    script_path = create_temp_script(mock_data)
    req_script = RequestScript(str(script_path))
    requests_parsed = req_script.get_requests()

    if len(requests_parsed) != 2:  # noqa: PLR2004
        msg = "Unexpected number of requests parsed"
        raise AssertionError(msg)

    req1 = requests_parsed[0]

    assert_values(req1["url"], "https://example.com/", "Unexpected URL")
    assert_values(req1["method"], "GET", "Unexpected method")
    assert_values(
        req1["headers"],
        {"Authorization": "Bearer token123"},
        "Unexpected headers",
    )
    assert_values(req1["number"], 3, "Unexpected number")
    assert_values(req1["concurrency"], 2, "Unexpected concurrency")

    req2 = requests_parsed[1]

    assert_values(req2["url"], "http://127.0.01:8080/", "Unexpected URL")
    assert_values(req2["method"], "GET", "Unexpected method")
    assert_values(
        req2["headers"], {"Authorization": "Bearer token123"}, "Unexpected headers",
    )
    assert_values(req2["number"], 5, "Unexpected number")
    assert_values(req2["concurrency"], 2, "Unexpected concurrency")

@patch("ccload.core.load_tester_features.aiohttp.ClientSession")
def test_script_load_tester(
    mock_session_cls: MagicMock,
    mock_client_session_factory: Callable[[int], MagicMock],
    mock_data: list[dict],
    create_temp_script: Callable[[dict | list[dict]], Path],
) -> None:
    """Test the script loading functionality."""
    mock_session_cls.return_value = mock_client_session_factory(200)

    script_path = create_temp_script(mock_data)
    stats = asyncio.run(
        script_load_tester(str(script_path)),
    )

    keys = stats.keys()
    assert_values(len(keys), 2, "Unexpected number of results")
