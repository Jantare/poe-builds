#!/usr/bin/env python3
"""
Baú do PoE Builds: lê as abas do seu baú no Path of Exile 1 e calcula o valor em Chaos e Divine.

- Roda no SEU computador. O POESESSID (cookie de login do site da GGG) nunca sai da sua máquina.
- Preços: API pública de economia do poe.ninja (cache local de 15 minutos).
- Gera snapshots/latest.json e snapshots/bau-AAAAMMDD-HHMMSS.json. Arraste esse arquivo na página
  https://jantare.github.io/poe-builds/bau/ para ver as abas, os itens e o histórico.

Uso:  python bau.py            (pergunta conta, liga e abas na primeira vez)
      python bau.py --config   (refaz as perguntas)
      python bau.py --demo     (gera um snapshot de exemplo com itens fictícios e preços reais)
Só usa a biblioteca padrão do Python 3.8+.
"""
import json, os, sys, time, getpass, re, urllib.request, urllib.parse, urllib.error, webbrowser
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, 'bau_config.json')
CACHE = os.path.join(HERE, '.cache')
SNAPS = os.path.join(HERE, 'snapshots')
UA = 'poe-builds-bau/1.0 (+https://github.com/Jantare/poe-builds)'
NINJA = 'https://poe.ninja/poe1/api/economy'
GGG = 'https://www.pathofexile.com/character-window/get-stash-items'
SITE = 'https://jantare.github.io/poe-builds/bau/'

EXCHANGE_TYPES = ['Currency', 'Fragment', 'Omen', 'DivinationCard', 'Essence', 'Fossil', 'Resonator', 'Oil',
                  'DeliriumOrb', 'Astrolabe', 'Artifact', 'Tattoo', 'Runegraft', 'AllflameEmber', 'Ducat',
                  'EnshroudingCrystal', 'DjinnCoin', 'Thread', 'SoulCore']
ITEM_TYPES = ['UniqueWeapon', 'UniqueArmour', 'UniqueAccessory', 'UniqueFlask', 'UniqueJewel', 'UniqueTincture',
              'UniqueRelic', 'SkillGem', 'ImbuedGem', 'ClusterJewel', 'Map', 'BlightedMap', 'UniqueMap', 'ValdoMap',
              'Invitation', 'Memory', 'IncursionTemple', 'Incubator', 'Vial', 'Wombgift', 'ForbiddenJewel', 'ScryingOrb']
CATEGORY = {  # nome mostrado no site
    'Currency': 'Currency', 'Fragment': 'Fragmentos', 'Omen': 'Omens', 'DivinationCard': 'Cartas', 'Essence': 'Essências',
    'Fossil': 'Fossils', 'Resonator': 'Fossils', 'Oil': 'Óleos', 'DeliriumOrb': 'Delirium', 'Astrolabe': 'Atlas',
    'Artifact': 'Expedition', 'Tattoo': 'Tattoos', 'Runegraft': 'Runegrafts', 'AllflameEmber': 'Allflame', 'Ducat': 'Currency',
    'EnshroudingCrystal': 'Mirage', 'DjinnCoin': 'Mirage', 'Thread': 'Threads', 'SoulCore': 'Soul Cores',
    'UniqueWeapon': 'Uniques', 'UniqueArmour': 'Uniques', 'UniqueAccessory': 'Uniques', 'UniqueFlask': 'Uniques',
    'UniqueJewel': 'Uniques', 'UniqueTincture': 'Uniques', 'UniqueRelic': 'Uniques', 'SkillGem': 'Gemas', 'ImbuedGem': 'Gemas',
    'ClusterJewel': 'Jewels', 'Map': 'Mapas', 'BlightedMap': 'Mapas', 'UniqueMap': 'Mapas', 'ValdoMap': 'Mapas',
    'Invitation': 'Fragmentos', 'Memory': 'Atlas', 'IncursionTemple': 'Mapas', 'Incubator': 'Outros', 'Vial': 'Outros',
    'Wombgift': 'Outros', 'ForbiddenJewel': 'Jewels', 'ScryingOrb': 'Outros'}


def http_json(url, headers=None, cache_name=None, max_age=900):
    if cache_name:
        os.makedirs(CACHE, exist_ok=True)
        path = os.path.join(CACHE, cache_name + '.json')
        if os.path.exists(path) and time.time() - os.path.getmtime(path) < max_age:
            with open(path, encoding='utf-8') as f:
                return json.load(f)
    req = urllib.request.Request(url, headers=dict({'User-Agent': UA, 'Accept': 'application/json'}, **(headers or {})))
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.loads(r.read().decode('utf-8'))
                rules = r.headers.get('X-Rate-Limit-Ip-State') or r.headers.get('X-Rate-Limit-Account-State')
                if rules and cache_name is None:
                    time.sleep(rate_pause(rules, r.headers))
                break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = int(e.headers.get('Retry-After') or 60)
                print(f'  Limite de requisições da GGG. Esperando {wait}s...')
                time.sleep(wait + 1)
                continue
            if e.code in (401, 403):
                raise SystemExit('Acesso negado pela GGG (401/403). Confira o POESESSID, a conta (Nome#1234) e se as abas do baú estão visíveis para você logado.')
            if cache_name:  # preço: categoria que não existe nesta liga (ex.: Threads antes da 3.30)
                return None
            raise
        except urllib.error.URLError as e:
            if cache_name:
                print(f'  Sem resposta do poe.ninja para {cache_name}: {e.reason}')
                return None
            raise SystemExit(f'Sem conexão com a GGG: {e.reason}')
    else:
        raise SystemExit('Muitas tentativas sem sucesso. Tente de novo em alguns minutos.')
    if cache_name:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    return data


def rate_pause(state, headers):
    """Respeita X-Rate-Limit: pausa mais se estiver perto do limite."""
    rules = headers.get('X-Rate-Limit-Ip') or headers.get('X-Rate-Limit-Account') or ''
    try:
        lim = [int(x.split(':')[0]) for x in rules.split(',')]
        cur = [int(x.split(':')[0]) for x in state.split(',')]
        near = any(c >= l - 2 for c, l in zip(cur, lim))
    except ValueError:
        near = False
    return 6 if near else 1.6


# ---------------- configuração ----------------
def load_config():
    if os.path.exists(CONFIG):
        with open(CONFIG, encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_config(cfg):
    with open(CONFIG, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def ask(prompt, default=''):
    v = input(f'{prompt}' + (f' [{default}]' if default else '') + ': ').strip()
    return v or default


def setup(cfg):
    print('\n=== Configuração ===')
    cfg['account'] = ask('Nome da conta com o número (ex.: Fulano#1234)', cfg.get('account', ''))
    leagues = http_json(NINJA + '/leagues', cache_name='leagues', max_age=3600) or []
    ids = [l['id'] for l in leagues]
    if ids:
        print('Ligas no poe.ninja:', ', '.join(ids))
    cfg['league'] = ask('Liga', cfg.get('league') or (ids[0] if ids else 'Standard'))
    print('\nO POESESSID é o cookie de login do pathofexile.com (F12 > Application > Cookies).')
    print('Ele dá acesso total à sua conta: nunca compartilhe. Ele fica só neste computador.')
    sess = read_sessid('POESESSID (cole e aperte Enter; o texto não aparece. Enter vazio mantém o atual): ')
    if sess:
        cfg['poesessid'] = sess
    if cfg.get('poesessid') and ask('Salvar o POESESSID neste computador para não perguntar de novo? (s/n)', 's').lower() != 's':
        cfg['_session_only'] = cfg.pop('poesessid')
    tabs = get_tabs(cfg)
    print('\nAbas do baú:')
    for t in tabs:
        print(f"  {t['i']:>3}  {t['n']}  ({t['type']})")
    sel = ask('Quais abas ler? Números separados por vírgula, ou "todas"', cfg.get('tabs_text', 'todas'))
    cfg['tabs_text'] = sel
    save_config({k: v for k, v in cfg.items() if not k.startswith('_')})
    return cfg


def read_sessid(prompt):
    """Lê o POESESSID sem mostrar na tela e confirma o que recebeu (só começo e fim).
    Também aceita a variável de ambiente POESESSID."""
    env = os.environ.get('POESESSID', '').strip()
    if env:
        print('Usando o POESESSID da variável de ambiente.')
        return env
    while True:
        try:
            s = getpass.getpass(prompt)
        except Exception:  # alguns terminais não suportam entrada oculta
            s = input(prompt.replace('o texto não aparece', 'o texto vai aparecer'))
        s = s.strip().strip('"').strip("'")
        if s.lower().startswith('poesessid='):
            s = s.split('=', 1)[1]
        if not s:
            return ''
        if re.fullmatch(r'[0-9a-fA-F]{32}', s):
            print(f'  Recebido: {s[:4]}...{s[-4:]} (32 caracteres)')
            return s
        print(f'  Isso não parece um POESESSID: recebi {len(s)} caracteres, o normal são 32 letras e números (0-9, a-f).')
        print('  Copie de novo o "Value" da linha POESESSID e cole aqui (Ctrl+V, ou botão direito no cmd).')


def session(cfg):
    s = cfg.get('poesessid') or cfg.get('_session_only')
    if not s:
        s = read_sessid('POESESSID (cole e aperte Enter; o texto não aparece): ')
        cfg['_session_only'] = s
    return s


def stash_request(cfg, tab_index, tabs_flag):
    q = urllib.parse.urlencode({'accountName': cfg['account'], 'realm': 'pc', 'league': cfg['league'],
                                'tabs': tabs_flag, 'tabIndex': tab_index})
    return http_json(f'{GGG}?{q}', headers={'Cookie': 'POESESSID=' + session(cfg)})


def get_tabs(cfg):
    data = stash_request(cfg, 0, 1)
    return data.get('tabs', [])


# ---------------- preços ----------------
def norm(s):
    return re.sub(r'\s+', ' ', (s or '').strip().lower())


def load_prices(league):
    prices = {'exchange': {}, 'items': {}, 'icons': {}, 'divine': None}
    lg = re.sub(r'\W', '_', league)
    for t in EXCHANGE_TYPES:
        d = http_json(f'{NINJA}/exchange/current/overview?' + urllib.parse.urlencode({'league': league, 'type': t}), cache_name=f'ex_{lg}_{t}')
        if not d or 'lines' not in d:
            continue
        names = {it['id']: it for it in d.get('items', [])}
        for ln in d['lines']:
            it = names.get(ln['id'])
            if not it:
                continue
            prices['exchange'][norm(it['name'])] = (ln['primaryValue'], t)
            if it.get('image'):
                prices['icons'][norm(it['name'])] = 'https://web.poecdn.com' + it['image']
        rate = (d.get('core') or {}).get('rates', {}).get('divine')
        if t == 'Currency' and rate:
            prices['divine'] = 1 / rate
    for t in ITEM_TYPES:
        d = http_json(f'{NINJA}/stash/current/item/overview?' + urllib.parse.urlencode({'league': league, 'type': t}), cache_name=f'it_{lg}_{t}')
        if not d or 'lines' not in d:
            continue
        for ln in d['lines']:
            ln['_type'] = t
            prices['items'].setdefault(norm(ln['name']), []).append(ln)
    if not prices['divine']:
        prices['divine'] = prices['exchange'].get('divine orb', (200, ''))[0]
    return prices


def prop(item, name):
    for p in item.get('properties', []) or []:
        if p.get('name') == name and p.get('values'):
            return p['values'][0][0]
    return None


def links(item):
    groups = {}
    for s in item.get('sockets', []) or []:
        groups[s['group']] = groups.get(s['group'], 0) + 1
    return max(groups.values()) if groups else 0


def price_item(item, P):
    """Devolve (preço unitário em chaos, categoria)."""
    name, tl = item.get('name') or '', item.get('typeLine') or ''
    base = item.get('baseType') or tl
    frame = item.get('frameType')
    # currency, fragmentos, cartas, essências etc.
    for key in (norm(tl), norm(base)):
        if key in P['exchange']:
            v, t = P['exchange'][key]
            return v, CATEGORY.get(t, 'Outros')
    # gemas
    if frame == 4:
        cands = P['items'].get(norm(tl)) or P['items'].get(norm(base)) or []
        if cands:
            lvl = int(re.sub(r'\D', '', str(prop(item, 'Level') or '1')) or 1)
            q = int(re.sub(r'\D', '', str(prop(item, 'Quality') or '0')) or 0)
            cor = bool(item.get('corrupted'))
            def score(l):
                return (abs((l.get('gemLevel') or 1) - lvl) * 3 + abs((l.get('gemQuality') or 0) - q) / 5
                        + (0 if bool(l.get('corrupted')) == cor else 4))
            best = min(cands, key=score)
            return best.get('chaosValue') or 0, 'Gemas'
        return 0, 'Gemas'
    # uniques
    if frame in (3, 9) and name:
        cands = [l for l in P['items'].get(norm(name), []) if not l.get('baseType') or norm(l['baseType']) == norm(base)] or P['items'].get(norm(name), [])
        if cands:
            lk = links(item)
            lk = lk if lk >= 5 else 0
            same = [l for l in cands if (l.get('links') or 0) == lk] or cands
            unc = [l for l in same if not l.get('corrupted')] or same
            best = min(unc, key=lambda l: l.get('chaosValue') or 0)
            return best.get('chaosValue') or 0, CATEGORY.get(best['_type'], 'Uniques')
    # mapas
    tier = prop(item, 'Map Tier')
    if tier:
        cands = P['items'].get(norm(base)) or P['items'].get(norm(tl)) or []
        cands = [l for l in cands if str(l.get('mapTier') or '') == str(tier)] or cands
        if cands:
            return min(l.get('chaosValue') or 0 for l in cands), 'Mapas'
        return 0, 'Mapas'
    # outros por nome
    for key in (norm(name), norm(tl), norm(base)):
        if key and key in P['items']:
            l = min(P['items'][key], key=lambda x: x.get('chaosValue') or 0)
            return l.get('chaosValue') or 0, CATEGORY.get(l['_type'], 'Outros')
    return 0, 'Sem preço'


def item_label(item):
    name, tl = item.get('name') or '', item.get('typeLine') or ''
    if item.get('frameType') == 4:
        lvl = re.sub(r'\D', '', str(prop(item, 'Level') or '')) or '1'
        q = re.sub(r'\D', '', str(prop(item, 'Quality') or '')) or '0'
        return f'{tl} - {lvl}/{q}'
    return f'{name} {tl}'.strip() if name else tl


# ---------------- snapshot ----------------
def build_snapshot(cfg, tabs, items_by_tab, P):
    out_tabs, out_items = [], []
    for t in tabs:
        c = t.get('colour') or {}
        out_tabs.append({'i': t['i'], 'name': t['n'], 'type': t.get('type', ''),
                         'color': '#%02x%02x%02x' % (c.get('r', 120), c.get('g', 120), c.get('b', 120))})
    for ti, items in items_by_tab.items():
        for it in items:
            qty = it.get('stackSize') or 1
            unit, cat = price_item(it, P)
            out_items.append({'name': item_label(it), 'tab': ti, 'qty': qty, 'price': round(unit, 4),
                              'total': round(unit * qty, 2), 'cat': cat, 'icon': it.get('icon', ''),
                              'rarity': it.get('frameType', 0)})
    total = sum(i['total'] for i in out_items)
    return {'app': 'poe-builds-bau', 'version': 1, 'time': datetime.now().isoformat(timespec='seconds'),
            'account': cfg.get('account', ''), 'league': cfg.get('league', ''), 'divine': round(P['divine'], 2),
            'total': round(total, 2), 'tabs': out_tabs, 'items': out_items}


def save_snapshot(snap):
    os.makedirs(SNAPS, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    path = os.path.join(SNAPS, f'bau-{stamp}.json')
    for p in (path, os.path.join(SNAPS, 'latest.json')):
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(snap, f, ensure_ascii=False)
    hist_path = os.path.join(SNAPS, 'history.json')
    hist = []
    if os.path.exists(hist_path):
        with open(hist_path, encoding='utf-8') as f:
            hist = json.load(f)
    cats = {}
    for i in snap['items']:
        cats[i['cat']] = round(cats.get(i['cat'], 0) + i['total'], 2)
    hist.append({'time': snap['time'], 'total': snap['total'], 'divine': snap['divine'], 'cats': cats})
    with open(hist_path, 'w', encoding='utf-8') as f:
        json.dump(hist, f)
    return path


def demo():
    """Snapshot de exemplo: itens fictícios, preços reais da Standard."""
    cfg = {'account': 'Exemplo#0000', 'league': 'Standard'}
    P = load_prices('Standard')
    tabs = [{'i': 0, 'n': 'Currency', 'type': 'CurrencyStash', 'colour': {'r': 196, 'g': 160, 'b': 70}},
            {'i': 1, 'n': 'Cartas', 'type': 'DivinationCardStash', 'colour': {'r': 90, 'g': 140, 'b': 210}},
            {'i': 2, 'n': 'Gemas', 'type': 'NormalStash', 'colour': {'r': 80, 'g': 170, 'b': 110}},
            {'i': 3, 'n': 'Fragmentos', 'type': 'FragmentStash', 'colour': {'r': 150, 'g': 90, 'b': 200}}]
    mk = lambda tl, n=1, **kw: dict({'typeLine': tl, 'baseType': tl, 'stackSize': n, 'frameType': 5,
                                     'icon': P['icons'].get(norm(tl), '')}, **kw)
    items = {0: [mk('Divine Orb', 14), mk('Chaos Orb', 520), mk('Orb of Fusing', 300), mk('Orb of Alchemy', 120),
                 mk('Exalted Orb', 6), mk('Orb of Regret', 50), mk('Chromatic Orb', 200), mk('Vaal Orb', 40)],
             1: [mk('The Journalist', 2, frameType=6), mk('Dark Dreams', 1, frameType=6), mk('The Wolf', 3, frameType=6)],
             2: [dict(typeLine='Spark', baseType='Spark', frameType=4, icon='', properties=[{'name': 'Level', 'values': [['20', 0]]}, {'name': 'Quality', 'values': [['+20%', 0]]}]),
                 dict(typeLine='Malevolence', baseType='Malevolence', frameType=4, icon='', properties=[{'name': 'Level', 'values': [['20', 0]]}])],
             3: [mk('Sacrifice at Dawn', 8, frameType=0), mk("Maven's Writ", 1, frameType=0)]}
    snap = build_snapshot(cfg, tabs, items, P)
    snap['demo'] = True
    return snap


def main():
    if '--demo' in sys.argv:
        snap = demo()
        path = os.path.join(HERE, 'exemplo.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(snap, f, ensure_ascii=False)
        print('Exemplo salvo em', path, '| total', round(snap['total']), 'c')
        return
    cfg = load_config()
    if '--config' in sys.argv or not cfg.get('account') or not cfg.get('tabs_text'):
        cfg = setup(cfg)
    print(f"\nConta: {cfg['account']} | Liga: {cfg['league']}")
    print('Buscando preços no poe.ninja...')
    P = load_prices(cfg['league'])
    print(f"  Divine = {P['divine']:.0f} chaos")
    tabs = get_tabs(cfg)
    want = cfg.get('tabs_text', 'todas')
    sel = tabs if want.lower().startswith('tod') else [t for t in tabs if str(t['i']) in [x.strip() for x in want.split(',')]]
    items_by_tab = {}
    for t in sel:
        print(f"  Lendo aba {t['i']}: {t['n']}")
        data = stash_request(cfg, t['i'], 0)
        items_by_tab[t['i']] = data.get('items', [])
        if t.get('type') in ('MapStash', 'UniqueStash') and not items_by_tab[t['i']]:
            print('    (abas de Mapas e de Uniques especiais não são lidas por este acesso)')
    snap = build_snapshot(cfg, sel, items_by_tab, P)
    path = save_snapshot(snap)
    d = snap['total'] / snap['divine'] if snap['divine'] else 0
    print(f"\nTotal: {snap['total']:.0f} chaos = {d:.1f} divine")
    print('Snapshot salvo em', path)
    print('Abra', SITE, 'e arraste o arquivo snapshots/latest.json (ou history.json para o gráfico).')
    if input('Abrir o site agora? (s/n) [s]: ').strip().lower() in ('', 's'):
        webbrowser.open(SITE)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nCancelado.')
