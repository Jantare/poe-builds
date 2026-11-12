"""Leveling routes into Spark for the Trickster Spark page, built from the guides' PoB files."""
import os, re, html, xml.etree.ElementTree as ET
from videos import showcase
import gen_safe
e = html.escape
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
clean = lambda s: re.sub(r'\^x[0-9A-Fa-f]{6}|\^\d', '', s or '').strip()

ROUTES = [
 dict(key='cobra', name='Cobra Lash → Poisonous Concoction', tag='Recomendada', xml='lvl-cobra.xml', author='xRoGeSx', league='3.30',
      video='n0QfdZIqGLE', guide='https://www.poebuilds.cc/poe1/build/n0QfdZIqGLE', pobb='qf2CPIx0WMfl', refund=63,
      sets=lambda t: t.lower().startswith('act'),
      intro='A rota mais rápida e mais atual (feita para a 3.30). Cobra Lash nos primeiros minutos e Poisonous Concoction até o fim da campanha. A Poisonous Concoction usa cargas de frasco em vez de arma, então você nem precisa achar arma boa.',
      pros=['Mais rápida e mais forte nos atos', 'Vídeo e PoB da 3.30', 'Não depende de arma'],
      cons=['Árvore de veneno e projétil: na troca, ~63 pontos para devolver', 'Precisa de Dex e de frascos com cargas']),
 dict(key='magma', name='Rolling Magma → Armageddon Brand', tag='Troca mais suave', xml='lvl-magma.xml', author='FearlessDumb0', league='3.23',
      video='LXwLgREzSOI', guide='https://www.poebuilds.cc/poe1/build/LXwLgREzSOI', pobb='_MDwwhrhEDrh', refund=55,
      sets=lambda t: t.lower().startswith('act'),
      intro='Rolling Magma nos Atos 1–2 e Armageddon Brand do Ato 3 ao 10, já como Trickster. É feitiço, então a troca para o Spark muda menos coisas. O Maxroll também usa Armageddon Brand no guia de leveling de Shadow (campanha em menos de 3 horas).',
      pros=['Já é Trickster e feitiço', 'Menos pontos para devolver (~55)', 'Skills sem mudança na 3.30'],
      cons=['Guia da 3.23 (mecânica igual, mas confira as gemas)', 'Precisa de Fire Trap para os bosses']),
]

def sets_of(route):
    root = ET.parse(os.path.join(ROOT, 'data/pob', route['xml'])).getroot()
    out = []
    for ss in root.find('Skills').findall('SkillSet'):
        title = clean(ss.get('title'))
        if not route['sets'](title):
            continue
        rows = []
        for sk in ss.findall('Skill'):
            gems = [g.get('nameSpec') for g in sk.findall('Gem') if g.get('nameSpec') and g.get('enabled') != 'false']
            if gems and sk.get('enabled') != 'false':
                rows.append(gems)
        rows.sort(key=lambda g: -len(g))
        out.append((title, rows))
    return out

def act_label(title):
    t = re.sub(r'(?i)^act', 'Ato', title)
    t = t.replace(' through ', '–').replace('Generals Cry', "General's Cry").replace('Adding Crit', 'crítico').replace('Pre-PCONC', 'início').replace('PCONC ( Right before Meriveil )', 'antes da Merveil')
    return t

def route_html(r):
    with open(os.path.join(ROOT, 'data/pob', r['xml']), 'rb') as f:
        gen_safe.write_code('lvl-' + r['key'], f.read())
    sets = sets_of(r)
    chips = ''.join(f'<a href="#{r["key"]}-{i}">{e(act_label(t).split(":")[0])}</a>' for i, (t, _) in enumerate(sets))
    cards = []
    for i, (t, rows) in enumerate(sets):
        lines = []
        linked = [g for g in rows if len(g) > 1]
        singles = [g[0] for g in rows if len(g) == 1]
        for j, g in enumerate(linked[:5]):
            gs = '<i class=chain></i>'.join(f'<span class="gem{" main" if k == 0 and j == 0 else ""}">{e(x)}</span>' for k, x in enumerate(g))
            lines.append(f'<div class="links">{gs}</div>')
        if singles:
            lines.append('<div class="links"><span class="sub" style="margin-right:4px">Também:</span>' + ''.join(f'<span class="gem">{e(x)}</span>' for x in singles) + '</div>')
        cards.append(f'<div class="actcard" id="{r["key"]}-{i}"><h4>{e(act_label(t))}</h4>{"".join(lines)}</div>')
    pros = ''.join(f'<li>{e(p)}</li>' for p in r['pros']); cons = ''.join(f'<li>{e(c)}</li>' for c in r['cons'])
    vid = showcase('lvl-' + r['key'], r['name']).replace('<section id="showcase"><h2>Showcase</h2>', '').replace('</section>', '')
    return f'''<div class="route" id="rota-{r["key"]}">
  <div class="mhead"><h3>{e(r["name"])}</h3><div class="tags"><span class="pill {"ok" if r["tag"] == "Recomendada" else "new"}">{e(r["tag"])}</span><span class="pill">{e(r["author"])} · {e(r["league"])}</span></div></div>
  <p>{e(r["intro"])}</p>
  <div class="cols"><div><h4 class="good">A favor</h4><ul>{pros}</ul></div><div><h4 class="badc">Contra</h4><ul>{cons}</ul></div></div>
  <div class="jump" aria-label="Ir para o ato">{chips}<a href="#troca">Troca para Spark</a></div>
  <div class="acts2">{"".join(cards)}</div>
  <div class="routefoot">
    {gen_safe.pob_button('lvl-' + r['key']).replace('Copiar código do PoB', 'Copiar PoB desta rota')}
    <p class="sub">Fonte: <a href="{e(r["guide"])}" target="_blank" rel="noopener">guia de {e(r["author"])}</a> · <a href="https://pobb.in/{e(r["pobb"])}" target="_blank" rel="noopener">PoB no pobb.in</a> · <a href="https://www.youtube.com/watch?v={e(r["video"])}" target="_blank" rel="noopener">vídeo</a></p>
  </div>
  {vid}
</div>'''

def section(old_spark_checklist):
    routes = ''.join(route_html(r) for r in ROUTES)
    return f'''<section id="atos">
  <h2>Leveling</h2>
  <p>O Spark é fraco nos primeiros atos: ele depende de crítico, de supports como Inspiration e Lightning Penetration e de arma de caster, que só chegam depois. O melhor é <b>upar com uma skill mais forte e trocar para o Spark no fim da campanha</b>.</p>
  <div class="jump big" aria-label="Escolha a rota"><a href="#rota-cobra">1 · Cobra Lash → Poisonous Concoction</a><a href="#rota-magma">2 · Rolling Magma → Armageddon Brand</a><a href="#troca">3 · Troca para Spark</a><a href="#spark-direto">4 · Spark desde o Ato 1</a></div>
  {routes}
  <div class="route" id="troca">
    <div class="mhead"><h3>Troca para Spark</h3><div class="tags"><span class="pill ok">Fim do Ato 10 ou primeiros mapas</span></div></div>
    <ol class="steps">
      <li>Durante a campanha, deixe o <b>Spark</b> num slot qualquer ganhando nível. Compre <b>Lightning Penetration, Inspiration e Increased Critical Strikes</b> (a Lilly Roth, no Ato 6, vende todas as gemas).</li>
      <li>Faça a <b>Rune Dagger</b> com +1 nível de gemas de raio: receita de vendor com Rune Dagger + 2 gemas de raio somando 40% de qualidade.</li>
      <li>Junte <b>Orbs of Regret</b>: são cerca de <b>63</b> pontos para devolver vindo da Cobra Lash e cerca de <b>55</b> vindo da Armageddon Brand (contando a árvore do Ato 10 de cada guia contra a nossa árvore do Spark). Na 3.30 a Orb of Regret também sai da receita de vendor de Bestiary.</li>
      <li>Troque a árvore aos poucos: primeiro os nós de dano (crítico de feitiço, raio), depois os de defesa (ES). Use a <a href="#arvore">árvore do Spark</a> como guia.</li>
      <li>Coloque o Spark no peito com 4–5 links e o equipamento de ES. Confira os <a href="#alvos">alvos de ES e resistência</a>. O Chaos Inoculation vem depois, com 4–5k de ES.</li>
    </ol>
  </div>
  <details class="route" id="spark-direto"><summary><b>Spark desde o Ato 1 (mais lento)</b> <span class="sub">checklist antigo, para quem quer jogar só de Spark</span></summary>
    {old_spark_checklist}
  </details>
</section>'''
