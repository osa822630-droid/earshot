# Claude web plugin zip (ملف البلوجين للرفع على Claude web)

`earshot-plugin.zip` is the **Claude web (claude.ai)** distribution of this repo: ONE plugin file that
contains ALL the agent skills from `skills/`, each in its own folder at the zip root:

```
earshot-plugin.zip
├── earshot/SKILL.md                  how an agent should listen with earshot
└── real-sound/                       premium realistic soundtracks from real licensed recordings
    ├── SKILL.md
    ├── references/
    ├── scripts/
    └── templates/
```

## How to install on Claude web (claude.ai)

1. Download **`earshot-plugin.zip`** from this folder (click the file → **Download raw file**, or from a release).
2. Open https://claude.ai → **Settings → Capabilities → Skills → Upload skill**.
3. Pick the downloaded `earshot-plugin.zip`. Both skills appear in your skills list and Claude can invoke
   them automatically when a task needs them.

Notes:
- Skills uploaded on claude.ai are instruction/reference bundles — they do not run the Python scripts
  locally. On claude.ai the skills tell Claude how to reason about sound with the tools available there;
  to actually *run* earshot (CLI / MCP / Python) install the package on a machine and use the skills there
  (see the repo README, "Agent skills"). `real-sound` is meant for agent environments that can execute its
  scripts (Claude Code / local agents).
- Rebuild the plugin after editing `skills/` with: `python scripts/build_plugin_zip.py`
