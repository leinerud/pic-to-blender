# Checks a pull request keeps the plugin healthy. Run from the repo root: python3 .github/scripts/check.py [base-ref]
# With a base ref (e.g. origin/main) it also checks the version was bumped when the plugin changed.
import json, os, re, subprocess, sys, ast

PLUGIN = "plugins/pic-to-blender"
SKILL = f"{PLUGIN}/skills/pic-to-blender/SKILL.md"
MAX_SKILL_BYTES = 12000
errors = []

def fail(msg): errors.append(msg)

def load_json(path):
    try:
        with open(path) as f: return json.load(f)
    except Exception as e:
        fail(f"{path}: not valid JSON ({e})"); return {}

market = load_json(".claude-plugin/marketplace.json")
plugin = load_json(f"{PLUGIN}/.claude-plugin/plugin.json")
entry = next((p for p in market.get("plugins", []) if p.get("name") == "pic-to-blender"), None)
if not entry: fail("marketplace.json: no plugin named pic-to-blender")
for k in ("name", "description", "version"):
    if not plugin.get(k): fail(f"plugin.json: missing {k}")
if entry and entry.get("version") != plugin.get("version"):
    fail(f"version differs: marketplace.json {entry.get('version')} vs plugin.json {plugin.get('version')}")

# SKILL.md: frontmatter and size (it's loaded for every user, every time the skill runs)
try:
    text = open(SKILL).read()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m: fail(f"{SKILL}: no frontmatter")
    else:
        fm = m.group(1)
        if not re.search(r"^name: pic-to-blender$", fm, re.M): fail(f"{SKILL}: frontmatter name must be pic-to-blender")
        d = re.search(r"^description: (.+)$", fm, re.M)
        if not d: fail(f"{SKILL}: frontmatter has no description")
        elif len(d.group(1)) > 1024: fail(f"{SKILL}: description is {len(d.group(1))} chars, keep it under 1024")
    size = len(text.encode())
    if size > MAX_SKILL_BYTES:
        fail(f"{SKILL}: {size} bytes, over {MAX_SKILL_BYTES}. Move detail into references/ or scripts/.")
except FileNotFoundError:
    fail(f"{SKILL}: missing")

# Python helpers must at least parse
for root, _, files in os.walk(PLUGIN):
    for fn in files:
        if fn.endswith(".py"):
            p = os.path.join(root, fn)
            try: ast.parse(open(p).read(), p)
            except SyntaxError as e: fail(f"{p}: {e}")

# No personal data or machine-specific paths
PATTERNS = [(r"/Users/[A-Za-z0-9._-]+", "a personal macOS path"), (r"/home/[A-Za-z0-9._-]+", "a personal Linux path"),
            (r"C:\\\\Users\\\\", "a personal Windows path"), (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}", "an email address"),
            (r"(ghp|gho|sk-ant|sk)-?[A-Za-z0-9_]{20,}", "something that looks like a token")]
ALLOWED = {"noreply@anthropic.com"}
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d != ".git"]
    for fn in files:
        p = os.path.join(root, fn)
        if p.endswith("check.py") or fn == "LICENSE": continue
        try: s = open(p, encoding="utf-8").read()
        except Exception: continue
        for pat, what in PATTERNS:
            for hit in re.findall(pat, s):
                hit = hit if isinstance(hit, str) else hit[0]
                if hit not in ALLOWED: fail(f"{p}: contains {what} ({hit[:40]})")

# The version must go up when the plugin changes
if len(sys.argv) > 1:
    base = sys.argv[1]
    changed = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], capture_output=True, text=True).stdout.split()
    if any(f.startswith(PLUGIN + "/skills/") for f in changed):
        try:
            old = json.loads(subprocess.run(["git", "show", f"{base}:{PLUGIN}/.claude-plugin/plugin.json"],
                                            capture_output=True, text=True, check=True).stdout).get("version")
            ver = lambda v: tuple(int(x) for x in v.split("."))
            if ver(plugin.get("version", "0.0.0")) <= ver(old):
                fail(f"the skill changed but the version is still {plugin.get('version')}: bump it in plugin.json and marketplace.json")
        except subprocess.CalledProcessError:
            pass

if errors:
    print("Problems:\n" + "\n".join("- " + e for e in errors)); sys.exit(1)
print("All good.")
