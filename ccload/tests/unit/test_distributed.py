"""Unit tests for the distributed module."""
import asyncio
from collections.abc import Callable
from unittest.mock import MagicMock, patch

from ccload.distributed.distributed_load_test import run_distributed_load_test
from tests.unit.utils import assert_values


@patch("ccload.distributed.distributed_load_test.aiohttp.ClientSession")
def test_run_distributed_load_test(
    mock_session_cls: MagicMock,
    mock_client_session_factory: Callable[[int, dict | None], MagicMock],
    test_url: str,
    test_workers: list[str],
) -> None:
    """Test the run_distributed_load_test function."""
    statistics = {
        "total_requests": 1,
        "successful_requests": 1,
        "failed_requests": 0,
    }
    mock_session_cls.return_value = mock_client_session_factory(
        200,
        statistics,
    )

    stats = asyncio.run(run_distributed_load_test(
            test_url, n_request=1,
            n_concurrency=1, workers=test_workers,
        ),
    )

    n_workers = len(test_workers)
    assert_values(len(stats), n_workers, "Unexpected number of results")
    assert_values(
        stats[0].keys(),
        statistics.keys(),
        "Unexpected statistics keys",
    )
