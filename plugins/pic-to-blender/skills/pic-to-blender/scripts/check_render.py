# Render quick check pictures from given viewpoints without touching the scene's own cameras or output settings.
# Run inside the live Blender (Blender MCP execute_blender_code):
#
#   VIEWS = {"entrance": ((14.5, 9.8, 2.4), (9.2, 4.6, 2.2), 24),   # name: (camera xyz, look-at xyz, lens mm)
#            "gable": ((2.5, -9, 4.5), (2.4, 1.45, 4.5), 30)}
#   OUT = "<scratchpad>/"          # folder for the PNGs
#   PCT = 25                       # resolution percentage (25 % of 1920x1080 is enough to judge shape, and cheap to look at)
#   PHOTOS = {"entre": "<folder>/entre_small.jpg"}   # optional: view name -> small copy of the user's photo
#   exec(open("<this skill>/scripts/check_render.py").read())
#
# With PHOTOS, each such view also gets <name>_vs.png: the render on the left, the photo scaled to the same height on
# the right. Read only those (one picture per view instead of two). Without PHOTOS, Read each PNG and compare.
# Keep renders small: one EEVEE frame at 25 % takes a few seconds, but the MCP call times out after about
# two minutes, so do at most 3-4 views per call (fewer with Cycles).
import bpy
import numpy as np
from mathutils import Vector

VIEWS = globals().get("VIEWS", {})
OUT = globals().get("OUT", "/tmp/")
PCT = globals().get("PCT", 25)
PHOTOS = globals().get("PHOTOS", {})


def _px(img):
    a = np.empty(img.size[0] * img.size[1] * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    return a.reshape(img.size[1], img.size[0], 4)


def side_by_side(render_path, photo_path, out_path):
    r = bpy.data.images.load(render_path); p = bpy.data.images.load(photo_path)
    try:
        h = r.size[1]
        p.scale(max(1, round(p.size[0] * h / p.size[1])), h)
        both = np.hstack([_px(r), _px(p)])
        out = bpy.data.images.new("_vs", both.shape[1], h, alpha=True)
        try:
            out.pixels.foreach_set(both.ravel())
            out.filepath_raw = out_path; out.file_format = 'PNG'; out.save()
        finally:
            bpy.data.images.remove(out)
    finally:
        bpy.data.images.remove(r); bpy.data.images.remove(p)

sc = bpy.context.scene
prev_cam, prev_fp, prev_pct = sc.camera, sc.render.filepath, sc.render.resolution_percentage
imf = sc.render.image_settings
prev_fmt = imf.file_format
prev_media = getattr(imf, "media_type", None)
cd = bpy.data.cameras.new("_check"); cam = bpy.data.objects.new("_check", cd)
sc.collection.objects.link(cam)
try:
    if prev_media is not None: imf.media_type = 'IMAGE'
    imf.file_format = 'PNG'
    sc.camera = cam; sc.render.resolution_percentage = PCT
    for name, (loc, target, lens) in VIEWS.items():
        cam.location = loc; cd.lens = lens
        cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = OUT + name + ".png"
        bpy.ops.render.render(write_still=True)
        if name in PHOTOS:
            side_by_side(sc.render.filepath, PHOTOS[name], OUT + name + "_vs.png")
finally:
    sc.camera = prev_cam; sc.render.filepath = prev_fp; sc.render.resolution_percentage = prev_pct
    if prev_media is not None: imf.media_type = prev_media
    imf.file_format = prev_fmt
    bpy.data.objects.remove(cam, do_unlink=True); bpy.data.cameras.remove(cd)
