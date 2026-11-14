"""Verificação 3.30 de cada build (12/11): o que a comunidade lançou e como fazer o leveling.
Cada item: (título, autor, data, vídeo, pobb, xml em data/pob ou None, texto)."""
NINJA = {'trickster-spark': 'Spark em 86º lugar, com 34 personagens (0,08%), e nenhum deles é Trickster. A Spark of the Nova tem 7.', 'trickster-ed': 'Essence Drain em 68º, com 55 personagens: 24 Occultist, 17 Witch e 14 Shadow (ainda sem ascensão). Nenhum Trickster no topo.', 'trickster-fireball': 'Fireball of Radiation em 210º, com 4 personagens. Quase ninguém testou ainda.', 'warden-tinturas': 'A Static Strike é a skill mais jogada da liga (5.163 personagens, 11,8%), mas com Guardian (1.722) e Slayer (1.621). A Warden tem só 133 personagens no total.', 'hierophant-ballista': 'Artillery Ballista em 22º, com 329 personagens, quase todos Deadeye (273). A versão de Hierophant aparece pouco.', 'rf-chieftain': 'Righteous Fire em 5º, com 1.628 personagens, 875 deles Chieftain. Continua uma das mais jogadas.', 'earthshatter-berserker': 'Earthshatter em 35º, com 181 personagens, 131 deles Berserker.', 'poison-srs-necromancer': 'Summon Raging Spirit em 11º, com 752 personagens: 439 Necromancer e 225 Witch (ainda nos atos).', 'stormburst-hierophant': 'Storm Burst em 10º, com 786 personagens, 714 deles Hierophant. Uma das mais fortes da liga até agora.', 'toxic-rain-pathfinder': 'Toxic Rain em 33º, com 192 personagens, 121 deles Pathfinder.', 'yt-ballista-hierophant': 'Explosive Arrow em 23º, com 300 personagens, 193 deles Hierophant.', 'yt-absolution-necromancer': 'Absolution em 4º, com 2.383 personagens, 1.451 deles Necromancer. Uma das mais jogadas da liga.', 'yt-cyclone-necromancer': 'Cyclone em 21º, com 345 personagens, mas quase todos Slayer (286). A versão de Necromancer aparece pouco.', 'yt-animate-weapon-necromancer': 'Animate Weapon em 60º (69 personagens) e a versão of Ranged Arms em 77º (41).', 'yt-spark-saboteur': 'Spark em 86º, com 34 personagens, e nenhum Saboteur entre eles. A Saboteur tem 122 personagens no total.'}
WARN = {'trickster-spark': 'Não recomendada. Testamos no começo da liga e não rendeu, e quase ninguém está jogando Spark na 3.30 (veja os números abaixo). Para começar a liga, prefira uma das builds mais jogadas: Righteous Fire, Storm Burst, Absolution ou SRS.', 'yt-spark-saboteur': 'Não recomendada por enquanto: é a mesma skill da Trickster Spark, que não rendeu no começo da liga.'}

U = {
 'trickster-spark': dict(status='Rotas de leveling adicionadas; nova alternativa de Spark com Saboteur', items=[
   ('Alternativa: Spark Saboteur (triggerbot)', 'Duleblade', '4/11', 'fN0Z-JV152M', 'sRdSgfUWKvQn', None,
    'Mesmo Spark com CI e Energy Shield, mas com Saboteur: a Arcanist Brand lança o Spark sozinha. No PoB de ~50 divines: 6,6 mil de ES, 93% de suppress e 4,1 milhões de DPS. Página completa em Do YouTube → Spark Saboteur.')],
   leveling='Suba com Cobra Lash → Poisonous Concoction (xRoGeSx, 3.30) ou Rolling Magma → Armageddon Brand e troque para Spark no fim da campanha. Detalhes na seção Leveling.'),
 'trickster-ed': dict(status='Saiu guia 3.30 da mesma skill (em Occultist)', items=[
   ('Essence Drain & Contagion Occultist', 'Goratha', '12/11', 'ACjUm3VMRBs', 'qmtZt-Dsx-gX', 'upd-qmtZt-Dsx-gX.xml',
    'Mesmo par de skills, mas em Occultist: 9 mil de ES e 26 milhões de DPS no PoB. Sobe com Kinetic Bolt (1–12), Kinetic Fusillade (12–28) e Spellslinger, e entra em Blight of Contagion com o cajado Cane of Unravelling. Bom para comparar dano e equipamento com a nossa versão em Trickster.')],
   leveling='O Essence Drain já funciona cedo. Se quiser campanha mais rápida, a rota de Cobra Lash da página do Trickster Spark serve igual, porque a árvore do começo é a mesma.'),
 'trickster-fireball': dict(status='Ainda sem guia de Trickster, mas o Pohx testou Fireball of Radiation', items=[
   ('Fireball of Radiation: novo dano de alvo único?', 'Pohx', '13/11', 'VVv9nJPu-yA', None, None,
    'Vídeo do Pohx testando a gema nova Fireball of Radiation como dano de alvo único para o RF. Não é guia de Trickster, mas é a primeira análise da gema por um criador grande. Vale ver antes de investir na nossa aposta.')],
   leveling='Fireball normal desde o Ato 1. O xRoGeSx tem um leveling de Fireball na 3.30 (Witch), que serve de referência para os links: Fireball nos Atos 1–3 e depois Spellslinger.'),
 'warden-tinturas': dict(status='Ascensão corrigida + guia 3.30 de Warden', items=[
   ('Static Strike Warden', 'tay6k', '12/11', 'Ibjwo3bowWo', '9xirqZz4Esg8', 'upd-9xirqZz4Esg8.xml',
    'Warden de verdade na 3.30, com raio corpo a corpo como a nossa ideia: Static Strike of Gathering Lightning + Trinity + Nightblade + Inspiration. Sobe com Rain of Arrows e troca para Static Strike. Usa Oath of Summer, Oath of Winter, Experienced Herbalist e Enduring Suffusion. Para seguir uma Warden pronta, este é o PoB mais concreto.')],
   leveling='Rain of Arrows na campanha e Static Strike depois, como no guia do tay6k.'),
 'hierophant-ballista': dict(status='Sem Artillery Ballista na 3.30; o POEGuy tem a versão de Explosive Arrow', items=[
   ('Atualização do POEGuy (Explosive Arrow Ballista)', 'POEGuy', '12/11', 'kJWbSFeivHU', None, None,
    'Vídeo novo do POEGuy: segundo o título, a build de Ballista dele não levou nerf e ganhou um buff importante na 3.30. Mesmo Hierophant e mesmos nós de totem da nossa aposta.'),
   ('Explosive Arrow Ballista Hierophant', 'POEGuy', '12/11', 'ds53La1IMD4', 'kQGOsJn7IbQX', 'upd-kQGOsJn7IbQX.xml',
    'O guia de totem de arco mais visto da 3.30. Mesmo Hierophant e mesmos nós de totem; troca a Artillery Ballista por Explosive Arrow com Ballista Totem.')],
   leveling='Holy Flame Totem nos Atos 1–3 (com Ancestral Bond) e Ballista do Ato 3 em diante, como no guia do POEGuy.'),
 'rf-chieftain': dict(status='Saiu guia 3.30 de RF (emiracle)', items=[
   ('Fireball of Radiation no RF', 'Pohx', '13/11', 'VVv9nJPu-yA', None, None,
    'O Pohx testou Fireball of Radiation como opção de dano de alvo único para o RF na 3.30. O guia escrito dele (link na descrição) é o lugar onde ele atualiza a build.'),
   ('Righteous Fire Chieftain', 'emiracle', '11/11', '28at7qBCvrI', '5iAfr9izzzWI', 'upd-5iAfr9izzzWI.xml',
    'Versão da 3.30: 5,8 mil de vida. Sobe com machado e Leap Slam, troca para RF cedo, usa Holy Flame Totem no nível 24 e volta ao RF no nível 31. O PoB tem árvores por nível (24, 31, 42, 49, 52, 60, 62) e por equipamento (Cloak of Flame, Rise of the Phoenix).')],
   leveling='No guia do Pohx (esta página), Sunder + Chance to Bleed até o nível ~31 e então RF. No do emiracle, Leap Slam e Holy Flame Totem. Os dois trocam para RF na mesma faixa.'),
 'earthshatter-berserker': dict(status='Ainda sem guia 3.30 de Earthshatter; o da 3.29 continua sem nerf', items=[],
   leveling='O PoB do The Wanderer começa no nível 75. Na campanha, use slams de leveling como no início do guia de RF do Pohx (Sunder ou Ground Slam + Chance to Bleed + Faster Attacks) até ter o Earthshatter com 4 links.'),
 'poison-srs-necromancer': dict(status='Saíram guias 3.30 de SRS', items=[
   ('Guia de campanha de SRS (Mobalytics)', 'ExFluent', '12/11', 'RrtlVywToJA', None, None,
    'Vídeo do ExFluent com o SRS de league start da 3.30 e um guia passo a passo no Mobalytics, do Ato 1 até os mapas (link na descrição). Bom complemento para o leveling desta página.'),
   ('Summon Raging Spirit Necromancer', 'LugoHQ e ExFluent', '11–12/11', 'Az9S_0sLcEE', '09K3EJQY0Jyj', 'upd-09K3EJQY0Jyj.xml',
    'Os dois usam o mesmo PoB da 3.30 (4,5 mil de vida no do LugoHQ). Bom para comparar com o do BalorMage desta página, que tem as árvores de leveling.')],
   leveling='Já incluído: o PoB do BalorMage tem árvores de 12, 30, 50 e 70 pontos e gemas por ato.'),
 'stormburst-hierophant': dict(status='Saíram planos 3.30 de Storm Burst (Palsteron, Blux e aer0)', items=[
   ('Storm Burst of Repulsion Hierophant (leveling)', 'Palsteron', '13/11', 'pwGUXX86mrA', 'UtDAEHasntHU', 'upd-UtDAEHasntHU.xml',
    'Plano de liga do Palsteron com Storm Burst of Repulsion. O PoB é a rota de leveling, com uma árvore por ato (1 ao 10) e respec no Ato 3: Holy Flame Totem e Fireball na campanha. Ele avisa que o guia completo sai durante a primeira semana.'),
   ('Storm Burst Totems Hierophant (SSF)', 'Blux', '12/11', 'rt4U8KAQ4PQ', 'bIad1Px2HBrM', 'upd-bIad1Px2HBrM.xml',
    'Plano SSF do Blux, montado a partir do personagem dele da 3.29: árvores do dia 1, do dia 2–3 e da troca para Storm Burst. No PoB: nível 96, 3,7 mil de vida e ~10 milhões de DPS por totem. Bom para ver a progressão sem trade.'),
   ('Stormburst Totem Hierophant', 'aer0planeGaming', '12/11', 'Md3YzL6L3b8', None, None,
    'O autor do guia de referência da 3.29 confirmou o Storm Burst como league starter da 3.30. O PoB e o FAQ ficam na planilha dele (link na descrição do vídeo).'),
   ('Freezing Pulse Hierophant (leveling)', 'ImSidVicious', '12/11', '5n5x3xifr5Y', 'yLFUu8sCzLUy', 'upd-yLFUu8sCzLUy.xml',
    'Hierophant de feitiço da 3.30 com árvore por ato (1 ao 10). Alternativa de leveling: Freezing Pulse na campanha e troca para Storm Burst em totens quando tiver Spell Totem e 4 links.')],
   leveling='Use a rota do Palsteron (acima): árvore por ato e Holy Flame Totem/Fireball na campanha. O Freezing Pulse do ImSidVicious continua como alternativa.'),
 'toxic-rain-pathfinder': dict(status='Atualizado para a versão 3.30 do PathofEvening', items=[],
   leveling='Já incluído: Caustic Arrow (1–12) e Toxic Rain do nível 12 em diante, com árvores do Ato 1 ao endgame.'),
 'yt-ballista-hierophant': dict(status='PoB atualizado pelo POEGuy em 12/11 e vídeo novo sem nerf', items=[
   ('Atualização da build (vídeo)', 'POEGuy', '12/11', 'kJWbSFeivHU', None, None,
    'Vídeo novo do POEGuy sobre o starter dele na 3.30. Pelo título, a build não levou nerf e ganhou um buff importante; nas notas da 3.30, a mudança que mais combina é a Artillery Quiver (+1 totem para skills de ataque). O guia escrito no poe-vault (link na descrição) é onde ele atualiza a build.'),],
   leveling='Já incluído: Holy Flame Totem nos Atos 1–3 e Explosive Arrow Ballista do Ato 3 ao 10.'),
 'yt-absolution-necromancer': dict(status='Sem mudanças desde o vídeo (já é da 3.30)', items=[], leveling='Já incluído: árvore e gemas por ato.'),
 'yt-cyclone-necromancer': dict(status='Sem mudanças desde o vídeo (já é da 3.30)', items=[], leveling='Já incluído: minions na campanha e Cyclone com Soulwrest no fim.'),
 'yt-spark-saboteur': dict(status='Vídeo da 3.30 (4/11); PoB ainda na árvore 3.29', items=[],
   leveling='O PoB do Duleblade não tem leveling. Na campanha, use as rotas da Trickster Spark (Cobra Lash ou Rolling Magma) e troque para Spark com Arcanist Brand no fim dos atos; o autor dá uma dica de craft de trigger no Ato 9 (no vídeo, aos 1:44).'),
 'yt-animate-weapon-necromancer': dict(status='Sem mudanças desde o vídeo (já é da 3.30)', items=[],
   leveling='O PoB do Aleshxile é só do endgame. Na campanha, suba de Summon Raging Spirit como no guia de Poison SRS (mesmo Necromancer) e troque para Animate Weapon of Ranged Arms nos mapas.'),
}

def section(slug, write_code, pob_button, esc):
    u = U.get(slug)
    if not u:
        return ''
    cards = []
    for title, author, date, vid, pobb, xml, text in u['items']:
        btn = ''
        if xml:
            import os
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            with open(os.path.join(root, 'data/pob', xml), 'rb') as f:
                write_code('upd-' + pobb, f.read())
            btn = pob_button('upd-' + pobb).replace('Copiar código do PoB', 'Copiar PoB 3.30')
        cards.append(f'''<div class="route"><div class="mhead"><h3>{esc(title)}</h3><div class="tags"><span class="pill new">3.30</span><span class="pill">{esc(author)} · {esc(date)}</span></div></div>
  <p>{esc(text)}</p>
  <p class="sub"><a href="https://www.youtube.com/watch?v={esc(vid)}" target="_blank" rel="noopener">Vídeo</a>{f' · <a href="https://www.poebuilds.cc/poe1/build/{esc(vid)}" target="_blank" rel="noopener">Guia no poebuilds.cc</a> · <a href="https://pobb.in/{esc(pobb)}" target="_blank" rel="noopener">PoB no pobb.in</a>' if pobb else ' · sem PoB no vídeo'}</p>
  {btn}</div>''')
    warn = f'<p class="note bad"><strong>⚠ {esc(WARN[slug])}</strong></p>' if slug in WARN else ''
    ninja = f'<p class="note"><strong>No poe.ninja (14/11, primeiro dia, 43.630 personagens):</strong> {esc(NINJA[slug])} Muita gente ainda está nos atos, então os números mudam nos próximos dias.</p>' if slug in NINJA else ''
    return f'''<section id="novidades">
  <h2>Atualização 3.30</h2>
  {warn}
  <p class="note"><strong>{esc(u["status"])}.</strong> Verificado em 13/11 (dia do lançamento) nos guias e vídeos da 3.30. O Path of Building ainda não tem a árvore 3.30: os PoBs usam a árvore 3.29.</p>
  {ninja}
  <p><b>Leveling:</b> {esc(u["leveling"])}</p>
  {"".join(cards)}
</section>'''
