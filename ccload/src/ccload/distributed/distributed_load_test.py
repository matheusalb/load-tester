"""Distributed load test module."""
import asyncio
from typing import Any

import aiohttp


async def send_task(
    session: aiohttp.ClientSession,
    worker_url: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Send a task to a worker."""
    try:
        print(f"Sending to {worker_url} with {payload['n_request']} requests")
        async with session.post(f"{worker_url}/run-test", json=payload) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"Failed to contact {worker_url}: {e}")
        return {}

async def run_distributed_load_test(  # noqa: PLR0913
    url: str, n_request: int, n_concurrency: int,
    method: str = "GET", headers: dict[str, str] | None = None,
    json_data: dict[str, Any] | None = None,
    workers: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Run a distributed load test."""
    if not workers:
        print("No workers specified")
        return []

    num_workers = len(workers)
    reqs_per_worker = n_request // num_workers
    remainder = n_request % num_workers

    payloads = []
    for i in range(num_workers):
        payload = {
            "url": url,
            "n_request": reqs_per_worker + (1 if i < remainder else 0),
            "n_concurrency": n_concurrency,
            "method": method,
            "headers": headers,
            "json_data": json_data,
        }
        payloads.append(payload)

    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [
            send_task(session, worker_url, payload)
            for worker_url, payload in zip(workers, payloads, strict=False)
        ]
        results = await asyncio.gather(*tasks)
        return [result for result in results if result]
