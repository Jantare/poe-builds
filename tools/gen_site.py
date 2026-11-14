"""Generates index.html and builds/*.html. Usage: python3 -I tools/gen_site.py <tree data.json> <spark source html>"""
import sys, os, re, json, html
sys.path.insert(0, os.path.dirname(__file__))
from treelib import Tree, plan, svg
from build_specs import SPECS
from content import BUILDS, ASC_PT
import gen_safe
import leveling_routes
import updates_330
from videos import showcase
import xml.sax.saxutils as sx
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = Tree(sys.argv[1]); SPARK = open(sys.argv[2], encoding='utf-8').read()
CRAFT = json.load(open(os.path.join(ROOT, 'data/craft/mods.json')))
BASES = json.load(open(os.path.join(ROOT, 'data/craft/bases.json')))
e = html.escape

def head(title, desc, depth):
    up = '../' * depth
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap">
<link rel="stylesheet" href="{up}assets/style.css">
<script src="{up}assets/nav.js" defer></script>
<script src="{up}assets/pobview.js" defer></script>
<script src="{up}assets/trade.js" defer></script>
</head>
<body>
<header class="topbar"><div class="in">
  <a class="brand" href="{up}">PoE Builds</a>
  <div class="links"><a href="{up}">Início</a><a href="{up}#builds">Seguras</a><a href="{up}#youtube">YouTube</a><a href="{up}#apostas">Apostas</a><a href="{up}farm/">Farm</a><a href="{up}craft/">Craft</a><a href="{up}bau/">Baú</a><a href="{up}preco/">Preço</a><a href="{up}#ferramentas">Ferramentas</a></div>
</div></header>
'''

def craft_link(p, depth=1):
    from urllib.parse import urlencode
    label, base, ilvl, m, t = p
    assert base in BASES, base
    groups = {v['g'] for v in CRAFT.values()}
    for g in t.split(','):
        assert g.split(':')[0] in groups, g
    return f'<a href="{"../"*depth}craft/?{e(urlencode({"base":base,"ilvl":ilvl,"m":m,"t":t}))}">{e(label)}</a>'


SPARK_GEMS = [('Body Armour', ['Spark','Lightning Penetration','Increased Critical Strikes','Inspiration','Spell Echo','Added Lightning Damage']),
              ('Boots', ['Flame Dash','Frostblink']), ('Gloves', ['Arcane Cloak','Conductivity']), ('Helmet', ['Zealotry','Wrath','Discipline'])]
SLOTS = ['Body Armour','Helmet','Gloves','Boots','Weapon 1','Weapon 2']

def bet_pob(slug, b, P):
    """Minimal Path of Building XML for a bet build: class, ascendancy, tree and gem links."""
    s = SPECS[slug]
    cls_idx = list(T.D['classes']).index(next(c for c in T.D['classes'] if c['name'] == s['cls']))
    ascs = T.D['classes'][cls_idx]['ascendancies']
    ids = [a.get('id', a['name']) for a in ascs]
    asc_idx = (ids.index(s['asc']) if s['asc'] in ids else [a['name'] for a in ascs].index(s['asc'])) + 1
    asc_name = ascs[asc_idx - 1]['name']
    nodes = [k for k in P['alloc'] if k != P['start']] + list(P['mpick']) + list(P['asel'])
    mast = ','.join('{%s,%s}' % (m, v[0]) for m, v in P['mpick'].items())
    groups = SPARK_GEMS if b.get('spark') else [(SLOTS[i] if i < len(SLOTS) else '', [g.rstrip('*').split(':')[0] for g in gems]) for i, (role, sub, gems) in enumerate(b['gems'])]
    skills = ''.join('<Skill enabled="true" slot="%s" mainActiveSkill="1">%s</Skill>' % (sx.escape(slot), ''.join(
        '<Gem nameSpec=%s level="20" quality="0" enabled="true"/>' % sx.quoteattr(g) for g in gems)) for slot, gems in groups)
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<PathOfBuilding>'
           f'<Build level="90" targetVersion="3_0" className="{s["cls"]}" ascendClassName="{asc_name}" mainSocketGroup="1" bandit="None"/>'
           f'<Tree activeSpec="1"><Spec title={sx.quoteattr(b["name"])} treeVersion="3_29" classId="{cls_idx}" ascendClassId="{asc_idx}" nodes="{",".join(nodes)}" masteryEffects="{mast}"><URL>{sx.escape(P["url"])}</URL></Spec></Tree>'
           f'<Skills activeSkillSet="1"><SkillSet id="1" title="Principal">{skills}</SkillSet></Skills>'
           '<Items activeItemSet="1"><ItemSet id="1"/></Items>'
           f'<Notes>{sx.escape(b["name"] + " - rascunho do site PoE Builds (3.30). Equipamento não incluído.")}</Notes>'
           '</PathOfBuilding>')
    gen_safe.write_code(slug, xml.encode('utf-8'))

def tree_section(slug, b):
    s = SPECS[slug]
    P = plan(T, s['cls'], s['phases'], s['masteries'], s['asc'], s['ascn'])
    bet_pob(slug, b, P)
    names = lambda ph: ', '.join(n for n in s['phases'][ph])
    c = P['counts']
    mrows = ''.join(f'<tr><td>{e(v[3])}</td><td>{e(v[1])}</td></tr>' for v in P['mpick'].values())
    asc = ''.join(
        f'<li><div class="when">{["Lab Normal · Ato 3","Lab Cruel · Atos 6–7","Lab Merciless · Atos 8–10","Uber Lab · mapas"][i] if i < 4 else ""}</div>'
        f'<div class="node">{e(nm)}</div><p>{e(ASC_PT.get(nm, ""))}</p><p class="muted" style="font-size:12px;margin-top:6px">{e(txt[:160])}</p></li>'
        for i, (nm, cost, txt) in enumerate(P['aorder']))
    return P, f'''<section id="ascensao">
  <h2>Ascensão</h2>
  <ol class="lab">{asc}</ol>
  <p class="muted" style="margin-top:8px;font-size:13px">O texto em cinza é o do jogo (dados 3.29). As mudanças da 3.30 estão no resumo acima dele.</p>
</section>
<section id="arvore">
  <h2>Árvore passiva</h2>
  <p>Rota real montada com os dados da árvore: <b>{P['total']} pontos</b> com {len(P['mpick'])} masteries. Os pontos que sobrarem até o nível 100 ficam para jewels e ajustes. Cada cor é uma fase; os círculos vermelhos são masteries.</p>
  <p><a class="treelink" href="{e(P['url'])}" target="_blank" rel="noopener">Abrir na árvore oficial</a></p>
  {gen_safe.pob_button(slug).replace('Copiar código do PoB','Copiar código do PoB (árvore + gemas)')}
  <p class="note">No <strong>Path of Building</strong>: Import/Export Build → cole o link da árvore oficial. Lá você ajusta a ordem dos pontos.</p>
  <div class="diagram tree-real" role="img" aria-label="Árvore passiva com a rota da build em três fases.">{svg(T, P)}</div>
  <div class="legend"><span><i class="sw" style="background:var(--spark)"></i>Fase 1</span><span><i class="sw" style="background:var(--accent)"></i>Fase 2</span><span><i class="sw" style="background:var(--gem-g)"></i>Fase 3</span><span><i class="sw" style="background:var(--bad)"></i>Mastery</span></div>
  <div class="phases">
    <div><b>Fase 1 · campanha · {c.get(1,0)} pontos</b><br>{e(names(0))}.</div>
    <div><b>Fase 2 · fim da campanha · {c.get(2,0)} pontos</b><br>{e(names(1))}.</div>
    <div><b>Fase 3 · mapas · {c.get(3,0)} pontos</b><br>{e(names(2))}.</div>
  </div>
  <h3 style="margin-top:18px">Masteries</h3>
  <div class="tbl" style="margin-top:8px"><table><thead><tr><th>Mastery</th><th>Escolha</th></tr></thead><tbody>{mrows}</tbody></table></div>
</section>'''

def gem_html(rows, cls, key):
    import pobview
    groups = []
    for role, sub, gems in rows:
        gs = [re.sub(r'(\*|:g)+$', '', g) for g in gems]
        groups.append((gs, f'{role} · {sub}' if sub else role))
    return pobview.view(key, [('Gemas', groups)], cls)

def build_page(b, P_tree):
    P, tree_html = P_tree
    facts = ''.join(f'<span class="fact">{e(f)}</span>' for f in [f'Classe: {b["cls"]} → {b["asc"]}'] + b['facts'])
    notice = f'<p class="note"><strong>Atenção:</strong> {e(b["notice"])}</p>' if b.get('notice') else ''
    why = ''.join(f'<div><h3>{e(h)}</h3><p>{e(p)}</p></div>' for h, p in b['why'])
    import trade
    gear = ''.join(f'<tr><td>{e(r[0])}</td>' + ''.join(f'<td>{trade.linkify(e(c))}</td>' for c in r[1:4]) + '</tr>' for r in b['gear'])
    craft = ' '.join(craft_link(p) for p in b['craft'])
    acts = ''.join(f'<div class="act"><h3>{e(a)}</h3><label><input type="checkbox" id="{b["slug"]}-{i}"><span>{e(t)}</span></label></div>' for i, (a, t) in enumerate(b['acts']))
    good = ''.join(f'<li>{e(x)}</li>' for x in b['league'][0]); bad = ''.join(f'<li>{e(x)}</li>' for x in b['league'][1])
    return head(b['name'] + ' · PoE Builds', b['card'], 1) + f'''<div class="wrap">
<header>
  <div class="eyebrow">Path of Exile 1 · 3.30 Covens of Umbra · {e(b["cls"])}</div>
  <h1>{e(b["name"])}</h1>
  <p class="lede">{e(b["lede"])}</p>
  <div class="facts">{facts}</div>
  {notice}
  <p class="note"><strong>Rascunho:</strong> gemas e equipamento são um ponto de partida. Confirme no Path of Building e nos guias da comunidade quando a liga abrir.</p>
</header>
<nav class="sec" aria-label="Seções"><a href="#novidades">3.30</a><a href="#showcase">Vídeo</a><a href="#porque">Por quê</a><a href="#ascensao">Ascensão</a><a href="#arvore">Árvore</a><a href="#gemas">Gemas</a><a href="#equipamento">Equipamento</a><a href="#craft">Craft</a><a href="#atos">Leveling</a><a href="#liga">Liga</a></nav>
{updates_330.section(b["slug"], gen_safe.write_code, gen_safe.pob_button, e)}
{showcase(b["slug"], b["name"])}
<section id="porque"><h2>Por que nessa liga</h2><div class="why">{why}</div></section>
{tree_html}
<section id="gemas"><h2>Gemas e links</h2>{gem_html(b["gems"], b["cls"], "gemas-" + b["slug"])}</section>
<section id="equipamento"><h2>Equipamento por orçamento</h2>{__import__('trade').league_bar()}<div class="tbl"><table><thead><tr><th>Slot</th><th><span class="tier t1">Barato</span></th><th><span class="tier t2">Médio</span></th><th><span class="tier t3">Final</span></th></tr></thead><tbody>{gear}</tbody></table></div></section>
<section id="craft"><h2>Craft</h2><p>Abra no simulador já configurado:</p><div class="presets">{craft}</div>
<p class="note" style="margin-top:12px">O passo a passo geral de craft (fossils, travar afixo, Harvest) está na página do <a href="trickster-spark.html#craft">Trickster Spark</a> e vale para estas peças também.</p></section>
<section id="atos"><h2>Leveling</h2>
  <div class="progress"><div class="meter"><i id="bar"></i></div><span id="count">0 de 0</span><button class="reset" id="reset" type="button">Limpar</button></div>
  <div class="acts" id="acts">{acts}</div></section>
<section id="liga"><h2>Estratégia na liga</h2><div class="cols"><div><h3 class="good">Rode</h3><ul>{good}</ul></div><div><h3 class="badc">Cuidado</h3><ul>{bad}</ul></div></div></section>
<footer>Árvore e ascensão: dados da árvore do Path of Building (3.29; a 3.30 não mudou a árvore passiva). Patch: <a href="https://www.pathofexile.com/forum/view-thread/4013680" target="_blank" rel="noopener">notas oficiais da 3.30.0</a>.</footer>
</div>
<script src="../assets/checklist.js" data-key="{b["slug"]}"></script>
<script src="../assets/pob.js"></script>\n<script src="../assets/video.js"></script>
</body></html>
'''

def leveling_section(old_atos):
    """Keeps the old Spark-from-act-1 checklist (inner part) inside the new routes section."""
    inner = re.sub(r'^<section id="atos">\s*<h2>[^<]*</h2>', '', old_atos.strip())
    inner = re.sub(r'</section>\s*$', '', inner)
    return leveling_routes.section(inner)

def spark_page(b, P_tree):
    P, tree_html = P_tree
    sect = lambda i: re.search(r'<section id="%s">.*?</section>' % i, SPARK, re.S).group(0)
    hdr = re.search(r'<header>.*?</header>', SPARK, re.S).group(0)
    craft = sect('craft')
    sim = ' '.join(craft_link(p) for p in [('Elmo Hubris','Hubris Circlet',84,'chaos','LocalEnergyShield:2,LocalEnergyShieldPercent:2'),
        ('Rune Dagger +1','Copper Kris',84,'chaos','GlobalIncreaseSpellSkillGemLevel:1'),('Luvas com supressão','Murder Mitts',84,'chaos','ChanceToSuppressSpells:3,LocalEvasionAndEnergyShield:3'),
        ('Botas','Murder Boots',84,'chaos','MovementVelocity:2,ChanceToSuppressSpells:3'),('Jewel ES + crítico','Cobalt Jewel',84,'chaos','EnergyShieldForJewel:1,SpellCritMultiplierForJewel:1')])
    craft = craft.replace('<h2>Como craftar</h2>', f'<h2>Como craftar</h2>\n  <p><b>Simulador do site:</b></p><div class="presets" style="margin-bottom:12px">{sim}</div>', 1)
    body = '\n'.join([hdr,
        '<nav class="sec" aria-label="Seções"><a href="#novidades">3.30</a><a href="#showcase">Vídeo</a><a href="#porque">Por quê</a><a href="#atos">Leveling</a><a href="#ascensao">Ascensão</a><a href="#arvore">Árvore</a><a href="#gemas">Gemas</a><a href="#equipamento">Equipamento</a><a href="#alvos">Alvos</a><a href="#craft">Craft</a><a href="#liga">Liga</a></nav>',
        updates_330.section(b['slug'], gen_safe.write_code, gen_safe.pob_button, e), showcase(b['slug'], b['name']), sect('porque'), leveling_section(sect('atos')), sect('ascensao'), tree_html.split('</section>',1)[1].strip(), sect('gemas'), __import__('trade').linkify_section(sect('equipamento')), sect('alvos'), craft, sect('liga')])
    body = body.replace(re.search(r'<section id="ascensao">.*?</section>', body, re.S).group(0), sect('ascensao'))
    foot = re.search(r'<footer>.*?</footer>', SPARK, re.S).group(0)
    return head(b['name'] + ' · PoE Builds', b['card'], 1) + '<div class="wrap">\n' + body + '\n' + foot + '\n</div>\n<script src="../assets/checklist.js" data-key="trickster-spark-330-checks"></script>\n<script src="../assets/pob.js"></script>\n<script src="../assets/video.js"></script>\n</body></html>\n'

os.makedirs(os.path.join(ROOT, 'builds'), exist_ok=True)
cards = []
for b in BUILDS:
    PT = tree_section(b['slug'], b)
    page = spark_page(b, PT) if b.get('spark') else build_page(b, PT)
    open(os.path.join(ROOT, 'builds', b['slug'] + '.html'), 'w', encoding='utf-8').write(page)
    tagcls = {'Não recomendada': 'bad', 'Recomendada': 'ok', 'Segura': 'ok', 'Aposta nova': 'new', 'Conceito': 'warn', 'Boss': 'ok'}[b['tag']]
    cards.append(f'<a class="card" href="builds/{b["slug"]}.html"><span class="cls">{e(b["cls"])} · {e(b["asc"])}</span><h3>{e(b["name"])}</h3><p>{e(b["card"])}</p><span class="pill {tagcls}">{e(b["tag"])}</span></a>')
    print(b['slug'], PT[0]['total'], 'pontos')

safe_cards = gen_safe.render_all(T, head)
yt_cards = gen_safe.render_all(T, head, gen_safe.YT, 'YouTube')
tools = re.search(r'<div class="toolgrid">.*?</div>\s*\n\s*\n', SPARK, re.S)
toolgrid = tools.group(0) if tools else ''
index = head('PoE Builds', 'Builds de Path of Exile 3.30 com árvore, crafting e leveling, mais um simulador de craft.', 0) + f'''<div class="wrap wide">
<header>
  <div class="eyebrow">Path of Exile 1 · 3.30 Covens of Umbra</div>
  <h1>PoE Builds</h1>
  <p class="lede">Nossas builds para a liga, com árvore real, ascensão, gemas, equipamento, craft e leveling. Mais um simulador de craft com os pesos reais dos mods.</p>
</header>
<section id="builds"><h2>Mais seguras</h2><p>As mais fortes da 3.29 que <b>não levaram nerf</b> na 3.30. Gemas, árvore e itens vêm do Path of Building dos autores dos guias.</p><div class="cards">{"".join(safe_cards)}</div></section>
<section id="youtube"><h2>Do YouTube (3.30)</h2><p>Os vídeos de league start da 3.30 mais vistos que trazem Path of Building completo, com árvore e gemas por ato. Lista tirada do poebuilds.cc, que reúne as builds dos vídeos.</p><div class="cards">{"".join(yt_cards)}</div></section>
<section id="apostas"><h2>Apostas para a 3.30</h2><p>Builds pensadas para as mudanças da 3.30. Podem ser mais fortes, mas têm mais risco. A árvore é real; gemas e itens são rascunho.</p><div class="cards">{"".join(cards)}</div></section>
<section id="bau"><h2>Meu Baú</h2>
  <div class="cards"><a class="card" href="bau/"><span class="cls">Ferramenta</span><h3>Quanto vale o seu baú</h3><p>Valor de cada aba em Chaos e Divine, breakdown por categoria, tabela de itens e histórico entre sessões de farm. O script roda no seu PC; nada sai dele.</p><span class="pill ok">bau.exe</span></a><a class="card" href="preco/"><span class="cls">Ferramenta</span><h3>Verificador de preço</h3><p>Aperte Ctrl+C num item do jogo e o preço aparece perto do mouse. Mais o guia do Awakened PoE Trade para preço de raros.</p><span class="pill new">Novo</span></a></div>
</section>
<section id="farm"><h2>Farm na 3.30</h2>
  <a class="card" href="farm/" style="max-width:520px"><span class="cls">Guia</span><h3>Como farmar na Covens of Umbra</h3><p>Como o loot mudou, como funcionam Threads, Regiões Moldadas e Fates, as melhores mecânicas e qual combina com cada build.</p><span class="pill new">Novo</span></a>
</section>
<section id="craft"><h2>Simulador de Craft</h2>
  <a class="card" href="craft/" style="max-width:520px"><span class="cls">Ferramenta</span><h3>Simulador de Craft</h3><p>Escolha base, item level e método (Chaos, Alteration, Essência, afixo travado). Ele calcula a chance de sair os mods que você quer e o custo médio.</p><span class="pill new">Novo</span></a>
</section>
<section id="liga"><h2>A liga em 6 pontos</h2><div class="why">
  <div><h3>Fates nos bosses</h3><p>Encontros das Covens dão Fates que você invoca nos bosses de área: mais difícil e mais loot.</p></div>
  <div><h3>Wickerman</h3><p>Bosses com Fate dropam Viscera, buffs permanentes por slot de equipamento.</p></div>
  <div><h3>Threads no lugar de Scarabs</h3><p>Até 8 Threads por mapa aplicam a mecânica e efeitos aleatórios. Regiões Moldadas dão Threads de graça.</p></div>
  <div><h3>Currency vem de raros</h3><p>A rarity do monstro decide o tipo de currency. Raros, uniques e bosses soltam a currency boa.</p></div>
  <div><h3>Quantidade quase acabou</h3><p>Virou Atlas Drops nos mapas. A rarity do jogador agora melhora o tier dos itens.</p></div>
  <div><h3>Crafting novo</h3><p>Travar 1 prefixo ou sufixo por 1 Divine, vendor de raros iguais (Chaos e Exalted) e Orb of Chance bem melhor.</p></div>
</div></section>
<section id="ferramentas"><h2>Ferramentas</h2>{toolgrid.replace('href="https://www.youtube.com', 'href="https://www.youtube.com')}</section>
<footer>Site gerado a partir dos dados do Path of Building e das <a href="https://www.pathofexile.com/forum/view-thread/4013680" target="_blank" rel="noopener">notas oficiais da 3.30.0</a>. Não é afiliado à Grinding Gear Games.</footer>
</div>
</body></html>
'''
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(index)
print('index ok')
