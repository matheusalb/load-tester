"""Unit tests for HTTP methods in the ccload package."""
import asyncio
from collections.abc import Callable
from unittest.mock import MagicMock, patch

import pytest

from ccload.core.load_tester_features import load_tester
from tests.unit.utils import assert_values


@patch("ccload.core.load_tester_features.aiohttp.ClientSession")
@pytest.mark.parametrize("http_method", ["GET", "POST", "PUT", "DELETE"])
def test_http_methods(
    mock_session_cls: MagicMock,
    mock_client_session_factory: Callable[[int], MagicMock],
    test_url: str,
    http_method: str,
) -> None:
    """Test the successful requests."""
    mock_session_cls.return_value = mock_client_session_factory(200)

    stats = asyncio.run(
        load_tester(test_url, 1, 1, method=http_method),
    )
    assert_values(
        stats["successful_requests"],
        1,
        "Unexpected number of successful requests",
    )

