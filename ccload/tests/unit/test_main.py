import asyncio
from ccload.main import load_tester

def test_one_request():
    url = "http://example.com"
    n_request = 1
    n_concurrency = 1
    response_code = asyncio.run(load_tester(url, n_request, n_concurrency))
    assert response_code == "Response code: 200"

def test_100_requests():
    url = "http://localhost:8000"
    n_request = 100
    n_concurrency = 1
    response_code = asyncio.run(load_tester(url, n_request, n_concurrency))
    assert response_code == "Successes: 100\nFailures: 0"

