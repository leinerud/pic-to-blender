# A small mesh builder: collect boxes, skewed boxes, cylinders and polygons with a material each, then make one object.
# One object per kind of thing (all legs, all screws, all windows) keeps the Outliner readable and the scene fast.
# Run inside Blender (execute_blender_code):
#   exec(open("<this skill>/scripts/mesh_builder.py").read())
#   wood = mat("Wood", (0.45, 0.30, 0.18), rough=0.6)
#   m = MB(); m.box((0, 0, 0), (0.9, 0.5, 0.03), wood); m.cyl((0.05, 0.05, -0.7), 0.02, 0.7, wood)
#   m.obj("Table", coll("Table"))
import bpy, bmesh, math

BOXF = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]

def coll(name, parent=None):
    """Get or make a collection (under parent, else under the scene)."""
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c

def mat(name, rgb, rough=0.5, metal=0.0, alpha=1.0):
    """Get or make a simple Principled material. Alpha < 1 makes it see-through (glass: alpha 0.15-0.35, rough 0)."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value = (*rgb, 1)
        b.inputs["Roughness"].default_value = rough
        b.inputs["Metallic"].default_value = metal
        b.inputs["Alpha"].default_value = alpha
    if alpha < 1:
        try: m.surface_render_method = 'BLENDED'
        except Exception: m.blend_method = 'BLEND'
        try: m.use_backface_culling = False
        except Exception: pass
    m.diffuse_color = (*rgb, alpha)
    return m

def clear(prefix):
    """Remove objects this script made before (name == prefix or starts with 'prefix '), so reruns don't duplicate."""
    for o in list(bpy.data.objects):
        if o.name == prefix or o.name.startswith(prefix + " "):
            bpy.data.objects.remove(o, do_unlink=True)

class MB:
    def __init__(s): s.v = []; s.f = []; s.mi = []; s.mats = []
    def _m(s, m):
        if m not in s.mats: s.mats.append(m)
        return s.mats.index(m)
    def hexa(s, v8, m=None):
        """8 corners: bottom 4 counter-clockwise seen from above, then the top 4 in the same order (for skewed or sloped pieces)."""
        o = len(s.v); s.v += [tuple(p) for p in v8]; s.f += [tuple(o + i for i in f) for f in BOXF]; s.mi += [s._m(m)] * 6
    def box(s, p0, p1, m=None):
        """Axis-aligned box from corner p0 to corner p1."""
        (x0, y0, z0), (x1, y1, z1) = p0, p1
        s.hexa([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], m)
    def cyl(s, base, r, h, m=None, n=24, half=None, r_top=None):
        """Upright cylinder (or cone with r_top) from base (x, y, z), height h. half=(a0, a1) in radians makes an open part, e.g. a gutter."""
        a0, a1 = half or (0, 2 * math.pi)
        full = half is None
        k = n if full else n + 1
        rt = r if r_top is None else r_top
        o = len(s.v); x, y, z = base
        for i in range(k):
            a = a0 + (a1 - a0) * i / n
            s.v.append((x + r * math.cos(a), y + r * math.sin(a), z))
            s.v.append((x + rt * math.cos(a), y + rt * math.sin(a), z + h))
        sides = [(o + 2 * i, o + 2 * ((i + 1) % k), o + 2 * ((i + 1) % k) + 1, o + 2 * i + 1) for i in range(n)]
        s.f += sides; s.mi += [s._m(m)] * len(sides)
        if full:
            s.f.append(tuple(o + 2 * i for i in reversed(range(k)))); s.f.append(tuple(o + 2 * i + 1 for i in range(k)))
            s.mi += [s._m(m)] * 2
    def poly(s, verts, faces, m=None):
        o = len(s.v); s.v += [tuple(p) for p in verts]; s.f += [tuple(o + i for i in f) for f in faces]; s.mi += [s._m(m)] * len(faces)
    def obj(s, name, c):
        me = bpy.data.meshes.new(name); me.from_pydata(s.v, [], s.f); me.validate(); me.update()
        for m in s.mats:
            if m: me.materials.append(m)
        if len(s.mats) > 1:
            for p, i in zip(me.polygons, s.mi): p.material_index = i
        bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new(name, me); c.objects.link(o); return o
