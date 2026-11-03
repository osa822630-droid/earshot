#!/usr/bin/env python3
"""Package the agent skills in `skills/` into upload-ready .zip files for Claude web (claude.ai).

Claude web (claude.ai) has no marketplace or CLI: you add a skill by uploading a .zip that contains
one skill folder (with SKILL.md at its root) via Settings -> Capabilities -> Skills -> Upload skill.

This script builds one such zip per skill into `plugins/`:

    plugins/earshot.zip        -> contains earshot/SKILL.md
    plugins/real-sound.zip     -> contains real-sound/SKILL.md, references/, scripts/, templates/

It also validates the SKILL.md frontmatter against the claude.ai constraints
(name: lowercase letters/numbers/hyphens, max 64 chars; description: max 1024 chars).

Usage:
    python scripts/build_skill_zips.py            # build all skills
    python scripts/build_skill_zips.py earshot     # build one skill
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
OUT_DIR = ROOT / "plugins"

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


def build_zip(skill_dir: Path, out_path: Path) -> int:
    name = validate_skill(skill_dir)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(skill_dir.rglob("*")):
            if f.is_file():
                # skill folder at the zip root, e.g. earshot/SKILL.md
                zf.write(f, arcname=f.relative_to(skill_dir.parent).as_posix())
                count += 1
    print(f"built {out_path.relative_to(ROOT)} ({name}, {count} files, {out_path.stat().st_size} bytes)")
    return count


def main(argv: list[str]) -> int:
    wanted = argv[1:]
    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())
    if wanted:
        skill_dirs = [p for p in skill_dirs if p.name in wanted]
        missing = set(wanted) - {p.name for p in skill_dirs}
        if missing:
            print(f"unknown skill(s): {', '.join(sorted(missing))}", file=sys.stderr)
            return 2
    if not skill_dirs:
        print("no skills found", file=sys.stderr)
        return 1
    for skill_dir in skill_dirs:
        build_zip(skill_dir, OUT_DIR / f"{skill_dir.name}.zip")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
