# Contributing

Thanks for helping make pic-to-blender better. The best contributions come from real builds: you modelled something
from photos, hit a problem, and found what works.

## What helps most

- **A technique** for a kind of object that isn't covered yet (cars, clothes, upholstered furniture, pottery, mechanical
  parts): add a section to `references/techniques.md` with what to do and the traps you hit.
- **A helper script** that's reusable on any object (like `trees.py`): put it in `scripts/`, start it with a comment
  saying what it builds and how to run it, and mention it in `SKILL.md` section 2.
- **A fix** to something in `SKILL.md` that led Claude the wrong way. Say in the pull request what happened.

## Rules

- **Keep `SKILL.md` short.** It's loaded every time the skill runs, so every line costs tokens for every user. Detail
  goes in `references/` or `scripts/`, and `SKILL.md` points to it.
- **Keep it general.** No personal data, addresses, photos of people or homes, or project-specific paths. Example
  scripts must work without a particular `.blend`.
- **Test it.** Run your script in a real Blender (4.2+) through the MCP before sending it, and say what you built.
- **No new dependencies.** Plain `bpy`, `bmesh` and `mathutils`.
- **Bump the version** in both `plugins/pic-to-blender/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
  (0.1.0 → 0.1.1 for a fix, 0.2.0 for something new), so installed copies update.

## How

1. Fork the repo and make a branch.
2. Make your change. To try it, add your fork as a marketplace in Claude Code:
   `/plugin marketplace add ./path/to/your/clone`, then `/plugin install pic-to-blender@pic-to-blender`.
3. Open a pull request saying what you changed and what you built to test it.
