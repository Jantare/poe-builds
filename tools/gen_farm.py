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
from atlas_render import render as RENDER
IMG = os.path.join(ROOT, 'farm', 'img'); os.makedirs(IMG, exist_ok=True)
ATLAS = AP.Atlas()
def node_rows(alloc, targets, prio, start=1):
    rows = []
    for i, t in enumerate(targets, start):
        k = ATLAS.find(t)
        rows.append(f'<tr><td><span class="num">{i}</span> <b>{e(ATLAS.N[k]["name"])}</b><br><span class="pill {"ok" if prio==1 else "warn"}">{"Essencial" if prio==1 else "Extra"}</span></td><td>{AP.PT[t]}</td></tr>')
    return ''.join(rows)
def atlas_section(slug, tips):
    ph = AP.STRATS[slug]
    alloc, per = ATLAS.plan(ph)
    rows = node_rows(alloc, ph[0], 1) + node_rows(alloc, ph[1], 2, len(ph[0]) + 1)
    tg = [ATLAS.find(t) for p in ph for t in p]
    RENDER(ATLAS, alloc, {k: i + 1 for i, k in enumerate(tg)}, os.path.join(IMG, slug + '.webp'))
    return f'''<section id="atlas"><h2>Pontos do Atlas</h2>
  <p class="note"><strong>Árvore oficial da 3.30</strong> (a GGG publicou antes da liga). Caminho a partir do centro: <b>{per[0]} pontos</b> para os essenciais e <b>+{per[1]}</b> para os extras. A árvore tem 150 pontos no total. Some com a <a href="./#atlas">base de sustento</a> (36 pontos).</p>
  <div class="tbl fit"><table class="split narrow"><colgroup><col style="width:34%"><col style="width:66%"></colgroup><thead><tr><th>Nó</th><th>O que faz</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p style="margin-top:12px"><a class="treelink" href="{ATLAS.url(alloc)}" target="_blank" rel="noopener">Abrir no site oficial (árvore do Atlas)</a></p>
  <p class="sub">Nós de escolha (Thread, exército, líder etc.) aparecem marcados no link; escolha a opção indicada na tabela ao clicar neles.</p>
  <figure class="atlasimg"><a href="img/{slug}.webp" target="_blank" rel="noopener"><img src="img/{slug}.webp" alt="Árvore do Atlas com o caminho desta mecânica aceso; os números batem com a tabela." loading="lazy"></a><figcaption>Arte oficial da árvore do Atlas. O caminho aceso é o que você pega; os números batem com a tabela. Toque para ampliar.</figcaption></figure>
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
phase_of = {}
for i, grp in enumerate(MAIN, 1):
    for t in grp: phase_of.setdefault(ATLAS.find(t), i)
RENDER(ATLAS, alloc, phase_of, os.path.join(IMG, 'plano.webp'), max_w=2400)
alt, per2 = ATLAS.plan([AP.BASE, S['ultimatum'][0], S['expedition'][0], ['Subtle Manipulations', 'Significant Troves']])
def names(lst): return ', '.join(f'<b>{e(x.strip())}</b>' for x in lst)
steps = [
 ('1. Base de sustento', 'Mapas brancos', AP.BASE, 'Mais raros, mapas subindo de tier e mais Threads de raros e do boss. Vale para qualquer mecânica.', None),
 ('2. Legion', 'Mapas amarelos', S['legion'][0], 'Sinistral Threads: escolha Legion.', 'legion.html'),
 ('3. Beyond', 'Mapas amarelos/vermelhos', S['beyond'][0], 'Outside Entities: escolha Demonic Evocator.', 'beyond.html'),
 ('4. Ritual', 'Mapas vermelhos', S['ritual'][0], 'Dextral Threads: escolha Ritual.', 'ritual.html'),
 ('5. Fechamento', 'Endgame', EXTRA, 'Blood Feud: escolha Karui ou Vaal.', None),
]
rows = ''.join(f'<tr><td><span class="num">{i + 1}</span> <b>{t[3:]}</b><br><span class="sub">{w}<br>{per[i]} pontos (total {cum[i]})</span></td>'
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
  <figure class="atlasimg"><a href="img/plano.webp" target="_blank" rel="noopener"><img src="img/plano.webp" alt="Árvore do Atlas com o plano completo aceso; o número em cada nó é a fase da tabela." loading="lazy"></a><figcaption>Arte oficial da árvore do Atlas. O número em cada nó é a fase da tabela. Nos nós de escolha, selecione a opção indicada. Toque para ampliar.</figcaption></figure>
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

# ---- hub: farm combinations (between combos markers) ----
SHR = ['Supplication', 'Syncretism', 'Drawn to Power', 'False Prophets']
COMBOS = [
 dict(key='legion-ritual', name='Shrines → Legion → Ritual (+ Harvest leve)', tag='O nosso combo', when='Do primeiro mapa ao endgame',
  phases=[('Base de sustento', AP.BASE), ('Shrines', ['Supplication', 'Syncretism', 'Drawn to Power']), ('Legion', S['legion'][0]), ('Ritual', S['ritual'][0]),
          ('Harvest leve', ['Call of the Grove', 'Doubling Season']),
          ('Fechamento', ['Outside Entities', 'Blood Feud', 'Subtle Manipulations', 'Significant Troves'])],
  threads='Só Legion e Ritual. Comece com 1–3 Legion Threads; quando tiver Ritual Threads, use as duas no mesmo mapa (por exemplo 4 + 4: com 4 Ritual Threads abrem 2 slots de Blood-filled Vessel). Shrines e Harvest não têm Thread: vêm da árvore.',
  why=['Shrines custam só 12 pontos e deixam o clear mais rápido e mais seguro desde o primeiro mapa: mais Shrines (Supplication), buffs 30% mais fortes com um efeito extra (Syncretism) e packs a mais perto deles (Drawn to Power).',
       'Os altares de Ritual revivem monstros que você já matou no mapa. A Legion solta dezenas de raros de uma vez, então o Ritual revive esses raros e dá muito Tribute (Exacting Tribute reduz a perda de Tribute dos revividos).',
       'Harvest leve: na 3.30 ele acontece dentro do mapa, sem descer no bosque, então não atrasa. Dois nós baratos (Call of the Grove e Doubling Season) fazem ele aparecer mais e render mais Lifeforce.',
       'Fechamento: Outside Entities com a Viridian Wildwood (+50% de Tribute no Ritual), Blood Feud (exército da Legion), Subtle Manipulations (20% de chance de não gastar as Threads) e Significant Troves (mais Threads dos uniques).'],
  build='Spark, RF, Toxic Rain, SRS: builds de clear que matam a Legion rápido e aguentam o último altar.'),
 dict(key='shrines', name='Começo sem gastar: Shrines → Legion', tag='Primeiros dias', when='Atlas branco e amarelo, antes de ter Threads sobrando',
  phases=[('Base de sustento', AP.BASE), ('Shrines', SHR), ('Legion', S['legion'][0])],
  threads='Nenhuma no começo: os Shrines vêm só da árvore. Quando sobrarem Legion Threads (das Regiões Moldadas e dos altares do Eater), entram aos poucos.',
  why=['Supplication põe mais Shrines no mapa, Syncretism deixa os buffs 30% mais fortes e com um efeito extra, e False Prophets dá um Apparition Shrine a mais.',
       'Os buffs de Shrine deixam o clear mais rápido e mais seguro sem gastar nada. É o que mais criadores estão usando para completar o Atlas na 3.30, segundo os títulos dos vídeos (sirgog, Coolingmoon).',
       'Drawn to Power põe packs extras perto dos Shrines: mais monstros, mais loot.'],
  build='Qualquer build. Bom para completar o Atlas e juntar Threads.'),
 dict(key='sirgog', fixed='sirgog-330.txt', name='Primeiros 60 pontos: Shrines + mapas + monstros mágicos (sirgog)', tag='Árvore de criador', author='sirgog',
  when='Começo do Atlas, antes de investir em Threads',
  video='https://www.youtube.com/watch?v=aBH5UZqjwxg',
  planner='https://www.pathofpathing.com/?v=3.30.0-atlas#AAAABgAADw4AB4ggN1AXYCFgZ219cXV7XYsYq3_KoupV767y33F1AAA=',
  phases=[('Sustento de mapas', ['Shaping the Mountains', 'Shaping the Skies', 'Shaping the World']),
          ('Shrines', ['Supplication', 'Syncretism', 'Drawn to Power', 'Path of Worship']),
          ('Monstros mágicos', ['Group Solidarity', 'Deep Bloodlines'])],
  threads='Nenhuma: tudo vem da árvore. É o plano para os primeiros 60 pontos, enquanto você junta Threads e completa o Atlas.',
  why=['Os três Shaping (Mountains, Skies e World) fazem os mapas que caem subirem de tier: é o que mantém você com mapas no começo, já que na 3.30 o boss solta bem menos mapa de tier acima.',
       'Shrines de graça: Supplication põe mais Shrines, Syncretism deixa os buffs 30% mais fortes com um efeito extra, Drawn to Power põe packs a mais perto deles, e Path of Worship deixa você escolher o tipo de Shrine.',
       'Monstros mágicos: Group Solidarity transforma 4 packs em mágicos e Deep Bloodlines aumenta o tamanho dos packs mágicos. Mais monstros mágicos, mais loot e mais experiência.',
       'Os 60 pontos batem exatamente com o título do vídeo. O link do Path of Pathing traz os nós-alvo; o caminho foi calculado aqui com a árvore oficial.'],
  build='Qualquer build. Depois dos 60 pontos, siga para o combo Legion → Ritual.'),
 dict(key='legion-beyond', name='Legion + Beyond', tag='Clear rápido', when='Mapas amarelos e vermelhos',
  phases=[('Base de sustento', AP.BASE), ('Legion', S['legion'][0]), ('Beyond', S['beyond'][0]), ('Fechamento', S['legion'][1] + S['beyond'][1])],
  threads='Só Legion Threads. O Beyond não tem Thread: os nós aumentam a chance do Demonic Evocator.',
  why=['Cada monstro morto pode abrir um portal de Beyond. A Legion mata dezenas de monstros de uma vez, então os portais aparecem em sequência.',
       'Na 3.30 os demônios raros e uniques do Beyond soltam a currency boa, e matar o boss do Beyond dá Demonic Power por 60s.',
       'Cuidado: os uniques do Beyond batem forte. Pegue Height of Horror e True Terrors só quando a build aguentar.'],
  build='Spark e Toxic Rain (muito clear). Precisa de defesa razoável.'),
 dict(key='ritual-harvest', name='Ritual + Harvest', tag='Mais tranquilo', when='Mapas vermelhos',
  phases=[('Base de sustento', AP.BASE), ('Ritual', S['ritual'][0]), ('Harvest', S['harvest'][0]), ('Fechamento', ['Outside Entities', 'Blended Realities', 'Rich Soil', 'Verdant Lands'])],
  threads='Ritual Threads (8 para 3 slots de Vessel). Harvest e Wildwood vêm da árvore.',
  why=['O Ritual dá Omens (na 3.30, rerolar sempre gera pelo menos uma) e o Harvest dá Lifeforce para vender ou craftar.',
       'Outside Entities com a Viridian Wildwood (+50% de Tribute) e Blended Realities com a Sacred Flora.',
       'Ritmo mais calmo que a Legion: bom para builds mais lentas ou mais tanques.'],
  build='RF, Earthshatter, Storm Burst, builds de minion.'),
 dict(key='poeguy', fixed='poeguy-330.txt', name='Blight + Ultimatum + Minério (POEGuy)', tag='Árvore de criador', author='POEGuy',
  when='Progressão do Atlas segundo o guia dele',
  video='https://www.youtube.com/watch?v=IRAJSTKWyWM',
  planner='https://poeplanner.com/atlas-tree/BQAeAACOAGEf-CtjD2XiGaZ0acBFePiUVujcuMo9JN6itLEl-Z0JRJW7LiySQG9doBo4Sgkz_c1TXurzWyt4TyzSSB4aUSiYvPvxASUkwV6dmtg6Psn9MHZ9WkgTCgvMtx19t13lpn2RpsEOSt7-2hSiUrcieYRN19t-A7mjD4MzCEB7YMKqh50qXtaa5br3Mkoh9vtj4QKKvceOOX4306WCUSRqC5HxavCAf-Kzx-euPkYSFNMCVrgVQvuxzWnhWX21llrEhUZdFeBe3xB3ThvgDMsXKNWC6MmIJDKRzsQfru-RiZNh_bXw_RiLC3EfybnE_W2P5RQX2voda_e3nj3VaRjUhpB4Ww9oEoo_CIYGB_vUbEBo5DNvOD77dri51NAoFAAfiwgAAAAAAAADAwAAAAAAAAAAAA==',
  phases=[('Sustento de mapas', ['Shaping the World', 'Shaping the Skies']),
          ('Blight', ["Cassia's Pride", 'Rampant Infection', 'Sprawling Veins', 'Immunosuppression', 'Epidemiology', 'Biological Vector', 'Mycelial Swarm', 'Templar Ingenuity']),
          ('Ultimatum', ['Ruinous Wager', 'Stand Your Ground', 'Prove Yourself Worthy', "Trialmaster's Boon", 'Controlled Chaos', 'Bound for Utzaal', 'Trial by Fire']),
          ('Minério (Kingsmarch)', ["Prospector's Luck", 'Yield Upon Yield', "Fortune's Favour", 'Mineral Influence', 'Verisium Infusion', 'Lost in Transit']),
          ('Altares do Eater of Worlds', ['Eldritch Gaze', 'The Shadow of Hunger', 'Rampant Growth'])],
  threads='Blight e Ultimatum. Os altares do Eater of Worlds podem soltar Blight Threads, e a árvore reforça esses altares (Eldritch Gaze): o ciclo se alimenta.',
  why=["Blight com o keystone Cassia's Pride: os monstros levam 75% menos dano de você, mas as torres ficam muito mais fortes. Você joga só com as torres, então funciona até com build fraca.",
       'Ultimatum com Ruinous Wager: os monstros causam 50% menos dano, mas você falha com 7 de Ruin. Recompensa maior por rodada.',
       'Minério: mais Ore Deposits nos mapas para os envios de Kingsmarch (gold e itens).',
       'Não tem Legion nem Ritual: é outra linha de farm, boa para variar ou se o preço de Blighted Maps e catalisadores estiver alto.'],
  build='Qualquer build no Blight (as torres fazem o trabalho). No Ultimatum, builds tanques.'),
]

def combo_html(c):
    ph = [p for _, p in c['phases']]
    if c.get('fixed'):  # árvore de um criador: nós exatos, sem recalcular caminho
        ids = open(os.path.join(ROOT, 'data', 'atlas', c['fixed'])).read().split(',')
        alloc = {ATLAS.start: 0, **{k: 1 for k in ids}}
        byname = {ATLAS.N[k]['name']: k for k in ids}
        badges = {byname[t]: i for i, grp in enumerate(ph, 1) for t in grp if t in byname}
        cum = [len(ids)]
        RENDER(ATLAS, alloc, badges, os.path.join(IMG, f'combo-{c["key"]}.webp'), max_w=2200)
        rows = ''.join(f'<tr><td><span class="num">{i + 1}</span> <b>{e(n)}</b></td><td>{names(g)}.</td></tr>' for i, (n, g) in enumerate(c['phases']))
        why = ''.join(f'<li>{e(w)}</li>' for w in c['why'])
        return f'''<div class="route" id="combo-{c["key"]}">
  <div class="mhead"><h3>{e(c["name"])}</h3><div class="tags"><span class="pill new">{e(c["tag"])}</span><span class="pill">{len(ids)} de 150 pontos</span></div></div>
  <p class="sub">{e(c["when"])} · árvore de <a href="{e(c["video"])}" target="_blank" rel="noopener">{e(c["author"])}</a> (<a href="{e(c["planner"])}" target="_blank" rel="noopener">poeplanner</a>)</p>
  <p><b>Threads:</b> {e(c["threads"])}</p>
  <h4 style="margin-top:6px">O que ela faz</h4><ul class="atl">{why}</ul>
  <div class="tbl fit" style="margin-top:10px"><table class="split narrow"><colgroup><col style="width:30%"><col style="width:70%"></colgroup><thead><tr><th>Bloco</th><th>Nós principais</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p style="margin-top:10px"><a class="treelink" href="{ATLAS.url(alloc)}" target="_blank" rel="noopener">Abrir no site oficial</a></p>
  <figure class="atlasimg"><a href="img/combo-{c["key"]}.webp" target="_blank" rel="noopener"><img src="img/combo-{c["key"]}.webp" alt="Árvore do Atlas de {e(c["author"])}; o número em cada nó é o bloco da tabela." loading="lazy"></a><figcaption>Nós exatos da árvore do {e(c["author"])}. O número em cada nó é o bloco da tabela. Nos nós de escolha, a opção não vem no link. Toque para ampliar.</figcaption></figure>
  <p class="sub" style="margin-top:8px"><b>Builds:</b> {e(c["build"])}</p>
</div>'''
    alloc, per = ATLAS.plan(ph)
    cum = [sum(per[:i + 1]) for i in range(len(per))]
    badges = {}
    for i, grp in enumerate(ph, 1):
        for t in grp: badges.setdefault(ATLAS.find(t), i)
    RENDER(ATLAS, alloc, badges, os.path.join(IMG, f'combo-{c["key"]}.webp'), max_w=2200)
    rows = ''.join(f'<tr><td><span class="num">{i + 1}</span> <b>{e(n)}</b><br><span class="sub">{per[i]} pontos (total {cum[i]})</span></td>'
                   f'<td>{names(g)}.</td></tr>' for i, (n, g) in enumerate(c['phases']))
    why = ''.join(f'<li>{e(w)}</li>' for w in c['why'])
    return f'''<div class="route" id="combo-{c["key"]}">
  <div class="mhead"><h3>{e(c["name"])}</h3><div class="tags"><span class="pill ok">{e(c["tag"])}</span><span class="pill">{cum[-1]} de 150 pontos</span></div></div>
  <p class="sub">{e(c["when"])}</p>
  <p><b>Threads:</b> {e(c["threads"])}</p>
  <h4 style="margin-top:6px">Por que combina</h4><ul class="atl">{why}</ul>
  <div class="tbl fit" style="margin-top:10px"><table class="split narrow"><colgroup><col style="width:30%"><col style="width:70%"></colgroup><thead><tr><th>Fase</th><th>Nós</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p style="margin-top:10px"><a class="treelink" href="{ATLAS.url(alloc)}" target="_blank" rel="noopener">Abrir no site oficial</a></p>
  <figure class="atlasimg"><a href="img/combo-{c["key"]}.webp" target="_blank" rel="noopener"><img src="img/combo-{c["key"]}.webp" alt="Árvore do Atlas do combo {e(c["name"])}; o número em cada nó é a fase." loading="lazy"></a><figcaption>O número em cada nó é a fase da tabela. Pegue na ordem: cada fase já funciona sozinha. Toque para ampliar.</figcaption></figure>
  <p class="sub" style="margin-top:8px"><b>Builds:</b> {e(c["build"])}</p>
</div>'''

jump = ''.join(f'<a href="#combo-{c["key"]}">{e(c["name"])}</a>' for c in COMBOS)
CH = f'''<!-- combos:start -->
<section id="combos">
  <h2>Combinações de farm</h2>
  <p>Na 3.30 dá para usar até 3 tipos de Thread no mesmo mapa (até 8 Threads no total), e Harvest, Beyond e Shrines vêm só da árvore. Estes combos juntam mecânicas que se ajudam. Cada um está em fases: comece pela primeira e vá somando.</p>
  <p class="note"><strong>Ainda é teoria:</strong> a liga acabou de abrir. Os combos seguem as regras das notas oficiais e a árvore oficial; o ganho real só aparece depois dos primeiros dias de farm.</p>
  <div class="jump">{jump}</div>
  {"".join(combo_html(c) for c in COMBOS)}
</section>
<!-- combos:end -->'''
h = open(ip).read()
if '<!-- combos:start -->' in h:
    a = h.index('<!-- combos:start -->'); b = h.index('<!-- combos:end -->') + len('<!-- combos:end -->')
    h = h[:a] + CH + h[b:]
else:
    i = h.index('<!-- atlas:end -->') + len('<!-- atlas:end -->'); h = h[:i] + '\n\n' + CH + h[i:]
if '<a href="#combos">' not in h:
    h = h.replace('<a href="#atlas">Atlas</a>', '<a href="#atlas">Atlas</a><a href="#combos">Combos</a>', 1)
open(ip, 'w').write(h); print('combos', len(COMBOS))
