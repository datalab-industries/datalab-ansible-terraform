"""Combine a base pyproject.toml with plugin dependencies from plugins.toml.

Produces a combined pyproject.toml suitable for `uv lock` outside of a git repo.

Uses only stdlib tomllib for reading; writes output via targeted text
manipulation on the original file to preserve formatting.

Usage:
    python scripts/combine_pyproject.py \
        --base src/datalab/pydatalab/pyproject.toml \
        --plugins src/plugins/plugins.toml \
        --output src/build/pyproject.toml
"""

from __future__ import annotations

import argparse
import re
import tomllib
from pathlib import Path


def load_toml(path: Path) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def format_toml_list(items: list[str], indent: str = "    ") -> str:
    """Format a list of strings as a TOML inline array (one item per line)."""
    if not items:
        return "[]"
    inner = ",\n".join(f'{indent}"{item}"' for item in items)
    return f"[\n{inner},\n]"


def format_uv_source(name: str, attrs: dict) -> str:
    """Format a single [tool.uv.sources] entry as TOML."""
    parts = []
    for key, val in attrs.items():
        if isinstance(val, bool):
            parts.append(f'{key} = {"true" if val else "false"}')
        else:
            parts.append(f'{key} = "{val}"')
    return f'{name} = {{ {", ".join(parts)} }}'


def combine(base_path: Path, plugins_path: Path) -> str:
    plugins = load_toml(plugins_path)
    plugin_deps = plugins.get("dependencies", [])
    plugin_sources = plugins.get("tool", {}).get("uv", {}).get("sources", {})

    text = base_path.read_text()

    # 1. Neutralise dynamic = ["version"] -> static version = "0.0.0"
    text = re.sub(
        r'^dynamic\s*=\s*\["version"\]\s*$',
        'version = "0.0.0"',
        text,
        flags=re.MULTILINE,
    )

    # 2. Remove [tool.setuptools_scm] section
    text = re.sub(
        r'^\[tool\.setuptools_scm\]\n(?:(?!\[)[^\n]*\n)*',
        "",
        text,
        flags=re.MULTILINE,
    )

    # 3. Merge app-plugins-git deps into app-plugins-deploy and remove app-plugins-git
    #    The upstream app-plugins-git extra causes circular deps when locking outside
    #    the git repo (plugins depend back on datalab-server). We fold those deps into
    #    app-plugins-deploy so they're still installed via --all-extras.
    base_data = load_toml(base_path)
    base_optional = base_data.get("project", {}).get("optional-dependencies", {})
    git_plugin_deps = base_optional.get("app-plugins-git", [])
    combined_plugin_deps = list(dict.fromkeys(git_plugin_deps + plugin_deps))
    deploy_extra_line = f"app-plugins-deploy = {format_toml_list(combined_plugin_deps)}"

    # Remove the app-plugins-git block (key + array, possibly with comments)
    text = re.sub(
        r'^app-plugins-git\s*=\s*\[.*?\]\s*\n\n?',
        "",
        text,
        count=1,
        flags=re.MULTILINE | re.DOTALL,
    )

    # Build new 'all' extra, replacing app-plugins-git ref with app-plugins-deploy
    deploy_ref = "datalab-server[app-plugins-deploy]"
    base_all = base_optional.get("all", [])
    new_all = []
    for item in base_all:
        if "app-plugins-git" in item:
            new_all.append(deploy_ref)
        else:
            new_all.append(item)
    if deploy_ref not in new_all:
        new_all.append(deploy_ref)
    new_all_line = "all = [" + ", ".join(f'"{item}"' for item in new_all) + "]"

    # Insert app-plugins-deploy before 'all' and replace 'all' line
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if re.match(r'^all\s*=\s*\[', line):
            lines[i] = deploy_extra_line + "\n" + new_all_line
            break
    text = "\n".join(lines)

    # 5. Merge plugin uv sources into [tool.uv.sources]
    if plugin_sources:
        source_lines = "\n".join(
            format_uv_source(name, attrs) for name, attrs in plugin_sources.items()
        )
        # Append after existing [tool.uv.sources] entries
        text = re.sub(
            r'(\[tool\.uv\.sources\]\n(?:(?!\[)[^\n]*\n)*)',
            r"\1" + source_lines + "\n",
            text,
            count=1,
            flags=re.MULTILINE,
        )

    return text


def main():
    parser = argparse.ArgumentParser(
        description="Combine base pyproject.toml with plugin dependencies"
    )
    parser.add_argument("--base", required=True, type=Path, help="Path to base pyproject.toml")
    parser.add_argument("--plugins", required=True, type=Path, help="Path to plugins.toml")
    parser.add_argument("--output", required=True, type=Path, help="Output path for combined TOML")
    args = parser.parse_args()

    combined = combine(args.base, args.plugins)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(combined)

    print(f"Combined pyproject.toml written to {args.output}")


if __name__ == "__main__":
    main()
