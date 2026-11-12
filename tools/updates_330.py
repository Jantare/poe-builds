"""Verificação 3.30 de cada build (12/11): o que a comunidade lançou e como fazer o leveling.
Cada item: (título, autor, data, vídeo, pobb, xml em data/pob ou None, texto)."""
U = {
 'trickster-spark': dict(status='Rotas de leveling adicionadas', items=[],
   leveling='Suba com Cobra Lash → Poisonous Concoction (xRoGeSx, 3.30) ou Rolling Magma → Armageddon Brand e troque para Spark no fim da campanha. Detalhes na seção Leveling.'),
 'trickster-ed': dict(status='Saiu guia 3.30 da mesma skill (em Occultist)', items=[
   ('Essence Drain & Contagion Occultist', 'Goratha', '12/11', 'ACjUm3VMRBs', 'qmtZt-Dsx-gX', 'upd-qmtZt-Dsx-gX.xml',
    'Mesmo par de skills, mas em Occultist: 9 mil de ES e 26 milhões de DPS no PoB. Sobe com Kinetic Bolt (1–12), Kinetic Fusillade (12–28) e Spellslinger, e entra em Blight of Contagion com o cajado Cane of Unravelling. Bom para comparar dano e equipamento com a nossa versão em Trickster.')],
   leveling='O Essence Drain já funciona cedo. Se quiser campanha mais rápida, a rota de Cobra Lash da página do Trickster Spark serve igual, porque a árvore do começo é a mesma.'),
 'trickster-fireball': dict(status='Ainda sem guia 3.30 com Fireball of Radiation', items=[],
   leveling='Fireball normal desde o Ato 1. O xRoGeSx tem um leveling de Fireball na 3.30 (Witch), que serve de referência para os links: Fireball nos Atos 1–3 e depois Spellslinger.'),
 'warden-tinturas': dict(status='Ascensão corrigida + guia 3.30 de Warden', items=[
   ('Static Strike Warden', 'tay6k', '12/11', 'Ibjwo3bowWo', '9xirqZz4Esg8', 'upd-9xirqZz4Esg8.xml',
    'Warden de verdade na 3.30, com raio corpo a corpo como a nossa ideia: Static Strike of Gathering Lightning + Trinity + Nightblade + Inspiration. Sobe com Rain of Arrows e troca para Static Strike. Usa Oath of Summer, Oath of Winter, Experienced Herbalist e Enduring Suffusion. Para seguir uma Warden pronta, este é o PoB mais concreto.')],
   leveling='Rain of Arrows na campanha e Static Strike depois, como no guia do tay6k.'),
 'hierophant-ballista': dict(status='Sem Artillery Ballista na 3.30; o POEGuy tem a versão de Explosive Arrow', items=[
   ('Explosive Arrow Ballista Hierophant', 'POEGuy', '12/11', 'ds53La1IMD4', 'kQGOsJn7IbQX', 'upd-kQGOsJn7IbQX.xml',
    'O guia de totem de arco mais visto da 3.30. Mesmo Hierophant e mesmos nós de totem; troca a Artillery Ballista por Explosive Arrow com Ballista Totem.')],
   leveling='Holy Flame Totem nos Atos 1–3 (com Ancestral Bond) e Ballista do Ato 3 em diante, como no guia do POEGuy.'),
 'rf-chieftain': dict(status='Saiu guia 3.30 de RF (emiracle)', items=[
   ('Righteous Fire Chieftain', 'emiracle', '11/11', '28at7qBCvrI', '5iAfr9izzzWI', 'upd-5iAfr9izzzWI.xml',
    'Versão da 3.30: 5,8 mil de vida. Sobe com machado e Leap Slam, troca para RF cedo, usa Holy Flame Totem no nível 24 e volta ao RF no nível 31. O PoB tem árvores por nível (24, 31, 42, 49, 52, 60, 62) e por equipamento (Cloak of Flame, Rise of the Phoenix).')],
   leveling='No guia do Pohx (esta página), Sunder + Chance to Bleed até o nível ~31 e então RF. No do emiracle, Leap Slam e Holy Flame Totem. Os dois trocam para RF na mesma faixa.'),
 'earthshatter-berserker': dict(status='Ainda sem guia 3.30 de Earthshatter; o da 3.29 continua sem nerf', items=[],
   leveling='O PoB do The Wanderer começa no nível 75. Na campanha, use slams de leveling como no início do guia de RF do Pohx (Sunder ou Ground Slam + Chance to Bleed + Faster Attacks) até ter o Earthshatter com 4 links.'),
 'poison-srs-necromancer': dict(status='Saíram guias 3.30 de SRS', items=[
   ('Summon Raging Spirit Necromancer', 'LugoHQ e ExFluent', '11–12/11', 'Az9S_0sLcEE', '09K3EJQY0Jyj', 'upd-09K3EJQY0Jyj.xml',
    'Os dois usam o mesmo PoB da 3.30 (4,5 mil de vida no do LugoHQ). Bom para comparar com o do BalorMage desta página, que tem as árvores de leveling.')],
   leveling='Já incluído: o PoB do BalorMage tem árvores de 12, 30, 50 e 70 pontos e gemas por ato.'),
 'stormburst-hierophant': dict(status='Ainda sem guia 3.30 de Storm Burst', items=[
   ('Freezing Pulse Hierophant (leveling)', 'ImSidVicious', '12/11', '5n5x3xifr5Y', 'yLFUu8sCzLUy', 'upd-yLFUu8sCzLUy.xml',
    'Hierophant de feitiço da 3.30 com árvore por ato (1 ao 10). Serve de rota de leveling: Freezing Pulse na campanha e troca para Storm Burst em totens quando tiver Spell Totem e 4 links.')],
   leveling='O PoB do Dsfarblarwaggle não tem leveling. Use o Freezing Pulse Hierophant do ImSidVicious (acima) ou o Holy Flame Totem dos Atos 1–3 do POEGuy, e troque para Storm Burst depois.'),
 'toxic-rain-pathfinder': dict(status='Atualizado para a versão 3.30 do PathofEvening', items=[],
   leveling='Já incluído: Caustic Arrow (1–12) e Toxic Rain do nível 12 em diante, com árvores do Ato 1 ao endgame.'),
 'yt-ballista-hierophant': dict(status='PoB atualizado pelo POEGuy em 12/11', items=[],
   leveling='Já incluído: Holy Flame Totem nos Atos 1–3 e Explosive Arrow Ballista do Ato 3 ao 10.'),
 'yt-absolution-necromancer': dict(status='Sem mudanças desde o vídeo (já é da 3.30)', items=[], leveling='Já incluído: árvore e gemas por ato.'),
 'yt-cyclone-necromancer': dict(status='Sem mudanças desde o vídeo (já é da 3.30)', items=[], leveling='Já incluído: minions na campanha e Cyclone com Soulwrest no fim.'),
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
  <p class="sub"><a href="https://www.youtube.com/watch?v={esc(vid)}" target="_blank" rel="noopener">Vídeo</a> · <a href="https://www.poebuilds.cc/poe1/build/{esc(vid)}" target="_blank" rel="noopener">Guia no poebuilds.cc</a> · <a href="https://pobb.in/{esc(pobb)}" target="_blank" rel="noopener">PoB no pobb.in</a></p>
  {btn}</div>''')
    return f'''<section id="novidades">
  <h2>Atualização 3.30</h2>
  <p class="note"><strong>{esc(u["status"])}.</strong> Verificado em 12/11 nos guias e vídeos da 3.30 do poebuilds.cc.</p>
  <p><b>Leveling:</b> {esc(u["leveling"])}</p>
  {"".join(cards)}
</section>'''
