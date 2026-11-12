"""YouTube showcase per build: (video id or None, caption)."""
VIDEOS = {
 'rf-chieftain': ('aXDVnydIXJw', 'Vídeo do guia do Pohx (3.29).'),
 'earthshatter-berserker': ('LiTI4yHtQiY', 'Vídeo do guia do The Wanderer (3.29).'),
 'poison-srs-necromancer': ('SX_52aI8Pws', 'Vídeo do guia do BalorMage (3.29).'),
 'stormburst-hierophant': ('im34olxgw_I', 'Vídeo do Dsfarblarwaggle (3.29).'),
 'toxic-rain-pathfinder': ('GsDMr2NZRao', 'Vídeo do PathofEvening (3.30).'),
 'yt-ballista-hierophant': ('zt5mwZTlRVI', 'Vídeo do POEGuy (3.30).'),
 'yt-absolution-necromancer': ('zotrvisDIuU', 'Vídeo do Travic (3.30).'),
 'yt-cyclone-necromancer': ('8X_geKpgCs8', 'Vídeo do Duleblade (3.30).'),
 'yt-animate-weapon-necromancer': ('WbDGNiNTJzI', 'Vídeo do Aleshxile (3.30).'),
 'trickster-spark': ('UIWNhYm03yg', 'Vídeo de referência: Spark Trickster contra Ubers (liga 3.26). Mostra a skill e o estilo; não é a nossa build exata.'),
 'trickster-ed': ('W9i9i4NZkNA', 'Vídeo de referência: Zizaran com Trickster de Essence Drain e Contagion (liga 3.26). Não é a nossa build exata.'),
 'warden-tinturas': ('9y0FlFp7OvU', 'Vídeo de referência: Lightning Strike Warden (liga 3.25). A ascensão da Warden mudou depois disso.'),
 'trickster-fireball': (None, 'A Fireball of Radiation é gema nova da 3.30 e ainda não tem vídeo de gameplay. Assim que a liga abrir, aparece aqui.'),
 'lvl-cobra': ('n0QfdZIqGLE', 'Vídeo do xRoGeSx: leveling de Shadow na 3.30 com Cobra Lash e Poisonous Concoction.'),
 'lvl-magma': ('LXwLgREzSOI', 'Vídeo do FearlessDumb0 (3.23): league start de Trickster, com o leveling de Rolling Magma e Armageddon Brand.'),
 'hierophant-ballista': (None, 'Ainda não achei vídeo de Artillery Ballista na 3.30. Para ver o estilo de totem de arco, veja a página do Explosive Arrow Ballista Hierophant do POEGuy.'),
}
def showcase(slug, name):
    import html
    vid, cap = VIDEOS.get(slug, (None, None))
    if cap is None: return ''
    if not vid:
        return f'<section id="showcase"><h2>Showcase</h2><div class="novideo">{html.escape(cap)}</div></section>'
    return (f'<section id="showcase"><h2>Showcase</h2><figure class="showcase"><div class="frame">'
            f'<button type="button" class="yt" data-id="{vid}" aria-label="Assistir: {html.escape(name)}">'
            f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="Miniatura do vídeo de {html.escape(name)}" loading="lazy"><span></span></button></div>'
            f'<figcaption>{html.escape(cap)} <a href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener">Abrir no YouTube</a></figcaption></figure></section>')
