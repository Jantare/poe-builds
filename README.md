# PoE Builds

Site estático com builds de Path of Exile 1 (liga 3.30 Covens of Umbra) e um simulador de craft.

- `index.html`: página inicial com as builds e as ferramentas.
- `builds/`: uma página por build (ascensão, árvore real, gemas, equipamento, craft, leveling).
- `craft/`: simulador de craft (Chaos, Alteration, Essência e afixos travados) com os pesos reais dos mods.
- `data/craft/`: bases, mods e essências gerados a partir dos dados do Path of Building Community.
- `tools/`: scripts que geram os dados e as páginas.

## Publicar no GitHub Pages

Settings → Pages → Build and deployment → Source: **Deploy from a branch**, Branch: **main**, pasta **/ (root)**.
O site fica em `https://jantare.github.io/poe-builds/`.

## Atualizar os dados

Os dados vêm do repositório [PathOfBuildingCommunity/PathOfBuilding](https://github.com/PathOfBuildingCommunity/PathOfBuilding), branch `dev`:

1. Baixe para uma pasta `pob/`: `src/Data/ModExplicit.lua`, `src/Data/ModJewel.lua`, `src/Data/Essence.lua` e os arquivos de `src/Data/Bases/` (amulet, axe, belt, body, boots, bow, claw, dagger, gloves, helmet, jewel, mace, quiver, ring, shield, staff, sword, wand).
2. `python3 tools/build_craft_data.py pob data/craft`
3. Baixe `src/TreeData/<versão>/tree.lua` e converta para JSON:
   `python3 -c "import sys,json; sys.path.insert(0,'tools'); import lualoader; json.dump(lualoader.load('tree.lua'), open('tree.json','w'))"`
4. `python3 tools/gen_site.py tree.json tools/spark-source.html`

O conteúdo das builds fica em `tools/content.py` (texto) e `tools/build_specs.py` (notables da árvore por fase, masteries e ordem da ascensão).

Não é afiliado à Grinding Gear Games. Path of Exile é marca da Grinding Gear Games.
