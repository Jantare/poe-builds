"""Monta mercado.json com os preços do poe.ninja para a página Mercado.
Roda no GitHub Actions a cada 30 minutos (e pode rodar à mão). Só usa a biblioteca padrão.
Uso: python3 tools/fetch_prices.py <saída.json>"""
import json, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone

UA = {'User-Agent': 'poe-builds-mercado/1.0 (+https://github.com/Jantare/poe-builds)'}
NJ = 'https://poe.ninja/poe1/api'
EXCHANGE = {  # tipo do poe.ninja -> nome na página
    'Currency': 'Currency', 'Thread': 'Threads', 'Fragment': 'Fragmentos', 'Omen': 'Omens', 'DivinationCard': 'Cartas',
    'Essence': 'Essências', 'Fossil': 'Fossils', 'Resonator': 'Resonators', 'Oil': 'Oils', 'DeliriumOrb': 'Delirium Orbs',
    'Astrolabe': 'Astrolabes', 'Artifact': 'Artefatos', 'Tattoo': 'Tattoos', 'Runegraft': 'Runegrafts',
    'AllflameEmber': 'Allflame Embers', 'EnshroudingCrystal': 'Enshrouding Crystals', 'Ducat': 'Ducats',
    'Viscera': 'Viscera', 'Fate': 'Fates', 'SoulCore': 'Soul Cores',  # da liga: aparecem quando o poe.ninja criar
}
ITEMS = {
    'UniqueWeapon': 'Uniques: armas', 'UniqueArmour': 'Uniques: armaduras', 'UniqueAccessory': 'Uniques: acessórios',
    'UniqueFlask': 'Uniques: frascos', 'UniqueJewel': 'Uniques: jewels', 'UniqueRelic': 'Relics', 'SkillGem': 'Gemas',
    'ClusterJewel': 'Cluster Jewels', 'Map': 'Mapas', 'UniqueMap': 'Mapas únicos', 'Invitation': 'Invitations',
    'BlightedMap': 'Blighted Maps', 'Wombgift': 'Wombgifts',
}
TOP = 60
FARM = {  # o que cada farm do site solta (busca por pedaço do nome)
    'Legion': ['Timeless', 'Enshrouding Crystal', 'Legion Thread'],
    'Ritual': ['Omen of', 'Ritual Vessel', 'Ritual Splinter', 'Ritual Thread', 'Blood-filled Vessel'],
    'Harvest': ['Crystallised Lifeforce'],
    'Threads': [' Thread', 'Threaded', 'Chisel of Threads'],
    'Pinnacles': ['Invitation', 'Fragment of', "Zorath's Eye", "Maven's Writ", 'Crescent Splinter', 'Reality Fragment'],
}


def get(path, **q):
    url = f'{NJ}/{path}?' + urllib.parse.urlencode(q)
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception:
            time.sleep(3 * (i + 1))
    return None


def league():
    st = get('data/index-state') or {}
    for l in st.get('economyLeagues', []):
        if l['name'] not in ('Standard', 'Hardcore') and 'Hardcore' not in l['name'] and 'SSF' not in l['name']:
            return l['name']
    return 'Standard'


GEM_TOP = 40


def gem_trade(l):
    """Busca do trade oficial para esta variação da gema (nível, qualidade, corrompida)."""
    if l.get('tradeFilter'):
        return l['tradeFilter']['query']
    f = {}
    if l.get('gemLevel'): f['gem_level'] = {'min': l['gemLevel']}
    if l.get('gemQuality'): f['quality'] = {'min': l['gemQuality']}
    f['corrupted'] = {'option': bool(l.get('corrupted'))}
    return {'type': l['name'], 'filters': {'misc_filters': {'filters': f}}}


def gems(lines):
    """Grupos da seção Gemas: Empower/Enlighten/Enhance (e Awakened), outras excepcionais (Greater etc.),
    transfiguradas, corrompidas 21/23 e as gemas novas da liga (Trarthus)."""
    groups = {'eee': [], 'excepcionais': [], 'transfiguradas': [], 'corrompidas': [], 'liga': []}
    for l in lines:
        kind = (l.get('metadata') or {}).get('gemKind')
        lv, q, cor = l.get('gemLevel') or 0, l.get('gemQuality') or 0, bool(l.get('corrupted'))
        sp = l.get('sparkLine') or l.get('lowConfidenceSparkLine') or {}
        r = {'n': l['name'], 'c': round(l.get('chaosValue') or 0, 1), 'ch': sp.get('totalChange'),
             'o': l.get('listingCount') or l.get('count') or 0, 'i': l.get('icon', ''),
             'lv': lv, 'q': q, 'cor': cor, 't': gem_trade(l)}
        if l['name'].replace('Awakened ', '') in ('Empower Support', 'Enlighten Support', 'Enhance Support'):
            groups['eee'].append(r)
        elif kind == 'exceptional':
            groups['excepcionais'].append(r)
        elif kind == 'trarthus':
            groups['liga'].append(r)
        elif kind == 'transfigured' and not cor:
            groups['transfiguradas'].append(r)
        if cor and (lv >= 21 or q >= 23) and kind != 'exceptional':
            groups['corrompidas'].append(r)
    out = {}
    for k, rows in groups.items():
        # preço de 1 anúncio só engana: as listas mostram primeiro o que tem ofertas suficientes
        rows.sort(key=lambda r: (r['o'] < 3, -r['c']))
        out[k] = rows[:GEM_TOP]
    return out


def main(out):
    lg = league()
    cats, divine = {}, None
    for t, label in EXCHANGE.items():
        d = get('economy/exchange/current/overview', league=lg, type=t)
        if not d or not d.get('lines'):
            continue
        if t == 'Currency':
            divine = 1 / d['core']['rates']['divine']
        meta = {i['id']: i for i in d.get('items', [])}
        rows = []
        for l in d['lines']:
            m = meta.get(l['id'], {})
            rows.append({'n': m.get('name', l['id']), 'c': round(l['primaryValue'], 2),
                         'ch': (l.get('sparkline') or {}).get('totalChange'),
                         'v': round(l.get('volumePrimaryValue') or 0, 1),
                         'i': ('https://web.poecdn.com' + m['image']) if m.get('image') else ''})
        cats[label] = rows
    gemlines = []
    for t, label in ITEMS.items():
        d = get('economy/stash/current/item/overview', league=lg, type=t)
        if not d or not d.get('lines'):
            continue
        if t == 'SkillGem':
            gemlines = d['lines']
        rows = []
        for l in d['lines']:
            n = l['name']
            if l.get('links'): n += f" ({l['links']}L)"
            if t == 'SkillGem': n += f" {l.get('gemLevel', '')}/{l.get('gemQuality') or 0}" + (' corr.' if l.get('corrupted') else '')
            if t == 'Map' and l.get('mapTier'): n += f" T{l['mapTier']}" if 'Tier' not in n else ''
            sp = l.get('sparkLine') or l.get('lowConfidenceSparkLine') or {}
            rows.append({'n': n, 'c': round(l.get('chaosValue') or 0, 1), 'ch': sp.get('totalChange'),
                         'o': l.get('listingCount') or l.get('count') or 0, 'i': l.get('icon', ''),
                         'b': l.get('baseType') or ''})
        cats[label] = rows
    for k in cats:
        cats[k] = sorted(cats[k], key=lambda r: -r['c'])
    # tudo junto (só o que tem ofertas suficientes, para não pegar preço de 1 anúncio)
    allrows = [dict(r, k=k) for k, rs in cats.items() for r in rs if r.get('o', 99) >= 5]
    top = sorted(allrows, key=lambda r: -r['c'])[:100]
    farm = {}
    for f, keys in FARM.items():
        hits = [dict(r, k=k) for k, rs in cats.items() for r in rs if any(x.lower() in r['n'].lower() for x in keys)]
        seen, uniq = set(), []
        for r in sorted(hits, key=lambda r: -r['c']):
            if r['n'] in seen: continue
            seen.add(r['n']); uniq.append(r)
        farm[f] = uniq[:25]
    data = {'league': lg, 'updated': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'divine': round(divine or 0, 1),
            'top': top, 'farm': farm, 'gems': gems(gemlines), 'cats': {k: v[:TOP] for k, v in cats.items()}}
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    print(lg, 'divine', data['divine'], 'categorias', len(cats), 'top', len(top))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'mercado.json')
