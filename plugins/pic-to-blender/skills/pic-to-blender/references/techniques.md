# Techniques and their traps

Lessons from building real things from photos in Blender through the MCP. Read the section for what you're building.

## Reading the evidence

- **Drawings.** Plans give lengths, wall thicknesses and where openings sit along each wall; sections give
  heights (floor levels, eaves, ridge, pitch); elevations give each facade's windows, sills and cladding. Take the
  scale from a printed dimension line (measure it in pixels), never from the paper's "1:100": printed or scanned
  copies are resized. Crop and enlarge before reading small figures. Heights given against a reference level
  (±0.00) are converted to the model's z = 0. Where a drawing and a photo disagree on the outside, the photo wins
  (buildings get changed after they're drawn): say so and note the drawing's version.
- **LiDAR depth + camera pose** (from an AR capture app). A depth pixel `(u, v)` with depth `d` m, scaled to the
  photo's resolution, is the camera-space point `X = (u - cx) d / fx`, `Y = (cy - v) d / fy`, `Z = d` (camera looking
  along +Z, Y up); the pose turns it into world space. Read eave height (wall foot to roof edge), ridge height and
  where across the front it sits, and door corners. Sample a few pixels inside a surface, not on its edge (depth is
  noisy at edges and on glass), and check one number you can verify (a door height) first. LiDAR reaches ~5 m;
  further away the map is mostly empty.
- **Write each number's source** next to its constant (`# drawing: section A`, `# LiDAR`, `# photo`, `# GUESSED`).

## Checking against a photo

- Camera where the photo was taken: position and direction from the pose, or estimated and nudged until the
  corners line up. Lens: `lens_mm = sensor_width / 2 / tan(hfov / 2)` (Blender's default sensor is 36 mm). Match
  the render's aspect ratio to the photo's: a portrait photo against a landscape render hides half the errors.
- Put photo and render side by side in one image and go through it detail by detail: corners and eaves line up,
  counts right, nothing floating or sunk, no light seams, finishes right.

## Any object

- **Proportions before detail.** Block the whole thing out in boxes and cylinders at the right size first, render it
  from the photo's angle, and only then add bevels, seams, screws and textures. Wrong proportions can't be saved by
  detail.
- **Bevels.** Real edges are never razor sharp: a BEVEL modifier (0.5–3 mm on small things, 1–2 cm on furniture and
  buildings, `limit_method = 'ANGLE'`) plus smooth shading by angle is the cheapest realism there is.
- **Curved and organic shapes.** Lathe (Screw modifier on a profile curve) for anything turned: bottles, vases, lamp
  bases, table legs. A profile curve along a path (curve with bevel object) for handles, pipes, frames, cables.
  Subdivision surface on a low-poly cage for soft shapes (cushions, car bodies); keep the cage in the script.
- **Booleans for holes** (DIFFERENCE, solver EXACT). Keep cutters in a hidden helper collection and tell the user not
  to delete them. A cutter must go fully through the part, or a thin skin is left behind.
- **Materials per part** as seen in the photos, not one colour for the whole object: a chair's seat, legs and screws
  are three materials. Name them in the user's language.
- **Text and logos** as Text objects (extruded slightly) or as an image texture if the user supplies the image; don't
  reproduce brand logos unless it's the user's own object and they want it.
- **Mirrored and repeated parts**: model one, then use a MIRROR or ARRAY modifier, or a loop in the script. Count the
  repeats in the photo (spokes, slats, buttons, windows) and match the number exactly.

## Figures, toys and characters

Soft, rounded things (vinyl figures, plush toys, mascots, statuettes) go wrong in a typical way: a stack of spheres
and ellipsoids at guessed positions, with features floating off the surface. Avoid it like this:

- **Proportions as ratios, measured in pixels.** In the straightest front and side photos, measure head width and
  height, body width, leg length and total height in pixels, and write the ratios down before modelling. Stylised
  figures break normal anatomy: a head can be 60 % of the height and twice as wide as the body. Known product lines
  have standard sizes (look them up) that set the scale.
- **Shape or paint?** For every feature decide whether it is sculpted (raised or sunk in the photo, it catches light
  and casts shadow) or only painted (flat, its edge crisp, no shadow). Painted eyes, brows, mouths, stripes and logos
  are flat: a material on the surface (assign faces of the body mesh, or a thin decal plane with a SHRINKWRAP
  modifier, offset ~0.1 mm), never a protruding blob.
- **Know the real size of what you made.** A SUBSURF on a cube shrinks it a lot (a unit cube at level 3 is far
  smaller than 1 × 1 × 1). Read the evaluated size (`obj.evaluated_get(depsgraph)`, bounding box) and scale until it
  matches the measured numbers, or use a BEVEL with many segments, which keeps the box's size.
- **Place things on the surface, not at guessed coordinates.** Use `closest_point_on_mesh` or `ray_cast` on the
  evaluated body to put eyes, ears, buttons and hands where they touch it, and parent them to the part they sit on.
- **One base shape per volume, from a cage.** A head, a torso, a shoe: a low-poly cage (boxes with extruded loops)
  with SUBSURF, shaped to the front and side silhouettes, not a scaled UV sphere. Limbs: a curve with bevel and taper,
  or the SKIN modifier on a few vertices, so the joints flow into each other.
- **Clothes as their own layers.** Each garment its own shape and material over the body: a jacket's sleeves, a vest
  over it with its quilted bands, trousers, shoes with soles, laces and stripes. Colour by what the photos show for
  each garment, not one colour per body part.
- **Hair is a shell plus locks.** Copy the head's surface, cut it along the hairline (a list of points read from the
  front, side and back photos), SOLIDIFY outward to the thickness the silhouette shows. Then add the locks the photos
  show as tapered curves (bevel + taper) following their flow from the crown or parting, overlapping, ending in
  points along the fringe and the neck. The hair's outline in the side and back photos is usually far bigger than
  the skull.
- **Props are held.** A thing in a hand touches the fingers and is placed by the hand, not floating beside it.
- **Check silhouettes from front, side and back** against the photos before any detail. If the outline is off, the
  detail won't save it.

## Glass, water and see-through things

- Glass: Principled, base nearly black-blue or near-white, roughness 0, coat 1, Alpha 0.15–0.35,
  `surface_render_method = 'BLENDED'`, no backface culling.
- Fully clear glass in front of a bare, lit interior reads as a white hole in EEVEE: give the inside a darkish material.
- The viewport's floor grid and axis lines show through glass and water ("why is it chequered / what is this green
  line"): it's overlays, not the model.

## Buildings

- Each volume is a box with two BOOLEAN DIFFERENCE modifiers: the window and door cutters and an interior box, so the
  wall is ~25 cm thick and hollow and windows can be seen through.
- **All openings in one table** `(facade, a0, a1, z0, z1, kind, panes)`: moving a door is editing a number and
  rerunning. A window under a roof slope takes `z1` as a function of the position along the wall.
- Each opening: frame flush with the outer face (set into the wall it leaves a light strip between frame and
  surround), sashes per pane, mullions, glass, outside sill flashing, inside sill, and the surround on the cladding.
  Frame and surround are separate materials.
- Standard sizes help when the photos are vague: a door ~0.9–1.0 × 2.1 m, a storey 2.6–2.8 m. Swedish window module
  sizes are width-height in decimetres (`11-15` = 110 × 150 cm).
- **Cladding as boards** (~15 cm visible, each thicker at the bottom so the joints shadow), cut exactly around every
  opening and along sloping roof lines. Cut each board into pieces and clip them to the roof line and around each
  opening; cutting only whole boards leaves stair steps under every slope. When clipping recursively, ignore crossings
  within 1e-5 m of a piece's ends or the recursion never stops. A bump texture alone is invisible in Solid mode.
- **Simple buildings (a garage, a shed)**: the walls can be one prism from the gable outline pushed back along the
  depth; thin dark shadow lines every board height read as cladding at a fraction of the cost of real boards. Don't
  assume the ridge is centred: on garages and extensions it often isn't, so measure it.
- **Roofs**: slabs from skewed boxes with a z(x) function; standing seams every 0.5 m; verge and fascia boards.
  Half-round gutters (two concentric half cylinders, end caps, hangers every 0.8 m); round downpipes from the outlet
  through a swan neck back to the wall, straight down with clips every 1.5 m and a shoe at the bottom.
- **Terrain levels**: look for steps in the ground in the photos (retaining walls, stairs, a garage lower than the
  house). Build the ground as a prism with real height, lower zones as their own surfaces, walls as blocks with a
  coping. Raising a building afterwards: move whole objects, but for meshes shared with another building move only
  the vertices inside its area.

## Plants

- **Hedge**: a cube scaled to length × 0.8 × 2.0 m, subdivided (~4 cuts per metre), DISPLACE with a CLOUDS texture
  (strength ~0.12, GLOBAL coordinates), SUBSURF 1.
- **Trees** (`scripts/trees.py`): a trunk that splits into levels of branches (count, start along the parent, angle,
  length and radius ratios, curl, tropism up or hanging down) as one curve object with per-point radius, and leaf
  cards on the last level, coloured per island with a little translucency. ~40 000 leaves per tree renders in seconds.
  Never blob crowns. Oak: short thick trunk, wide crown. Birch: tall white trunk, hanging twigs, small light leaves.
- **Grass**: a procedural ground material (voronoi × noise for blades, large noise patches, faint mowing stripes,
  bump). Instanced blade tufts look good up close but cost a lot; leave them out unless asked.

## Blender API traps

- On save Blender drops materials nobody uses: scripts must create a material if `bpy.data.materials.get()` is None.
- `bpy.ops` operators need the right context (mode, active object, selection); set them explicitly or use the data API.
- `FunctionNodeRandomValue` inputs: set `inputs["Min"]` / `["Max"]` by name; index 2 is an integer ID socket.
- Variables from one `exec` leak into the next: don't reuse short names like `B` for paths.
- A boolean on an object outlines the cut in orange while the object is selected; it's the selection, not the model.
