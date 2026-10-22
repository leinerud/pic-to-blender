# Trees and shrubs: recursive branches (one curve object with per-point radius) and individual leaf cards (one mesh).
# Run inside Blender (execute_blender_code):
#   exec(open("<this skill>/scripts/trees.py").read())
#   setup_materials(); make_tree("Oak", (x, y, z), OAK, seed=1)
# Presets: OAK, BIRCH, RHODO (a shrub). Copy one and change the numbers to match the photos.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Quaternion

D = bpy.data
def _coll(name="Trees"):
    c = D.collections.get(name)
    if c is None:
        c = D.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c
tg = _coll()

def leaf_mat(name, c1, c2):
    m = D.materials.get(name) or D.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    oi = nt.nodes.new("ShaderNodeObjectInfo")  # fallback
    rnd = nt.nodes.new("ShaderNodeValToRGB")
    rnd.color_ramp.elements[0].color = (*c1, 1); rnd.color_ramp.elements[1].color = (*c2, 1)
    try:
        nt.links.new(geo.outputs["Random Per Island"], rnd.inputs[0])
    except KeyError:
        nt.links.new(oi.outputs["Random"], rnd.inputs[0])
    b = nt.nodes.new("ShaderNodeBsdfPrincipled"); b.inputs["Roughness"].default_value = 0.45
    tr = nt.nodes.new("ShaderNodeBsdfTranslucent")
    nt.links.new(rnd.outputs[0], b.inputs["Base Color"]); nt.links.new(rnd.outputs[0], tr.inputs[0])
    mx = nt.nodes.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.3
    nt.links.new(b.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0])
    m.diffuse_color = (*[(a + c) / 2 for a, c in zip(c1, c2)], 1)
    try: m.use_backface_culling = False
    except Exception: pass
    return m

def clear(prefix):
    for o in list(D.objects):
        if o.name == prefix or o.name.startswith(prefix + " "):
            D.objects.remove(o, do_unlink=True)

def perp(d):
    a = Vector((1, 0, 0)) if abs(d.x) < 0.9 else Vector((0, 1, 0))
    return d.cross(a).normalized()

def make_tree(name, base, P, seed):
    """P: parameters per level. Returns (branch curve object, leaf object, leaf count)."""
    rnd = random.Random(seed)
    base = Vector(base)
    splines = []      # list of [(point, radius), ...]
    leaves = []       # (position, direction)

    def grow(p, d, length, radius, lvl):
        lp = P["levels"][lvl]
        nseg = lp["segs"]; pts = [(p.copy(), radius)]
        cur, cd = p.copy(), d.normalized()
        seglen = length / nseg
        for i in range(nseg):
            cd = (cd + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * lp["curve"]
                  + Vector((0, 0, 1)) * lp["tropism"]).normalized()
            cur = cur + cd * seglen
            r = radius * (1 - (i + 1) / nseg * lp["taper"])
            pts.append((cur.copy(), max(r, 0.004)))
        splines.append(pts)
        if lvl + 1 < len(P["levels"]):
            ch = P["levels"][lvl + 1]
            n = ch["count"]
            for k in range(n):
                t = rnd.uniform(ch["start"], 1.0) if ch.get("along", True) else 1.0
                idx = min(int(t * nseg), nseg - 1); f = t * nseg - idx
                a, b2 = pts[idx], pts[idx + 1]
                sp = a[0].lerp(b2[0], f); sr = a[1] + (b2[1] - a[1]) * f
                pd = (pts[idx + 1][0] - pts[idx][0]).normalized()
                ang = math.radians(rnd.uniform(*ch["angle"]))
                rot = rnd.uniform(0, 2 * math.pi) if not ch.get("spiral") else k * 2.39996 + rnd.uniform(-0.3, 0.3)
                side = perp(pd)
                side = Quaternion(pd, rot) @ side
                nd = (pd * math.cos(ang) + side * math.sin(ang)).normalized()
                L = length * ch["ratio"] * rnd.uniform(0.75, 1.15) * (1.15 - 0.5 * t if ch.get("shape") == "cone" else 1)
                grow(sp, nd, L, sr * ch["rratio"], lvl + 1)
        else:
            # leaves along the outermost twigs
            for (q, r), (q2, _) in zip(pts[:-1], pts[1:]):
                for _ in range(P["leaves_per_seg"]):
                    lp2 = q.lerp(q2, rnd.random())
                    leaves.append((lp2, (q2 - q).normalized()))

    grow(base, Vector((0, 0, 1)), P["trunk_len"], P["trunk_r"], 0)

    # --- branches as one curve object with radius
    cu = D.curves.new(name + " grenar", 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = 1.0; cu.bevel_resolution = 1; cu.use_fill_caps = True
    for pts in splines:
        s = cu.splines.new('POLY'); s.points.add(len(pts) - 1)
        for i, (q, r) in enumerate(pts):
            s.points[i].co = (q.x, q.y, q.z, 1); s.points[i].radius = r
    cu.resolution_u = 2
    co = D.objects.new(name + " grenar", cu); tg.objects.link(co); cu.materials.append(D.materials[P["bark"]])

    # --- leaves
    L, Wd = P["leaf_len"], P["leaf_w"]
    shape = [(0, 0), (Wd, 0.3 * L), (0.75 * Wd, 0.72 * L), (0, L), (-0.75 * Wd, 0.72 * L), (-Wd, 0.3 * L)]
    verts, faces = [], []
    for pos, bd in leaves:
        # leaf direction: out from the twig, drooping a little, random twist
        out = (perp(bd) * rnd.uniform(-1, 1) + bd.cross(perp(bd)) * rnd.uniform(-1, 1)).normalized()
        ld = (out + Vector((0, 0, P["leaf_droop"])) + bd * 0.3).normalized()
        nrm = ld.cross(perp(ld)); nrm = (Quaternion(ld, rnd.uniform(-1.2, 1.2)) @ nrm)
        xax = nrm.cross(ld).normalized()
        s = rnd.uniform(0.7, 1.25)
        stem = pos + ld * 0.01
        o = len(verts)
        for x, y in shape:
            verts.append(stem + xax * (x * s) + ld * (y * s) + nrm * (-(x * x) * 2.0 * s))
        faces.append((o, o + 1, o + 2, o + 3)); faces.append((o, o + 3, o + 4, o + 5))
    me = D.meshes.new(name + " blad"); me.from_pydata(verts, [], faces); me.update()
    me.materials.append(D.materials[P["leaf_mat"]])
    lo = D.objects.new(name + " blad", me); tg.objects.link(lo)
    return co, lo, len(leaves)

OAK = dict(trunk_len=3.2, trunk_r=0.34, bark="Bark oak", leaf_mat="Leaf oak", leaf_len=0.11, leaf_w=0.035,
           leaf_droop=-0.2, leaves_per_seg=7,
           levels=[dict(segs=5, curve=0.12, tropism=0.05, taper=0.35),
                   dict(count=5, start=0.75, angle=(30, 55), ratio=1.25, rratio=0.62, segs=6, curve=0.25, tropism=0.08, taper=0.6),
                   dict(count=6, start=0.25, angle=(35, 65), ratio=0.5, rratio=0.55, segs=4, curve=0.3, tropism=0.1, taper=0.6),
                   dict(count=5, start=0.2, angle=(35, 70), ratio=0.45, rratio=0.55, segs=3, curve=0.35, tropism=0.15, taper=0.7),
                   dict(count=4, start=0.2, angle=(30, 70), ratio=0.45, rratio=0.6, segs=2, curve=0.4, tropism=0.2, taper=0.7)])
BIRCH = dict(trunk_len=9.0, trunk_r=0.17, bark="Bark birch", leaf_mat="Leaf birch", leaf_len=0.06, leaf_w=0.025,
             leaf_droop=-0.8, leaves_per_seg=7,
             levels=[dict(segs=8, curve=0.04, tropism=0.1, taper=0.8),
                     dict(count=30, start=0.3, angle=(45, 70), ratio=0.32, rratio=0.35, segs=5, curve=0.2, tropism=-0.15, taper=0.7, spiral=True, shape="cone"),
                     dict(count=5, start=0.2, angle=(25, 55), ratio=0.5, rratio=0.5, segs=4, curve=0.25, tropism=-0.45, taper=0.7),
                     dict(count=4, start=0.2, angle=(20, 45), ratio=0.5, rratio=0.6, segs=3, curve=0.2, tropism=-0.8, taper=0.7)])
RHODO = dict(trunk_len=0.25, trunk_r=0.05, bark="Bark oak", leaf_mat="Leaf rhododendron", leaf_len=0.15, leaf_w=0.03,
             leaf_droop=0.1, leaves_per_seg=10,
             levels=[dict(segs=1, curve=0.1, tropism=0.0, taper=0.3),
                     dict(count=9, start=0.9, angle=(20, 70), ratio=4.5, rratio=0.6, segs=3, curve=0.25, tropism=0.1, taper=0.5),
                     dict(count=4, start=0.4, angle=(25, 60), ratio=0.45, rratio=0.6, segs=2, curve=0.3, tropism=0.25, taper=0.6)])

def bark_mat(name, c):
    m = D.materials.get(name) or D.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b: b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = 0.9
    m.diffuse_color = (*c, 1)
    return m

def setup_materials():
    bark_mat("Bark oak", (0.09, 0.075, 0.06)); bark_mat("Bark birch", (0.75, 0.73, 0.68))
    leaf_mat("Leaf oak", (0.035, 0.09, 0.02), (0.16, 0.26, 0.06))
    leaf_mat("Leaf birch", (0.12, 0.24, 0.04), (0.40, 0.46, 0.10))
    leaf_mat("Leaf rhododendron", (0.02, 0.07, 0.025), (0.08, 0.18, 0.06))
