#!/bin/bash
# Apply local patches to the source checkouts in src/.
#
# Patches live in src/patches/<name>/*.patch and are applied, in filename order,
# to the checkout at src/<name> (e.g. src/patches/datalab/ -> src/datalab).
# Patches that are already applied are skipped, so this is safe to re-run.
# Any patch that does not apply cleanly aborts the whole run with a non-zero exit code.
#
# Usage:
#   ./apply-patches.sh [--revert] [<name>...]
#
#   --revert   un-apply the patches instead (in reverse order)
#   <name>     only handle the patches for these checkouts (default: all of src/patches/*)
#
# The playbook uses this to patch a temporary copy of src/datalab before syncing it to
# the server; the locations can be overridden with the PATCHES_ROOT (default: src/patches)
# and SOURCE_ROOT (default: src) environment variables.
set -e -u -o pipefail
shopt -s nullglob

PATCHES_ROOT="${PATCHES_ROOT:-src/patches}"
SOURCE_ROOT="${SOURCE_ROOT:-src}"

revert=false
names=()
for arg in "$@"; do
    case "$arg" in
        --revert) revert=true ;;
        -*)
            echo "Usage: $0 [--revert] [<name>...]"
            exit 1
            ;;
        *) names+=("$arg") ;;
    esac
done

if [ ! -d "$PATCHES_ROOT" ]; then
    echo "No $PATCHES_ROOT directory found; nothing to do."
    exit 0
fi

if [ ${#names[@]} -eq 0 ]; then
    for patch_dir in "$PATCHES_ROOT"/*/; do
        names+=("$(basename "$patch_dir")")
    done
fi

for name in "${names[@]}"; do
    patch_dir="$PATCHES_ROOT/$name"
    target="$SOURCE_ROOT/$name"
    patches=("$patch_dir"/*.patch)
    if [ ${#patches[@]} -eq 0 ]; then
        continue
    fi
    if [ ! -d "$target" ]; then
        echo "Error: patches found for '$name' but $target does not exist."
        exit 1
    fi

    if [ "$revert" = true ]; then
        mapfile -t patches < <(printf '%s\n' "${patches[@]}" | sort -r)
    fi

    for patch in "${patches[@]}"; do
        patch_path=$(realpath "$patch")
        label="$name/$(basename "$patch")"
        if [ "$revert" = true ]; then
            if git -C "$target" apply --check --reverse "$patch_path" 2>/dev/null; then
                git -C "$target" apply --reverse "$patch_path"
                echo "Reverted  $label"
            else
                echo "Skipping  $label (not applied)"
            fi
        else
            if git -C "$target" apply --check --reverse "$patch_path" 2>/dev/null; then
                echo "Skipping  $label (already applied)"
            elif git -C "$target" apply --check "$patch_path" 2>/dev/null; then
                git -C "$target" apply "$patch_path"
                echo "Applied   $label"
            else
                echo "Error: $label does not apply cleanly to $target:" >&2
                git -C "$target" apply --check "$patch_path" || true
                echo "If files 'already exist', the patch is partially applied (e.g. the checkout was" >&2
                echo "reset or updated but new files were left behind): remove those files and re-run." >&2
                echo "Otherwise, regenerate the patch against the current version of $target." >&2
                exit 1
            fi
        fi
    done
done
