"""Shared fixtures for testing."""
import types
from unittest.mock import AsyncMock, MagicMock
from typing import Callable

import pytest
from aiohttp import StreamReader


class MockResponse:
    """Mock response object for aiohttp."""

    def __init__(self, status: int) -> None:
        """Initialize the mock response object."""
        self.status = status
        self.content = MagicMock(spec=StreamReader)
        self.content.read = AsyncMock(return_value=b"data")
        self._read = AsyncMock(return_value=b"full response")

    async def __aenter__(self) -> "MockResponse":
        """Enter the context manager."""
        return self

    async def __aexit__(
        self,
        exc_typ: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Exit the context manager."""
        return

    async def read(self) -> bytes:
        """Read the response."""
        return await self._read()

# @pytest.fixture
# def mock_client_session_factory():
#     """Fixture for a mocked aiohttp.ClientSession."""
#     mock_response = MockResponse(200)
#     mock_session = MagicMock()
#     # Configure the context manager behavior of the session
#     mock_session.__aenter__.return_value = mock_session
#     # When get() is called, return a context manager that yields mock_response
#     mock_session.get.return_value.__aenter__.return_value = mock_response
#     return mock_session

@pytest.fixture
def mock_client_session_factory() -> Callable[[int], MagicMock]:
    """Fixture for a mocked aiohttp.ClientSession."""
    def factory(status: int = 200) -> MagicMock:
        mock_response = MockResponse(status)
        mock_session = MagicMock()
        # Simulate async context manager behavior for the session
        mock_session.__aenter__.return_value = mock_session
        # Simulate async context manager behavior for the get() method
        mock_session.get.return_value.__aenter__.return_value = mock_response
        return mock_session
    return factory

@pytest.fixture
def test_url() -> str:
    """Fixture for the test URL."""
    return "http://example.com"
