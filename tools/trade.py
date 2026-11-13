"""'Comprar pronto' links to the official trade site.
The query is stored in data-q; assets/trade.js turns it into a URL for the league the visitor picked."""
import html, json, os, re

e = html.escape
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIQUES = json.load(open(os.path.join(ROOT, 'data', 'unique_bases.json')))
BASES = set(json.load(open(os.path.join(ROOT, 'data', 'craft', 'bases.json'))))
GEAR_SLOTS = {'Helmet', 'Body Armour', 'Gloves', 'Boots', 'Belt', 'Amulet', 'Ring 1', 'Ring 2', 'Weapon 2'}
ES_INC = re.compile(r'^(\d+)% increased (?:Energy Shield|Armour and Energy Shield|Evasion and Energy Shield|Armour, Evasion and Energy Shield)$')


def _val(line):
    """'{range:0.5}+(80-89) to maximum Life' -> ('+X to maximum Life', 84.5)."""
    rng = re.search(r'\{range:([\d.]+)\}', line)
    line = re.sub(r'\{[^}]*\}', '', line).strip()
    r = float(rng.group(1)) if rng else 0.5
    def pick(m):
        lo, hi = float(m.group(1)), float(m.group(2))
        return str(round(lo + (hi - lo) * r))
    return re.sub(r'\((-?[\d.]+)-(-?[\d.]+)\)', pick, line)


def rare_filters(lines):
    life = res = chaos = ms = 0
    es_base = es_flat = es_inc = 0
    quality = 20
    for raw in lines:
        l = _val(raw)
        m = re.match(r'^Energy Shield: (\d+)', l)
        if m: es_base = int(m.group(1)); continue
        m = re.match(r'^Quality: \+?(\d+)', l)
        if m: quality = max(20, int(m.group(1))); continue
        m = re.match(r'^\+(\d+) to maximum Life$', l)
        if m: life += int(m.group(1))
        m = re.match(r'^\+(\d+) to maximum Energy Shield$', l)
        if m: es_flat += int(m.group(1))
        m = ES_INC.match(l)
        if m: es_inc += int(m.group(1))
        m = re.match(r'^\+(\d+)% to (.+?) Resistances?$', l)
        if m:
            v, what = int(m.group(1)), m.group(2)
            if what == 'all Elemental': res += 3 * v
            else:
                for part in re.split(r' and |, ', what):
                    if part in ('Fire', 'Cold', 'Lightning'): res += v
                    elif part == 'Chaos': chaos += v
        m = re.match(r'^(\d+)% increased Movement Speed$', l)
        if m: ms += int(m.group(1))
    stats = []
    f = lambda v: int(v * 0.85)
    if life >= 20: stats.append({'id': 'pseudo.pseudo_total_life', 'value': {'min': f(life)}})
    if res >= 20: stats.append({'id': 'pseudo.pseudo_total_elemental_resistance', 'value': {'min': f(res)}})
    if chaos >= 10: stats.append({'id': 'pseudo.pseudo_total_chaos_resistance', 'value': {'min': f(chaos)}})
    if ms >= 10: stats.append({'id': 'pseudo.pseudo_increased_movement_speed', 'value': {'min': ms}})
    es = 0
    if es_base:
        es = (es_base + es_flat) * (1 + (es_inc + quality) / 100)
    return stats, (f(es) if es >= 60 else 0), dict(life=life, res=res, chaos=chaos, ms=ms, es=round(es))


def item_query(slot, rarity, name, base, lines):
    q = {'status': {'option': 'online'}}
    if rarity == 'Unique' and name:
        q.update(name=name, type=base or UNIQUES.get(name, ''))
        if not q['type']: q.pop('type')
        return {'query': q, 'sort': {'price': 'asc'}}, 'unique'
    if rarity == 'Rare' and base and slot in GEAR_SLOTS:
        stats, es, info = rare_filters(lines)
        if not stats and not es:  # sem vida/ES/resistência para filtrar: a busca só pela base não ajuda
            return None, None
        q['type'] = base
        q['filters'] = {'type_filters': {'filters': {'rarity': {'option': 'nonunique'}}}}
        if es:
            q['filters']['armour_filters'] = {'filters': {'es': {'min': es}}}
        if stats:
            q['stats'] = [{'type': 'and', 'filters': stats}]
        return {'query': q, 'sort': {'price': 'asc'}}, info
    return None, None


def link(query, label='Comprar', title=''):
    data = e(json.dumps(query, separators=(',', ':')), quote=True)
    t = f' title="{e(title)}"' if title else ''
    return f'<a class="buy" data-q="{data}" href="https://www.pathofexile.com/trade" target="_blank" rel="noopener"{t}>{e(label)} ↗</a>'


def describe(info):
    if not isinstance(info, dict):
        return ''
    parts = []
    if info['es'] >= 60: parts.append(f"{int(info['es'] * 0.85)}+ de ES")
    if info['life'] >= 20: parts.append(f"{int(info['life'] * 0.85)}+ de vida")
    if info['res'] >= 20: parts.append(f"{int(info['res'] * 0.85)}%+ de resistências")
    if info['chaos'] >= 10: parts.append(f"{int(info['chaos'] * 0.85)}%+ de chaos")
    if info['ms'] >= 10: parts.append(f"{info['ms']}%+ de movimento")
    return ', '.join(parts)


def league_bar():
    return ('<div class="tradebar"><label>Liga do trade <select class="tradelg"></select></label>'
            '<span class="sub">Os links abrem o site de trade oficial com o item já pesquisado, do mais barato para o mais caro.</span></div>')


def linkify(cell_html):
    """Bets' free-text cells: add a buy link after unique and base names (first occurrence of each)."""
    names = sorted([n for n in UNIQUES if len(n) > 5] + [b for b in BASES if len(b) > 8], key=len, reverse=True)
    out, done = cell_html, set()
    for n in names:
        if n in done:
            continue
        hit = next((c for c in (n, e(n), n.replace("'", '&#39;')) if c in out), None)
        if not hit:
            continue
        idx = out.find(hit)
        if out.rfind('<', 0, idx) > out.rfind('>', 0, idx):  # inside a tag
            continue
        end = idx + len(hit)
        if out[end:end + 4] == '</b>': end += 4
        if n in UNIQUES:
            q = {'query': {'status': {'option': 'online'}, 'name': n, 'type': UNIQUES[n]}, 'sort': {'price': 'asc'}}
        else:
            q = {'query': {'status': {'option': 'online'}, 'type': n}, 'sort': {'price': 'asc'}}
        out = out[:end] + ' ' + link(q, 'comprar', f'Buscar {n} no trade') + out[end:]
        done.add(n)
        done.update(x for x in names if x in n)  # e.g. "Hubris Circlet" contains no smaller names we want twice
    return out


def linkify_section(sec_html):
    """Hand-written equipment section: league bar after the h2 and buy links inside every <td>."""
    import re as _re
    sec_html = _re.sub(r'(<td>)(.*?)(</td>)', lambda m: m.group(1) + linkify(m.group(2)) + m.group(3), sec_html, flags=_re.S)
    return _re.sub(r'(</h2>)', lambda m: m.group(1) + league_bar(), sec_html, count=1)
