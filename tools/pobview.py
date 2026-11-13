"""Compact gem viewer in the style of pobb.in: one set (act / phase) at a time, picked from a dropdown.
Each gem has its colour and a tooltip with the minimum level and where the build's class gets it
(quest reward or vendor), from data/gem_info.json (built from exile-leveling, MIT)."""
import html, json, os, re

e = html.escape
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POB_COLORS = json.load(open(os.path.join(ROOT, 'data', 'gem_colors.json')))
INFO = json.load(open(os.path.join(ROOT, 'data', 'gem_info.json')))
CLASSES = ['Marauder', 'Ranger', 'Witch', 'Duelist', 'Templar', 'Shadow', 'Scion']


def base_of(name):
    """'Vaal Spark of the Nova' -> ('Spark', 'vaal+transfig'); 'Spark' -> ('Spark', '')."""
    n, kind = name, []
    if n.startswith('Vaal ') and n not in INFO:
        n = n[5:]; kind.append('vaal')
    if n not in INFO and ' of ' in n and n.split(' of ')[0] in INFO:
        n = n.split(' of ')[0]; kind.append('transfig')
    return n, '+'.join(kind)


def color(name):
    b, _ = base_of(name)
    i = INFO.get(name) or INFO.get(b)
    if i:
        return i['c']
    c = POB_COLORS.get(name) or POB_COLORS.get(b) or 'w'
    return c[0]


def sources(name, cls):
    """Short list for the tooltip: [(act, npc, quest, 'q'|'v')], only for this class."""
    i = INFO.get(name)
    if not i:
        return []
    ci = str(CLASSES.index(cls)) if cls in CLASSES else None
    seen, out = set(), []
    for act, npc, quest, kind, cl in i['s']:
        if cl and ci is not None and ci not in cl:
            continue
        key = (act, npc)  # mesma NPC no mesmo ato: fica só a primeira (recompensa vem antes de compra)
        if key in seen:
            continue
        seen.add(key)
        out.append((act, npc, quest, kind))
    # quest reward first, then the first vendor; Siosa (Ato 3) and Lilly Roth (Ato 6) only if nothing earlier
    early = [s for s in out if s[1] not in ('Siosa', 'Lilly Roth')]
    late = [s for s in out if s[1] in ('Siosa', 'Lilly Roth')]
    return (early[:3] + late[:1]) if early else late[:2]


def tip_data(names, cls):
    d = {}
    for n in names:
        b, kind = base_of(n)
        i = INFO.get(n) or INFO.get(b) or {}
        d[n] = {'l': i.get('l'), 'k': kind, 'b': b if b != n else '', 's': sources(b, cls)}
    return d


def group(gems, slot=''):
    """gems: list of names, the first is the main skill; slot: optional small label (Body Armour…)."""
    same = slot and slot.split(' (')[0].strip().lower() == gems[0].lower()
    head = f'<span class="pvslot">{e(slot)}</span>' if slot and not same else ''
    main = f'<b class="pvm c-{color(gems[0])}" data-g="{e(gems[0])}" tabindex="0">{e(gems[0])}</b>'
    sup = ''.join(f'<li class="c-{color(g)}" data-g="{e(g)}" tabindex="0">{e(g)}</li>' for g in gems[1:])
    return f'<div class="pvg">{head}{main}{"<ul>" + sup + "</ul>" if sup else ""}</div>'


def view(key, sets, cls, label='Ato', extra=''):
    """sets: list of (title, [ (gems, slot), ... ]); cls: character class (for where to get each gem)."""
    opts = ''.join(f'<option value="{i}">{e(t)}</option>' for i, (t, _) in enumerate(sets))
    body, names = [], []
    for i, (t, groups) in enumerate(sets):
        for g, _ in groups:
            names += [n for n in g if n not in names]
        gs = ''.join(group(g, s) for g, s in groups)
        body.append(f'<div class="pvset" id="{e(key)}-{i}"><h4 class="pvtitle">{e(t)}</h4><div class="pvgrid">{gs}</div></div>')
    bar = ''
    if len(sets) > 1:
        bar = (f'<div class="pvbar"><label class="pvlab"><span>{e(label)}</span> <select class="pvsel">{opts}</select></label>'
               f'<button type="button" class="pvnav" data-d="-1" aria-label="Anterior">‹</button>'
               f'<button type="button" class="pvnav" data-d="1" aria-label="Próximo">›</button>'
               f'<span class="pvcount"></span>{extra}</div>')
    data = json.dumps(tip_data(names, cls), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return (f'<div class="pobview" data-cls="{e(cls)}">{bar}{"".join(body)}'
            f'<script type="application/json" class="pvinfo">{data}</script></div>')
