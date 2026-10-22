# pic-to-blender

A Claude skill: send Claude photos of any object (a cup, a chair, a bike, a house with its garden) and it builds the
object in Blender. Then it renders the model from the same angles as your photos, compares, and fixes it until it
matches. Your measurements and corrections ("the legs are thinner", "there are four screws") always win.

## Install

In Claude Code:

```
/plugin marketplace add leinerud/pic-to-blender
/plugin install pic-to-blender@pic-to-blender
```

Without the plugin system, copy `plugins/pic-to-blender/skills/pic-to-blender/` into `~/.claude/skills/`. In the Claude
app, zip that folder and upload it under Settings → Capabilities → Skills.

## You also need

- Blender 4.2 or newer, running.
- The Blender MCP add-on: in Blender, Preferences → Get Extensions → add the remote repository
  `https://lab.blender.org/`, install "MCP", then Preferences → Add-ons → MCP → *Start MCP Bridge Server* (port 9876)
  and *Save Preferences*.
- The Blender MCP server connected to Claude.

Then drag in your photos and say "build this in Blender".

## What's in it

| Path (under `plugins/pic-to-blender/skills/pic-to-blender/`) | What it is |
|---|---|
| `SKILL.md` | The workflow: read the evidence, build from numbers, render from the photo's angle, compare, fix |
| `references/techniques.md` | How to do bevels, lathes, booleans, glass, buildings, plants, and Blender API traps |
| `scripts/mesh_builder.py` | Helper that builds boxes, cylinders and polygons with materials into one object |
| `scripts/trees.py` | Real-looking trees and shrubs (oak, birch, rhododendron) |
| `scripts/check_render.py` | Small check renders from given viewpoints, without touching the scene's cameras |

## Contributing

Improvements are very welcome, especially new techniques for kinds of objects the skill doesn't cover well yet. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT, see [LICENSE](LICENSE).
