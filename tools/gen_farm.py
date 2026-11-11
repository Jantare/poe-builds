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
</head>
<body>
<header class="topbar"><div class="in">
  <a class="brand" href="../">PoE Builds</a>
  <div class="links"><a href="../">Início</a><a href="../#builds">Seguras</a><a href="../#youtube">YouTube</a><a href="../#apostas">Apostas</a><a href="./" aria-current="page">Farm</a><a href="../craft/">Craft</a><a href="../bau/">Baú</a><a href="../#ferramentas">Ferramentas</a></div>
</div></header>
'''
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
    builds = ', '.join(f'<a href="../builds/{s}.html">{e(n)}</a>' for s, n in m['builds'])
    vids = ''.join(video(v, c) for v, c in m['videos'])
    vids += (f'<p class="note" style="margin-top:12px"><a class="treelink" href="{e(YT(m["search"]))}" target="_blank" rel="noopener">Ver vídeos da 3.30 no YouTube</a><br>'
             'Busca pronta pela 3.30. A árvore nova do Atlas só sai no lançamento, então os vídeos de farm da 3.30 começam a aparecer a partir do dia 13.</p>')
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
<section id="atlas"><h2>Pontos do Atlas</h2>
  <p class="note"><strong>A árvore do Atlas foi refeita na 3.30</strong> e os nomes dos nós só saem no lançamento (13/11). Por enquanto, estes são os grupos de nós que o patch notes descreve. Quando a árvore sair, a gente coloca os nós exatos aqui.</p>
  <ul class="atl">{atlas}</ul></section>
<section id="build"><h2>Build que combina</h2><p>{e(m["build_note"])}</p><p>Do site: {builds}.</p></section>
<section id="videos"><h2>Vídeos</h2>{vids}</section>
<footer>Regras: <a href="https://www.pathofexile.com/forum/view-thread/4013680" target="_blank" rel="noopener">notas oficiais da 3.30.0</a>. Vídeos de ligas anteriores servem de referência de como a mecânica funciona; as recompensas e o Atlas mudaram.</footer>
</div>
<script src="../assets/video.js"></script>
</body></html>
'''
    open(os.path.join(ROOT, 'farm', m['slug'] + '.html'), 'w', encoding='utf-8').write(HEAD.format(title=e(m['name']), desc=e(m['intro'])) + body)
    print(m['slug'])
