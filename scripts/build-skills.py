#!/usr/bin/env python3
"""Build installable skill packages from canonical harness sources.

agentic-foundry is canonical-first: `harnesses/<name>/canonical/` is the semantic source of
truth, and the adapter under `harnesses/<name>/adapters/<runtime>/` is thin, hand-authored,
and owns provider concerns only. This script compiles those two into a self-contained,
committed package under `skills/<name>/` that a user can install or vendor.

    python3 scripts/build-skills.py            # write the package
    python3 scripts/build-skills.py --check     # fail if committed output is stale

Generated files are committed on purpose — that is what makes the package installable without
a build step on the consumer's machine. `--check` is what keeps them honest. Wire it to CI;
a drift check nobody runs is the drift it was meant to catch.

Never edit anything under skills/ directly. Edit the canonical source or the adapter source
and re-run this.
"""

from __future__ import annotations

import argparse
import difflib
import os.path
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

BANNER = (
    "<!-- GENERATED FILE — DO NOT EDIT.\n"
    "     Built by scripts/build-skills.py from {source}\n"
    "     Edit that file and re-run the build. Direct edits here are lost and will\n"
    "     fail `python3 scripts/build-skills.py --check`. -->\n"
)

# Markdown link targets that stay linked inside a package: in-page anchors, absolute URLs,
# and siblings that the package actually ships. Everything else is delinked to plain text,
# because a relative link that escapes the package directory resolves on the author's
# machine and 404s on the installer's.
LINK_RE = re.compile(r"\[([^\]\n]*)\]\(([^)\s]+)\)")

# Delinking alone leaves prose pointing at `../adapters/`, which reads as a path relative to
# the installed package and resolves to nothing. Known escaping targets get honest prose
# instead. An unlisted target still delinks to its bare label and is reported by the build.
LABEL_REWRITES = {
    "../adapters/": "the harness's runtime adapters",
    "./portable-prompt.md": "the harness's portable copy-paste prompt",
}

# Targets that live elsewhere in the source tree but are shipped into the package as siblings.
# Rewritten to the packaged filename so the same link resolves in both layouts, instead of
# being delinked as an escaping path.
LINK_TARGET_REWRITES = {
    "../knowledgebase/examples/PM-EXAMPLE-backfill-wrong-database.md": (
        "PM-EXAMPLE-backfill-wrong-database.md"
    ),
}


class Package:
    """One installable skill package compiled from canonical + adapter sources."""

    def __init__(self, name: str, adapter: str, canonical: dict[str, str]) -> None:
        self.name = name
        self.adapter = REPO / adapter
        # packaged relative path -> canonical source path
        self.canonical = {k: REPO / v for k, v in canonical.items()}
        self.out = REPO / "skills" / name

    @property
    def shipped(self) -> set[str]:
        return {Path(p).name for p in self.canonical}


PACKAGES = [
    Package(
        name="postmortem",
        adapter="harnesses/postmortem/adapters/claude-code/postmortem/SKILL.md",
        canonical={
            "references/postmortem-record.md": "harnesses/postmortem/canonical/postmortem-record.md",
            "references/reference.md": "harnesses/postmortem/canonical/reference.md",
            "references/PM-EXAMPLE-backfill-wrong-database.md": (
                "harnesses/postmortem/knowledgebase/examples/PM-EXAMPLE-backfill-wrong-database.md"
            ),
        },
    )
]


def split_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter_block_including_delimiters, body). Empty frontmatter if absent."""
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[: end + 5], text[end + 5 :]


def delink_escaping(text: str, shipped: set[str], report: list[str]) -> str:
    """Strip relative markdown links that would not resolve inside the package."""

    def repl(m: re.Match[str]) -> str:
        label, target = m.group(1), m.group(2)
        if target.startswith(("#", "http://", "https://", "mailto:")):
            return m.group(0)
        target = LINK_TARGET_REWRITES.get(target, target)
        if Path(target).name in shipped and "/" not in target.lstrip("./"):
            return f"[{label}]({target})"
        report.append(target)
        return LABEL_REWRITES.get(target, label)

    return LINK_RE.sub(repl, text)


def rewrite_adapter_paths(text: str, pkg: Package, report: list[str]) -> str:
    """Point the adapter's repo-relative canonical references at the packaged copies.

    The adapter source deliberately uses in-repo relative paths so it stays readable and
    usable from a checkout. The package needs ${CLAUDE_SKILL_DIR}-anchored paths so it
    resolves wherever it is installed.
    """
    for packaged, source in pkg.canonical.items():
        # the path the adapter source uses in-repo, e.g. ../../../canonical/reference.md
        needle = os.path.relpath(source, pkg.adapter.parent)
        replacement = "${CLAUDE_SKILL_DIR}/" + packaged
        if needle in text:
            report.append(f"{needle} -> {replacement}")
            text = text.replace(needle, replacement)
    return text


def render(pkg: Package) -> tuple[dict[str, str], list[str]]:
    """Return (packaged relative path -> content, human-readable transform notes)."""
    notes: list[str] = []
    files: dict[str, str] = {}

    # --- the adapter becomes the package SKILL.md ---
    raw = pkg.adapter.read_text()
    fm, body = split_frontmatter(raw)
    if not fm:
        sys.exit(f"error: {pkg.adapter} has no YAML frontmatter; refusing to package.")

    rewrites: list[str] = []
    body = rewrite_adapter_paths(body, pkg, rewrites)
    if rewrites:
        notes.append(f"SKILL.md: rewrote {len(rewrites)} canonical path(s) to ${{CLAUDE_SKILL_DIR}}")

    escaped: list[str] = []
    body = delink_escaping(body, pkg.shipped, escaped)
    if escaped:
        notes.append(f"SKILL.md: delinked {len(escaped)} escaping link(s): {sorted(set(escaped))}")

    banner = BANNER.format(source=pkg.adapter.relative_to(REPO))
    files["SKILL.md"] = f"{fm}\n{banner}{body.lstrip(chr(10))}"

    # --- canonical files are copied verbatim, banner-stamped, and self-containment-checked ---
    for packaged, source in pkg.canonical.items():
        text = source.read_text()
        escaped = []
        text = delink_escaping(text, pkg.shipped, escaped)
        if escaped:
            notes.append(f"{packaged}: delinked {len(escaped)} escaping link(s): {sorted(set(escaped))}")
        files[packaged] = BANNER.format(source=source.relative_to(REPO)) + "\n" + text

    return files, notes


def leftover_files(pkg: Package, expected: dict[str, str]) -> list[str]:
    """Committed files under the package that the build no longer produces."""
    if not pkg.out.exists():
        return []
    found = {str(p.relative_to(pkg.out)) for p in pkg.out.rglob("*") if p.is_file()}
    return sorted(found - set(expected))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="verify committed output matches sources; write nothing")
    args = ap.parse_args()

    stale = False
    for pkg in PACKAGES:
        files, notes = render(pkg)
        orphans = leftover_files(pkg, files)

        if args.check:
            for rel, content in files.items():
                target = pkg.out / rel
                current = target.read_text() if target.exists() else None
                if current == content:
                    continue
                stale = True
                if current is None:
                    print(f"MISSING  skills/{pkg.name}/{rel}")
                    continue
                print(f"STALE    skills/{pkg.name}/{rel}")
                diff = difflib.unified_diff(
                    current.splitlines(True), content.splitlines(True),
                    fromfile=f"committed/{rel}", tofile=f"rebuilt/{rel}",
                )
                sys.stdout.writelines(diff)
            for rel in orphans:
                stale = True
                print(f"ORPHAN   skills/{pkg.name}/{rel} (not produced by the build)")
        else:
            for rel, content in files.items():
                target = pkg.out / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content)
            print(f"built skills/{pkg.name}/ ({len(files)} files)")
            for note in notes:
                print(f"  - {note}")
            for rel in orphans:
                print(f"  ! orphan not produced by the build: skills/{pkg.name}/{rel}")

    if args.check:
        if stale:
            print("\nCommitted skill packages are out of date. Run: python3 scripts/build-skills.py")
            return 1
        print("skill packages match canonical sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
