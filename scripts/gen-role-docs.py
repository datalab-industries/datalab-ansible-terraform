#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Generate the variable reference from the roles' argument specs.

Each role in ansible/roles declares the variables it accepts in
meta/argument_specs.yml, which Ansible validates the inventory against at the
start of every run. This script renders those specs as a single page, so the
documentation cannot drift from what the playbook actually validates.

The page is deduplicated by variable rather than split by role: a variable used
by several roles is documented once, listing the roles that use it. Variables
that appear in ansible/inventory.example.yml are listed first, as the settings a
deployment is expected to provide; the rest are defaults, grouped by role.

Run by `make docs`; the output is not committed.
"""

import pathlib
import shutil
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
ROLES = ROOT / "ansible" / "roles"
PLAYBOOK = ROOT / "ansible" / "playbook.yml"
EXAMPLE = ROOT / "ansible" / "inventory.example.yml"
OUT = ROOT / "docs" / "reference"

# Roles whose variables belong together under one heading, with a friendlier
# title and the page that explains them.
GROUPS = {
    "datalab": ("Core deployment", "../configuration.md"),
    "nginx": ("Core deployment", "../configuration.md"),
    "ssl_first_run": ("Core deployment", "../configuration.md"),
    "setup": ("Core deployment", "../configuration.md"),
    "bootstrap_user": ("Core deployment", "../configuration.md"),
    "bootstrap_probe": ("Core deployment", "../configuration.md"),
    "preflight": ("Core deployment", "../configuration.md"),
    "docker": ("Docker and externally managed hosts", "../managed-hosts.md"),
    "borg": ("Backups", "../backups.md"),
    "monitoring": ("Monitoring", "../monitoring.md"),
    "cron_email": ("Emails for failed cron jobs", "../cron-email.md"),
    "cheminventory": ("ChemInventory syncing", "../cheminventory.md"),
    "extras": ("Additional containers", "../extras.md"),
    "fail2ban": ("Hardening", None),
    "ssh_hardening": ("Hardening", None),
    "apt_upgrade": ("Hardening", None),
}
GROUP_ORDER = [
    "Core deployment",
    "Backups",
    "Monitoring",
    "Emails for failed cron jobs",
    "ChemInventory syncing",
    "Additional containers",
    "Docker and externally managed hosts",
    "Hardening",
]


def load_specs() -> dict[str, dict]:
    """Every role's declared options, keyed by role name."""
    specs = {}
    for path in sorted(ROLES.glob("*/meta/argument_specs.yml")):
        entry = (yaml.safe_load(path.read_text()) or {}).get("argument_specs", {})
        main = entry.get("main") or next(iter(entry.values()), {})
        specs[path.parts[-3]] = main
    return specs


def role_defaults(role: str) -> dict:
    path = ROLES / role / "defaults" / "main.yml"
    return (yaml.safe_load(path.read_text()) if path.exists() else {}) or {}


def example_variables() -> list[str]:
    """Variable names in the example inventory, in the order they appear."""
    names, seen = [], set()
    for line in EXAMPLE.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or ":" not in stripped:
            continue
        name = stripped.split(":", 1)[0].strip()
        if name.isidentifier() and name not in seen and not name.startswith("<"):
            seen.add(name)
            names.append(name)
    return names


def as_text(value) -> str:
    if isinstance(value, list):
        return " ".join(str(v).strip() for v in value)
    return str(value or "").strip()


def as_code(value) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, bool):
        return f"`{str(value).lower()}`"
    if isinstance(value, (list, dict)):
        return f"`{yaml.safe_dump(value, default_flow_style=True).strip()}`"
    text = str(value)
    if "{{" in text:
        return "computed"
    return f"`{text}`"


def collect() -> dict[str, dict]:
    """One entry per variable, merging the roles that declare it."""
    specs = load_specs()
    variables: dict[str, dict] = {}
    conflicts = []
    for role, main in specs.items():
        defaults = role_defaults(role)
        for name, option in (main.get("options") or {}).items():
            option = option or {}
            record = {
                "type": option.get("type", "str"),
                "required": bool(option.get("required")),
                "default": option.get("default", defaults.get(name)),
                "description": as_text(option.get("description")),
                "choices": option.get("choices"),
            }
            if name not in variables:
                variables[name] = record | {"roles": [role]}
                continue
            existing = variables[name]
            existing["roles"].append(role)
            existing["required"] = existing["required"] or record["required"]
            if existing["default"] is None:
                existing["default"] = record["default"]
            if record["description"] and record["description"] != existing["description"]:
                conflicts.append((name, existing["roles"][0], role))
    if conflicts:
        for name, first, second in conflicts:
            print(f"'{name}' is described differently in {first} and {second}; make them match")
        sys.exit(1)
    return variables


def table(rows: list[tuple[str, dict]]) -> list[str]:
    lines = [
        "| Variable | Type | Default | Used by | Description |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name, var in rows:
        description = var["description"]
        if var["choices"]:
            description += " One of: " + ", ".join(as_code(c) for c in var["choices"]) + "."
        if var["required"]:
            description = "**Required.** " + description
        cells = [
            f"`{name}`",
            f"`{var['type']}`",
            as_code(var["default"]),
            ", ".join(f"`{r}`" for r in var["roles"]),
            description,
        ]
        lines.append("| " + " | ".join(c.replace("|", r"\|") for c in cells) + " |")
    return lines


def tag_for(roles: list[str], tags: dict[str, list[str]]) -> str:
    for role in roles:
        role_tags = [t for t in tags.get(role, []) if t not in ("setup", "always")]
        if role_tags:
            return role_tags[0]
    return ""


def role_tags() -> dict[str, list[str]]:
    tags: dict[str, list[str]] = {}
    for play in yaml.safe_load(PLAYBOOK.read_text()) or []:
        for role in play.get("roles") or []:
            if isinstance(role, dict) and "role" in role:
                tags.setdefault(role["role"], []).extend(role.get("tags") or [])
    return tags


def main() -> None:
    variables = collect()
    provided = [n for n in example_variables() if n in variables]
    tags = role_tags()

    lines = [
        "---",
        "title: Variables",
        "---",
        "",
        "# Variables",
        "",
        "Every variable the playbooks accept, generated from the roles' argument specs.",
        "Ansible validates your inventory against those specs at the start of every run, including under `--check` and when running a single tag, so a missing or wrongly typed value fails before anything is changed on the server.",
        "",
        "!!! note",
        "    Validation only checks the variables listed here.",
        "    A variable whose name is misspelled is not recognised, so it is silently ignored rather than reported.",
        "",
        "Set these per host in `ansible/inventory.yml`.",
        "See [Configuration](../configuration.md) for how the inventory fits together.",
        "",
        "## Settings you provide",
        "",
        "These appear in `ansible/inventory.example.yml`.",
        "Only `ansible_user`, `api_url` and `app_url` are required; the rest switch on an optional feature, and each feature is skipped entirely unless its settings are given.",
        "",
        *table([(n, variables[n]) for n in provided]),
        "",
        "## Defaults you can override",
        "",
        "Everything else the roles accept, with the value used when you leave it unset.",
        "Most deployments never change these.",
        "A default shown as `computed` is derived from other settings, such as the user or whether rootless Docker is in use.",
        "",
    ]

    rest = {n: v for n, v in variables.items() if n not in provided}
    grouped: dict[str, list[tuple[str, dict]]] = {}
    for name, var in sorted(rest.items()):
        group = GROUPS.get(var["roles"][0], ("Core deployment", None))[0]
        grouped.setdefault(group, []).append((name, var))

    for group in GROUP_ORDER:
        rows = grouped.get(group)
        if not rows:
            continue
        page = next(
            (GROUPS[r][1] for _, v in rows for r in v["roles"] if GROUPS.get(r, (None, None))[1]),
            None,
        )
        lines += [f"### {group}", ""]
        tag = tag_for(rows[0][1]["roles"], tags)
        context = []
        if page:
            context.append(f"See [the {group.lower()} page]({page}).")
        if tag:
            context.append(f"Run these tasks on their own with `make {tag}`.")
        if context:
            lines += [" ".join(context), ""]
        lines += table(rows) + [""]

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "index.md").write_text("\n".join(lines))
    print(f"Wrote {len(variables)} variables ({len(provided)} set per deployment) to {OUT.relative_to(ROOT)}/index.md")


if __name__ == "__main__":
    main()
