"""Pages for the safe 3.29 builds, built from the authors' Path of Building XML (data/pob/*.xml)."""
import os, re, html, base64, struct, collections
import xml.etree.ElementTree as ET, zlib
from treelib import svg, CLASS_IDX
from safe_content import SAFE, YT
from videos import showcase
import updates_330
import pobview
e = html.escape
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
clean = lambda s: re.sub(r'\^x[0-9A-Fa-f]{6}|\^\d', '', s or '').strip()

def parse_spec(s):
    nodes = [x for x in (s.get('nodes') or '').split(',') if x]
    me = re.findall(r'\{(\d+),(\d+)\}', s.get('masteryEffects') or '')
    return nodes, [(m, int(ef)) for m, ef in me]

def build_P(T, b, root):
    specs = root.find('Tree').findall('Spec')
    N = T.N
    final_idx = b['phases'][-1][-1]
    fnodes, fmast = parse_spec(specs[final_idx])
    cls_idx = int(specs[final_idx].get('classId')); asc_idx = int(specs[final_idx].get('ascendClassId'))
    start = [k for k, v in N.items() if v.get('classStartIndex') == cls_idx][0]
    first = {}
    for ph, group in enumerate(b['phases'], 1):
        for si in group:
            for n in parse_spec(specs[si])[0]:
                first.setdefault(n, ph)
    alloc = {start: 0}
    asc_nodes = []
    for n in fnodes:
        if n not in N: continue
        v = N[n]
        if v.get('ascendancyName'): asc_nodes.append(n); continue
        if v.get('isMastery'): continue
        alloc[n] = first.get(n, len(b['phases']))
    mpick = {}
    for m, ef in fmast:
        if m not in N: continue
        eff = [x for x in N[m].get('masteryEffects', []) if x['effect'] == ef]
        grp = [str(x) for x in T.G[str(N[m]['group'])].get('nodes', [])]
        ph = min([alloc[i] for i in grp if i in alloc] or [len(b['phases'])])
        mpick[m] = (ef, ' / '.join(eff[0]['stats']) if eff else '', ph, N[m].get('name', 'Mastery'))
    # ascendancy order: first spec (in phase order) where each notable appears
    order = []
    for group in b['phases']:
        for si in group:
            for n in parse_spec(specs[si])[0]:
                v = N.get(n, {})
                if v.get('ascendancyName') and v.get('isNotable') and n not in order: order.append(n)
    for n in asc_nodes:
        if N[n].get('isNotable') and n not in order: order.append(n)
    order = [n for n in order if n in asc_nodes]
    nodes = [int(k) for k in alloc if k != start] + [int(m) for m in mpick] + [int(a) for a in asc_nodes]
    raw = struct.pack('>IBBB', 6, cls_idx, asc_idx, len(nodes)) + b''.join(struct.pack('>H', n) for n in nodes) + struct.pack('>B', 0)
    raw += struct.pack('>B', len(mpick)) + b''.join(struct.pack('>HH', v[0], int(m)) for m, v in mpick.items())
    url = 'https://www.pathofexile.com/passive-skill-tree/' + base64.b64encode(raw).decode().replace('+', '-').replace('/', '_')
    counts = collections.Counter(v for k, v in alloc.items() if k != start)
    return dict(start=start, alloc=alloc, mpick=mpick, asel=asc_nodes, url=url, counts=counts,
                total=sum(counts.values()) + len(mpick), order=order, specs=specs, final=final_idx)

SLOT_PT = {'Body Armour': 'Peito', 'Helmet': 'Elmo', 'Gloves': 'Luvas', 'Boots': 'Botas', 'Weapon 1': 'Arma', 'Weapon 2': 'Arma 2 / escudo',
           'Weapon 1 Swap': 'Arma (troca)', 'Weapon 2 Swap': 'Arma 2 (troca)', 'Amulet': 'Amuleto', 'Ring 1': 'Anel', 'Ring 2': 'Anel 2'}

def gems_html(root, cls, key):
    sets = []
    for ss in root.find('Skills').findall('SkillSet') or [root.find('Skills')]:
        groups = []
        for sk in ss.findall('Skill'):
            if sk.get('enabled') == 'false': continue
            gs = [g.get('nameSpec') for g in sk.findall('Gem') if g.get('nameSpec') and g.get('enabled') != 'false']
            if not gs: continue
            slot = clean(sk.get('slot') or '')
            label = clean(sk.get('label') or '')
            groups.append((gs, label or SLOT_PT.get(slot, slot)))
        groups.sort(key=lambda g: -len(g[0]))
        if groups:
            sets.append((clean(ss.get('title')) or 'Gemas', groups))
    return pobview.view(key, sets, cls, label='Fase')

def items_html(root):
    it = root.find('Items'); items = {i.get('id'): i for i in it.findall('Item')}
    out = []
    order = ['Weapon 1', 'Weapon 2', 'Helmet', 'Body Armour', 'Gloves', 'Boots', 'Belt', 'Amulet', 'Ring 1', 'Ring 2', 'Flask 1', 'Flask 2', 'Flask 3', 'Flask 4', 'Flask 5']
    for k, st in enumerate(it.findall('ItemSet')[:3]):
        slots = {sl.get('name'): sl.get('itemId') for sl in st.findall('Slot')}
        rows = []
        for name in order:
            iid = slots.get(name)
            if iid in (None, '0') or iid not in items: continue
            lines = [l.strip() for l in (items[iid].text or '').strip().splitlines()]
            rar = lines[0].replace('Rarity: ', '').title()
            nm, base = lines[1], (lines[2] if len(lines) > 2 and rar in ('Unique', 'Rare') else '')
            if nm in ('New Item',) or nm.startswith('Example'): nm = 'Raro' if rar == 'Rare' else nm
            tag = '<span class="pill new">Unique</span> ' if rar == 'Unique' else ''
            rows.append(f'<tr><td>{e(name)}</td><td>{tag}{e(nm)}</td><td>{e(base)}</td></tr>')
        if rows:
            out.append(f'<details class="craft"{" open" if k == 0 else ""}><summary><b>{e(clean(st.get("title")) or "Equipamento")}</b></summary><div class="craft-body"><div class="tbl"><table><thead><tr><th>Slot</th><th>Item</th><th>Base</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></div></details>')
    return '<div class="crafts">' + ''.join(out) + '</div>'

def pob_button(slug):
    return (f'<button type="button" class="treelink" data-pob="../data/pob/{slug}.txt" aria-controls="pob-{slug}">Copiar código do PoB</button>'
            f'<textarea class="pobbox" id="pob-{slug}" hidden readonly aria-label="Código do Path of Building"></textarea>'
            '<p class="pobhow">No Path of Building: <b>Import/Export Build</b> → cole o código (ou o link do pobb.in) em <b>Import from</b> → <b>Import</b>.</p>')

def write_code(slug, xml_bytes):
    code = base64.urlsafe_b64encode(zlib.compress(xml_bytes, 9)).decode()
    open(os.path.join(ROOT, 'data/pob', slug + '.txt'), 'w').write(code)

def page(T, b, head):
    raw_xml = open(os.path.join(ROOT, 'data/pob', b['xml']), 'rb').read()
    write_code(b['slug'], raw_xml)
    root = ET.fromstring(raw_xml)
    P = build_P(T, b, root)
    N = T.N; specs = P['specs']
    phase_titles = [', '.join(clean(specs[i].get('title')) or 'Árvore' for i in g) for g in b['phases']]
    phases = ''.join(f'<div><b>Fase {i+1} · {P["counts"].get(i+1,0)} pontos</b><br>{e(t)}</div>' for i, t in enumerate(phase_titles))
    asc = ''.join(f'<li><div class="when">{["1º lab","2º lab","3º lab","4º lab"][i] if i < 4 else ""}</div><div class="node">{e(N[n]["name"])}</div><p class="muted" style="font-size:12.5px">{e(" / ".join(N[n].get("stats", [])).replace(chr(10), " ")[:220])}</p></li>' for i, n in enumerate(P['order']))
    mrows = ''.join(f'<tr><td>{e(v[3])}</td><td>{e(v[1])}</td></tr>' for v in P['mpick'].values())
    why = ''.join(f'<div><h3>{e(h)}</h3><p>{e(p)}</p></div>' for h, p in b['why'])
    good = ''.join(f'<li>{e(x)}</li>' for x in b['league'][0]); bad = ''.join(f'<li>{e(x)}</li>' for x in b['league'][1])
    pob = f'https://pobb.in/{b["pobb"]}'
    legend = ''.join(f'<span><i class="sw" style="background:var({c})"></i>Fase {i+1}</span>' for i, c in enumerate(['--spark', '--accent', '--gem-g'][:len(b['phases'])]))
    return head(b['name'] + ' · PoE Builds', b['card'], 1) + f'''<div class="wrap">
<header>
  <div class="eyebrow">Path of Exile 1 · {e(b.get("eyebrow","build segura da 3.29"))} · {e(b["cls"])}</div>
  <h1>{e(b["name"])}</h1>
  <p class="lede">{e(b["lede"])}</p>
  <div class="facts"><span class="fact">Classe: {e(b["cls"])} → {e(b["asc"])}</span><span class="fact">{"Vídeo" if b.get("views") else "Guia"}: {e(b["author"])}</span>{f'<span class="fact">{e(b["views"])} visualizações</span>' if b.get("views") else ""}</div>
  <p class="note"><strong>Na 3.30:</strong> {e(b["change"])}</p>
  <p class="note">Gemas, árvore e itens tirados do Path of Building do guia original. <a href="{e(b["guide"])}" target="_blank" rel="noopener">{"Assistir o vídeo" if b.get("views") else "Abrir o guia"}</a> · <a href="{e(pob)}" target="_blank" rel="noopener">Abrir o PoB (pobb.in)</a></p>
</header>
<nav class="sec" aria-label="Seções"><a href="#novidades">3.30</a><a href="#showcase">Vídeo</a><a href="#porque">Por quê</a><a href="#ascensao">Ascensão</a><a href="#arvore">Árvore</a><a href="#gemas">Gemas</a><a href="#equipamento">Equipamento</a><a href="#liga">Liga</a></nav>
{updates_330.section(b["slug"], write_code, pob_button, e)}
{showcase(b["slug"], b["name"])}
<section id="porque"><h2>{"Por que vale a pena" if b.get("views") else "Por que é seguro"}</h2><div class="why">{why}</div></section>
<section id="ascensao"><h2>Ascensão</h2><ol class="lab">{asc}</ol><p class="muted" style="font-size:13px;margin-top:8px">Ordem inferida das árvores de leveling do guia. Texto do jogo em inglês.</p></section>
<section id="arvore"><h2>Árvore passiva</h2>
  <p>Árvore do guia (versão "{e(clean(specs[P["final"]].get("title")) or "principal")}"): <b>{P["total"]} pontos</b> com {len(P["mpick"])} masteries. Cada cor mostra em qual árvore de leveling do guia o nó aparece primeiro.</p>
  <p><a class="treelink" href="{e(P["url"])}" target="_blank" rel="noopener">Abrir na árvore oficial</a> <a class="treelink" style="background:none;color:var(--accent);border:1px solid var(--accent)" href="{e(pob)}" target="_blank" rel="noopener">Abrir no pobb.in</a></p>
  {pob_button(b["slug"])}
  <div class="diagram tree-real" role="img" aria-label="Árvore passiva da build.">{svg(T, P)}</div>
  <div class="legend">{legend}<span><i class="sw" style="background:var(--bad)"></i>Mastery</span></div>
  <div class="phases">{phases}</div>
  <h3 style="margin-top:18px">Masteries</h3><div class="tbl" style="margin-top:8px"><table><thead><tr><th>Mastery</th><th>Escolha</th></tr></thead><tbody>{mrows}</tbody></table></div>
</section>
<section id="gemas"><h2>Gemas e links por fase</h2><p>Escolha a fase (ou o ato) no seletor. Passe o mouse ou toque numa gema para ver o nível mínimo e onde conseguir.</p>{gems_html(root, b['cls'], 'gemas-' + b['slug'])}</section>
<section id="equipamento"><h2>Equipamento do guia</h2><p>"Raro" é item raro com os status do guia; abra o PoB para ver os mods de cada um.</p>{items_html(root)}</section>
<section id="liga"><h2>Na Covens of Umbra</h2><div class="cols"><div><h3 class="good">Rode</h3><ul>{good}</ul></div><div><h3 class="badc">Cuidado</h3><ul>{bad}</ul></div></div></section>
<footer>Build de {e(b["author"])}. Dados do <a href="{e(pob)}" target="_blank" rel="noopener">Path of Building do guia</a>; árvore desenhada com os dados 3.29 do Path of Building Community. Confira o guia original para detalhes de leveling e craft.</footer>
</div><script src="../assets/pob.js"></script><script src="../assets/video.js"></script></body></html>
'''

def render_all(T, head, builds=None, label='Segura'):
    cards = []
    for b in (SAFE if builds is None else builds):
        if builds is not None: b.setdefault('eyebrow', 'build do YouTube para a 3.30')
        open(os.path.join(ROOT, 'builds', b['slug'] + '.html'), 'w', encoding='utf-8').write(page(T, b, head))
        cards.append(f'<a class="card" href="builds/{b["slug"]}.html"><span class="cls">{e(b["cls"])} · {e(b["asc"])}</span><h3>{e(b["name"])}</h3><p>{e(b["card"])}</p><span class="pill {'new' if b.get('views') else 'ok'}">{e(label)} · {e(b["author"].split(" (")[0])}{(' · ' + e(b['views'])) if b.get('views') else ''}</span></a>')
        print(b['slug'], 'ok')
    return cards
