"""The Claude web skill zips in plugins/ must stay upload-ready:
one skill folder per zip, SKILL.md at its root, valid claude.ai frontmatter."""
import re
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
PLUGINS_DIR = ROOT / "plugins"

NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")


def skill_dirs():
    return sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())


def frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, f"{skill_md}: missing frontmatter"
    return dict(line.split(":", 1) for line in m.group(1).splitlines())


@pytest.mark.parametrize("skill_dir", skill_dirs(), ids=lambda p: p.name)
def test_skill_frontmatter_valid_for_claude_web(skill_dir):
    fm = frontmatter(skill_dir / "SKILL.md")
    name = fm["name"].strip()
    assert NAME_RE.match(name), name
    assert skill_dir.name == name
    desc = fm["description"].strip()
    assert desc and len(desc) <= 1024


@pytest.mark.parametrize("skill_dir", skill_dirs(), ids=lambda p: p.name)
def test_skill_zip_exists_and_is_upload_ready(skill_dir):
    zpath = PLUGINS_DIR / f"{skill_dir.name}.zip"
    assert zpath.is_file(), f"missing {zpath}; run scripts/build_skill_zips.py"
    with zipfile.ZipFile(zpath) as zf:
        names = zf.namelist()
        assert f"{skill_dir.name}/SKILL.md" in names
        # one skill only, nothing outside the skill folder
        assert all(n == f"{skill_dir.name}/SKILL.md" or n.startswith(f"{skill_dir.name}/") for n in names)
        # zip content matches the skill folder on disk
        for f in skill_dir.rglob("*"):
            if f.is_file():
                assert f"{skill_dir.name}/{f.relative_to(skill_dir).as_posix()}" in names
