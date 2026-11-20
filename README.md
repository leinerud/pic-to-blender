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

Without the plugin system, copy `plugins/pic-to-blender/skills/pic-to-blender/` into `~/.claude/skills/`.

In the Claude app, download [pic-to-blender.zip](https://github.com/leinerud/pic-to-blender/releases/latest/download/pic-to-blender.zip)
from the latest release and upload it under Settings → Capabilities → Skills. To hear about new versions, use
Watch → Custom → Releases on this page.

## You also need

- Blender 4.2 or newer, running.
- The Blender MCP add-on: in Blender, Preferences → Get Extensions → add the remote repository
  `https://lab.blender.org/`, install "MCP", then Preferences → Add-ons → MCP → *Start MCP Bridge Server* (port 9876)
  and *Save Preferences*.
- The Blender MCP server connected to Claude.

Then drag in your photos and say "build this in Blender".

Optional, but they make a big difference: **drawings** (floor plans, sections, elevations, a dimensioned sketch),
**your own measurements**, and photos from a **phone with LiDAR** through an AR capture app (depth plus where the
phone stood), so sizes are measured instead of guessed.

## How to get the best result

[GUIDE.md](GUIDE.md) walks through the whole process for people: which photos to take, how to use drawings and
LiDAR depth, how the numbers are fixed before anything is built, how the model is checked against your photos, and
how to give corrections.

## Testing it

Thanks for trying it. To make results comparable:

1. **First task:** a mug or a simple chair you own, from three photos (front, side, and a corner at 45°), plus one
   measurement with a ruler or tape. Say "build this in Blender" and give it the photos and the measurement.
2. **Then anything you like**, ideally something with drawings or a LiDAR phone if you have one.
3. **Report each build** with the [Test report](https://github.com/leinerud/pic-to-blender/issues/new?template=test-report.yml)
   form: what you gave it, how well it matched, how long it took, and what went wrong.

## What's in it

| Path (under `plugins/pic-to-blender/skills/pic-to-blender/`) | What it is |
|---|---|
| `SKILL.md` | The workflow Claude follows: read the evidence, build from numbers, render from the photo's angle, compare, fix |
| `references/techniques.md` | How to do bevels, lathes, booleans, glass, buildings, plants, and Blender API traps |
| `scripts/mesh_builder.py` | Helper that builds boxes, cylinders and polygons with materials into one object |
| `scripts/trees.py` | Real-looking trees and shrubs (oak, birch, rhododendron) |
| `scripts/check_render.py` | Small check renders from given viewpoints, without touching the scene's cameras |

## Contributing

Improvements are very welcome, especially new techniques for kinds of objects the skill doesn't cover well yet. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT, see [LICENSE](LICENSE).
