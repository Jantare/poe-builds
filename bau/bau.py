#!/usr/bin/env python3
"""
Baú do PoE Builds: mostra quanto vale o seu baú do Path of Exile 1 em Chaos e Divine, aba por aba.

- Abre um app no seu navegador (http://127.0.0.1:7373), só acessível do seu próprio computador.
- O POESESSID (cookie de login do site da GGG) fica só nesta máquina e só é enviado ao pathofexile.com.
- Preços: API pública de economia do poe.ninja (cache local de 15 minutos).
- Configuração, snapshots e histórico ficam na mesma pasta deste arquivo (ou do bau.exe).

- Verificador de preço (opcional): aperte Ctrl+C num item do jogo e o preço aparece perto do mouse (precheck.py).

Uso:  bau.exe  ou  python bau.py   (abre o app no navegador)
      python bau.py --cli          (versão de terminal)
      python bau.py --demo         (gera exemplo.json com itens fictícios e preços reais)
Só usa a biblioteca padrão do Python 3.8+.
"""
import json, os, sys, time, getpass, re, urllib.request, urllib.parse, urllib.error, webbrowser
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import precheck

FROZEN = getattr(sys, 'frozen', False)  # rodando como bau.exe (PyInstaller)
HERE = os.path.dirname(sys.executable if FROZEN else os.path.abspath(__file__))  # onde ficam config e snapshots
BUNDLE = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))  # onde ficam app.html e style.css
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


class BauError(Exception):
    """Erro com mensagem para mostrar ao usuário."""


# ---------------- visual do terminal ----------------
def _enable_terminal():
    """Liga cores ANSI e UTF-8 no console do Windows 10/11.
    No bau.exe (sem janela) não existe console: sys.stdout/stderr vêm vazios (None)."""
    has_console = sys.stdout is not None and sys.stderr is not None
    if sys.stdout is None:
        sys.stdout = open(os.devnull, 'w', encoding='utf-8')
    if sys.stderr is None:
        sys.stderr = open(os.devnull, 'w', encoding='utf-8')
    if not has_console:
        return False
    if os.name == 'nt':
        os.system('')  # ativa o modo VT do console
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(encoding='utf-8')
        except Exception:
            pass
    if os.environ.get('FORCE_COLOR'):
        return True
    try:
        tty = sys.stdout.isatty()
    except Exception:
        tty = False
    return not os.environ.get('NO_COLOR') and (tty or os.name == 'nt')


COLOR = _enable_terminal()
def _c(code):
    return (lambda t: f'\033[{code}m{t}\033[0m') if COLOR else (lambda t: str(t))
BLUE, GOLD, GREEN, RED, GRAY, BOLD, CYAN = _c('38;2;108;184;255'), _c('38;2;214;178;110'), _c('38;2;89;196;138'), _c('38;2;255;111;97'), _c('38;2;143;155;179'), _c('1'), _c('38;2;160;220;255')


def swatch(hexcolor):
    if not COLOR or not hexcolor:
        return '■'
    r, g, b = int(hexcolor[1:3], 16), int(hexcolor[3:5], 16), int(hexcolor[5:7], 16)
    return f'\033[38;2;{r};{g};{b}m■\033[0m'


def banner():
    w = 58
    print()
    print(BLUE('  ╔' + '═' * w + '╗'))
    print(BLUE('  ║') + GOLD(BOLD('  B A Ú'.ljust(20))) + GRAY('PoE Builds · valor do seu baú'.rjust(w - 20 - 2))+ '  ' + BLUE('║'))
    print(BLUE('  ║') + GRAY('  Chaos e Divine por aba, preços do poe.ninja'.ljust(w)) + BLUE('║'))
    print(BLUE('  ╚' + '═' * w + '╝'))


def section(title):
    print('\n  ' + GOLD(BOLD(title)) + ' ' + BLUE('─' * max(4, 54 - len(title))))


def info(msg):
    print('  ' + GRAY('·') + ' ' + msg)


def good(msg):
    print('  ' + GREEN('✔') + ' ' + msg)


def warn(msg):
    print('  ' + GOLD('!') + ' ' + msg)


def bad(msg):
    print('  ' + RED('✖') + ' ' + msg)


def progress(i, n, label):
    width = 26
    done = int(width * i / max(n, 1))
    bar = BLUE('█' * done) + GRAY('░' * (width - done))
    sys.stdout.write(f'\r  {bar} {i}/{n}  {label[:28]:<28}')
    sys.stdout.flush()
    if i >= n:
        print()


def fmt_val(c, divine):
    if divine and c >= divine:
        return f'{c / divine:,.1f}d'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f'{c:,.0f}c'.replace(',', '.')


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
                warn(f'Limite de requisições da GGG. Esperando {wait}s...')
                time.sleep(wait + 1)
                continue
            if e.code in (401, 403):
                raise BauError('Acesso negado pela GGG. Confira o POESESSID (pode ter expirado se você saiu da conta) e o nome da conta com o número, exatamente como no site (ex.: Hygopenido#4999).')
            if cache_name:  # preço: categoria que não existe nesta liga (ex.: Threads antes da 3.30)
                return None
            if e.code == 404:
                raise BauError('A GGG não achou essa conta ou liga. Confira o nome da conta com o número e a liga.')
            raise BauError(f'A GGG respondeu com erro {e.code}. Tente de novo em alguns minutos.')
        except urllib.error.URLError as e:
            if cache_name:
                warn(f'Sem resposta do poe.ninja para {cache_name}: {e.reason}')
                return None
            raise BauError(f'Sem conexão com o site da GGG: {e.reason}')
    else:
        raise BauError('A GGG limitou as requisições. Tente de novo em alguns minutos.')
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
    v = input('  ' + BLUE('›') + ' ' + prompt + (GRAY(f' [{default}]') if default else '') + ': ').strip()
    return v or default


def setup(cfg):
    section('Configuração')
    cfg['account'] = ask('Nome da conta com o número (ex.: Fulano#1234)', cfg.get('account', ''))
    ids = list_leagues()
    if ids:
        info('Ligas no poe.ninja: ' + CYAN(', '.join(ids)))
    cfg['league'] = ask('Liga', cfg.get('league') or (ids[0] if ids else 'Standard'))
    section('Login (POESESSID)')
    info('É o cookie de login do pathofexile.com: F12 > Application > Cookies > POESESSID.')
    warn('Ele dá acesso total à sua conta. Nunca compartilhe. Fica só neste computador.')
    if cfg.get('poesessid') and ask('Já existe um POESESSID salvo. Trocar? (s/n)', 'n').lower() != 's':
        sess = ''
    else:
        sess = read_sessid('POESESSID: ')
    if sess:
        cfg['poesessid'] = sess
    if cfg.get('poesessid') and ask('Salvar o POESESSID neste computador para não perguntar de novo? (s/n)', 's').lower() != 's':
        cfg['_session_only'] = cfg.pop('poesessid')
    tabs = get_tabs(cfg)
    section('Abas do baú')
    for t in tabs:
        c = t.get('colour') or {}
        hx = '#%02x%02x%02x' % (c.get('r', 120), c.get('g', 120), c.get('b', 120))
        print(f"   {GRAY(str(t['i']).rjust(3))}  {swatch(hx)} {t['n']}  {GRAY('(' + t.get('type', '') + ')')}")
    sel = ask('Quais abas ler? Números separados por vírgula, ou "todas"', cfg.get('tabs_text', 'todas'))
    cfg['tabs_text'] = sel
    save_config({k: v for k, v in cfg.items() if not k.startswith('_')})
    return cfg


def masked_input(prompt):
    """Entrada que mostra * para cada caractere (Windows: msvcrt; outros: getpass sem eco)."""
    try:
        import msvcrt
    except ImportError:
        return getpass.getpass(prompt + '(o texto não aparece) ')
    sys.stdout.write(prompt); sys.stdout.flush()
    buf = []
    while True:
        ch = msvcrt.getwch()
        if ch in ('\r', '\n'):
            print(); return ''.join(buf)
        if ch == '\x03':
            raise KeyboardInterrupt
        if ch == '\x16':  # Ctrl+V que o terminal não colou: lê a área de transferência
            txt = clipboard_text()
            buf.extend(txt); sys.stdout.write('*' * len(txt)); sys.stdout.flush(); continue
        if ch in ('\b', '\x7f'):
            if buf:
                buf.pop(); sys.stdout.write('\b \b'); sys.stdout.flush()
            continue
        if ch in ('\x00', '\xe0'):  # teclas especiais (setas etc.)
            msvcrt.getwch(); continue
        buf.append(ch); sys.stdout.write('*'); sys.stdout.flush()


def clipboard_text():
    """Lê o texto copiado (Windows: PowerShell; macOS: pbpaste; Linux: xclip/wl-paste)."""
    import subprocess
    cmds = [['powershell', '-NoProfile', '-Command', 'Get-Clipboard'], ['pbpaste'],
            ['wl-paste', '-n'], ['xclip', '-selection', 'clipboard', '-o']]
    for c in cmds:
        try:
            out = subprocess.run(c, capture_output=True, text=True, timeout=8)
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            continue
    try:
        import tkinter
        r = tkinter.Tk(); r.withdraw(); t = r.clipboard_get(); r.destroy()
        return (t or '').strip()
    except Exception:
        return ''


def read_sessid(prompt):
    """Lê o POESESSID sem mostrar na tela e confirma o que recebeu (só começo e fim).
    Também aceita a variável de ambiente POESESSID."""
    env = os.environ.get('POESESSID', '').strip()
    if env:
        good('Usando o POESESSID da variável de ambiente.')
        return env
    info('Copie o ' + BOLD('Value') + ' da linha POESESSID no navegador e então:')
    info(BOLD('ENTER') + ' aqui: eu pego o que você copiou, ou')
    info('cole/digite (aparecem ' + BLUE('*') + ') e aperte ' + BOLD('ENTER') + '.')
    while True:
        s = masked_input('  ' + BLUE('›') + ' POESESSID: ')
        if s == '':
            s = clipboard_text()
            if not s:
                bad('Não achei nada copiado. Copie o Value do POESESSID e aperte Enter de novo, ou cole aqui.')
                continue
            good('Peguei o que estava copiado.')
        s = s.strip().strip('"').strip("'")
        if s.lower().startswith('poesessid='):
            s = s.split('=', 1)[1]
        if not s:
            return ''
        if re.fullmatch(r'[0-9a-fA-F]{32}', s):
            good(f'Recebido: {s[:4]}...{s[-4:]} ' + GRAY('(32 caracteres)'))
            return s
        bad(f'Isso não parece um POESESSID: recebi {len(s)} caracteres, o normal são 32 letras e números (0-9, a-f).')
        info('Copie de novo o "Value" da linha POESESSID e cole aqui.')


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


def list_leagues():
    """Ligas de trade: lista oficial da GGG (tem a liga nova desde o primeiro minuto) + as do poe.ninja."""
    out = []
    try:
        ggg = http_json('https://www.pathofexile.com/api/leagues?type=main', cache_name='leagues_ggg', max_age=900) or []
        ids = [l['id'] for l in ggg if 'SSF' not in l['id'] and 'Ruthless' not in l['id'] and 'Solo Self' not in l['id']]
        out = [i for i in ids if i not in ('Standard', 'Hardcore')] + [i for i in ids if i in ('Standard', 'Hardcore')]
    except Exception:
        pass
    try:
        for l in http_json(NINJA + '/leagues', cache_name='leagues', max_age=900) or []:
            if l['id'] not in out:
                out.append(l['id'])
    except Exception:
        pass
    return out or ['Standard']


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


def summary(snap, path):
    dv = snap['divine']
    tabs = {t['i']: t for t in snap['tabs']}
    by_tab = {}
    for it in snap['items']:
        by_tab[it['tab']] = by_tab.get(it['tab'], 0) + it['total']
    top = max(by_tab.values() or [1]) or 1
    section('Resultado')
    for i, v in sorted(by_tab.items(), key=lambda kv: -kv[1]):
        t = tabs.get(i, {})
        bar = BLUE('▇' * max(1, int(18 * v / top))) if v else GRAY('·')
        print(f"   {swatch(t.get('color'))} {t.get('name', i)[:22]:<22} {fmt_val(v, dv):>10}  {bar}")
    best = sorted(snap['items'], key=lambda x: -x['total'])[:5]
    if best and best[0]['total']:
        section('Mais valiosos')
        for it in best:
            if it['total']:
                print(f"   {GOLD('◆')} {it['name'][:34]:<34} {GRAY('x' + str(it['qty'])):>8} {fmt_val(it['total'], dv):>10}")
    unpriced = sum(1 for it in snap['items'] if not it['price'])
    total = snap['total']
    print()
    print(BLUE('  ┌' + '─' * 44 + '┐'))
    chaos_txt = f'{total:,.0f}'.replace(',', '.')
    line = f"TOTAL  {fmt_val(total, dv)}  ·  {chaos_txt} chaos"
    print(BLUE('  │ ') + GOLD(BOLD(line.ljust(43))) + BLUE('│'))
    print(BLUE('  │ ') + GRAY(f'Divine a {dv:.0f}c · {len(snap["items"])} itens · {unpriced} sem preço'.ljust(43)) + BLUE('│'))
    print(BLUE('  └' + '─' * 44 + '┘'))
    good('Snapshot salvo: ' + GRAY(os.path.relpath(path, HERE)))
    info('No site, arraste ' + BOLD('snapshots/latest.json') + ' e ' + BOLD('history.json') + ': ' + CYAN(SITE))


def cli_main():
    banner()
    if '--demo' in sys.argv:
        snap = demo()
        path = os.path.join(HERE, 'exemplo.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(snap, f, ensure_ascii=False)
        summary(snap, path)
        return
    cfg = load_config()
    if '--config' in sys.argv or not cfg.get('account') or not (cfg.get('tabs_text') or cfg.get('tabs')):
        cfg = setup(cfg)
    section('Lendo o baú')
    info(f"Conta {BOLD(cfg['account'])} · Liga {BOLD(cfg['league'])}")
    info('Buscando preços no poe.ninja...')
    P = load_prices(cfg['league'])
    good('Preços carregados · Divine = ' + GOLD(f"{P['divine']:.0f}c"))
    tabs = get_tabs(cfg)
    want = cfg.get('tabs_text', 'todas')
    if cfg.get('tabs'):
        want = ','.join(str(i) for i in cfg['tabs'])
    sel = tabs if want.lower().startswith('tod') else [t for t in tabs if str(t['i']) in [x.strip() for x in want.split(',')]]
    items_by_tab, skipped = {}, []
    for k, t in enumerate(sel, 1):
        progress(k - 1, len(sel), t['n'])
        data = stash_request(cfg, t['i'], 0)
        items_by_tab[t['i']] = data.get('items', [])
        if t.get('type') in ('MapStash', 'UniqueStash') and not items_by_tab[t['i']]:
            skipped.append(t['n'])
        progress(k, len(sel), t['n'])
    for n in skipped:
        warn(f'"{n}": abas de Mapas e de Uniques especiais não são lidas por este acesso.')
    snap = build_snapshot(cfg, sel, items_by_tab, P)
    path = save_snapshot(snap)
    summary(snap, path)
    if ask('Abrir o site agora? (s/n)', 's').lower() == 's':
        webbrowser.open(SITE)


# ---------------- app local (navegador) ----------------
import threading, secrets, socket
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

PORT = 7373
TOKEN = secrets.token_urlsafe(24)
LAST_PING = [time.time()]
JOB = {'running': False, 'done': 0, 'total': 0, 'label': '', 'error': '', 'finished': None}
LOG = os.path.join(HERE, 'bau.log')
CHECKER = None  # verificador de preço (precheck.Checker), criado no app_main


def log(msg):
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat(timespec='seconds')} {msg}\n")
    except OSError:
        pass


def read_json(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def public_config(cfg):
    return {'account': cfg.get('account', ''), 'league': cfg.get('league', ''), 'tabs': cfg.get('tabs', []),
            'has_session': bool(cfg.get('poesessid') or cfg.get('_session_only')), 'session_saved': bool(cfg.get('poesessid'))}


def pricecheck_state(cfg):
    c = CHECKER
    return {'enabled': bool(c and c.enabled), 'status': c.status if c else 'desligado',
            'league': cfg.get('league') or 'Standard', 'last': c.last if c else None}


def list_snapshots():
    if not os.path.isdir(SNAPS):
        return []
    return sorted(f for f in os.listdir(SNAPS) if f.startswith('bau-') and f.endswith('.json'))


def refresh_job(cfg):
    JOB.update(running=True, done=0, total=0, label='Buscando preços no poe.ninja', error='', warn='', finished=None)
    try:
        P = load_prices(cfg['league'])
        tabs = get_tabs(cfg)
        want = set(cfg.get('tabs') or [t['i'] for t in tabs])
        sel = [t for t in tabs if t['i'] in want]
        JOB.update(total=len(sel))
        items_by_tab = {}
        for k, t in enumerate(sel, 1):
            JOB.update(label=f"Lendo a aba {t['n']}", done=k - 1)
            items_by_tab[t['i']] = stash_request(cfg, t['i'], 0).get('items', [])
            JOB.update(done=k)
        save_snapshot(build_snapshot(cfg, sel, items_by_tab, P))
        if not P['exchange'] and not P['items']:
            JOB['warn'] = f"O poe.ninja ainda não tem preços da liga {cfg['league']} (costuma levar algumas horas depois da abertura). Os itens foram lidos, mas aparecem sem preço. Atualize o baú de novo mais tarde."
        JOB.update(label='Pronto', finished=datetime.now().isoformat(timespec='seconds'))
    except BauError as e:
        JOB.update(error=str(e))
    except Exception as e:  # mostra o erro na página em vez de travar o app
        log(f'erro na atualização: {e!r}')
        JOB.update(error=f'Erro inesperado: {e}. Detalhes em bau.log.')
    finally:
        JOB['running'] = False


class Handler(BaseHTTPRequestHandler):
    cfg = None
    server_version = 'Bau'

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype='application/json; charset=utf-8'):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(data)

    def _allowed(self, api):
        host = (self.headers.get('Host') or '').split(':')[0]
        if host not in ('127.0.0.1', 'localhost'):  # bloqueia DNS rebinding
            return False
        return (not api) or secrets.compare_digest(self.headers.get('X-Bau-Token', ''), TOKEN)

    def _body(self):
        n = int(self.headers.get('Content-Length') or 0)
        if n > 100_000:
            return {}
        try:
            return json.loads(self.rfile.read(n) or b'{}')
        except ValueError:
            return {}

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        api = path.startswith('/api/')
        if not self._allowed(api):
            return self._send(403, {'error': 'proibido'})
        if path in ('/', '/index.html'):
            html = open(os.path.join(BUNDLE, 'app.html'), encoding='utf-8').read()
            html = html.replace('<!--BAU_LOCAL-->', f'<script>window.BAU_LOCAL={{token:{json.dumps(TOKEN)}}}</script>')
            return self._send(200, html.encode('utf-8'), 'text/html; charset=utf-8')
        if path == '/assets/style.css':
            for c in (os.path.join(BUNDLE, 'style.css'), os.path.join(BUNDLE, '..', 'assets', 'style.css')):
                if os.path.exists(c):
                    return self._send(200, open(c, 'rb').read(), 'text/css; charset=utf-8')
            return self._send(404, {'error': 'css'})
        cfg = self.cfg
        if path == '/api/state':
            hist = read_json(os.path.join(SNAPS, 'history.json'), [])
            latest = read_json(os.path.join(SNAPS, 'latest.json'), None)
            leagues = list_leagues()
            return self._send(200, {'config': public_config(cfg), 'leagues': leagues, 'latest': latest, 'history': hist,
                                    'snapshots': list_snapshots(), 'job': JOB, 'pricecheck': pricecheck_state(cfg)})
        if path == '/api/snapshot':
            name = urllib.parse.parse_qs(self.path.split('?', 1)[-1]).get('f', [''])[0]
            if name not in list_snapshots():
                return self._send(404, {'error': 'snapshot não encontrado'})
            return self._send(200, read_json(os.path.join(SNAPS, name), None))
        if path == '/api/progress':
            return self._send(200, JOB)
        if path == '/api/pricecheck':
            return self._send(200, pricecheck_state(cfg))
        if path == '/api/ping':
            LAST_PING[0] = time.time()
            return self._send(200, {'ok': True})
        return self._send(404, {'error': 'não encontrado'})

    def do_POST(self):
        path = self.path.split('?', 1)[0]
        if not self._allowed(True):
            return self._send(403, {'error': 'proibido'})
        cfg, b = self.cfg, self._body()
        try:
            if path == '/api/connect':
                acc, league, sess = (b.get('account') or '').strip(), (b.get('league') or '').strip(), (b.get('poesessid') or '').strip()
                if sess.lower().startswith('poesessid='):
                    sess = sess.split('=', 1)[1]
                if not re.fullmatch(r'[^#\s]+#\d{4}', acc):
                    return self._send(400, {'error': 'Use o nome da conta com o número, como aparece no site: Nome#1234.'})
                if sess and not re.fullmatch(r'[0-9a-fA-F]{32}', sess):
                    return self._send(400, {'error': f'Isso não parece um POESESSID: tem {len(sess)} caracteres. O certo são 32 letras e números (0-9, a-f).'})
                cfg.update(account=acc, league=league or 'Standard')
                if sess:
                    cfg.pop('poesessid', None); cfg.pop('_session_only', None)
                    cfg['poesessid' if b.get('save') else '_session_only'] = sess
                elif not (cfg.get('poesessid') or cfg.get('_session_only')):
                    return self._send(400, {'error': 'Cole o POESESSID.'})
                tabs = get_tabs(cfg)
                save_config({k: v for k, v in cfg.items() if not k.startswith('_')})
                out = []
                for t in tabs:
                    c = t.get('colour') or {}
                    out.append({'i': t['i'], 'name': t['n'], 'type': t.get('type', ''),
                                'color': '#%02x%02x%02x' % (c.get('r', 120), c.get('g', 120), c.get('b', 120))})
                return self._send(200, {'tabs': out, 'config': public_config(cfg)})
            if path == '/api/tabs':
                cfg['tabs'] = [int(i) for i in b.get('tabs', [])]
                save_config({k: v for k, v in cfg.items() if not k.startswith('_')})
                return self._send(200, {'config': public_config(cfg)})
            if path == '/api/refresh':
                if JOB['running']:
                    return self._send(409, {'error': 'Já está atualizando.'})
                if not (cfg.get('poesessid') or cfg.get('_session_only')) or not cfg.get('account'):
                    return self._send(400, {'error': 'Conecte sua conta primeiro.'})
                threading.Thread(target=refresh_job, args=(cfg,), daemon=True).start()
                return self._send(200, {'started': True})
            if path == '/api/pricecheck':
                lg = (b.get('league') or '').strip()
                if lg:
                    cfg['league'] = lg
                cfg['price_check'] = bool(b.get('enabled'))
                save_config({k: v for k, v in cfg.items() if not k.startswith('_')})
                CHECKER.set(cfg['price_check'], cfg.get('league') or 'Standard')
                return self._send(200, pricecheck_state(cfg))
            if path == '/api/pricecheck/test':
                CHECKER.test(precheck.SAMPLE)
                return self._send(200, {'ok': True})
            if path == '/api/forget':
                cfg.pop('poesessid', None); cfg.pop('_session_only', None)
                save_config({k: v for k, v in cfg.items() if not k.startswith('_')})
                return self._send(200, {'config': public_config(cfg)})
            if path == '/api/quit':
                self._send(200, {'bye': True})
                threading.Thread(target=self.server.shutdown, daemon=True).start()
                return
        except BauError as e:
            return self._send(400, {'error': str(e)})
        return self._send(404, {'error': 'não encontrado'})


def already_running():
    try:
        with socket.create_connection(('127.0.0.1', PORT), timeout=0.5):
            return True
    except OSError:
        return False


def app_main():
    if already_running():
        webbrowser.open(f'http://127.0.0.1:{PORT}/')  # já aberto: só mostra de novo
        return
    global CHECKER
    Handler.cfg = load_config()
    srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    CHECKER = precheck.Checker(load_prices, price_item, log)
    if Handler.cfg.get('price_check'):
        CHECKER.set(True, Handler.cfg.get('league') or 'Standard')
    def watchdog():  # fecha sozinho uns minutos depois que a página foi fechada (menos com o verificador ligado)
        while True:
            time.sleep(30)
            if time.time() - LAST_PING[0] > 300 and not JOB['running'] and not CHECKER.enabled:
                srv.shutdown(); return
    threading.Thread(target=watchdog, daemon=True).start()
    url = f'http://127.0.0.1:{PORT}/'
    log('app iniciado em ' + url)
    if not FROZEN:
        print(f'Baú aberto em {url} (feche a página ou use "Fechar o app" para encerrar)')
    webbrowser.open(url)
    srv.serve_forever()


def selftest_precos():
    """Usado pelo GitHub Actions no .exe: testa a leitura do item e abre a janelinha por 2 segundos."""
    out = []
    try:
        P = {'exchange': {'divine orb': (180.0, 'Currency')}, 'items': {}, 'icons': {}, 'divine': 180.0}
        r = precheck.evaluate(precheck.SAMPLE, P, 'Standard', price_item)
        out.append('parse ' + ('ok' if r and r['lines'] and r['lines'][0][1] == '1,00 divine' else 'fail ' + repr(r)))
        c = precheck.Checker(lambda lg: P, price_item, log)
        c.P, c.P_league, c.P_time = P, 'Standard', time.time()
        c.test(precheck.SAMPLE)
        for _ in range(40):  # até 10 s
            time.sleep(0.25)
            if c.last or c.error:
                break
        out.append('window ' + ('ok' if c.last and c._thread.is_alive() else 'fail'))
        if c.error:
            out.append(c.error)
    except Exception as e:
        out.append('error ' + repr(e))
    with open(os.path.join(HERE, 'selftest.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))


def main():
    if '--selftest-precos' in sys.argv:
        return selftest_precos()
    if '--cli' in sys.argv or '--demo' in sys.argv:
        try:
            cli_main()
        except BauError as e:
            bad(str(e))
        return
    app_main()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n  ' + GOLD('Cancelado.'))
