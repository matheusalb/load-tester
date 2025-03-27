"""ccload - A simple load tester for HTTP servers."""
import argparse
import asyncio
import json
import shutil
import subprocess
import time
from collections.abc import Callable
from typing import Any

from ccload.core.load_tester_features import _display_results, load_tester
from ccload.distributed.distributed_load_test import run_distributed_load_test
from ccload.exporters.metric_exporter import export_metrics
from ccload.script.request_script import script_load_tester


def _handle_result(
    results: dict[str, Any],
    name: str | None,
    export: str | None,
    output: str | None,
) -> None:
    _display_results(results, name)
    if export and output:
        export_metrics(results, export, output)

def _create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
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
    distribution_group.add_argument(
        "--workers",
        help="Comma-separated list of worker URLs",
        type=str,
        default=None,
    )

    return parser


def _process_request_data(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> tuple[str, dict[str, str] | None, dict[str, Any] | None] | None:
    """Process headers and JSON data from arguments."""
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
            return None

    json_data = None
    if args.json:
        try:
            json_data = json.loads(args.json)
        except json.JSONDecodeError:
            notify_format_error("JSON data must be valid JSON")
            return None

    # Check for mutually exclusive options
    input_count = sum(1 for x in [url, args.file, args.script] if x is not None)
    if input_count == 0:
        notify_format_error("URL, file, or script must be provided.")
        return None
    if input_count > 1:
        notify_format_error("Only one of URL, file, or script can be provided.")
        return None

    return url, headers, json_data


def _run_script_test(args: argparse.Namespace) -> None:
    """Run tests from a script file."""
    print(f"Running script test from: {args.script}")
    results = asyncio.run(script_load_tester(args.script))
    for url, result in results.items():
        _handle_result(result, url, args.export, args.output)


def _run_distributed_test(
    url: str,
    args: argparse.Namespace,
    headers: dict | None,
    json_data: dict | None,
    notify_format_error: Callable[[str], None],
) -> None:
    """Run distributed load testing."""
    worker_list = []
    worker_processes = []

    if args.distributed_workers > 0:
        base_port = 8001
        ports = list(range(base_port, base_port + args.distributed_workers))
        worker_list = [f"http://127.0.0.1:{port}" for port in ports]
        print(f"Spawning {args.distributed_workers} local worker servers...")

        uvicorn_path = shutil.which("uvicorn")
        if not uvicorn_path:
            print("Error: uvicorn executable not found in PATH")
            return
        for port in ports:
            proc = subprocess.Popen(  # noqa: S603
                [
                    uvicorn_path, "ccload.distributed.worker_server:app",
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

    results_list = asyncio.run(
        run_distributed_load_test(
            url=url,
            n_request=args.number,
            n_concurrency=args.concurrency,
            method=args.method,
            headers=headers,
            json_data=json_data,
            workers=worker_list,
        ),
    )

    if worker_processes:
        for proc in worker_processes:
            proc.terminate()

    for result in results_list:
        _handle_result(result, url, args.export, args.output)


def _run_standard_test(
    url: str,
    args: argparse.Namespace,
    headers: dict | None,
    json_data: dict | None,
) -> None:
    """Run standard single-node load testing."""
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
    _handle_result(results, url, args.export, args.output)


def _cli() -> None:
    """Command-line interface for ccload."""
    parser = _create_argument_parser()
    args = parser.parse_args()

    if args.script:
        _run_script_test(args)
        return

    def notify_format_error(msg: str) -> None:
        """Print an error message and the help message."""
        print(f"Error: {msg}")
        parser.print_help()

    result = _process_request_data(args, parser)
    if result is None:
        return

    url, headers, json_data = result

    if url is not None:
        if args.distributed:
            _run_distributed_test(url, args, headers, json_data, notify_format_error)
        else:
            _run_standard_test(url, args, headers, json_data)
