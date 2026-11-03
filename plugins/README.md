# Claude web skill zips (ملفات ready للرفع على Claude web)

These `.zip` files are the **Claude web (claude.ai)** distribution of the agent skills in `skills/`.
Claude web has no CLI or marketplace — you add a skill by uploading a zip. Each zip contains one skill
folder with its `SKILL.md` at the root, exactly the layout claude.ai expects.

| file | skill | what it does |
|---|---|---|
| `earshot.zip` | `earshot` | how an agent should listen with earshot: which command answers which question, how to read verdicts, when not to trust them |
| `real-sound.zip` | `real-sound` | full process for premium, realistic soundtracks for code-made films from real licensed recordings |

## How to install on Claude web (claude.ai)

1. Download the zip you want from this folder (click the file → **Download raw file**, or from a release).
2. Open https://claude.ai → **Settings → Capabilities → Skills → Upload skill**.
3. Choose the downloaded `.zip` (e.g. `earshot.zip`). The skill appears in your skills list and Claude
   can invoke it automatically when a task needs it.

Notes:
- One zip = one skill; upload each zip separately if you want both.
- Skills uploaded on claude.ai are instruction/reference bundles — they do not run the Python scripts
  locally. On claude.ai, `earshot.zip` tells Claude how to reason about sound with the tools available
  there; to actually *run* earshot (CLI / MCP / Python) install the package on a machine and use the
  skill there (see the repo README, "Agent skills"). `real-sound.zip` is meant for agent environments
  that can execute its scripts (Claude Code / local agents).
- Rebuild the zips after editing `skills/` with: `python scripts/build_skill_zips.py`
