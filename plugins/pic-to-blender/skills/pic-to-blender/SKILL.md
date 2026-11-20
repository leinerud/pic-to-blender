---
name: pic-to-blender
description: Build a real object in Blender from photos, through the Blender MCP — anything from a cup, chair, bike or car to a house with its garden — with drawings and measurements when there are any, and check it against the photos with renders until it matches. Use whenever the user sends pictures of something and wants it modelled, built, recreated or fixed in Blender ("make this in Blender", "model my chair from these photos", "rita upp huset"), or sends corrections like "the legs are thinner", "move the door", "fönstren ska vara…", even without naming the skill.
---

# Pictures to Blender

Take photos of any object and build it in a live Blender through the **Blender MCP** (`mcp__Blender__*` tools,
mainly `execute_blender_code`). What makes the result good is not modelling skill, it's the loop:
**read the evidence, build from numbers, render from the photo's point of view, compare, fix, repeat**, and treat
every remark from the user as the truth about their object.

## Spend tokens where they show

This work burns tokens fast if done carelessly. Every rule here saves thousands:

- **Code goes in files, not in tool calls.** Write the build script to a file once (next to the `.blend`, or in a
  `scripts/` folder), then run it with a one-line `exec(open(path).read())`. Fix it with a small edit, never by
  resending the whole script.
- **Return a little.** Blender code returns a short dict (counts, a few positions, errors), never mesh data, full
  object lists or `print` dumps. Don't call `get_objects_summary` on a big scene; ask for one collection or one spot.
- **Read only what you need.** `grep` the helper scripts and `references/techniques.md` for the part you need instead
  of reading them whole.
- **Small pictures, few of them.** Check renders at 25 % (480 × 270) of 1–3 views, only of the part that changed. Use
  `scale` on screenshots. Look at a picture once; don't re-read old renders to remember them, write down what you saw.
  Full-size renders are for the user: send them without reading them yourself.
- **One change, one check.** Batch the user's corrections into one script edit and one render round, not one render
  per correction.
- **Long waits in the background** (film renders, exports): a background command, not polling.
- **Short replies**: what changed, what was guessed, the next step.

## 0. Before anything

- **Blender connection.** Call a cheap tool first (`get_blendfile_summary_path_info`). If it can't connect to
  localhost:9876: Blender isn't running, the MCP add-on isn't installed (Preferences → Get Extensions → add the remote
  repository `https://lab.blender.org/`, install "MCP"), or its server isn't started (Preferences → Add-ons → MCP →
  *Start MCP Bridge Server*; port 9876; then *Save Preferences*, or the repository can vanish after a restart). Don't
  edit an open `.blend` from a second, background Blender: the two will overwrite each other.
- **Photos.** You can only use photos you can actually see. Files inside a photo library package (macOS
  `Photos Library.photoslibrary`) usually can't be read: ask the user to drag the images into the chat or export them
  to a folder. Say plainly which photos you couldn't see; never pretend you did.
- **Versions.** Never build over the user's only file. Work in `<name>_v1.0.blend`; for a big change or an experiment
  save a copy (`save_as_mainfile`) such as `<name>_v1.1_<what>.blend`, and say which file is open. Move rejected
  versions to the Trash rather than deleting them for good.
- **Other people's things.** Someone else's home, a person's face or a trademarked product for sale are worth a short
  question about what it's for. The user's own things and public buildings are fine.

## 1. Read the evidence and fix the numbers

Write the key dimensions down as constants before modelling anything. Sources, strongest first:

1. **The user's own measurements** ("the table is 90 × 50", "the gap is 183 cm", a dimensioned sketch). These override
   everything, including your earlier guesses: rebuild around them and move the neighbouring parts.
2. **Drawings** (floor plans, sections, elevations, technical drawings, exploded views). Read the scale from a
   printed dimension, not the paper; crop and enlarge the part you need (`sips -c … --cropOffset … && sips -Z 1300`
   on macOS, or Pillow) and look again. Where a drawing and a photo disagree on the outside, the photo wins.
3. **LiDAR depth and the camera pose** from an AR capture app: real 3D points for heights, widths and door corners.
   See `references/techniques.md` (Reading the evidence).
4. **Photos.** Count everything: parts, panels, holes, screws, slats, spokes, windows, panes, and where each sits
   relative to edges and to each other. Get scale from something of known size in the picture (a door ~2.1 m, a
   storey ~2.7 m, a credit card 85.6 × 54 mm, an A4 sheet, a hand ~19 cm, a car, a standard brick). Note the colour
   and finish of each part separately (matte, glossy, brushed metal, worn wood).
5. **Product pages.** For bought things fetch the real spec and dimensions from the maker's page.
6. **Map / aerial view** for footprints of buildings and lots when nothing better exists.

**Be suspicious of text specs** that contradict the photos or drawings: they may be wrong or AI-written. Point out the
concrete contradictions, offer options, and if the user still wants it, build it in a *new file* so it can be thrown
away.

Write each number's source in a comment next to it (drawing, LiDAR, photo, guessed). Every summary to the user ends with what was estimated and what a photo or a measurement
would settle.

## 2. Build it from scripts, not by hand

Everything is made by Python run through `execute_blender_code`, so it can be rebuilt and corrected:

- **Real-world units: metres, Z up.** Pick an origin that makes sense (the object's base centre, a house corner) and
  axes along its main edges. Keep the numbers as constants at the top of the script.
- **Collections per part or area** under one root named after the object (Seat, Legs, Hardware; or House, Garage,
  Garden). Names in the user's language; they read the Outliner.
- **Data tables for what gets corrected most**: a list of holes, slats, buttons or windows, one row each, so moving one
  is editing a number and rerunning.
- **Idempotent scripts**: each deletes what it made before it builds again, and reads positions it depends on from the
  scene, so it still works after something else moved.
- **Keep long scripts in files** (next to the `.blend` or in a `scripts/` folder) and run them with
  `exec(open(path).read())`.
- **Save after every change** (`bpy.ops.wm.save_mainfile()`), and say so.

Helpers in this skill:

- `scripts/mesh_builder.py`: `MB` (box, skewed box, cylinder, polygon, each with a material, made into one object),
  `mat()`, `coll()`, `clear()`.
- `scripts/trees.py`: real-looking trees and shrubs (oak, birch, rhododendron presets) from recursive branches and
  leaf cards.
- `scripts/check_render.py`: quick check renders from given viewpoints (see step 3).
- `references/techniques.md`: how to do bevels, lathes, booleans, glass, buildings (walls, windows, cladding, roofs,
  gutters, terrain), plants, and the Blender API traps. Read the section for what you're building.

Detail comes in rounds, once the basics stand: proportions first, then the parts the user cares about, then the small
things that make it convincing (bevelled edges, seams, screws, handles, worn edges, the right number of everything).

## 3. Check every change by looking at it

After each change, render from where the user's photo was taken and compare, detail by detail, before you report.
Put the camera where the photo was taken (from its pose, or nudged until the corners line up), with the photo's
field of view and aspect ratio (see `references/techniques.md`, Checking against a photo).
`scripts/check_render.py` makes small renders from given viewpoints without touching the scene's cameras: set
`VIEWS`, `OUT` (a temp folder), `PCT` (25 is enough), exec it, then look at the PNGs side by side with the photo. A viewport
screenshot (`get_screenshot_of_area_as_image`) is quicker for layout checks.

- Keep MCP calls under ~2 minutes (they time out): 2–3 EEVEE views per call. A timeout doesn't stop Blender;
  wait for the file to appear before rendering again.
- Look for what's wrong, not for confirmation: wrong proportions, a count that's off, parts floating or sunk into each
  other, a hole in the wrong place, a light seam between parts, a colour that's off.
- When the user sends a screenshot with an area marked, find the objects there by coordinates (bounding boxes per
  object) before changing anything, and change only what they pointed at.

## 4. Working with the user

- Answer in the user's language, short: what changed, what moved along with it, what was guessed, and one or two
  sensible next steps. Send renders when a picture says more.
- Their corrections are facts about their object ("the frame is white", "there are four screws, not two"). Apply them,
  generalise them to the same thing elsewhere when it's obviously meant, and don't argue from your earlier guess. When
  you removed too much or misread a marked area, say so and put it back.
- Ask only when it changes the result and the evidence can't settle it. Offer the choices.
- Keep their Blender tidy: deselect after scripting (an orange outline or dot is just a selection or an origin), stop
  animation playback (`screen.animation_cancel`) if the view "drives around" (space bar starts it), and explain view
  modes (Z pie: Solid, Material Preview, Rendered).

## 5. Light, renders, films and export

- Light: for outdoor things a sun lamp plus a matching physical sky (`ShaderNodeTexSky`), for small objects a simple
  studio (a large soft key light, a fill, a rim, a seamless backdrop). AgX view transform. Stay in Solid while editing.
- Turntable or fly-by: a camera with a Track To on an empty, keyframed through a few viewpoints, 24 fps, MP4/H.264.
- Quick film: EEVEE. Realistic: Cycles on the GPU, 128 samples, adaptive, denoise, no motion blur. Start long renders
  in the user's Blender with `bpy.ops.render.render('INVOKE_DEFAULT', animation=True)` and a `render_post` handler that
  writes progress to a file, and wait for it in the background rather than blocking.
- Export when asked: glTF (`.glb`) for the web and game engines, FBX for Unity/Unreal, STL/3MF for 3D printing (then
  check the mesh is closed and manifold, and the scale is in millimetres as the slicer expects), USDZ for AR on iPhone.
  Apply modifiers on export, and keep the polygon count sensible for where it's going.
