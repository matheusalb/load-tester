"""ccload - A simple load tester for HTTP servers."""
import argparse
import asyncio
import json
import subprocess
import time

from ccload.core import _print_results, load_tester
from ccload.distributed_load_test import run_distributed_load_test
from ccload.request_script import script_load_tester


def _cli() -> None:
    """Command-line interface for ccload."""
    parser = argparse.ArgumentParser()

    url_group = parser.add_argument_group("URL Options")
    url_group.add_argument(
        "url_positional", nargs="?",
        help="URL to test", default=None,
    )
    url_group.add_argument(
        "-u",
        "--url",
        help="URL to test (alternative to positional argument)",
        dest="url_option",
        default=None,
    )
    url_group.add_argument(
        "-f",
        "--file",
        help="File containing URLs to test (one per line)",
        type=argparse.FileType("r"),
        default=None,
    )
    url_group.add_argument(
        "-s",
        "--script",
        help="Script file with request definitions (JSON)",
        type=str,
        default=None,
    )

    request_group = parser.add_argument_group("Request Options")
    request_group.add_argument(
        "-m",
        "--method",
        help="HTTP method to use (GET, POST, PUT, etc.)",
        type=str,
        default="GET",
    )
    request_group.add_argument(
        "--headers",
        help="HTTP headers in JSON format",
        type=str,
        default=None,
    )
    request_group.add_argument(
        "--json",
        help="JSON data to send with POST/PUT requests",
        type=str,
        default=None,
    )

    parser.add_argument(
        "-n", "--number", help="Number of requests to make", type=int, default=10,
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        help="Number of requests to make concurrently",
        type=int,
        default=1,
    )

    export_group = parser.add_argument_group("Export Options")
    export_group.add_argument(
        "--export",
        help="Export metrics in specified format (json, csv, prometheus, influxdb)",
        choices=["json", "csv", "prometheus", "influxdb"],
        default=None,
    )
    export_group.add_argument(
        "--output",
        help="Output file path for exported metrics",
        type=str,
        default=None,
    )

    distribution_group = parser.add_argument_group("Distributed Options")
    distribution_group.add_argument(
        "--distributed",
        help="Enable distributed load testing",
        action="store_true",
    )
    distribution_group.add_argument(
        "--distributed-workers",
        help="Number of distributed workers to use",
        type=int,
        default=1,
    )

    args = parser.parse_args()

    url = args.url_option if args.url_option is not None else args.url_positional

    def notify_format_error(msg: str) -> None:
        """Print an error message and the help message."""
        print(f"Error: {msg}")
        parser.print_help()

    # Process headers and JSON data if provided
    headers = None
    if args.headers:
        try:
            headers = json.loads(args.headers)
        except json.JSONDecodeError:
            notify_format_error("Headers must be valid JSON")

    json_data = None
    if args.json:
        try:
            json_data = json.loads(args.json)
        except json.JSONDecodeError:
            notify_format_error("JSON data must be valid JSON")

    if args.script:
        print(f"Running script test from: {args.script}")
        results = asyncio.run(script_load_tester(args.script))
        for url, result in results.items():
            _print_results(result, url, args.export, args.output)
        return

    # Check for mutually exclusive options
    input_count = sum(1 for x in [url, args.file, args.script] if x is not None)
    if input_count == 0:
        notify_format_error("URL, file, or script must be provided.")
        return
    if input_count > 1:
        notify_format_error("Only one of URL, file, or script can be provided.")
        return

    if url is not None:
        if args.distributed:
            worker_list = []
            worker_processes = []

            if args.distributed_workers > 0:
                base_port = 8001
                ports = list(range(base_port, base_port + args.distributed_workers))
                worker_list = [f"http://127.0.0.1:{port}" for port in ports]

                print(f"Spawning {args.distributed_workers} local worker servers...")
                for port in ports:
                    proc = subprocess.Popen(
                        [
                            "uvicorn", "ccload.worker_server:app",
                            "--host", "127.0.0.1",
                            "--port", str(port),
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    worker_processes.append(proc)

                time.sleep(2)  # Wait for workers to be ready

            elif args.workers:
                worker_list = [w.strip() for w in args.workers.split(",")]
            else:
                notify_format_error("You must provide --workers or --distributed-workers")
                return

            results_list = run_distributed_load_test(
                url=url,
                n_request=args.number,
                n_concurrency=args.concurrency,
                method=args.method,
                headers=headers,
                json_data=json_data,
                workers=worker_list,
            )

            if worker_processes:
                for proc in worker_processes:
                    proc.terminate()

            for result in results_list:
                _print_results(result, url, args.export, args.output)
            return

        results = asyncio.run(
            load_tester(
                url,
                args.number,
                args.concurrency,
                method=args.method,
                headers=headers,
                json_data=json_data,
            ),
        )
        _print_results(results, url, args.export, args.output)
