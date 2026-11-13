"""Builds data/gem_info.json from exile-leveling (MIT, github.com/HeartofPhos/exile-leveling):
gem -> required level, colour and where each class gets it (quest reward or vendor, act, NPC, quest).
Usage: python3 -I tools/build_gem_data.py <path to exile-leveling/common/data/json>"""
import json, os, sys
SRC = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
q = json.load(open(os.path.join(SRC, 'quests.json')))
g = json.load(open(os.path.join(SRC, 'gems.json')))
COL = {'strength': 'r', 'dexterity': 'g', 'intelligence': 'b', 'none': 'w'}
CLASSES = ['Marauder', 'Ranger', 'Witch', 'Duelist', 'Templar', 'Shadow', 'Scion']
out = {}
def nm(gid):
    n = g[gid]['name']
    return n[:-len(' Support')] if g[gid]['is_support'] and n.endswith(' Support') else n
for gid, v in g.items():
    out[nm(gid)] = {'l': v['required_level'], 'c': COL.get(v['primary_attribute'], 'w'), 's': []}
for qid, quest in q.items():
    for oid, off in (quest.get('reward_offers') or {}).items():
        qq = q.get(oid, quest)
        act = int(qq['act'])
        for kind, items in (('q', off.get('quest') or {}), ('v', off.get('vendor') or {})):
            for gid, info in items.items():
                if gid not in g:
                    continue
                cls = ''.join(str(CLASSES.index(c)) for c in info.get('classes', []) if c in CLASSES)
                npc = info.get('npc') or off.get('quest_npc') or ''
                out[nm(gid)]['s'].append([act, npc, qq['name'], kind, cls])
for v in out.values():
    v['s'].sort(key=lambda s: (s[0], s[3] != 'q'))
json.dump(out, open(os.path.join(ROOT, 'data', 'gem_info.json'), 'w'), ensure_ascii=False, separators=(',', ':'), sort_keys=True)
print(len(out), 'gems')
