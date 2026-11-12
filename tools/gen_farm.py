"""Generates farm/<mechanic>.html from tools/farm_content.py."""
import os, sys, html
sys.path.insert(0, os.path.dirname(__file__))
from farm_content import FARM, YT
e = html.escape
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEAD = '''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title} · Farm 3.30 · PoE Builds</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap">
<link rel="stylesheet" href="../assets/style.css">
<script src="../assets/nav.js" defer></script>
</head>
<body>
<header class="topbar"><div class="in">
  <a class="brand" href="../">PoE Builds</a>
  <div class="links"><a href="../">Início</a><a href="../#builds">Seguras</a><a href="../#youtube">YouTube</a><a href="../#apostas">Apostas</a><a href="./" aria-current="page">Farm</a><a href="../craft/">Craft</a><a href="../bau/">Baú</a><a href="../#ferramentas">Ferramentas</a></div>
</div></header>
'''
import atlas_plan as AP
ATLAS = AP.Atlas()
def node_rows(alloc, targets, prio):
    rows = []
    for t in targets:
        k = ATLAS.find(t)
        rows.append(f'<tr><td><b>{e(ATLAS.N[k]["name"])}</b><br><span class="pill {"ok" if prio==1 else "warn"}">{"Essencial" if prio==1 else "Extra"}</span></td><td>{AP.PT[t]}</td></tr>')
    return ''.join(rows)
def atlas_section(slug, tips):
    ph = AP.STRATS[slug]
    alloc, per = ATLAS.plan(ph)
    rows = node_rows(alloc, ph[0], 1) + node_rows(alloc, ph[1], 2)
    return f'''<section id="atlas"><h2>Pontos do Atlas</h2>
  <p class="note"><strong>Árvore oficial da 3.30</strong> (a GGG publicou antes da liga). Caminho a partir do centro: <b>{per[0]} pontos</b> para os essenciais e <b>+{per[1]}</b> para os extras. A árvore tem 150 pontos no total. Some com a <a href="./#atlas">base de sustento</a> (36 pontos).</p>
  <div class="tbl fit"><table class="split narrow"><colgroup><col style="width:34%"><col style="width:66%"></colgroup><thead><tr><th>Nó</th><th>O que faz</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p style="margin-top:12px"><a class="treelink" href="{ATLAS.url(alloc)}" target="_blank" rel="noopener">Abrir no site oficial (árvore do Atlas)</a></p>
  <p class="sub">Nós de escolha (Thread, exército, líder etc.) aparecem marcados no link; escolha a opção indicada na tabela ao clicar neles.</p>
  <div class="diagram tree-real" role="img" aria-label="Árvore do Atlas com o caminho desta mecânica: essenciais em destaque, extras em outra cor.">{ATLAS.svg(alloc)}</div>
  <h3 style="margin-top:14px">Dicas</h3><ul class="atl">{tips}</ul></section>'''

def video(vid, cap):
    return (f'<figure class="showcase"><div class="frame"><button type="button" class="yt" data-id="{vid}" aria-label="Assistir: {e(cap)}">'
            f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="Miniatura do vídeo" loading="lazy"><span></span></button></div>'
            f'<figcaption>{e(cap)} <a href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener">Abrir no YouTube</a></figcaption></figure>')
SHORT = {'fates': 'Fates', 'pinnacles': 'Pinnacles'}
nav = ''.join(f'<a href="{m["slug"]}.html">{e(SHORT.get(m["slug"], m["name"]))}</a>' for m in FARM)
for m in FARM:
    tags = ''.join(f'<span class="pill {c}">{e(t)}</span>' for c, t in m['tags'])
    steps = ''.join(f'<li>{e(s)}</li>' for s in m['steps'])
    setup = ''.join(f'<tr><td>{e(a)}</td><td>{e(b)}</td></tr>' for a, b in m['setup'])
    atlas = ''.join(f'<li>{e(a)}</li>' for a in m['atlas'])
    atlas_html = atlas_section(m['slug'], atlas)
    builds = ', '.join(f'<a href="../builds/{s}.html">{e(n)}</a>' for s, n in m['builds'])
    vids = ''.join(video(v, c) for v, c in m['videos'])
    vids += (f'<p class="note" style="margin-top:12px"><a class="treelink" href="{e(YT(m["search"]))}" target="_blank" rel="noopener">Ver vídeos da 3.30 no YouTube</a><br>'
             'Busca pronta pela 3.30. A árvore do Atlas saiu antes da liga; os vídeos de farm da 3.30 começam a aparecer a partir do lançamento (13/11).</p>')
    if not m['videos']:
        vids = '<p class="muted">Ainda não há vídeo de farm desta mecânica na 3.30.</p>' + vids
    body = f'''<div class="wrap">
<header>
  <div class="eyebrow">Farm 3.30 · Covens of Umbra</div>
  <h1>{e(m["name"])}</h1>
  <div class="facts">{tags}</div>
  <p class="lede">{e(m["intro"])}</p>
</header>
<nav class="sec" aria-label="Mecânicas"><a href="./">Todas</a>{nav}</nav>
<section id="como"><h2>Como fazer</h2><ol class="steps">{steps}</ol></section>
<section id="setup"><h2>Montagem do mapa</h2><div class="tbl fit"><table class="split"><colgroup><col style="width:28%"><col style="width:72%"></colgroup><thead><tr><th>Item</th><th>Como usar</th></tr></thead><tbody>{setup}</tbody></table></div></section>
{atlas_html}
<section id="build"><h2>Build que combina</h2><p>{e(m["build_note"])}</p><p>Do site: {builds}.</p></section>
<section id="videos"><h2>Vídeos</h2>{vids}</section>
<footer>Regras: <a href="https://www.pathofexile.com/forum/view-thread/4013680" target="_blank" rel="noopener">notas oficiais da 3.30.0</a>. Vídeos de ligas anteriores servem de referência de como a mecânica funciona; as recompensas e o Atlas mudaram.</footer>
</div>
<script src="../assets/video.js"></script>
</body></html>
'''
    open(os.path.join(ROOT, 'farm', m['slug'] + '.html'), 'w', encoding='utf-8').write(HEAD.format(title=e(m['name']), desc=e(m['intro'])) + body)
    print(m['slug'])

# ---- hub: Atlas plan section inside farm/index.html (between markers) ----
S = AP.STRATS
EXTRA = ['Subtle Manipulations', 'Significant Troves', 'Blood Feud', 'Height of Horror']
MAIN = [AP.BASE, S['legion'][0], S['beyond'][0], S['ritual'][0], EXTRA]
alloc, per = ATLAS.plan(MAIN)
cum = [sum(per[:i + 1]) for i in range(len(per))]
color = {0: 1, 1: 1, 2: 2, 3: 2, 4: 3, 5: 3}
show = {k: color[p] for k, p in alloc.items()}
alt, per2 = ATLAS.plan([AP.BASE, S['ultimatum'][0], S['expedition'][0], ['Subtle Manipulations', 'Significant Troves']])
def names(lst): return ', '.join(f'<b>{e(x.strip())}</b>' for x in lst)
steps = [
 ('1. Base de sustento', 'Mapas brancos', AP.BASE, 'Mais raros, mapas subindo de tier e mais Threads de raros e do boss. Vale para qualquer mecânica.', None),
 ('2. Legion', 'Mapas amarelos', S['legion'][0], 'Sinistral Threads: escolha Legion.', 'legion.html'),
 ('3. Beyond', 'Mapas amarelos/vermelhos', S['beyond'][0], 'Outside Entities: escolha Demonic Evocator.', 'beyond.html'),
 ('4. Ritual', 'Mapas vermelhos', S['ritual'][0], 'Dextral Threads: escolha Ritual.', 'ritual.html'),
 ('5. Fechamento', 'Endgame', EXTRA, 'Blood Feud: escolha Karui ou Vaal.', None),
]
rows = ''.join(f'<tr><td><b>{t}</b><br><span class="sub">{w}<br>{per[i]} pontos (total {cum[i]})</span></td>'
               f'<td>{names(n)}. {d}{f" <a href={chr(34)}{l}#atlas{chr(34)}>Detalhes →</a>" if l else ""}</td></tr>'
               for i, (t, w, n, d, l) in enumerate(steps))
HUB = f'''<!-- atlas:start -->
<section id="atlas">
  <h2>Árvore do Atlas 3.30: o plano</h2>
  <p>A GGG publicou a árvore nova do Atlas antes da liga. A gente calculou os caminhos com os dados oficiais (o mesmo arquivo que o site da GGG usa).</p>
  <div class="why">
    <div><h3>150 pontos, do centro para fora</h3><p>A árvore cresce a partir do centro. Delve e Heist saíram. Os efeitos dos antigos Scarabs viraram nós da árvore.</p></div>
    <div><h3>Você escolhe a Thread que cai</h3><p><b>Sinistral Threads</b> (Abyss, Bestiary, Blight, Betrayal, Legion) e <b>Dextral Threads</b> (Breach, Ritual, Ultimatum, Expedition, Incursion) dão +200% de chance das Threads caírem do tipo escolhido. <b>Threadbare</b> e <b>Unthreaded</b> bloqueiam um tipo.</p></div>
    <div><h3>Nós de escolha</h3><p>Vários nós pedem uma escolha: <b>Outside Entities</b> (Wildwood, Evocator, Delirium…), <b>Blended Realities</b> (Harvest, Shrine…), <b>Blood Feud</b> (exército da Legion), <b>Kalguuran Companionship</b> (Tujen, Gwennen…).</p></div>
    <div><h3>Threads em todo lugar</h3><p><b>Amplified Artefacts</b> (raros), <b>Chittering Champions</b> (boss) e <b>Significant Troves</b> (uniques) aumentam a Thread que cai. <b>Subtle Manipulations</b>: 20% de chance de não gastar as Threads.</p></div>
  </div>
  <h3 style="margin-top:16px">Plano recomendado: Legion + Beyond + Ritual ({cum[-1]} de 150 pontos)</h3>
  <p class="sub">Combina com as builds de clear do site (Spark, RF, Toxic Rain, SRS). Pegue na ordem: cada fase já funciona sozinha.</p>
  <div class="tbl fit"><table class="split narrow"><colgroup><col style="width:30%"><col style="width:70%"></colgroup><thead><tr><th>Fase</th><th>O que pegar</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p style="margin-top:12px"><a class="treelink" href="{ATLAS.url(alloc)}" target="_blank" rel="noopener">Abrir o plano completo no site oficial</a></p>
  <div class="diagram tree-real" role="img" aria-label="Árvore do Atlas com o plano: base e Legion numa cor, Beyond e Ritual em outra, fechamento em uma terceira.">{ATLAS.svg(show)}</div>
  <p class="sub">Cores: base e Legion · Beyond e Ritual · fechamento. Nos nós de escolha, selecione a opção indicada na tabela.</p>
  <h3 style="margin-top:16px">Alternativa para builds tanques: Ultimatum + Expedition ({sum(per2)} pontos)</h3>
  <p>Base de sustento ({per2[0]}) + <a href="ultimatum.html#atlas">Ultimatum</a> ({per2[1]}) + <a href="expedition.html#atlas">Expedition</a> ({per2[2]}) + Subtle Manipulations e Significant Troves ({per2[3]}). Use Dextral Threads para a mecânica principal. Boa para Earthshatter, Storm Burst e as builds de minion/DoT. <a href="{ATLAS.url(alt)}" target="_blank" rel="noopener">Abrir no site oficial</a>.</p>
</section>
<!-- atlas:end -->'''
ip = os.path.join(ROOT, 'farm', 'index.html'); h = open(ip).read()
if '<!-- atlas:start -->' in h:
    a = h.index('<!-- atlas:start -->'); b = h.index('<!-- atlas:end -->') + len('<!-- atlas:end -->')
    h = h[:a] + HUB + h[b:]
else:
    i = h.index('<section id="fases">'); h = h[:i] + HUB + '\n\n' + h[i:]
open(ip, 'w').write(h); print('hub', per, cum[-1], per2)
