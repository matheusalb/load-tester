import requests
import json

from typing import Any

import concurrent.futures

def send_task(worker_url: str, payload: dict) -> dict:
    """Send a task to a worker."""
    try:
        print(f"Sending to {worker_url} with {payload['n_request']} requests")
        response = requests.post(
            f"{worker_url}/run-test",
            json=payload,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to contact {worker_url}: {e}")
        return {}

def run_distributed_load_test(
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

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(send_task, worker_url, payload)
            for worker_url, payload in zip(workers, payloads)
        ]
        return [future.result() for future in futures if future.result()]

