"""Minimal parser for the Lua table literals in Path of Building data files."""
import re
class P:
    def __init__(s, t): s.t=t; s.i=0; s.n=len(t)
    def ws(s):
        t=s.t
        while s.i<s.n:
            c=t[s.i]
            if c in ' \t\r\n,;': s.i+=1
            elif t.startswith('--',s.i):
                if t.startswith('--[[',s.i): s.i=t.index(']]',s.i)+2
                else:
                    j=t.find('\n',s.i); s.i=s.n if j<0 else j+1
            else: break
    def val(s):
        s.ws(); t=s.t; c=t[s.i]
        if c=='{': return s.table()
        if c in '"\'': return s.string()
        if t.startswith('[[',s.i):
            j=t.index(']]',s.i); v=t[s.i+2:j]; s.i=j+2; return v
        m=re.compile(r'-?(0x[0-9a-fA-F]+|\d+\.?\d*(e[-+]?\d+)?)').match(t,s.i)
        if m:
            s.i=m.end(); x=m.group(0)
            if 'x' in x: return int(x,16)
            return float(x) if ('.' in x or 'e' in x) else int(x)
        m=re.compile(r'[A-Za-z_][A-Za-z0-9_]*').match(t,s.i)
        s.i=m.end(); w=m.group(0)
        return {'true':True,'false':False,'nil':None}.get(w,w)
    def string(s):
        t=s.t; q=t[s.i]; s.i+=1; out=[]
        while True:
            c=t[s.i]
            if c=='\\':
                d=t[s.i+1]; out.append({'n':'\n','t':'\t'}.get(d,d)); s.i+=2
            elif c==q: s.i+=1; return ''.join(out)
            else: out.append(c); s.i+=1
    def table(s):
        s.i+=1; arr=[]; d={}
        while True:
            s.ws()
            if s.t[s.i]=='}': s.i+=1; break
            if s.t[s.i]=='[':
                s.i+=1; k=s.val(); s.ws(); s.i+=1  # ]
                s.ws(); s.i+=1  # =
                d[k]=s.val(); continue
            m=re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)').match(s.t,s.i)
            if m: s.i=m.end(); d[m.group(1)]=s.val(); continue
            arr.append(s.val())
        if d and arr:
            for i,v in enumerate(arr,1): d[i]=v
            return d
        return d if d else arr
def load(path):
    t=open(path,encoding='utf-8').read()
    i=t.index('return')+6
    p=P(t); p.i=i; return p.val()
def load_assign(path, prefix):
    """Parse files made of lines like  itemBases["X"] = { ... }"""
    t=open(path,encoding='utf-8').read(); out={}
    for m in re.finditer(re.escape(prefix)+r'\["((?:[^"\\]|\\.)*)"\]\s*=\s*',t):
        p=P(t); p.i=m.end(); out[m.group(1)]=p.val()
    return out
