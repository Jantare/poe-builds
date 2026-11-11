"""Builds data/craft/*.json for the crafting simulator from Path of Building data files.
Usage: python3 -I tools/build_craft_data.py <pob_data_dir> <out_dir>
<pob_data_dir> must contain ModExplicit.lua, ModJewel.lua, Essence.lua and the Bases/*.lua files (flat)."""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(__file__))
import lualoader
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
BASEFILES = ['amulet','belt','body','boots','bow','claw','dagger','gloves','helmet','jewel','mace','quiver','ring','shield','staff','sword','wand','axe']
SKIP_TAG = {'demigods','not_for_sale_in_gambling'}
bases = {}
for f in BASEFILES:
    for name, b in lualoader.load_assign(os.path.join(src, f + '.lua'), 'itemBases').items():
        tags = b.get('tags') or {}
        if not isinstance(tags, dict): continue
        if b.get('hidden') or any(t in tags for t in SKIP_TAG): continue
        if b.get('type') == 'Jewel' and b.get('subType') in ('Abyss',): continue
        if b.get('type') == 'Jewel' and 'Cluster' in name: continue
        bases[name] = {
            'type': b.get('type'), 'sub': b.get('subType') or '',
            'tags': sorted(k for k, v in tags.items() if v),
            'imp': b.get('implicit') or '',
            'lvl': (b.get('req') or {}).get('level', 1) if isinstance(b.get('req'), dict) else 1,
        }
alltags = set(t for b in bases.values() for t in b['tags'])
mods = {}
explicit = lualoader.load(os.path.join(src, 'ModExplicit.lua'))
jewelmods = lualoader.load(os.path.join(src, 'ModJewel.lua'))
for mid in jewelmods: jewelmods[mid]['_jewel'] = True
explicit.update(jewelmods)
for mid, m in explicit.items():
    if not isinstance(m, dict) or m.get('type') not in ('Prefix', 'Suffix'): continue
    if re.match(r'(Delve|Synthesis|Incursion|Bestiary|Veiled|Harvest|Necropolis|Eldritch|Abyss)', mid): continue
    wk, wv = m.get('weightKey') or [], m.get('weightVal') or []
    if not any(v > 0 and k in alltags for k, v in zip(wk, wv)): continue
    text = [m[i] for i in range(1, 10) if i in m and isinstance(m[i], str)]
    mods[mid] = {'t': 'P' if m['type'] == 'Prefix' else 'S', 'x': text, 'l': m.get('level', 1),
                 'g': m.get('group', mid), 'wk': wk, 'wv': wv, 'tg': m.get('modTags') or []}
    if m.get('_jewel'): mods[mid]['j'] = 1  # only rolls on jewels
ess = []
for k, e in lualoader.load(os.path.join(src, 'Essence.lua')).items():
    em = {t: mid for t, mid in (e.get('mods') or {}).items() if mid in mods}
    if em: ess.append({'n': e['name'], 'tier': e.get('tier', 0), 'm': em})
ess.sort(key=lambda e: (e['n'].split(' of ')[-1], e['tier']))
for name, data in (('bases', bases), ('mods', mods), ('essences', ess)):
    with open(os.path.join(out, name + '.json'), 'w') as fh:
        json.dump(data, fh, ensure_ascii=False, separators=(',', ':'))
    print(name, len(data), os.path.getsize(os.path.join(out, name + '.json')))
