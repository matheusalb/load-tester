"""Shared fixtures for testing."""
import json
import types
from collections.abc import Callable
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiohttp import StreamReader


class MockResponse:
    """Mock response object for aiohttp."""

    def __init__(self, status: int, json_data: dict | None) -> None:
        """Initialize the mock response object."""
        self.status = status
        self.content = MagicMock(spec=StreamReader)
        self.content.read = AsyncMock(return_value=b"data")
        self._read = AsyncMock(return_value=b"full response")
        self._json_data = json_data or {}

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

    async def json(self) -> dict:
        """Return the JSON data."""
        return self._json_data

    def raise_for_status(self) -> None:
        """Mock raise_for_status. Raise if status is error."""
        http_error_threshold = 400
        if self.status >= http_error_threshold:
            msg = f"HTTP Error: status {self.status}"
            raise Exception(msg)  # noqa: TRY002


@pytest.fixture
def mock_client_session_factory() -> Callable[[int, dict | None], MagicMock]:
    """Fixture for a mocked aiohttp.ClientSession."""
    def factory(status: int = 200, json_data: dict | None = None) -> MagicMock:
        mock_response = MockResponse(status, json_data)
        mock_session = MagicMock()
        # Simulate async context manager behavior for the session
        mock_session.__aenter__.return_value = mock_session
        # Simulate async context manager behavior for the get() method
        mock_session.get.return_value.__aenter__.return_value = mock_response
        # Simulate async context manager behavior for the post() method
        mock_session.post.return_value.__aenter__.return_value = mock_response
        # Simulate async context manager behavior for request() method
        mock_session.request.return_value.__aenter__.return_value = mock_response
        return mock_session
    return factory

@pytest.fixture
def test_url() -> str:
    """Fixture for the test URL."""
    return "http://example.com"

@pytest.fixture
def create_temp_script(tmp_path: Path) -> Callable[[dict | list[dict]], Path]:
    """Fixture for creating a temporary script file."""
    def _create(data: dict | list[dict]) -> Path:
        file_path = tmp_path / "script.json"
        file_path.write_text(json.dumps(data))
        return file_path
    return _create

@pytest.fixture
def mock_data() -> list[dict]:
    """Fixture for mock script data."""
    return [
        {
            "url": "https://example.com/",
            "method": "GET",
            "headers": {"Authorization": "Bearer token123"},
            "number": 3,
            "concurrency": 2,
        },
        {
            "url": "http://127.0.01:8080/",
            "method": "GET",
            "headers": {"Authorization": "Bearer token123"},
            "number": 5,
            "concurrency": 2,
        },
    ]

@pytest.fixture
def test_workers() -> list[str]:
    """Fixture for the test workers."""
    return ["http://worker1", "http://worker2", "http://worker3"]
