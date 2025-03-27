"""Core functionality for the load testing tool."""
import asyncio
import time
from typing import Any

import aiohttp


async def read_url(
    url: str, session: aiohttp.ClientSession,
    method: str = "GET", headers: dict[str, str] | None = None,
    json_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Read a URL and return the status code and time taken."""
    start_time = time.perf_counter()

    async with session.request(
        method, url,
        headers=headers,
        json=json_data,
        ssl=False,
    ) as response:
        await response.content.read(1)
        ttfb = time.perf_counter() - start_time  # Time to first byte
        await response.read()
        ttlb = time.perf_counter() - start_time  # Time to last byte
        return {
            "status": response.status,
            "ttfb": ttfb,
            "ttlb": ttlb,
            "request_time": time.perf_counter() - start_time,
        }


def _calculate_statistics(
    results: list[dict[str, Any]], total_time: float,
) -> dict[str, Any]:
    """Calculate statistics from the results of the load test."""
    statistics = {
        "total_requests": len(results),
        "successful_requests": 0,
        "failed_requests": 0,
        "request_time_min": float("inf"),
        "request_time_max": float("-inf"),
        "request_time_mean": 0,
        "ttfb_min": float("inf"),
        "ttfb_max": float("-inf"),
        "ttfb_mean": 0,
        "ttlb_min": float("inf"),
        "ttlb_max": float("-inf"),
        "ttlb_mean": 0,
        "requests_per_second": 0,
    }

    request_time_total = 0
    ttfb_total = 0
    ttlb_total = 0
    for result in results:
        if isinstance(result, Exception):
            statistics["failed_requests"] += 1
            continue

        if 500 <= result["status"] < 600:  # noqa: PLR2004
            statistics["failed_requests"] += 1
        elif 200 <= result["status"] < 300:  # noqa: PLR2004
            statistics["successful_requests"] += 1

            # Total request time stats
            statistics["request_time_min"] = min(
                statistics["request_time_min"],
                result["request_time"],
            )
            statistics["request_time_max"] = max(
                statistics["request_time_max"],
                result["request_time"],
            )
            request_time_total += result["request_time"]

            # TTFB stats
            statistics["ttfb_min"] = min(
                statistics["ttfb_min"],
                result["ttfb"],
            )
            statistics["ttfb_max"] = max(
                statistics["ttfb_max"],
                result["ttfb"],
            )
            ttfb_total += result["ttfb"]

            # TTLB stats
            statistics["ttlb_min"] = min(
                statistics["ttlb_min"],
                result["ttlb"],
            )
            statistics["ttlb_max"] = max(
                statistics["ttlb_max"],
                result["ttlb"],
            )
            ttlb_total += result["ttlb"]

    statistics["request_time_mean"] = (
        request_time_total / statistics["successful_requests"]
        if statistics["successful_requests"] > 0 else 0
    )
    statistics["ttfb_mean"] = (
        ttfb_total / statistics["successful_requests"]
        if statistics["successful_requests"] > 0 else 0
    )
    statistics["ttlb_mean"] = (
        ttlb_total / statistics["successful_requests"]
        if statistics["successful_requests"] > 0 else 0
    )
    statistics["requests_per_second"] = (
        statistics["successful_requests"] / total_time
        if total_time > 0 else 0
    )

    return statistics


async def load_tester(  # noqa: PLR0913
    url: str, n_request: int, n_concurrency: int,
    method: str = "GET", headers: dict[str, str] | None = None,
    json_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run a load test on a URL."""
    results: list = []
    connector = aiohttp.TCPConnector(limit=n_concurrency)

    start_time = time.perf_counter()
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [read_url(
            url=url,
            session=session,
            method=method,
            headers=headers,
            json_data=json_data,
        ) for _ in range(n_request)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.perf_counter() - start_time

    return _calculate_statistics(results, total_time)


def _display_results(results: dict[str, Any], name: str | None = None) -> None:
    """Print the results of the load test."""
    if name:
        print(f"-> Testing URL: {name}")
    print("\nResults:")
    print(
        " Total Requests (2XX).......................:",
        f"{results['successful_requests']}",
    )
    print(f" Failed Requests (5XX)......................: {results['failed_requests']}")
    print(
        " Requests/second............................:",
        f"{results['requests_per_second']:.2f}",
    )
    print()
    print(
        "Total Request Time (s) (Min, Max, Mean).....: ",
        f"{results['request_time_min']:.2f}, {results['request_time_max']:.2f}, "
        f"{results['request_time_mean']:.2f}",
    )
    print(
        "Time to First Byte (s) (Min, Max, Mean).....: ",
        f"{results['ttfb_min']:.2f}, {results['ttfb_max']:.2f}, "
        f"{results['ttfb_mean']:.2f}",
    )
    print(
        "Time to Last Byte (s) (Min, Max, Mean)......: ",
        f"{results['ttlb_min']:.2f}, {results['ttlb_max']:.2f}, "
        f"{results['ttlb_mean']:.2f}",
    )
    print("-" * 80)
