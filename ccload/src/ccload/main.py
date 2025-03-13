import argparse
import aiohttp
import asyncio
import time

async def read_url(url: str, session: aiohttp.ClientSession) -> aiohttp.ClientResponse:
    start_time = time.perf_counter()
    
    async with session.get(url) as response:
        ttfb = time.perf_counter() - start_time # Time to first byte
        
        
        await response.read()
        ttlb = time.perf_counter() - start_time # Time to last byte
                
        return {
            "status": response.status,
            "ttfb": ttfb,
            "ttlb": ttlb,
            "request_time": time.perf_counter() - start_time,
        }

def _calculate_statistics(results: list[dict[str, any]], total_time: float) -> dict[str, any]:
    statistics = {
        "total_requests": len(results),
        "successful_requests": 0,
        "failed_requests": 0,
        "request_time_min": float("inf"),
        "request_time_max": float("-inf"),
        "request_time_mean": 0,
        "ttfb_min": float("inf"),
        'ttfb_max': float("-inf"),
        'ttfb_mean': 0,
        'ttlb_min': float("inf"),
        'ttlb_max': float("-inf"),
        'ttlb_mean': 0,
        'requests_per_second': 0,
    }
    

    request_time_total = 0
    ttfb_total = 0
    ttlb_total = 0
    for result in results:
        if isinstance(result, Exception):
            statistics["failed_requests"] += 1
            continue
        
        if 500 <= result["status"] < 600:
            statistics["failed_requests"] += 1
        elif 200 <= result["status"] < 300:
            statistics["successful_requests"] += 1
            
            # Total request time stats
            if result["request_time"] < statistics["request_time_min"]:
                statistics["request_time_min"] = result["request_time"]
            if result["request_time"] > statistics["request_time_max"]:
                statistics["request_time_max"] = result["request_time"]
            request_time_total += result["request_time"]
            
            # TTFB stats
            if result["ttfb"] < statistics["ttfb_min"]:
                statistics["ttfb_min"] = result["ttfb"]
            if result["ttfb"] > statistics["ttfb_max"]:
                statistics["ttfb_max"] = result["ttfb"]
            ttfb_total += result["ttfb"]
            
            # TTLB stats
            if result["ttlb"] < statistics["ttlb_min"]:
                statistics["ttlb_min"] = result["ttlb"]
            if result["ttlb"] > statistics["ttlb_max"]:
                statistics["ttlb_max"] = result["ttlb"]
            ttlb_total += result["ttlb"]
    
    statistics["request_time_mean"] = request_time_total / statistics["successful_requests"]
    statistics["ttfb_mean"] = ttfb_total / statistics["successful_requests"]
    statistics["ttlb_mean"] = ttlb_total / statistics["successful_requests"]
    statistics["requests_per_second"] = statistics["successful_requests"] / total_time

    return statistics

    
async def load_tester(url: str, n_request: int, n_concurrency: int) -> int:
    results: list[dict[str, any]] = []
    connector = aiohttp.TCPConnector(limit=n_concurrency)

    start_time = time.perf_counter()
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [read_url(url, session) for _ in range(n_request)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.perf_counter() - start_time
    
    statistics = _calculate_statistics(results, total_time)
    
    return statistics

def _print_results(results: dict[str, any]):
    print("\nResults:")
    print(f" Total Requests (2XX).......................: {results['successful_requests']}")
    print(f" Failed Requests (5XX)......................: {results['failed_requests']}")
    print(f" Request/second.............................: {results['requests_per_second']:.2f}")
    print()
    print(f"Total Request Time (s) (Min, Max, Mean).....: {results['request_time_min']:.2f}, {results['request_time_max']:.2f}, {results['request_time_mean']:.2f}")
    print(f"Time to First Byte (s) (Min, Max, Mean).....: {results['ttfb_min']:.2f}, {results['ttfb_max']:.2f}, {results['ttfb_mean']:.2f}")
    print(f"Time to Last Byte (s) (Min, Max, Mean)......: {results['ttlb_min']:.2f}, {results['ttlb_max']:.2f}, {results['ttlb_mean']:.2f}")
    

def _cli():
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "url_positional", 
        nargs="?",
        help="URL to test",
        default=None
    )
    
    parser.add_argument(
        "-u", "--url",
        help="URL to test (alternative to positional argument)",
        dest="url_option",
        default=None
    )
    parser.add_argument(
        "-n", "--number",
        help="Number of requests to make",
        type=int,
        default=10
    )
    parser.add_argument(
        "-c", "--concurrency",
        help="Number of requests to make concurrently",
        type=int,
        default=1
    )
    
    args = parser.parse_args()

    url = args.url_option if args.url_option is not None else args.url_positional
    if url is None:
        parser.print_help()
        return
    
    results = asyncio.run(load_tester(url, args.number, args.concurrency))

    _print_results(results)

if __name__ == "__main__":
    _cli()
