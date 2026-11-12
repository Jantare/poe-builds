"""Atlas 3.30 planner: greedy shortest-path tree from the Atlas start to chosen notables.
Data: GGG atlastree-export (data/atlas/atlas-330.json)."""
import json, collections, base64, struct, os, re
from treelib import svg as _svg

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, '..', 'data', 'atlas', 'atlas-330.json')


class Atlas:
    def __init__(s, path=PATH):
        D = json.load(open(path)); s.D = D
        s.N = {str(k): v for k, v in D['nodes'].items()}
        for v in s.N.values():
            for f in ('out', 'in'):
                if f in v: v[f] = [str(x) for x in v[f]]
        s.G = {str(k): v for k, v in D['groups'].items()}
        s.start = s.N['root']['out'][0]
        s.adj = collections.defaultdict(set)
        for k, v in s.N.items():
            if k == 'root' or v.get('isMastery'): continue
            for o in v.get('out', []):
                if o == 'root' or s.N[o].get('isMastery'): continue
                s.adj[k].add(o); s.adj[o].add(k)

    def bfs(s, src, block=()):
        dist = {a: 0 for a in src}; prev = {}; q = collections.deque(src)
        while q:
            u = q.popleft()
            if u in block: continue  # can be reached but never walked through
            for w in sorted(s.adj[u]):
                if w not in dist: dist[w] = dist[u] + 1; prev[w] = u; q.append(w)
        return dist, prev

    def find(s, name):
        ids = [k for k, v in s.N.items() if v.get('name') == name and (v.get('isNotable') or v.get('isKeystone'))]
        if not ids: raise KeyError(name)
        if len(ids) == 1: return ids[0]
        d, _ = s.bfs([s.start]); return min(ids, key=lambda k: d.get(k, 999))

    def stats(s, k):
        v = s.N[k]; t = ' / '.join(v.get('stats', [])).replace('\n', ' ')
        return re.sub(r'\[[^|\]]*\|([^\]]*)\]', r'\1', t)

    def plan(s, phases):
        """phases: list of lists of node ids/names. Returns alloc {node: phase}, order, points per phase."""
        alloc = {s.start: 0}; per = []
        want = {t if t in s.N else s.find(t) for ph in phases for t in ph}
        # keystones we did not ask for are never used as stepping stones
        block = {k for k, v in s.N.items() if v.get('isKeystone') and k not in want}
        for ph, targets in enumerate(phases, 1):
            todo = [t if t in s.N else s.find(t) for t in targets]; used = 0
            while todo:
                dist, prev = s.bfs(list(alloc), block)
                t = min(todo, key=lambda k: dist.get(k, 999)); todo.remove(t)
                path = []; u = t
                while u not in alloc: path.append(u); u = prev[u]
                for p in path: alloc[p] = ph
                used += len(path)
        # count per phase
            per.append(sum(1 for k, p in alloc.items() if p == ph))
        return alloc, per

    def url(s, alloc):
        nodes = [int(k) for k in alloc if k != s.start]
        b = struct.pack('>IBBB', 6, 0, 0, len(nodes)) + b''.join(struct.pack('>H', n) for n in nodes) + struct.pack('>BB', 0, 0)
        return 'https://www.pathofexile.com/atlas-skill-tree/' + base64.urlsafe_b64encode(b).decode()

    def svg(s, alloc):
        class T: pass
        t = T(); t.N = s.N; t.G = s.G; t.D = s.D
        P = {'alloc': {k: min(max(p, 1), 3) for k, p in alloc.items()}, 'start': s.start, 'mpick': {}}
        return _svg(t, P)

# Portuguese summary of each notable used in the plans (from the official 3.30 stats)
PT = {
 'Shaping the Mountains': '+10% monstros raros nos mapas e 15% de chance de mapas T1–15 caírem 1 tier acima.',
 'Shaping the World': 'Boss final com 5% de chance de soltar mapa 1 tier acima; 10% de chance de mapas subirem de tier.',
 'Amplified Artefacts': 'Raros soltam Threads com +50% de chance por mod que tiverem.',
 'Chittering Champions': 'Boss final com 25% de chance de soltar uma Thread extra.',
 'Subtle Manipulations': '20% de chance do Map Device não gastar as Threads.',
 'Significant Troves': 'Uniques com +200% de chance de soltar Threads.',
 'Anomie': 'Raros ganham 1 mod a mais (mais perigosos, mais loot e mais Threads com Amplified Artefacts).',
 'Sinistral Threads': 'Escolha <b>Legion</b>: +200% de chance das Threads que caem serem de Legion.',
 'Dextral Threads': 'Escolha a Thread da sua mecânica (Ritual, Ultimatum, Expedition ou Breach): +200% de chance de cair desse tipo.',
 'Prolonged Struggle': 'Legion dura 60% mais e os monstros congelados levam 60% mais dano.',
 'Leader of Men': 'Encontros com general têm os dois generais e +50% de splinters deles.',
 'Extra Provisions': 'Cada Legion tem um War Hoard a mais e os baús dão uma recompensa extra.',
 'Chain of Command': '+4 sargentos por encontro (mais recompensas).',
 'Battle-Tested': 'Monstros com recompensa têm chance de ganhar mais 1 ou 2 recompensas.',
 'Blood Feud': 'Escolha um exército: +100% de chance de aparecer e +30% de Enshrouding Crystal dos generais. Karui ou Vaal são boas escolhas gerais.',
 'Spoils of War': 'Baús quebrados passam as recompensas para os monstros que soltam (mais difíceis).',
 'Occult Devotion': 'Mapa com Ritual sempre tem 4 altares.',
 'Blood Pact': 'Os altares oferecem 30% mais recompensas.',
 'Flexible Dogma': '+2 rerolls de recompensa, e 1 reroll grátis.',
 'Exacting Tribute': 'Monstros revividos perdem menos Tribute e uniques no altar dão o dobro.',
 'Burial Rites': '+50% de recompensas especiais e um Rare Itemised Corpse a mais.',
 'Sacrificial Due': '25% de chance do último altar soltar um Blood-filled Vessel.',
 'Outside Entities': 'Escolha a mecânica terciária: Viridian Wildwood (Ritual), Demonic Evocator (Beyond), Delirium, Mirage ou Buried Sentinel.',
 'Stand Your Ground': 'Recompensas como se você fizesse 1 rodada a mais (o círculo encolhe 3% por rodada).',
 'Prove Yourself Worthy': 'Mods começam 1 tier acima e 25% de chance de duplicar a recompensa.',
 'Brave The Tower': 'Mais chance de boss na última rodada; o boss solta 10 catalisadores.',
 "Trialmaster's Boon": 'Escolha o tipo de recompensa: Currency, Uniques ou Divination Cards (+80%). Currency é a mais segura.',
 'Controlled Chaos': 'Escolha o objetivo das rodadas. "Só sobreviver" (30% mais curto) ou "matar ondas" (30% menos inimigos) são os mais rápidos.',
 'Bound for Utzaal': '25% de chance de catalisador virar Inscribed Ultimatum.',
 'Trial by Fire': '+10% de experiência e +4% de rarity por rodada.',
 'What Lies Beneath ': '+60% Logbooks dos Runic Monsters.',
 'Nothing Ventured, Nothing Gained': 'Logbooks com 4 implícitos e monstros mais ricos a cada remanescente detonado.',
 'Kalguuran Companionship': 'Escolha o líder: Rog, Gwennen ou Tujen (+150%) ou Dannig (+75%). Tujen é o padrão para currency.',
 'Distinguished Demolitionist': '+50% de explosivos: alcança mais remanescentes e baús.',
 'Extreme Archaeology': 'Keystone: 1 explosivo só, mas com +200% de raio e +100% de alcance.',
 'Call of the Grove': '+40% de chance de Sacred Flora (Harvest) nos mapas.',
 'Doubling Season': 'Lifeforce com 15% de chance de duplicar.',
 'Heart of the Grove': 'A Flora nunca é normal e a Fauna tem +50% de chance de ser boss.',
 'Verdant Lands': 'A Fauna dá Crops extras iguais à Lifeforce solta (mas com 50% mais vida).',
 'Arboriculture': '+100% de chance para um tipo de Sacred Flora.',
 'Rich Soil': 'Mods da Sacred Flora com +50% de efeito.',
 'Blended Realities': 'Escolha: Sacred Flora, Tormented Spirit, Imprisoned Monster ou Shrine.',
 'Torn Veil': '+50% de chance de Demonic Evocator (Beyond).',
 'Scent of Blood': '+60% de chance de Demonic Evocator (Beyond).',
 'Height of Horror': 'Uniques ganham 1 mod e dão +50% de experiência.',
 'True Terrors': 'Uniques ganham 2 mods (mais loot, mais perigo).',
 'Baptised by Fire': '10% de chance de progresso em dobro para o Searing Exarch.',
 'Etched by Acid': '10% de chance de progresso em dobro para o Eater of Worlds.',
 'The Light of Dawn': '50% de chance de altar do Exarch quando a influência dele aparece.',
 'The Shadow of Hunger': '+20% de chance de altares do Eater of Worlds.',
 'Wrath of the Cosmos': 'Keystone: altares do Exarch com 50% de chance de 1 vantagem extra (mas desvantagens 100% mais fortes).',
 'Eldritch Gaze': 'Keystone: altares do Eater com +50% no efeito das vantagens e 1 desvantagem extra.',
 'Unwavering Vision': 'Keystone: só 1 tipo de Thread por mapa, +2 Threads acima do limite de 8, mas 75% das Threads que caem viram gold.',
 'Fate Bespoken': 'Cartas que caem no mapa vão para o boss final, que pode duplicá-las.',
 'Crystal Resonance': 'O boss final ganha mods das essências e pode soltar Calcified Map no T16.',
}
BASE = ['Shaping the Mountains', 'Shaping the World', 'Amplified Artefacts', 'Chittering Champions']
STRATS = {
 'legion': [['Sinistral Threads', 'Prolonged Struggle', 'Leader of Men', 'Extra Provisions', 'Chain of Command', 'Battle-Tested'], ['Blood Feud', 'Spoils of War']],
 'beyond': [['Torn Veil', 'Scent of Blood', 'Outside Entities'], ['Height of Horror', 'True Terrors', 'Significant Troves']],
 'ritual': [['Dextral Threads', 'Occult Devotion', 'Blood Pact', 'Flexible Dogma', 'Exacting Tribute', 'Burial Rites'], ['Sacrificial Due', 'Outside Entities']],
 'ultimatum': [['Dextral Threads', 'Stand Your Ground', 'Prove Yourself Worthy', "Trialmaster's Boon", 'Controlled Chaos'], ['Brave The Tower', 'Bound for Utzaal', 'Trial by Fire']],
 'expedition': [['Dextral Threads', 'What Lies Beneath ', 'Nothing Ventured, Nothing Gained', 'Kalguuran Companionship', 'Distinguished Demolitionist'], ['Extreme Archaeology']],
 'harvest': [['Call of the Grove', 'Doubling Season', 'Heart of the Grove', 'Arboriculture'], ['Verdant Lands', 'Rich Soil', 'Blended Realities']],
 'pinnacles': [['Baptised by Fire', 'Etched by Acid', 'The Light of Dawn', 'The Shadow of Hunger'], ['Wrath of the Cosmos', 'Eldritch Gaze']],
 'fates': [['Shaping the World', 'Chittering Champions', 'Fate Bespoken'], ['Crystal Resonance']],
}
