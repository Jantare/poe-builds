import json, collections, math, base64, struct, re
CLASS_IDX={'Scion':0,'Marauder':1,'Ranger':2,'Witch':3,'Duelist':4,'Templar':5,'Shadow':6}
class Tree:
    def __init__(s, path):
        D=json.load(open(path)); s.D=D
        s.N={str(k):v for k,v in D['nodes'].items()}
        for v in s.N.values():
            for f in ('out','in'):
                if f in v: v[f]=[str(x) for x in v[f]]
        s.G={str(k):v for k,v in D['groups'].items()}
    def start(s, cls):
        idx=CLASS_IDX[cls]
        return [k for k,v in s.N.items() if v.get('classStartIndex')==idx][0]
    def graph(s, start):
        N=s.N
        def ok(k):
            v=N.get(k)
            if not v or k=='root': return False
            if v.get('ascendancyName') or v.get('isMastery') or v.get('isProxy'): return False
            if v.get('classStartIndex') is not None and k!=start: return False
            return True
        adj=collections.defaultdict(set)
        for k,v in N.items():
            if not ok(k): continue
            for o in v.get('out',[])+v.get('in',[]):
                if ok(o): adj[k].add(o); adj[o].add(k)
        return adj
    def near(s, cls, pattern, limit=60, alloc=None):
        st=s.start(cls); adj=s.graph(st)
        src=list(alloc) if alloc else [st]
        dist={a:0 for a in src}; q=collections.deque(src)
        while q:
            u=q.popleft()
            for w in adj[u]:
                if w not in dist: dist[w]=dist[u]+1; q.append(w)
        pat=re.compile(pattern,re.I); rows=[]
        for k,v in s.N.items():
            if k in dist and dist[k]>0 and (v.get('isNotable') or v.get('isKeystone') or v.get('isJewelSocket')):
                txt=' / '.join(v.get('stats',[])).replace('\n',' ')
                if pat.search(txt) or pat.search(v.get('name','')): rows.append((dist[k],k,v.get('name'),txt[:120]))
        return sorted(rows)[:limit]

A16=[0,30,45,60,90,120,135,150,180,210,225,240,270,300,315,330]
A40=[0,10,20,30,40,45,50,60,70,80,90,100,110,120,130,135,140,150,160,170,180,190,200,210,220,225,230,240,250,260,270,280,290,300,310,315,320,330,340,350]

def plan(T, cls, phases, masteries, asc, ascnotables):
    """phases: list of lists of notable/keystone names. masteries: list of (mastery name, effect regex).
    Returns dict with alloc (node->phase), mastery picks, asc nodes, url, counts."""
    st=T.start(cls); adj=T.graph(st); N=T.N
    byname={}
    for k,v in N.items():
        if k in adj and (v.get('isNotable') or v.get('isKeystone') or v.get('isJewelSocket')):
            byname.setdefault(v.get('name'),k)
    alloc={st:0}; order=[]
    for ph,targets in enumerate(phases,1):
        for t in targets:
            tid=byname[t]
            prev={a:None for a in alloc}; q=collections.deque(alloc)
            while q:
                u=q.popleft()
                if u==tid: break
                for w in adj[u]:
                    if w not in prev: prev[w]=u; q.append(w)
            path=[]; u=tid
            while prev[u] is not None: path.append(u); u=prev[u]
            for p in reversed(path): alloc[p]=ph
            order.append((ph,t,len(path)))
    # masteries: pick a mastery node of that name in a group with an allocated notable
    mpick={}
    for mname,rx in masteries:
        for g,grp in T.G.items():
            ids=[str(x) for x in grp.get('nodes',[])]
            ms=[i for i in ids if N.get(i,{}).get('isMastery') and N[i].get('name')==mname and i not in mpick]
            if not ms: continue
            if not any(i in alloc and (N[i].get('isNotable')) for i in ids): continue
            m=ms[0]; eff=[e for e in N[m].get('masteryEffects',[]) if re.search(rx,' '.join(e['stats']),re.I)]
            if not eff: continue
            ph=min(alloc[i] for i in ids if i in alloc and N[i].get('isNotable'))
            mpick[m]=(eff[0]['effect'],' / '.join(eff[0]['stats']),ph,mname); break
    # ascendancy
    an={k:v for k,v in N.items() if v.get('ascendancyName')==asc}
    astart=[k for k,v in an.items() if v.get('isAscendancyStart')][0]
    aadj=collections.defaultdict(set)
    for k,v in an.items():
        for o in v.get('out',[])+v.get('in',[]):
            if o in an: aadj[k].add(o); aadj[o].add(k)
    asel=[]; aorder=[]
    for nm in ascnotables:
        tid=[k for k,v in an.items() if v.get('name')==nm and v.get('isNotable')][0]
        prev={astart:None}; q=collections.deque([astart])
        while q:
            u=q.popleft()
            for w in aadj[u]:
                if w not in prev: prev[w]=u; q.append(w)
        p=[]; u=tid
        while u!=astart: p.append(u); u=prev[u]
        new=[x for x in reversed(p) if x not in asel]; asel+=new
        aorder.append((nm,len(new),' / '.join(an[tid].get('stats',[])).replace('\n',' ')))
    cls_idx=CLASS_IDX[cls]
    asc_idx=[a['name'] for a in T.D['classes'][cls_idx]['ascendancies']].index(asc)+1
    nodes=[int(k) for k in alloc if k!=st]+[int(m) for m in mpick]+[int(a) for a in asel]
    b=struct.pack('>IBBB',6,cls_idx,asc_idx,len(nodes))+b''.join(struct.pack('>H',n) for n in nodes)+struct.pack('>B',0)
    b+=struct.pack('>B',len(mpick))+b''.join(struct.pack('>HH',e[0],int(m)) for m,e in mpick.items())
    url='https://www.pathofexile.com/passive-skill-tree/'+base64.b64encode(b).decode().replace('+','-').replace('/','_')
    counts=collections.Counter(v for k,v in alloc.items() if k!=st)
    for m,e in mpick.items(): counts[e[2]]+=1
    return {'start':st,'alloc':alloc,'order':order,'mpick':mpick,'asel':asel,'aorder':aorder,'url':url,
            'counts':dict(sorted(counts.items())),'total':sum(counts.values()),'asc_points':len(asel)}

def svg(T, P):
    N,G=T.N,T.G; R=T.D['constants']['orbitRadii']; S=T.D['constants']['skillsPerOrbit']
    alloc=dict(P['alloc']); st=P['start']; MAST=P['mpick']
    def pos(k):
        v=N[k]; g=G[str(v['group'])]; o=v.get('orbit',0); i=v.get('orbitIndex',0); n=S[o]
        a=A16[i] if n==16 else A40[i] if n==40 else 360*i/n
        a=math.radians(a); return g['x']+R[o]*math.sin(a), g['y']-R[o]*math.cos(a)
    XY={k:pos(k) for k,v in N.items() if k!='root' and 'group' in v and not v.get('ascendancyName') and not v.get('isProxy')}
    sel=list(alloc)+list(MAST)
    xs=[XY[k][0] for k in sel]; ys=[XY[k][1] for k in sel]; M=650
    x0,x1,y0,y1=min(xs)-M,max(xs)+M,min(ys)-M,max(ys)+M
    inb=lambda k: k in XY and x0<=XY[k][0]<=x1 and y0<=XY[k][1]<=y1
    out=[f'<svg viewBox="{x0:.0f} {y0:.0f} {x1-x0:.0f} {y1-y0:.0f}" xmlns="http://www.w3.org/2000/svg">']
    seen=set(); bg=[]; fg={1:[],2:[],3:[]}
    for k,v in N.items():
        if not inb(k) or v.get('isMastery'): continue
        if v.get('classStartIndex') is not None and k!=st: continue
        for o in v.get('out',[]):
            if not inb(o) or N[o].get('isMastery'): continue
            if N[o].get('classStartIndex') is not None and o!=st: continue
            e=tuple(sorted((k,o)))
            if e in seen: continue
            seen.add(e); (ax,ay),(bx,by)=XY[k],XY[o]; seg=f'M{ax:.0f} {ay:.0f}L{bx:.0f} {by:.0f}'
            if k in alloc and o in alloc: fg[max(alloc[k],alloc[o],1)].append(seg)
            else: bg.append(seg)
    out.append(f'<path class="e0" d="{"".join(bg)}"/>')
    for ph in (1,2,3): out.append(f'<path class="e{ph}" d="{"".join(fg[ph])}"/>')
    dots=[]; ad={1:[],2:[],3:[]}; labels=[]
    for k in XY:
        if not inb(k): continue
        v=N[k]
        if v.get('classStartIndex') is not None: continue
        x,y=XY[k]; big=v.get('isNotable') or v.get('isKeystone') or v.get('isJewelSocket')
        r=46 if v.get('isKeystone') else 34 if big else 18
        if v.get('isMastery'):
            if k in MAST: out.append(f'<circle class="m" cx="{x:.0f}" cy="{y:.0f}" r="40"/>')
            continue
        if k in alloc and k!=st:
            ad[alloc[k]].append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}"/>')
            if big: labels.append((x,y,v.get('name','')))
        else: dots.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r*0.8:.0f}"/>')
    out.append(f'<g class="n0">{"".join(dots)}</g>')
    for ph in (1,2,3): out.append(f'<g class="n{ph}">{"".join(ad[ph])}</g>')
    sx,sy=XY[st]
    out.append(f'<circle class="st" cx="{sx:.0f}" cy="{sy:.0f}" r="70"/><text class="lb" x="{sx:.0f}" y="{sy+170:.0f}" text-anchor="middle">INÍCIO</text>')
    for x,y,nm in labels:
        nm=nm.replace('&','&amp;')
        out.append(f'<text class="lb" x="{x:.0f}" y="{y-58:.0f}" text-anchor="middle">{nm}</text>')
    out.append('</svg>')
    return ''.join(out)
