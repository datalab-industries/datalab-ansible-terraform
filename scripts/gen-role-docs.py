#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Generate the variable reference from the playbook's argument spec.

Every setting the playbook accepts is declared in one file,
ansible/roles/common/meta/argument_specs.yml, which Ansible validates the
inventory against at the start of every run, and its defaults are set in
ansible/roles/common/defaults/main.yml. This script renders the two as a single
page, so the documentation cannot drift from what the playbook validates.

Variables that appear in ansible/inventory.example.yml are listed first, as the
settings a deployment is expected to provide. The rest are grouped by the
section comments (e.g. `# Backups`) in the argument spec.

Run by `make docs`; the output is not committed.
"""

import pathlib
import re
import shutil

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEC = ROOT / "ansible" / "roles" / "common" / "meta" / "argument_specs.yml"
DEFAULTS = ROOT / "ansible" / "roles" / "common" / "defaults" / "main.yml"
EXAMPLE = ROOT / "ansible" / "inventory.example.yml"
OUT = ROOT / "docs" / "reference"

# For each section of the argument spec: the page that explains it, as (title,
# path), and the `make` target that runs its tasks on their own. Sections are
# listed in the order they appear in the spec.
SECTIONS = {
    "Core deployment": (("Configuration", "../configuration.md"), None),
    "Docker and externally managed hosts": (("Rootless Docker and managed hosts", "../managed-hosts.md"), None),
    "Backups": (("Backups", "../backups.md"), "borg"),
    "Monitoring": (("Monitoring", "../monitoring.md"), "monitoring"),
    "Emails for failed cron jobs": (("Emails for failed cron jobs", "../cron-email.md"), "cron_email"),
    "ChemInventory syncing": (("ChemInventory syncing", "../cheminventory.md"), "cheminventory"),
    "Additional containers": (("Additional containers", "../extras.md"), "extras"),
    "Hardening and system upgrades": (None, None),
}


def sections() -> dict[str, str]:
    """The section of each option, from the `# Section` comments in the spec."""
    found, current = {}, None
    for line in SPEC.read_text().splitlines():
        if re.match(r"^  \w+:$", line) and found:
            break  # the next entry point repeats some options
        if comment := re.match(r"^      # (.+)$", line):
            current = comment.group(1)
        elif option := re.match(r"^      (\w+):$", line):
            found[option.group(1)] = current
    unknown = set(found.values()) - set(SECTIONS)
    if unknown:
        raise SystemExit(f"Unknown sections in {SPEC.name}: {', '.join(sorted(map(str, unknown)))}; add them to SECTIONS")
    return found


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


# Longer list and dict defaults are shown as a YAML block under the table, as a
# table cell can only hold a single line.
INLINE_LIMIT = 60


def inline_yaml(value) -> str:
    """A list or dict as one line of flow-style YAML, in its original order."""
    return yaml.safe_dump(value, default_flow_style=True, sort_keys=False, width=float("inf")).strip()


def is_block(value) -> bool:
    """Whether a default is too long or complex to show inline in the table."""
    if not isinstance(value, (list, dict)):
        return False
    text = inline_yaml(value)
    return len(text) > INLINE_LIMIT or "`" in text


class IndentedDumper(yaml.SafeDumper):
    """Indents list items under their key, as in the playbooks' own YAML."""

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def block_anchor(name: str) -> str:
    return f"default-{name.replace('_', '-')}"


def as_code(value) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, bool):
        return f"`{str(value).lower()}`"
    if isinstance(value, (list, dict)):
        return f"`{inline_yaml(value)}`"
    text = str(value)
    if "{{" in text:
        return "computed"
    return f"`{text}`"


def default_blocks(rows: list[tuple[str, dict]]) -> list[str]:
    """The long defaults of a table, as YAML that can be pasted into the inventory."""
    lines = []
    for name, var in rows:
        if not is_block(var["default"]):
            continue
        body = yaml.dump(
            {name: var["default"]}, Dumper=IndentedDumper, default_flow_style=False, sort_keys=False, width=100
        )
        lines += [
            f'<a id="{block_anchor(name)}"></a>',
            f'??? example "Default for `{name}`"',
            "",
            "    ```yaml",
            *(f"    {line}" if line else "" for line in body.rstrip().splitlines()),
            "    ```",
            "",
        ]
    return lines


def collect() -> dict[str, dict]:
    """One entry per variable, in the order of the spec."""
    options = yaml.safe_load(SPEC.read_text())["argument_specs"]["main"]["options"]
    defaults = yaml.safe_load(DEFAULTS.read_text()) or {}
    section = sections()
    return {
        name: {
            "type": option.get("type", "str"),
            "required": bool(option.get("required")),
            "default": defaults.get(name),
            "description": as_text(option.get("description")),
            "choices": option.get("choices"),
            "section": section[name],
        }
        for name, option in options.items()
    }


def table(rows: list[tuple[str, dict]]) -> list[str]:
    lines = [
        "| Variable | Type | Default | Description |",
        "| --- | --- | --- | --- |",
    ]
    for name, var in rows:
        description = var["description"]
        if var["choices"]:
            description += " One of: " + ", ".join(as_code(c) for c in var["choices"]) + "."
        if var["required"]:
            description = "**Required.** " + description
        default = var["default"]
        cells = [
            f"`{name}`",
            f"`{var['type']}`",
            f"[see below](#{block_anchor(name)})" if is_block(default) else as_code(default),
            description,
        ]
        lines.append("| " + " | ".join(c.replace("|", r"\|") for c in cells) + " |")
    return lines


def main() -> None:
    variables = collect()
    provided = [n for n in example_variables() if n in variables]

    lines = [
        "---",
        "title: Variables",
        "---",
        "",
        "# Variables",
        "",
        "Every variable the playbook accepts, generated from its argument spec in `ansible/roles/common/meta/argument_specs.yml`.",
        "Ansible validates the inventory against it at the start of every run, including under `--check` and when running a single tag, so a missing or wrongly typed value fails before anything is changed on the server.",
        "",
        "!!! note",
        "    Validation only checks the variables listed here.",
        "    A variable whose name is misspelled is not recognised, so it is silently ignored rather than reported.",
        "",
        "Set these per host in `ansible/inventory.yml`.",
        "See [Configuration](../configuration.md) for how the inventory fits together.",
        "",
        "## Per-deployment settings",
        "",
        "The settings in `ansible/inventory.example.yml`.",
        "Only `ansible_user`, `api_url` and `app_url` are required; the others each enable an optional feature, which is skipped unless its settings are given.",
        "",
        *table([(n, variables[n]) for n in provided]),
        "",
        *default_blocks([(n, variables[n]) for n in provided]),
        "## Defaults",
        "",
        "All other variables, with the value used when unset.",
        "A default shown as `computed` is derived from other settings, such as the user or whether rootless Docker is in use.",
        "",
    ]

    rest = {n: v for n, v in variables.items() if n not in provided}
    grouped: dict[str, list[tuple[str, dict]]] = {}
    for name, var in sorted(rest.items()):
        grouped.setdefault(var["section"], []).append((name, var))

    for group, (page, tag) in SECTIONS.items():
        rows = grouped.get(group)
        if not rows:
            continue
        lines += [f"### {group}", ""]
        context = []
        if page:
            context.append(f"See [{page[0]}]({page[1]}).")
        if tag:
            context.append(f"Run these tasks on their own with `make {tag}`.")
        if context:
            lines += [" ".join(context), ""]
        lines += table(rows) + [""] + default_blocks(rows)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "index.md").write_text("\n".join(lines))
    print(f"Wrote {len(variables)} variables ({len(provided)} set per deployment) to {OUT.relative_to(ROOT)}/index.md")


if __name__ == "__main__":
    main()
