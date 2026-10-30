"""Ansible callback that records each run of a datalab deployment playbook.

Every run of `<repo>/ansible/playbook.yml` appends a `start` record to
`runs/<repo>.jsonl` in this meta repo (git state of the deployment repo, datalab
and upstream ansible versions, tags), and a `finish` record once the play recap
is reached (status plus a few details learned from the hosts). A run with a
`start` but no `finish` record was interrupted and is treated as failed.

Enable via ~/.ansible.cfg:

    [defaults]
    callback_plugins = ~/repos/datalab/deployments-meta/callback_plugins
    callbacks_enabled = deployment_ledger

Set DEPLOYMENT_LEDGER_DIR to write records elsewhere. Recording never fails a run.
"""

from __future__ import annotations

import datetime
import getpass
import json
import os
import subprocess
import uuid
from pathlib import Path

from ansible import context
from ansible.plugins.callback import CallbackBase

DOCUMENTATION = """
    name: deployment_ledger
    type: notification
    short_description: Record datalab deployment runs to a local ledger
    description:
      - Appends start/finish records for each deployment playbook run to a JSONL file per repo.
    requirements:
      - enable in configuration
"""

# Task names whose output is worth keeping, mapped to the key it is stored under
CAPTURED_TASKS = {"Check Docker Compose version": "compose_version"}
# Inventory variables worth keeping (e.g., so the API can be probed later)
CAPTURED_VARS = ("api_url", "app_url")


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _git(repo: Path, *args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        ).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return None


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "notification"
    CALLBACK_NAME = "deployment_ledger"
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ledger: Path | None = None
        self._run_id: str | None = None
        self._hosts: dict[str, dict] = {}

    def _write(self, record: dict) -> None:
        try:
            self._ledger.parent.mkdir(parents=True, exist_ok=True)
            with self._ledger.open("a") as f:
                f.write(json.dumps(record, sort_keys=True) + "\n")
        except Exception as exc:  # never break a deployment over bookkeeping
            self._display.warning(f"deployment_ledger: could not write record: {exc}")

    def v2_playbook_on_start(self, playbook):
        try:
            self._start(Path(playbook._file_name).resolve())
        except Exception as exc:
            self._display.warning(f"deployment_ledger: not recording this run: {exc}")
            self._ledger = None

    def _start(self, playbook_path: Path) -> None:
        args = context.CLIARGS
        repo = playbook_path.parent.parent
        # Only record deployment repos (<repo>/ansible/playbook.yml), and only real runs
        if playbook_path.name != "playbook.yml" or playbook_path.parent.name != "ansible":
            return
        if args.get("check") or args.get("syntax") or args.get("listtasks") or args.get("listhosts"):
            return

        ledger_dir = Path(
            os.environ.get("DEPLOYMENT_LEDGER_DIR") or Path(__file__).resolve().parent.parent / "runs"
        )
        self._ledger = ledger_dir / f"{repo.name}.jsonl"
        self._run_id = uuid.uuid4().hex[:12]

        dirty = _git(repo, "status", "--porcelain", "--ignore-submodules=none")
        self._write(
            {
                "event": "start",
                "run_id": self._run_id,
                "time": _now(),
                "user": getpass.getuser(),
                "deployment": repo.name,
                "commit": _git(repo, "rev-parse", "HEAD"),
                "branch": _git(repo, "rev-parse", "--abbrev-ref", "HEAD"),
                "dirty_files": [line[3:] for line in dirty.splitlines()] if dirty else [],
                "datalab_version": _git(repo / "src" / "datalab", "describe", "--tags", "--match", "v*"),
                "datalab_commit": _git(repo / "src" / "datalab", "rev-parse", "HEAD"),
                "ansible_upstream_version": _git(repo / "src" / "datalab-ansible-terraform", "describe", "--tags"),
                "tags": sorted(args.get("tags") or []),
                "skip_tags": sorted(args.get("skip_tags") or []),
                "limit": args.get("subset"),
            }
        )

    def v2_playbook_on_play_start(self, play):
        if self._ledger is None:
            return
        try:
            variable_manager = play.get_variable_manager()
            for host in variable_manager._inventory.get_hosts(play.hosts):
                host_vars = variable_manager.get_vars(play=play, host=host)
                info = self._hosts.setdefault(host.get_name(), {})
                for key in CAPTURED_VARS:
                    value = host_vars.get(key)
                    if isinstance(value, str) and "{{" not in value:
                        info[key] = value
        except Exception as exc:
            self._display.warning(f"deployment_ledger: could not read host vars: {exc}")

    def v2_runner_on_ok(self, result):
        if self._ledger is None:
            return
        try:
            info = self._hosts.setdefault(result.host.get_name(), {})
            res = result.result
            facts = res.get("ansible_facts") or {}
            if "ansible_distribution" in facts:
                info["os"] = f"{facts['ansible_distribution']} {facts.get('ansible_distribution_version', '')}".strip()
            key = CAPTURED_TASKS.get(result.task.get_name().split(" : ")[-1])
            if key and res.get("stdout"):
                info[key] = res["stdout"].strip()
        except Exception:
            pass

    def v2_playbook_on_stats(self, stats):
        if self._ledger is None:
            return
        per_host = {host: stats.summarize(host) for host in sorted(stats.processed)}
        failed = any(s["failures"] or s["unreachable"] for s in per_host.values())
        self._write(
            {
                "event": "finish",
                "run_id": self._run_id,
                "time": _now(),
                "status": "failed" if failed else "success",
                "stats": per_host,
                "hosts": self._hosts,
            }
        )
