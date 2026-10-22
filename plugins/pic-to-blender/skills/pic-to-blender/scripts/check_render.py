# Render quick check pictures from given viewpoints without touching the scene's own cameras or output settings.
# Run inside the live Blender (Blender MCP execute_blender_code):
#
#   VIEWS = {"entre": ((14.5, 9.8, 2.4), (9.2, 4.6, 2.2), 24),   # name: (camera xyz, look-at xyz, lens mm)
#            "gavel": ((2.5, -9, 4.5), (2.4, 1.45, 4.5), 30)}
#   OUT = "<scratchpad>/"          # folder for the PNGs
#   PCT = 25                       # resolution percentage (25 % of 1920x1080 is enough to judge shape, and cheap to look at)
#   exec(open("<this skill>/scripts/check_render.py").read())
#
# Then Read each PNG and compare it with the user's photo. Keep renders small: one EEVEE frame at 25 % takes a few
# seconds, but the MCP call times out after about two minutes, so do at most 3-4 views per call (fewer with Cycles).
import bpy
from mathutils import Vector

VIEWS = globals().get("VIEWS", {})
OUT = globals().get("OUT", "/tmp/")
PCT = globals().get("PCT", 25)

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
finally:
    sc.camera = prev_cam; sc.render.filepath = prev_fp; sc.render.resolution_percentage = prev_pct
    if prev_media is not None: imf.media_type = prev_media
    imf.file_format = prev_fmt
    bpy.data.objects.remove(cam, do_unlink=True); bpy.data.cameras.remove(cd)
