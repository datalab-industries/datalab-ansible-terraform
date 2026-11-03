#!/usr/bin/python3
"""Write apt / unattended-upgrades health metrics for node_exporter's textfile collector.

Usage: datalab-apt-metrics <textfile collector directory>

Run hourly by datalab-apt-metrics.timer, and after each apt-daily-upgrade run.

apt-daily-upgrade.service always exits successfully, even when unattended-upgrade
fails, because apt.systemd.daily swallows its exit code. It does only touch
/var/lib/apt/periodic/upgrade-stamp when unattended-upgrade exits 0, so the age
of that stamp is the reliable "upgrades are working" signal. (unattended-upgrade
also exits 0 when there is nothing to upgrade, so the stamp is touched daily.)
"""

from __future__ import annotations

import os
import sys
import time

OUTPUT_NAME = "datalab-apt.prom"

UPGRADE_STAMP = "/var/lib/apt/periodic/upgrade-stamp"
UPDATE_STAMP = "/var/lib/apt/periodic/update-stamp"
KEPT_BACK_FILE = "/var/lib/unattended-upgrades/kept-back"
REBOOT_REQUIRED_FILE = "/var/run/reboot-required"


def write_atomically(path: str, content: str) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(content)
    os.chmod(tmp, 0o644)
    os.rename(tmp, path)


def mtime_or_none(path: str) -> float | None:
    try:
        return os.stat(path).st_mtime
    except FileNotFoundError:
        return None


def stamp_metrics() -> list[str]:
    lines = []
    for name, path, help_text in (
        (
            "apt_unattended_upgrade_last_success_timestamp_seconds",
            UPGRADE_STAMP,
            "Last time unattended-upgrade exited successfully.",
        ),
        (
            "apt_update_last_success_timestamp_seconds",
            UPDATE_STAMP,
            "Last time the periodic apt-get update succeeded.",
        ),
    ):
        ts = mtime_or_none(path)
        # Omit rather than report 0, so a fresh host doesn't look years overdue
        if ts is not None:
            lines += [f"# HELP {name} {help_text}", f"# TYPE {name} gauge", f"{name} {ts:.0f}"]

    since = mtime_or_none(REBOOT_REQUIRED_FILE)
    lines += [
        "# HELP node_reboot_required Whether /var/run/reboot-required exists.",
        "# TYPE node_reboot_required gauge",
        f"node_reboot_required {0 if since is None else 1}",
    ]
    if since is not None:
        lines += [
            "# HELP node_reboot_required_since_timestamp_seconds When the pending reboot was requested.",
            "# TYPE node_reboot_required_since_timestamp_seconds gauge",
            f"node_reboot_required_since_timestamp_seconds {since:.0f}",
        ]

    try:
        with open(KEPT_BACK_FILE) as f:
            kept_back = len(f.read().split())
    except FileNotFoundError:
        kept_back = 0
    lines += [
        "# HELP apt_unattended_upgrade_kept_back Packages unattended-upgrade could not upgrade on its last run.",
        "# TYPE apt_unattended_upgrade_kept_back gauge",
        f"apt_unattended_upgrade_kept_back {kept_back}",
    ]
    return lines


def cache_metrics() -> list[str]:
    import apt
    import apt_pkg

    # Read-only view of the local cache; does not touch the network or the dpkg lock
    cache = apt.Cache()

    # Anything else (unpacked, half-configured/installed, triggers-awaited/pending)
    # means dpkg was interrupted. python3-apt has no constants for the triggers
    # states, so list the healthy ones instead.
    ok_states = {
        apt_pkg.CURSTATE_NOT_INSTALLED,
        apt_pkg.CURSTATE_CONFIG_FILES,
        apt_pkg.CURSTATE_INSTALLED,
    }
    reinst_required = {apt_pkg.INSTSTATE_REINSTREQ, apt_pkg.INSTSTATE_HOLD_REINSTREQ}
    pending = {"security": 0, "other": 0}
    held = 0
    dpkg_broken = 0
    for pkg in cache:
        raw = pkg._pkg
        if raw.current_state not in ok_states or raw.inst_state in reinst_required:
            dpkg_broken += 1
        if raw.selected_state == apt_pkg.SELSTATE_HOLD:
            held += 1
        if pkg.is_upgradable:
            is_security = any(o.archive.endswith("-security") for o in pkg.candidate.origins)
            pending["security" if is_security else "other"] += 1

    lines = [
        "# HELP apt_upgrades_pending Installed packages with an available upgrade.",
        "# TYPE apt_upgrades_pending gauge",
    ]
    lines += [f'apt_upgrades_pending{{type="{t}"}} {n}' for t, n in pending.items()]
    lines += [
        "# HELP apt_upgrades_held Packages marked as held with apt-mark hold.",
        "# TYPE apt_upgrades_held gauge",
        f"apt_upgrades_held {held}",
        "# HELP apt_dpkg_broken_packages Packages left half-installed/unconfigured by dpkg.",
        "# TYPE apt_dpkg_broken_packages gauge",
        f"apt_dpkg_broken_packages {dpkg_broken}",
        "# HELP apt_cache_broken_dependencies Packages with unmet dependencies.",
        "# TYPE apt_cache_broken_dependencies gauge",
        f"apt_cache_broken_dependencies {cache.broken_count}",
    ]
    return lines


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(f"usage: {sys.argv[0]} <textfile collector directory>")
    out_dir = sys.argv[1]

    lines = []
    ok = 1
    for collect in (stamp_metrics, cache_metrics):
        try:
            lines += collect()
        except Exception as e:
            print(f"datalab-apt-metrics: {collect.__name__} failed: {e}", file=sys.stderr)
            ok = 0
    lines += [
        "# HELP apt_metrics_collector_success Whether every apt metrics collector succeeded.",
        "# TYPE apt_metrics_collector_success gauge",
        f"apt_metrics_collector_success {ok}",
        "# HELP apt_metrics_last_run_timestamp_seconds When these apt metrics were collected.",
        "# TYPE apt_metrics_last_run_timestamp_seconds gauge",
        f"apt_metrics_last_run_timestamp_seconds {int(time.time())}",
    ]
    write_atomically(os.path.join(out_dir, OUTPUT_NAME), "\n".join(lines) + "\n")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
