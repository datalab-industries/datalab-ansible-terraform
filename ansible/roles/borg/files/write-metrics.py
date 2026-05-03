#!/usr/bin/env python3
"""Write borgmatic status metrics for node_exporter's textfile collector.

Invoked by borgmatic's after_backup / on_error hooks.
Usage: write-metrics.py {success|error}

Two separate prom files are written so a failed run does not erase the last
successful run's size metrics. node_exporter merges all *.prom files in the
textfile directory at scrape time.
"""
import json
import os
import subprocess
import sys
import time

METRICS_DIR = "/metrics"


def write_atomically(path: str, content: str) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(content)
    os.rename(tmp, path)


def collect_repo_stats() -> list[str]:
    out = subprocess.check_output(
        ["borgmatic", "info", "--json", "--last", "1"],
        stderr=subprocess.DEVNULL,
        timeout=300,
    )
    data = json.loads(out)[0]
    stats = data["cache"]["stats"]
    lines = [
        f"borgmatic_repo_unique_size_bytes {stats['unique_csize']}",
        f"borgmatic_repo_total_size_bytes {stats['total_size']}",
    ]
    archives = data.get("archives") or []
    if archives:
        a = archives[0]["stats"]
        lines.extend([
            f"borgmatic_last_archive_original_size_bytes {a['original_size']}",
            f"borgmatic_last_archive_compressed_size_bytes {a['compressed_size']}",
            f"borgmatic_last_archive_deduplicated_size_bytes {a['deduplicated_size']}",
        ])
    return lines


def main() -> None:
    status = sys.argv[1] if len(sys.argv) > 1 else "error"
    ts = int(time.time())

    if status == "success":
        lines = [f"borgmatic_last_success_timestamp_seconds {ts}"]
        try:
            lines.extend(collect_repo_stats())
        except Exception as e:
            print(f"borgmatic metrics: failed to capture repo info: {e}", file=sys.stderr)
        path = os.path.join(METRICS_DIR, "borgmatic-success.prom")
    else:
        lines = [f"borgmatic_last_failure_timestamp_seconds {ts}"]
        path = os.path.join(METRICS_DIR, "borgmatic-failure.prom")

    write_atomically(path, "\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
