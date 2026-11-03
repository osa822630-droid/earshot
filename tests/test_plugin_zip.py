"""The Claude web plugin zip in plugins/ must stay upload-ready:
one zip, every skill folder at the root with a valid SKILL.md inside."""
import re
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
ZIP_PATH = ROOT / "plugins" / "earshot-plugin.zip"

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


def test_plugin_zip_exists_and_contains_every_skill():
    assert ZIP_PATH.is_file(), f"missing {ZIP_PATH}; run scripts/build_plugin_zip.py"
    with zipfile.ZipFile(ZIP_PATH) as zf:
        names = zf.namelist()
        for skill_dir in skill_dirs():
            # each skill folder sits at the zip root with its SKILL.md, nothing outside skill folders
            assert f"{skill_dir.name}/SKILL.md" in names
            assert all(n == f"{skill_dir.name}/SKILL.md" or n.startswith(f"{skill_dir.name}/")
                       for n in names if n.startswith(f"{skill_dir.name}/"))
            # zip content matches the skill folder on disk
            for f in skill_dir.rglob("*"):
                if f.is_file():
                    assert f"{skill_dir.name}/{f.relative_to(skill_dir).as_posix()}" in names
        # no stray files outside any skill folder
        tops = {n.split("/", 1)[0] for n in names}
        assert tops == {d.name for d in skill_dirs()}
