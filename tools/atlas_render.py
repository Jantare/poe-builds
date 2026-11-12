"""Renders an Atlas plan as an image using GGG's official tree art (grindinggear/atlastree-export assets).
Allocated path is lit like in game; chosen notables get numbered badges and name labels."""
import math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, '..', 'data', 'atlas', 'assets')
ZOOM = '0.2972'
S = float(ZOOM)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
A16 = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330]
A40 = [0, 10, 20, 30, 40, 45, 50, 60, 70, 80, 90, 100, 110, 120, 130, 135, 140, 150, 160, 170, 180, 190, 200, 210, 220, 225, 230, 240, 250, 260, 270, 280, 290, 300, 310, 315, 320, 330, 340, 350]
LINE_OFF = (78, 70, 56, 255)
LINE_ON = (232, 198, 120, 255)
GOLD = (240, 210, 140)


class Sheets:
    def __init__(s, D):
        sp = D['sprites']; s.cache = {}; s.sp = sp
    def img(s, key):
        fn = os.path.basename(s.sp[key][ZOOM]['filename'].split('?')[0])
        if fn not in s.cache: s.cache[fn] = Image.open(os.path.join(ASSETS, fn)).convert('RGBA')
        return s.cache[fn]
    def get(s, key, name):
        c = s.sp[key][ZOOM]['coords'].get(name)
        if not c: return None
        return s.img(key).crop((c['x'], c['y'], c['x'] + c['w'], c['y'] + c['h']))


def angle(n_per, i):
    return A16[i] if n_per == 16 else A40[i] if n_per == 40 else 360 * i / n_per


def render(A, alloc, badges, out, title=None, max_w=2000, margin=700, full=False):
    """alloc: {node_id: phase}; badges: {node_id: label text (number)}."""
    D, N, G = A.D, A.N, A.G
    R = D['constants']['orbitRadii']; SPO = D['constants']['skillsPerOrbit']
    sh = Sheets(D)

    def pos(k):
        v = N[k]; g = G[str(v['group'])]; o = v.get('orbit', 0)
        a = math.radians(angle(SPO[o], v.get('orbitIndex', 0)))
        return g['x'] + R[o] * math.sin(a), g['y'] - R[o] * math.cos(a)
    XY = {k: pos(k) for k, v in N.items() if k != 'root'}
    if full:
        x0, x1, y0, y1 = D['min_x'] - 400, D['max_x'] + 400, D['min_y'] - 400, D['max_y'] + 400
    else:
        pts = [XY[k] for k in alloc]
        x0 = min(p[0] for p in pts) - margin; x1 = max(p[0] for p in pts) + margin
        y0 = min(p[1] for p in pts) - margin; y1 = max(p[1] for p in pts) + margin
    W, H = int((x1 - x0) * S), int((y1 - y0) * S)
    P = lambda x, y: ((x - x0) * S, (y - y0) * S)

    # 1. background tile + atlas art centred on the start node
    im = Image.new('RGBA', (W, H), (8, 10, 14, 255))
    tile = sh.get('background', 'Background2')
    if tile:
        for ty in range(0, H, tile.height):
            for tx in range(0, W, tile.width): im.alpha_composite(tile, (tx, ty))
    art = sh.get('atlasBackground', 'AtlasPassiveBackground')
    sx, sy = P(*XY[A.start])
    im.alpha_composite(art, (int(sx - art.width / 2), int(sy - art.height / 2)))
    # 2. group backgrounds
    for gk, g in G.items():
        b = g.get('background')
        if not b: continue
        spr = sh.get('groupBackground', b['image'])
        if not spr: continue
        gx, gy = P(g['x'] + b.get('offsetX', 0), g['y'] + b.get('offsetY', 0))
        if -spr.width < gx < W + spr.width and -spr.height < gy < H + spr.height:
            im.alpha_composite(spr, (int(gx - spr.width / 2), int(gy - spr.height / 2)))
    # 3. connections
    lines = Image.new('RGBA', (W, H)); ld = ImageDraw.Draw(lines)
    glow = Image.new('RGBA', (W, H)); gd = ImageDraw.Draw(glow)
    worm = {k for k, v in N.items() if v.get('isWormhole')}
    seen = set(); wid = max(3, int(17 * S * 0.55))
    for k, v in N.items():
        if k == 'root' or v.get('isMastery'): continue
        spec = {c['to']: c for c in v.get('connections', [])}
        for o in v.get('out', []):
            if o == 'root' or N[o].get('isMastery') or (k in worm and o in worm): continue
            e = tuple(sorted((k, o)))
            if e in seen: continue
            seen.add(e)
            on = k in alloc and o in alloc
            col = LINE_ON if on else LINE_OFF
            targets = [(ld, col, wid)] + ([(gd, (255, 200, 90, 200), wid * 3)] if on else [])
            (ax, ay), (bx, by) = XY[k], XY[o]
            arc = None
            if o in spec and spec[o].get('orbit'):
                c = spec[o]; arc = (c['orbitX'], c['orbitY'], math.dist((ax, ay), (c['orbitX'], c['orbitY'])))  # radius = real distance to the given centre
            elif N[o]['group'] == v['group'] and N[o].get('orbit') == v.get('orbit') and v.get('orbit', 0) > 0:
                g = G[str(v['group'])]; arc = (g['x'], g['y'], R[v['orbit']])
            for dr, cl, w in targets:
                if arc:
                    cx, cy, r = arc
                    a1 = math.degrees(math.atan2(ay - cy, ax - cx)); a2 = math.degrees(math.atan2(by - cy, bx - cx))
                    d = (a2 - a1) % 360
                    if d > 180: a1, a2 = a2, a1
                    px, py = P(cx, cy); rr = r * S
                    dr.arc((px - rr, py - rr, px + rr, py + rr), a1, a1 + min(d, 360 - d), fill=cl, width=w)
                else:
                    dr.line([P(ax, ay), P(bx, by)], fill=cl, width=w)
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(wid * 1.5)))
    im.alpha_composite(lines)
    # 4. masteries (decoration at group centres)
    for k, v in N.items():
        if not v.get('isMastery'): continue
        spr = sh.get('mastery', v.get('icon', ''))
        if not spr: continue
        x, y = P(*XY[k]); spr = spr.copy(); spr.putalpha(spr.getchannel('A').point(lambda a: a * 0.75))
        im.alpha_composite(spr, (int(x - spr.width / 2), int(y - spr.height / 2)))
    # 5. nodes (soft glow under the allocated ones)
    halo = Image.new('RGBA', (W, H)); hd = ImageDraw.Draw(halo)
    for k in alloc:
        if k == A.start: continue
        x, y = P(*XY[k]); r = 40 if (N[k].get('isNotable') or N[k].get('isKeystone')) else 24
        hd.ellipse((x - r, y - r, x + r, y + r), fill=(255, 205, 110, 170))
    im.alpha_composite(halo.filter(ImageFilter.GaussianBlur(10)))
    for k, v in N.items():
        if k in ('root', A.start) or v.get('isMastery'): continue
        x, y = P(*XY[k])
        if x < -100 or y < -100 or x > W + 100 or y > H + 100: continue
        on = k in alloc
        kind = 'keystone' if v.get('isKeystone') else 'notable' if v.get('isNotable') else 'wormhole' if v.get('isWormhole') else 'normal'
        icon = sh.get(kind + ('Active' if on else 'Inactive'), v.get('icon', ''))
        if icon is None:
            for alt in ('notable', 'normal', 'keystone'):
                icon = sh.get(alt + ('Active' if on else 'Inactive'), v.get('icon', ''))
                if icon: break
        if icon:
            m = Image.new('L', icon.size, 0); ImageDraw.Draw(m).ellipse((1, 1, icon.width - 2, icon.height - 2), fill=255)
            icon.putalpha(Image.composite(icon.getchannel('A'), m, m))
            im.alpha_composite(icon, (int(x - icon.width / 2), int(y - icon.height / 2)))
        fname = {'keystone': 'KeystoneFrame', 'notable': 'NotableFrame', 'wormhole': 'WormholeFrame'}.get(kind)
        fname = (fname + ('Allocated' if on else 'Unallocated')) if fname else ('PSSkillFrameActive' if on else 'PSSkillFrame')
        fr = sh.get('frame', fname)
        if fr: im.alpha_composite(fr, (int(x - fr.width / 2), int(y - fr.height / 2)))
    st = sh.get('startNode', 'AtlasPassiveSkillScreenStart')
    if st: im.alpha_composite(st, (int(sx - st.width / 2), int(sy - st.height / 2)))
    # 6. scale down, then badges + labels at final resolution (stay readable)
    f = min(1.0, max_w / W)
    if f < 1: im = im.resize((int(W * f), int(H * f)), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    fs = 22 if full else 20
    fnt = ImageFont.truetype(FONT, fs); fnum = ImageFont.truetype(FONT, fs + 2)
    boxes = []
    for k, lab in sorted(badges.items(), key=lambda kv: XY[kv[0]][1]):
        x, y = P(*XY[k]); x *= f; y *= f
        name = f"{lab} · {N[k]['name']}"
        tw = d.textlength(name, font=fnt)
        ty = y + 26
        for _ in range(12):  # push the label down until it does not overlap a previous one
            bb = (x - tw / 2 - 7, ty - 3, x + tw / 2 + 7, ty + fs + 5)
            if not any(bb[0] < o[2] and o[0] < bb[2] and bb[1] < o[3] and o[1] < bb[3] for o in boxes): break
            ty += fs + 10
        boxes.append((x - tw / 2 - 7, ty - 3, x + tw / 2 + 7, ty + fs + 5))
        d.rounded_rectangle((x - tw / 2 - 7, ty - 3, x + tw / 2 + 7, ty + fs + 5), 6, fill=(10, 12, 18, 225), outline=(150, 120, 70, 255))
        d.text((x - tw / 2, ty), name, font=fnt, fill=GOLD)
        r = 17
        bx, by = x + 22, y - 22
        d.ellipse((bx - r, by - r, bx + r, by + r), fill=(92, 170, 255, 255), outline=(10, 12, 18, 255), width=3)
        d.text((bx, by + 1), str(lab), font=fnt if len(str(lab)) > 1 else fnum, fill=(6, 16, 28), anchor='mm')
    if title:
        tf = ImageFont.truetype(FONT, 26)
        d.rounded_rectangle((12, 12, 30 + d.textlength(title, font=tf), 56), 8, fill=(10, 12, 18, 230))
        d.text((21, 18), title, font=tf, fill=GOLD)
    im.convert('RGB').save(out, 'WEBP', quality=80, method=6)
    return im.size
