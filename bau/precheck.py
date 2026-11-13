"""Verificador de preço do Meu Baú.

Como funciona: no jogo, você passa o mouse em cima de um item e aperta Ctrl+C (o atalho do
próprio Path of Exile para copiar o item). O app percebe que a área de transferência mudou,
lê o texto do item e mostra o preço do poe.ninja numa janelinha perto do mouse.
O app não envia teclas para o jogo, não lê a memória nem a tela do jogo.
"""
import json, re, sys, threading, time, urllib.parse, webbrowser

FRAME = {'Normal': 0, 'Magic': 1, 'Rare': 2, 'Unique': 3, 'Gem': 4, 'Currency': 5, 'Divination Card': 6}
SEP = re.compile(r'\n-{4,}\n?')


def _num(s):
    m = re.search(r'\d[\d.,\s]*', s or '')
    return int(re.sub(r'\D', '', m.group(0))) if m else 0


def parse(text):
    """Texto copiado do jogo -> dict com raridade, nome, base etc. None se não for um item do PoE."""
    if not text:
        return None
    text = text.replace('\r', '').strip()
    first = text.splitlines()[:3]
    if not any(l.startswith(('Item Class:', 'Rarity:')) for l in first):
        return None
    blocks = [b.strip().splitlines() for b in SEP.split(text)]
    it = {'cls': '', 'rarity': '', 'name': '', 'base': '', 'stack': 1, 'level': 0, 'quality': 0,
          'tier': 0, 'ilvl': 0, 'corrupted': False, 'sockets': '', 'unid': False}
    names = []
    for line in blocks[0]:
        if line.startswith('Item Class:'):
            it['cls'] = line.split(':', 1)[1].strip()
        elif line.startswith('Rarity:'):
            it['rarity'] = line.split(':', 1)[1].strip()
        elif line.strip():
            names.append(line.strip())
    if not it['rarity'] or not names:
        return None
    if it['rarity'] in ('Unique', 'Rare') and len(names) >= 2:
        it['name'], it['base'] = names[0], names[1]
    else:
        it['base'] = names[-1]
    if it['base'].startswith('Superior '):
        it['base'] = it['base'][len('Superior '):]
    for b in blocks[1:]:
        if b and b[0].strip().startswith('Requirements'):  # "Level: 70" daqui é requisito, não nível da gema
            continue
        for line in b:
            l = line.strip()
            if l.startswith('Stack Size:'):
                it['stack'] = _num(l.split(':', 1)[1].split('/')[0]) or 1
            elif l.startswith('Level:') and it['rarity'] == 'Gem' and not it['level']:
                it['level'] = _num(l)
            elif l.startswith('Quality'):
                it['quality'] = _num(l.split(':', 1)[1].split('(')[0]) if ':' in l else 0
            elif l.startswith('Map Tier:'):
                it['tier'] = _num(l)
            elif l.startswith('Item Level:'):
                it['ilvl'] = _num(l)
            elif l.startswith('Sockets:'):
                it['sockets'] = l.split(':', 1)[1].strip()
            elif l == 'Corrupted':
                it['corrupted'] = True
            elif l == 'Unidentified':
                it['unid'] = True
    return it


def to_api_item(it):
    """Converte para o mesmo formato de item da API do baú, para reaproveitar price_item()."""
    props = []
    if it['level']:
        props.append({'name': 'Level', 'values': [[str(it['level']), 0]]})
    if it['quality']:
        props.append({'name': 'Quality', 'values': [[f"+{it['quality']}%", 0]]})
    if it['tier']:
        props.append({'name': 'Map Tier', 'values': [[str(it['tier']), 0]]})
    sockets = []
    for g, grp in enumerate(it['sockets'].split()):  # "R-G-B B" -> grupos ligados
        sockets += [{'group': g}] * len(grp.split('-'))
    return {'name': it['name'], 'typeLine': it['base'], 'baseType': it['base'],
            'frameType': FRAME.get(it['rarity'], 0), 'properties': props, 'sockets': sockets,
            'corrupted': it['corrupted']}


def trade_url(it, league):
    q = {'status': {'option': 'online'}}
    if it['rarity'] == 'Unique' and it['name']:
        q.update(name=it['name'], type=it['base'])
    elif it['rarity'] == 'Gem':
        q['type'] = it['base']
        mf = {}
        if it['level']:
            mf['gem_level'] = {'min': it['level']}
        if it['quality']:
            mf['quality'] = {'min': it['quality']}
        if mf:
            q['filters'] = {'misc_filters': {'filters': mf}}
    elif it['rarity'] != 'Magic':  # mágico: o nome tem os afixos, não dá para saber a base com certeza
        q['type'] = it['base']
    return ('https://www.pathofexile.com/trade/search/' + urllib.parse.quote(league) + '?q='
            + urllib.parse.quote(json.dumps({'query': q}, separators=(',', ':'))))


def fmt(c, divine):
    if c is None:
        return '—'
    if divine and c >= divine:
        return f'{c / divine:.2f} divine'.replace('.', ',')
    return (f'{c:.1f}' if c < 10 else f'{c:.0f}').replace('.', ',') + ' chaos'


def evaluate(text, P, league, price_item):
    """Devolve o que mostrar na janelinha, ou None se o texto não for item."""
    it = parse(text)
    if not it:
        return None
    title = (f"{it['name']} — {it['base']}" if it['name'] else it['base'])
    if it['rarity'] == 'Gem':
        title += f" ({it['level']}/{it['quality']})"
    out = {'title': title, 'rarity': it['rarity'], 'trade': trade_url(it, league), 'lines': [], 'note': ''}
    if P is None:
        out['note'] = 'Carregando preços do poe.ninja…'
        return out
    if it['rarity'] in ('Rare', 'Magic') or it['unid'] and it['rarity'] != 'Unique':
        out['note'] = 'Itens raros e mágicos não têm preço fixo. Use "Buscar no trade".'
        return out
    unit, cat = price_item(to_api_item(it), P)
    d = P.get('divine')
    if not unit:
        out['note'] = 'Sem preço no poe.ninja para este item.'
        return out
    out['category'] = cat
    out['lines'].append(('Preço', fmt(unit, d)))
    if it['stack'] > 1:
        out['lines'].append((f"Pilha ({it['stack']})", fmt(unit * it['stack'], d)))
    if d and unit < d * 0.99:
        out['lines'].append(('Em divine', f'{unit / d:.3f}'.replace('.', ',')))
    return out


# --------------------------------------------------------------------------- janelinha (tkinter)
class Checker:
    """Roda numa thread própria: uma janela tkinter escondida que olha a área de transferência."""

    def __init__(self, load_prices, price_item, log=lambda m: None):
        self.load_prices, self.price_item, self.log = load_prices, price_item, log
        self.enabled = False
        self.league = 'Standard'
        self.P = None
        self.P_league = None
        self.P_time = 0
        self.last = None  # último resultado, para a página do app
        self.status = 'desligado'
        self._thread = None
        self._q = []  # pedidos vindos de outras threads (executados na thread do tk)

    # ---- chamado pela página do app (outra thread)
    def set(self, enabled, league):
        self.league = league or 'Standard'
        self.enabled = bool(enabled)
        self.status = 'ligado' if enabled else 'desligado'
        if enabled:
            self._ensure_thread()
            self._q.append('arm')
            threading.Thread(target=self._prices, daemon=True).start()

    def test(self, text):
        self._ensure_thread()
        self._q.append(('show_text', text))

    # ---- preços (thread separada para não travar a janela)
    def _prices(self, force=False):
        if not force and self.P is not None and self.P_league == self.league and time.time() - self.P_time < 900:
            return
        try:
            self.status = 'carregando preços'
            P = self.load_prices(self.league)
            self.P, self.P_league, self.P_time = P, self.league, time.time()
            self.status = 'ligado' if self.enabled else 'desligado'
        except Exception as e:  # sem internet etc.
            self.log(f'precheck: erro ao carregar preços: {e!r}')
            self.status = 'sem preços (erro ao falar com o poe.ninja)'

    def _ensure_thread(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    # ---- thread do tk
    def _seq(self):
        if sys.platform == 'win32':
            import ctypes
            return ctypes.windll.user32.GetClipboardSequenceNumber()
        return None

    def _run(self):
        if sys.platform == 'win32':
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)  # coordenadas do mouse certas em telas com zoom
            except Exception:
                pass
        import tkinter as tk
        self.tk = tk
        root = tk.Tk(); root.withdraw(); self.root = root
        win = tk.Toplevel(root); win.withdraw(); win.overrideredirect(True)
        win.attributes('-topmost', True)
        win.configure(bg='#a07a4c')
        self.win = win
        self.frame = tk.Frame(win, bg='#0d1320', padx=12, pady=10)
        self.frame.pack(padx=1, pady=1)
        self.hide_at = 0
        self.last_seq = self._seq()
        self.last_text = self._clip()
        root.after(300, self._tick)
        root.mainloop()

    def _clip(self):
        try:
            return self.root.clipboard_get()
        except Exception:
            return ''

    def _tick(self):
        try:
            while self._q:
                job = self._q.pop(0)
                if job == 'arm':  # não mostrar o que já estava copiado antes de ligar
                    self.last_seq = self._seq(); self.last_text = self._clip()
                elif isinstance(job, tuple) and job[0] == 'show_text':
                    self._show(job[1])
            if self.enabled:
                seq = self._seq()
                if seq is None or seq != self.last_seq:
                    self.last_seq = seq
                    t = self._clip()
                    if t != self.last_text:
                        self.last_text = t
                        if parse(t):
                            self._show(t)
            if self.hide_at and time.time() > self.hide_at:
                self.win.withdraw(); self.hide_at = 0
        except Exception as e:
            self.log(f'precheck: {e!r}')
        self.root.after(250, self._tick)

    def _show(self, text):
        if self.P is None or self.P_league != self.league:
            threading.Thread(target=self._prices, daemon=True).start()
        r = evaluate(text, self.P, self.league, self.price_item)
        if not r:
            return
        self.last = r
        tk = self.tk
        for w in self.frame.winfo_children():
            w.destroy()
        color = {'Unique': '#e2a35a', 'Gem': '#3fb5a5', 'Currency': '#c9b27c', 'Divination Card': '#9fd3f5',
                 'Rare': '#ece079', 'Magic': '#8888ff'}.get(r['rarity'], '#e8e6e0')
        tk.Label(self.frame, text=r['title'], fg=color, bg='#0d1320', font=('Segoe UI', 11, 'bold'),
                 wraplength=360, justify='left').pack(anchor='w')
        for k, v in r['lines']:
            row = tk.Frame(self.frame, bg='#0d1320'); row.pack(anchor='w', fill='x', pady=(4, 0))
            tk.Label(row, text=k, fg='#9aa6bd', bg='#0d1320', font=('Segoe UI', 10)).pack(side='left')
            tk.Label(row, text=v, fg='#f0d28c', bg='#0d1320', font=('Segoe UI', 12, 'bold')).pack(side='right', padx=(16, 0))
        if r.get('category'):
            tk.Label(self.frame, text=r['category'] + ' · poe.ninja · ' + self.league, fg='#6f7a90', bg='#0d1320',
                     font=('Segoe UI', 8)).pack(anchor='w', pady=(4, 0))
        if r['note']:
            tk.Label(self.frame, text=r['note'], fg='#c8cfdb', bg='#0d1320', font=('Segoe UI', 9),
                     wraplength=360, justify='left').pack(anchor='w', pady=(4, 0))
        link = tk.Label(self.frame, text='Buscar no trade ↗', fg='#5caaff', bg='#0d1320', cursor='hand2',
                        font=('Segoe UI', 9, 'underline'))
        link.pack(anchor='w', pady=(6, 0))
        link.bind('<Button-1>', lambda e, u=r['trade']: (webbrowser.open(u), self.win.withdraw()))
        for w in [self.frame] + list(self.frame.winfo_children()):
            if w is not link:
                w.bind('<Button-1>', lambda e: self.win.withdraw())
        self.win.update_idletasks()
        x, y = self.root.winfo_pointerxy()
        w, h = self.win.winfo_reqwidth(), self.win.winfo_reqheight()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x = min(max(0, x + 18), sw - w - 4); y = min(max(0, y + 18), sh - h - 4)
        self.win.geometry(f'+{x}+{y}')
        self.win.deiconify(); self.win.lift(); self.win.attributes('-topmost', True)
        self.hide_at = time.time() + 8


SAMPLE = """Item Class: Stackable Currency
Rarity: Currency
Divine Orb
--------
Stack Size: 3/20
--------
Randomises the numeric values of the random modifiers on an item
--------
Right click this item then left click a magic, rare or unique item to apply it."""
