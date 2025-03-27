"""Worker server for ccload."""

from typing import Any

from fastapi import FastAPI, Request

from ccload.core import load_tester

app = FastAPI()

@app.post("/run-test")
async def run_test(request: Request) -> dict[str, Any]:
    """Run a load test."""
    payload = await request.json()
    return await load_tester(
        url=payload["url"],
        n_request=payload["n_request"],
        n_concurrency=payload["n_concurrency"],
        method=payload.get("method", "GET"),
        headers=payload.get("headers"),
        json_data=payload.get("json_data"),
    )
