# From photos to a Blender model: the process, step by step

This guide is for people. It explains what to collect, what to ask for and what good looks like, so you get the
most out of the skill. The skill (`SKILL.md`) gives Claude the same rules in short form.

The steps work the same for a cup, a chair or a house. The examples are from a building, because buildings
use every step.

The loop matters more than any modelling trick:
**gather evidence → fix the numbers → build from a script → render from where the photo was taken → compare →
fix → repeat.**

---

## What you need

| | Needed? | Notes |
|---|---|---|
| Blender 4.2 or newer, running | yes | |
| Blender MCP add-on | yes | Preferences → Get Extensions → add the remote repository `https://lab.blender.org/` → install **MCP** → Add-ons → MCP → *Start MCP Bridge Server* (port 9876) → *Save Preferences*. |
| Claude with this skill | yes | See the README to install it. |
| Photos | yes | One good photo is enough to start; more photos give a better model. |
| Drawings | if you have them | Floor plans, sections, elevations, a dimensioned sketch, product drawings. These are the best source after your own measurements. |
| A phone with LiDAR and an AR capture app | optional, very useful | Saves a depth map plus the phone's position and lens with each photo, so heights and widths are measured, not guessed. |
| A map footprint | optional, for buildings | Gives the outline and size of the floor plan, from OpenStreetMap or a property map. |
| A tape measure | optional | One real measurement beats any estimate. |

---

## Step 1: Take the right photos

- **Each side straight on**, standing far enough back to get all of it in.
- **Each corner at about 45°**, so two sides and the top show in one picture. These show depth and roof
  shape best.
- **Close-ups** of what you care about: handles, screws, door panels, window frames, gutters, lamps.
- **Something of known size** in the frame: a door (~2.1 m), a brick, a credit card (85.6 × 54 mm), an A4
  sheet.
- **Hold the phone level.** A tilted photo makes vertical edges lean.
- **With LiDAR, stay within about 5 m.** LiDAR doesn't reach further than that, and the depth map goes empty.

> **Privacy:** photos carry GPS in their EXIF data. Strip it before sharing (`exiftool -gps:all= photo.jpg`).
> Model your own things and public buildings, or ask the owner first.

---

## Step 2: Put the evidence in one folder

```
my-object/
  photo-1.jpg             the photos
  photo-1-depth.png       LiDAR depth (e.g. 16-bit grey, millimetres, 0 = no reading), if you have it
  photo-1-pose.json       where the phone stood, which way it faced, and its lens (fx, fy, cx, cy)
  drawings/               plans, sections, elevations, sketches (PDF or images)
  notes.md                what you know: measurements, materials, colours, what you couldn't photograph
  build.py                the Blender script (step 5)
  my-object_v1.0.blend    the model
```

Write what you know in `notes.md` as plain sentences ("the door is black, four horizontal panels").
Claude reads all of it.

---

## Step 3: Fix the numbers before modelling

Every key dimension is written down as a constant **before** anything is built. Use the strongest source you
have:

1. **Your own measurements.** These always win, even over Claude's earlier guesses.
2. **Drawings.** Read the scale from a dimension printed on the drawing, not from the paper size (see below).
3. **LiDAR depth plus the camera pose.** Each depth pixel can be turned into a real 3D point (see below).
4. **A map footprint**, for a building's width and depth.
5. **Counting and proportions in the photos.** Count panels, boards, windows, screws, and use the known sizes in
   the frame for scale.
6. **Standard sizes.** Doors are ~0.9–1.0 × 2.1 m, a storey is 2.6–2.8 m, a single garage door ~2.4 m wide and a
   double one ~4–5 m.

**Write down what was guessed**, for example *"side windows: position and size guessed, not in any photo"*.
Every update from Claude should end with that list, and say which photo or measurement would settle each guess.

### Using drawings

- **Which drawing gives what.** Floor plans give lengths, wall thicknesses, and where doors and windows sit
  along each wall. Sections give heights: floor levels, ceilings, eaves, ridge and roof pitch. Elevations give
  each facade: window sizes and sill heights, cladding direction, roof overhangs.
- **Scale from a printed dimension.** A PDF printed or scanned at another size no longer matches its "1:100".
  Find a dimension line you can read, measure it in pixels, and work out metres per pixel from that.
- **Crop and enlarge** the part you need before reading small numbers (Preview, `sips` on macOS, Pillow).
  Don't guess a blurry figure.
- **Levels.** Section heights are often given against a reference level (e.g. ±0.00 = the ground floor). Pick
  one level as z = 0 in the model and convert every other height to it.
- **Drawings show the plan; photos show what was built.** Buildings get changed: a window moved, a door added, a
  porch built later. When a drawing and a photo disagree, **the photo wins** for the outside. Say so, and keep the
  drawing's version in a note.
- **Fill in what the photos can't show:** the back of a building nobody photographed, the inside of a cabinet,
  the exact roof pitch.

### Using LiDAR depth and the camera pose

With the lens (`fx, fy` = focal length in pixels; `cx, cy` = image centre) and a depth `d` in metres at pixel
`(u, v)`, scaled to the photo's resolution (depth maps are usually much smaller than the photo):

```
X = (u - cx) * d / fx        # right
Y = (cy - v) * d / fy        # up
Z = d                        # forward
```

Rotate and move these points by the phone's pose to put them in the world. Then read off what matters:

- **wall foot → roof edge above it**: the eave height
- **the ridge**: its height, and where across the front it sits (it's often not centred)
- **a door's corners**: its width, height and distance from the corner

Check one number you can verify (a door height) before trusting the rest. Depth is noisy at edges and on glass,
so read a few pixels inside a surface, not right on its edge.

---

## Step 4: Choose a frame

- **Origin**: a corner on the ground (a building), or the centre of the base (a piece of furniture).
- **Axes along the main edges**: for example x along the front, y back, z up.
- **Metres** throughout.

Now "the door starts 0.7 m from the left corner" is simply `x0 = 0.7`, and a drawing's dimension goes
straight into the script.

---

## Step 5: Build from a script, never by hand

Everything is made by one Python file that Claude runs in Blender with `exec(open('build.py').read())`. That
way every correction is a number changed and the script run again.

- **Constants at the top**, each with a comment saying where the number came from (*drawing*, *LiDAR*,
  *photo*, *guessed*).
- **Idempotent**: the script removes what it made last time before building again.
- **One collection per part**: Walls, Roof, Doors & windows, Details, Ground.
- **Tables for what gets corrected most** (windows, panels, slats): one row each.
- **One material per finish**, not per object: white cladding, black trim, matte black roof, glass.
- **Save after every run, and keep versions**: `_v1.0`, `_v1.1_new-roof`. Never build over your only file.

A skeleton using the skill's helpers (`scripts/mesh_builder.py`); the numbers are only an example:

```python
import bpy
exec(open('<skill>/scripts/mesh_builder.py').read())   # MB, mat, coll

W, D = 6.0, 7.0               # footprint: front width, depth (drawing: floor plan)
EAVE = 2.8                    # wall top at the eaves (LiDAR: roof edge over the wall foot)
RIDGE_X, RIDGE = 3.8, 4.0     # ridge across the front, and its height (drawing: section)
DOOR = dict(x0=0.8, x1=5.0, z1=2.2, panels=4)   # LiDAR corners; panels counted in the photo
WINDOWS = [('left', 1.5, 1.5, 0.4, 0.6)]        # (wall, centre, sill, width, height) - GUESSED

white = mat('White cladding', (0.86, 0.87, 0.86), rough=0.7)
black = mat('Black trim', (0.02, 0.02, 0.022), rough=0.45)

root = coll('Building')
for o in list(root.all_objects): bpy.data.objects.remove(o, do_unlink=True)   # start clean
walls = coll('Walls', root)

# walls: the gable outline, pushed back along y
pent = [(0, 0), (W, 0), (W, EAVE), (RIDGE_X, RIDGE), (0, EAVE)]
n = len(pent)
vs = [(x, 0, z) for x, z in pent] + [(x, D, z) for x, z in pent]
faces = [tuple(range(n))[::-1], tuple(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
m = MB(); m.poly(vs, faces, white); m.obj('Walls', walls)
# ...roof, door, windows, trim, ground: one block each, all from the numbers above
```

### Build in passes

1. **Shell**: get the proportions right first. For a building, the walls can be a prism made from the gable
   outline.
2. **Roof**: sloping sheets with overhangs, then fascia boards, soffits, gutters and downpipes.
3. **Openings**: frames, panels, sashes, glass.
4. **Surfaces**: cladding, corner boards, bevels.
5. **Details**: lamps, numbers, handles, thresholds.
6. **Ground**: just enough for the photo comparison.

`references/techniques.md` has the how-to for each of these and the traps people hit.

---

## Step 6: Render from where the photo was taken, and compare

This step is what makes the model match the real thing. After every change:

1. **Put a camera where the photo was taken.** With a pose file, use its position and direction. Turn the lens
   into Blender's focal length: `lens_mm = sensor_width_mm / 2 / tan(horizontal_fov / 2)` (Blender's default sensor
   is 36 mm wide). Set the render's aspect ratio to the photo's (a portrait photo needs a portrait render).
   Without a pose, estimate the camera's position and move it until the corners line up.
2. **Render small**: `scripts/check_render.py` at 25%, EEVEE, at most 2–3 views per check.
3. **Put the photo and the render side by side** in one image, and go through it detail by detail:
   - Do the corners, eaves and ridge line up?
   - Is every count right (panels, boards, windows, screws)?
   - Is anything floating, or sunk into something else?
   - Are there light seams between parts?
   - Is a colour or finish off (glossy vs matte)?
4. Fix the numbers in `build.py`, run it again, render again. Look for **what's wrong**, not for confirmation.

---

## Step 7: Corrections

Your remarks are facts about your object: "the corner boards are black", "the door has four panels, not
five". Claude applies each one to the numbers, wherever it obviously belongs (all four corners, not one), and
checks it with a render.

Group several corrections into **one** message. That means one script edit and one render round, which is faster
and cheaper than one round per remark.

---

## Step 8 (optional): Light, film and export

- **Light**: a sun lamp plus a matching sky for outdoors, a simple studio for small objects, AgX view
  transform.
- **Final render**: Cycles on the GPU, ~128 samples, denoised.
- **Export**: `.glb` for the web and game engines, FBX for Unity/Unreal, USDZ for AR on an iPhone, STL/3MF for
  3D printing.

---

## Prompts that work

```
Here are photos and the drawings of my garage in ./my-garage. Build it in my open Blender.
Read the numbers from the drawings and the LiDAR depth first, write them as constants
at the top of ./my-garage/build.py with where each came from, and tell me what you guessed.
```

```
Render it from where photo-1 was taken, put it side by side with the photo,
and list what doesn't match.
```

```
Corrections: the corner boards are black, the door is 4.4 m wide and starts 0.7 m
from the left corner, the ridge is off-centre towards the right. One edit, one render.
```

---

## Common mistakes

- **Building before the numbers are fixed.** Details can't save wrong proportions.
- **Assuming things are centred or symmetric.** Ridges, doors and windows often aren't. Measure them.
- **Reading a drawing's scale from the paper.** Use a printed dimension instead.
- **Trusting a drawing or written spec over the photo.** The building may have been changed since. Show the
  contradiction, and build the other version in a separate file if wanted.
- **LiDAR from too far away.** Past ~5 m the depth map is mostly empty.
- **Comparing from a different angle.** A render that doesn't match the photo's viewpoint hides errors.
