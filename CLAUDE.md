# CLAUDE.md — contexto do projeto (leia antes de começar)

Este arquivo é lido automaticamente em toda sessão nova. Ele existe para ninguém precisar reler a conversa inteira.
**Quando terminar algo importante, atualize as seções "Estado atual" e "Pendências" deste arquivo e faça commit junto.**

## Quem é o usuário e como responder
- Joga **Path of Exile 1** (liga **3.30 Covens of Umbra**) e **Path of Exile 2** (prepara a **1.0, lançamento 11/12/2026**).
- **Responder sempre em português (Brasil)**, direto e prático. Fala informal; mensagens por voz chegam com erros de transcrição ("POI" = PoE, "Never5" = NeverSink, "ciborgue" = sirgog, "Covis" = Covens).
- Gosta de **farmar muitas Divines por hora**; mapeia rápido e **paga carry de Ubers no TFT** (The Forbidden Trove). Não precisa de build de boss.
- Conta PoE 1: `Hygopenido#4999`. **Nunca pedir, guardar ou mostrar o POESESSID.**
- Prefere coisas prontas para copiar (links de trade, regex completos, PoB) e páginas visuais no site.

## O repositório e o site
- Repo **`Jantare/poe-builds`** → site **https://jantare.github.io/poe-builds/** (GitHub Pages, branch `main`, raiz).
- Commits direto na `main`, mensagem em português. Testar antes de publicar (ver "Como testar").
- Páginas:
  - `index.html` (gerado): Mais seguras, Do YouTube (3.30), Apostas, ferramentas (Baú, Preço, Mercado), Farm.
  - `builds/*.html` (gerados): seguras = RF Chieftain, Earthshatter Berserker, Poison SRS Necro, Storm Burst Hierophant, Toxic Rain PF; YouTube = **Blight of Contagion Trickster** (Ky), EA Ballista Hierophant, Absolution Necro, Cyclone Necro, Animate Weapon Necro; apostas = Trickster ED, Trickster Fireball, Warden tinturas, Hierophant Ballista. **Spark (Trickster e Saboteur) foi removida** — não rendeu na liga.
  - Cada build: seção "Atualização 3.30" (`tools/updates_330.py`: dicts `U`, `NINJA` = popularidade no poe.ninja, `WARN` = avisos), árvore, **gemas estilo pobb.in** (`tools/pobview.py` + `assets/pobview.js`: seletor por ato, cor da gema, onde conseguir por classe — dados `data/gem_info.json` do exile-leveling, MIT), equipamento com **"Comprar pronto"** (`tools/trade.py` + `assets/trade.js`, liga padrão `Covens`).
  - `farm/`: página principal + uma por mecânica (`tools/gen_farm.py`, `tools/farm_content.py`). **Árvore do Atlas 3.30 oficial** desenhada com a arte da GGG (`tools/atlas_plan.py`, `tools/atlas_render.py`, `data/atlas/`). Seção **Combinações de farm** (6 combos: nosso Shrines → Legion → Ritual + Harvest leve; Shrines → Legion; sirgog 60 pontos; Legion + Beyond; Ritual + Harvest; POEGuy Blight + Ultimatum + Minério) e análise "Ainda vale a pena?" de 15/11.
  - `mercado/`: preços ao vivo do poe.ninja (mais caros, por farm, por categoria, **Gemas**). Dados em `https://raw.githubusercontent.com/Jantare/poe-builds/mercado-data/mercado.json`, gerados a cada 30 min pelo workflow `.github/workflows/mercado.yml` (`tools/fetch_prices.py`, ramo `mercado-data` com 1 commit só).
  - `bau/`: **Meu Baú** — `bau.py` vira `bau.exe` pelo workflow `bau-exe.yml` (release `bau-latest`, com autoteste no Windows). Valor do baú por aba + **verificador de preço** (Ctrl+C no item → preço do poe.ninja; `bau/precheck.py`). Ligas vêm da API oficial + poe.ninja; `CURRENT_LEAGUES` e `APP_VERSION` em `bau.py`.
  - `preco/`: guia do verificador do Baú + Awakened PoE Trade.
  - `craft/`: simulador de craft (Monte Carlo com pesos do PoB).
  - `poe2/`: **plano para o PoE 2 1.0** (ver abaixo).

## Como gerar e testar (cuidados)
- Builds: `python3 -I tools/gen_site.py <tree.json 3.29 do PoB> tools/spark-source.html`.
  **O gerador de árvore das Apostas não é determinístico.** Depois de gerar, restaurar do HEAD a `<section id="arvore">` das páginas trickster-ed, trickster-fireball, warden-tinturas e hierophant-ballista e os `data/pob/*.txt` delas (`git checkout HEAD -- …`), para não trocar árvores que o pessoal já copiou.
- Farm: `python3 -I tools/gen_farm.py` (determinístico).
- Testar com `python3 -m http.server` + Playwright (celular 390px e desktop 1280px): sem overflow horizontal, sem erro no console, links funcionando.
- PoB: códigos são base64url(zlib(XML)); raw do pobb.in em `https://pobb.in/<id>/raw`.

## Fontes de dados que funcionam
- **poe.ninja**: economia (`poe1/api/economy/exchange/current/overview?league=Covens&type=…`, `…/stash/current/item/overview…`) e **builds** em protobuf (`poe1/api/builds/<versão>/search?overview=covens&type=exp[&skills=Nome]`; versão em `poe1/api/data/index-state`; dicionários `poe1/api/builds/dictionary/<hash>` no formato "NDIC": tamanhos 1 byte + nomes). Dá para ver skills, classes e **nós do Atlas mais usados**.
- GGG: `pathofexile.com/api/leagues?type=main`, atlas/skill tree exports no GitHub (`grindinggear/*-export`).
- YouTube: busca funciona; **oEmbed** dá título/canal. Página do vídeo e descrições costumam ser bloqueadas na nuvem ("não sou robô").
- **Bloqueados na nuvem**: Mobalytics e trade oficial (Cloudflare), poebuilds.cc (fora da rede). Não contornar — pedir ao usuário o link do pobb.in/descrição, ou rodar a sessão no PC dele (Claude Desktop / `claude remote-control`).

## Estado atual (PoE 1 · Covens)
- Personagem: Spark não rendeu; Blight Trickster ele **não gostou** (página fica no site). Estava morrendo em T1. Recomendado: **RF Chieftain** (Pohx https://www.youtube.com/watch?v=QHdav1bFVls) ou **Static Strike Guardian** (Aleshxile https://www.youtube.com/watch?v=1lNHXQ8vxps). Ainda não decidiu.
- Farm: Legion com **Blood Feud = Maraketh** (Emblem ~1 div, Crystal ~45c). Ritual vale pelas **Omens of Fortune / Connections**. Threads baratas (usar, não vender). Maioria dos jogadores pega Shrines; Legion e Ritual com pouca concorrência.
- **Filtros** (fora do repo, no PC dele): `3.30_LeagueStart_Jantare`, `3.30_Fase2_Amarelos_Jantare`, `3.30_Fase3_Vermelhos_Jantare` — NeverSink 8.21.0a (3-Strict Cobalt) + personalizações do filtro antigo "3.29_marcaosoaresoficial". Para atualizar: aplicar as diferenças (liga/desliga, Show/Hide, estilo) entre o NeverSink 8.20.0b original e o filtro antigo sobre o NeverSink novo.

## PoE 2 (rumo à 1.0, 11/12/2026) — página `poe2/`
- Notas da 1.0 saem ~4/12: tudo marcado "conferir" depende delas.
- **Plano A: Spark Stormweaver** (Sorceress) — Spark desde a primeira área; endgame crítico + **Cast on Critical com Comet**, depois CI. Referência: guia da animeprincess (0.5.5). Ascendência: Constant Gale → Strike Twice → Shaper of Storms → Storm's Recollection. Risco: crítico sai da árvore na 1.0 (vem do equipamento).
- **Plano B: Shadow Assassin Spark** (classe nova Dex/Int) — aposta, depende das adagas e de o Spark não ser nerfado.
- **Farm planejada: Ritual + Breach** (escalam com densidade) atrás de **Headhunter e Mageblood**; Omens e uniques novos do Ritual, catalisadores e Genesis Tree da Breach. Atlas da 1.0 com ~75 pontos.

## Pendências
- PoE 1: escolher a build nova e, se for Static Strike/Tendrils, montar a página a partir do pobb.in do guia; atualizar `NINJA` em `tools/updates_330.py` de tempos em tempos; refazer os filtros quando o NeverSink atualizar os tiers.
- PoE 2: quando saírem as notas da 1.0, revisar tudo que está "conferir" na página `poe2/` e o plano Spark.
- Path of Building ainda sem a árvore 3.30 (última 2.67.2): quando sair, gerar o site com a árvore nova.
