"""ccload - A simple load tester for HTTP servers."""
import argparse
import asyncio

from ccload.core import _print_results, load_tester


def _cli() -> None:
    """Command-line interface for ccload."""
    parser = argparse.ArgumentParser()

    parser.add_argument("url_positional", nargs="?", help="URL to test", default=None)

    parser.add_argument(
        "-u",
        "--url",
        help="URL to test (alternative to positional argument)",
        dest="url_option",
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
    parser.add_argument(
        "-f",
        "--file",
        help="File containing URLs to test (one per line)",
        type=argparse.FileType("r"),
        default=None,
    )

    args = parser.parse_args()

    url = args.url_option if args.url_option is not None else args.url_positional

    def notify_format_error(msg: str) -> None:
        """Print an error message and the help message."""
        print(msg)
        parser.print_help()

    if url is None and args.file is None:
        notify_format_error("Error: URL or file must be provided.")
        return
    if url is not None and args.file is not None:
        notify_format_error("Error: Only one of URL or file can be provided.")
        return

    if args.file is not None:
        urls = args.file.read().splitlines()
        for url in urls:
            print("-" * 80)
            print(f"Testing URL: {url}")
            results = asyncio.run(load_tester(url, args.number, args.concurrency))
            _print_results(results)
        return

    if url is not None:
        results = asyncio.run(load_tester(url, args.number, args.concurrency))
        _print_results(results)
