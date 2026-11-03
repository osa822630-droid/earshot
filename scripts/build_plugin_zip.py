#!/usr/bin/env python3
"""Package ALL agent skills in `skills/` into ONE upload-ready plugin .zip for Claude web (claude.ai).

Claude web (claude.ai) has no marketplace or CLI: you add skills by uploading a .zip via
Settings -> Capabilities -> Skills -> Upload skill. A zip may contain several skill folders;
each must have its SKILL.md at the folder root.

This script builds a single plugin file:

    plugins/earshot-plugin.zip
        earshot/SKILL.md
        real-sound/SKILL.md
        real-sound/references/..., scripts/..., templates/...

It also validates every SKILL.md frontmatter against the claude.ai constraints
(name: lowercase letters/numbers/hyphens, max 64 chars, equals the folder name;
description: max 1024 chars).

Usage:
    python scripts/build_plugin_zip.py
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
OUT_PATH = ROOT / "plugins" / "earshot-plugin.zip"

NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
MAX_DESCRIPTION = 1024


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise ValueError(f"{skill_md}: missing YAML frontmatter (--- ... ---)")
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip()
    return fm


def validate_skill(skill_dir: Path) -> str:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        raise ValueError(f"{skill_dir}: no SKILL.md at the skill root")
    fm = parse_frontmatter(skill_md)
    name = fm.get("name", "")
    if not NAME_RE.match(name):
        raise ValueError(f"{skill_md}: invalid skill name {name!r} (lowercase letters/numbers/hyphens, <=64 chars)")
    if skill_dir.name != name:
        raise ValueError(f"{skill_dir}: folder name {skill_dir.name!r} must equal the frontmatter name {name!r}")
    desc = fm.get("description", "")
    if not desc:
        raise ValueError(f"{skill_md}: missing description")
    if len(desc) > MAX_DESCRIPTION:
        raise ValueError(f"{skill_md}: description is {len(desc)} chars, max {MAX_DESCRIPTION}")
    return name


def main() -> int:
    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())
    if not skill_dirs:
        print("no skills found in skills/", file=sys.stderr)
        return 1
    names = [validate_skill(d) for d in skill_dirs]
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(OUT_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for skill_dir in skill_dirs:
            for f in sorted(skill_dir.rglob("*")):
                if f.is_file():
                    # skill folders at the zip root, e.g. earshot/SKILL.md
                    zf.write(f, arcname=f"{skill_dir.name}/{f.relative_to(skill_dir).as_posix()}")
                    count += 1
    print(f"built {OUT_PATH.relative_to(ROOT)} (skills: {', '.join(names)}; "
          f"{count} files, {OUT_PATH.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
