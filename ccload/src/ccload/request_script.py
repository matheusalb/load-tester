"""Module for parsing and executing load test scripts."""
import asyncio
import json
import time
from pathlib import Path
from typing import Any

import aiohttp

from ccload.core import _calculate_statistics, read_url


class RequestScript:
    """Class for parsing and executing load test scripts."""

    def __init__(self, script_path: str) -> None:
        """Initialize the request script parser.

        Args:
            script_path: Path to the script file.

        """
        self.script_path = script_path
        self.requests: list[dict[str, Any]] = []
        self._parse()

    def _parse(self) -> None:
        """Parse the script file."""
        with Path(self.script_path).open() as f:
            data = json.load(f)

        if not isinstance(data, list):
            msg = "Script must be a list of requests"
            raise TypeError(msg)

        for request in data:
            if "url" not in request:
                msg = "Each request must have a URL"
                raise ValueError(msg)

            # Set defaults for optional fields
            if "method" not in request:
                request["method"] = "GET"
            if "headers" not in request:
                request["headers"] = {}
            if "data" not in request:
                request["data"] = None
            if "json" not in request:
                request["json"] = None
            if "number" not in request:
                request["number"] = 1
            if "concurrency" not in request:
                request["concurrency"] = 1

            self.requests.append(request)

    def get_requests(self) -> list[dict[str, Any]]:
        """Get the parsed requests.

        Returns:
            List of request specifications.

        """
        return self.requests


async def script_load_tester(script_path: str) -> dict[str, dict[str, Any]]:
    """Run a load test using a script file.

    Args:
        script_path: Path to the script file.
        n_concurrency: Number of concurrent requests.

        if not isinstance(data, list):
            msg = "Script must be a list of requests"
            raise TypeError(msg)

    """
    script = RequestScript(script_path)
    requests = script.get_requests()

    results: list = []
    stats: dict[str, dict[str, Any]] = {}
    for req in requests:
        connector = aiohttp.TCPConnector(limit=req["concurrency"])
        start_time = time.perf_counter()
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            tasks.extend([
                read_url(
                    url=req["url"],
                    session=session,
                    method=req.get("method", "GET"),
                    headers=req.get("headers"),
                    json_data=req.get("json"),
                )
                for _ in range(req.get("concurrency", 1))
            ])

            results.extend(await asyncio.gather(*tasks, return_exceptions=True))

        total_time = time.perf_counter() - start_time
        stats[req["url"]] = _calculate_statistics(results, total_time)

    return stats
