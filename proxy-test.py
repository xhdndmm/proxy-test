#!/usr/bin/env python3
#[https://github.com/xhdndmm/proxy-test]
#MIT License
#Copyright (c) 2026 喜欢电脑的猫咪

import argparse
import statistics
import time
import urllib.request
import urllib.error
import urllib.parse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

class ProxyTester:
    def __init__(self, args):
        self.args = args
        self.proxy_url = (
            f"{args.proxy_protocol}://{args.proxy_host}:{args.proxy_port}"
        )

    def build_opener(self):
        proxy_handler = urllib.request.ProxyHandler({
            "http": self.proxy_url,
            "https": self.proxy_url,
        })

        return urllib.request.build_opener(proxy_handler)

    def test_once(self, index, url):
        opener = self.build_opener()

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
                "Accept": "*/*",
                "Connection": "close",
            }
        )

        start = time.perf_counter()

        try:
            with opener.open(
                request,
                timeout=self.args.timeout
            ) as response:
                body = response.read()
                elapsed = time.perf_counter() - start

                status = response.status
                size = len(body)

                return {
                    "index": index,
                    "url": url,
                    "success": 200 <= status < 400,
                    "status": status,
                    "elapsed": elapsed,
                    "size": size,
                    "error": None,
                }

        except urllib.error.HTTPError as e:
            elapsed = time.perf_counter() - start

            try:
                size = len(e.read())
            except Exception:
                size = 0

            return {
                "index": index,
                "url": url,
                "success": False,
                "status": e.code,
                "elapsed": elapsed,
                "size": size,
                "error": f"HTTP {e.code}: {e.reason}",
            }

        except Exception as e:
            elapsed = time.perf_counter() - start

            return {
                "index": index,
                "url": url,
                "success": False,
                "status": "-",
                "elapsed": elapsed,
                "size": 0,
                "error": f"{type(e).__name__}: {e}",
            }

    def run(self):
        tasks = [
            (i + 1, self.args.urls[i % len(self.args.urls)])
            for i in range(self.args.count)
        ]

        results = []

        print("=" * 75)
        print("                 Proxy Test")
        print("=" * 75)
        print(f"Proxy      : {self.proxy_url}")
        print(f"URLs       : {len(self.args.urls)}")
        print(f"Count      : {self.args.count}")
        print(f"Timeout    : {self.args.timeout}s")
        print(f"Concurrency: {self.args.workers}")
        print("=" * 75)

        total_start = time.perf_counter()

        with ThreadPoolExecutor(
            max_workers=self.args.workers
        ) as executor:

            futures = {
                executor.submit(self.test_once, i, url): i
                for i, url in tasks
            }

            for future in as_completed(futures):
                result = future.result()
                results.append(result)

                if result["success"]:
                    print(
                        f"[{result['index']:03d}] "
                        f"OK  "
                        f"HTTP {result['status']}  "
                        f"{result['elapsed'] * 1000:.2f} ms  "
                        f"{result['size']} bytes"
                    )
                else:
                    print(
                        f"[{result['index']:03d}] "
                        f"FAIL "
                        f"HTTP {result['status']}  "
                        f"{result['elapsed'] * 1000:.2f} ms  "
                        f"{result['error']}"
                    )

        total_elapsed = time.perf_counter() - total_start

        self.show_statistics(results, total_elapsed)

    def show_statistics(self, results, total_elapsed):
        total = len(results)
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        latencies = [r["elapsed"] for r in successful]

        total_bytes = sum(r["size"] for r in results)

        print("\n" + "=" * 75)
        print("                         Statistics")
        print("=" * 75)

        print(f"Total requests : {total}")
        print(f"Successful    : {len(successful)}")
        print(f"Failed        : {len(failed)}")

        success_rate = (
            len(successful) / total * 100 if total else 0
        )

        print(f"Success rate  : {success_rate:.2f}%")
        print(f"Failure rate  : {100 - success_rate:.2f}%")

        if latencies:
            print("\nLatency (successful requests only):")
            print(f"Average       : {statistics.mean(latencies) * 1000:.2f} ms")
            print(f"Median        : {statistics.median(latencies) * 1000:.2f} ms")
            print(f"Fastest       : {min(latencies) * 1000:.2f} ms")
            print(f"Slowest       : {max(latencies) * 1000:.2f} ms")

        print("\nTraffic:")
        print(f"Total received: {total_bytes:,} bytes")
        print(f"Total time    : {total_elapsed:.2f} seconds")

        if total_elapsed > 0:
            print(
                f"Throughput    : "
                f"{total_bytes / total_elapsed / 1024:.2f} KB/s"
            )

        print("=" * 75)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Test HTTP/HTTPS proxies using real web requests."
    )

    parser.add_argument(
        "-p", "--proxy-protocol",
        choices=["http", "https"],
        default="http",
        help="Proxy protocol (default: http)"
    )

    parser.add_argument(
        "-H", "--proxy-host",
        default="127.0.0.1",
        help="Proxy server address"
    )

    parser.add_argument(
        "-P", "--proxy-port",
        type=int,
        default=7890,
        help="Proxy server port"
    )

    parser.add_argument(
        "-u", "--url",
        action="append",
        dest="urls",
        help="Test URL; can be specified multiple times"
    )

    parser.add_argument(
        "-n", "--count",
        type=int,
        default=10,
        help="Total number of requests (default: 10)"
    )

    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=10,
        help="Request timeout in seconds (default: 10)"
    )

    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=1,
        help="Concurrent workers (default: 1)"
    )

    args = parser.parse_args()

    if not args.urls:
        args.urls = ["https://www.google.com/generate_204"]

    if args.count < 1:
        parser.error("count must be >= 1")

    if args.timeout <= 0:
        parser.error("timeout must be > 0")

    if args.workers < 1:
        parser.error("workers must be >= 1")

    if not 1 <= args.proxy_port <= 65535:
        parser.error("proxy port must be between 1 and 65535")

    for url in args.urls:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            parser.error(f"Invalid URL: {url}")

    return args


def main():
    try:
        args = parse_args()
        tester = ProxyTester(args)
        tester.run()

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(130)


if __name__ == "__main__":
    main()
