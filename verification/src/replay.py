"""Exact positive-recursion checks and exhaustive small cut-lemma checks."""
from itertools import product
from collections import deque, defaultdict

def build(n,clauses):
    clauses=list(clauses)+[(i,-i) for i in range(1,n+1)]
    fam={}
    for i in range(1,n+1):
        fam['var',i]={'a','b',('l',i),('l',-i)}
    for j,cs in enumerate(clauses):
        fam['cl',j]={'a','b',('c',j),*(('s',j,k) for k in range(len(cs)))}
        fam['ref',j]={'a',('c',j)}
        for k,l in enumerate(cs):
            fam['eq',j,k]={('l',l),('s',j,k)}
    K=3*len(fam)
    def loc(x): return (x,K) if x in ('a','b') else x
    ch={'h':{'v',('a',0),('b',0)}}
    for j,(g,children) in enumerate(fam.items()):
        stages=range(3*j+1,3*j+4)
        ch[g]={loc(x) for x in children}|{('z',i) for i in stages}
        ch['F',j]={('y',i) for i in stages}
        for i in stages:
            ch['r',i]={('a',i-1),('b',i-1),('a',i),('b',i)}
            ch['t',i]={('a',i-1),('a',i),('b',i),('z',i),('y',i)}
    assert all(sum(v in C for C in ch.values())>=2
               for v in set.union(*ch.values())-{'v'})
    return ch,clauses,fam,K

def size(ch,U,W,S):
    G=defaultdict(dict)
    def add(a,b):
        G[a][b]=1
        G[b][a]=0
    for u in U: add('source',('left',u))
    for w in W: add(('right',w),'sink')
    for g,C in ch.items():
        if g in S: continue
        add(('in',g),('out',g))
        for u in C&U: add(('left',u),('in',g))
        for w in C&W: add(('out',g),('right',w))
    flow=0
    while True:
        queue=deque(['source'])
        trace={'source':None}
        while queue and 'sink' not in trace:
            a=queue.popleft()
            for b,cap in G[a].items():
                if cap and b not in trace:
                    trace[b]=a
                    queue.append(b)
        if 'sink' not in trace: return flow
        b='sink'
        while b!='source':
            a=trace[b]
            G[a][b]-=1
            G[b][a]+=1
            b=a
        flow+=1

def check(ch,U,W,S,v,g):
    assert U and len(U)==len(W) and not U&W and v not in U|W
    assert {h for h,C in ch.items() if v in C}-S=={g}
    assert size(ch,U,W,S)==len(U)
    assert size(ch,U|{v},W|{v},S)==len(U)

def positive(n,formula,bits):
    ch,clauses,fam,K=build(n,formula)
    path={'h':(('a',0),('b',0))}
    for i in range(1,K+1):
        path['r',i]=(('a',i),('b',i))
    truth=lambda l: bits[abs(l)-1]==(l>0)
    for i in range(1,n+1):
        left=-i if truth(i) else i
        path['var',i]=(('l',left),('l',-left))
    for j,cs in enumerate(clauses):
        k=next(k for k,l in enumerate(cs) if truth(l))
        path['cl',j]=(('c',j),('s',j,k))
    left,right=map(set,zip(*path.values()))
    for j,g in enumerate(fam):
        L=bool(ch[g]&left)
        R=bool(ch[g]&right)
        use_z_left=L or not R
        for i in range(3*j+1,3*j+4):
            a,b=('z',i),('y',i)
            path['t',i]=(a,b) if use_z_left else (b,a)
    S=set()
    def advance(v,g):
        U,W=map(set,zip(*(x for h,x in path.items() if h not in S)))
        check(ch,U,W,S,v,g)
        S.add(g)
    advance('v','h')
    for i in range(1,K+1):
        advance(('b',i-1),('r',i))
        advance(('a',i-1),('t',i))
    for j,g in enumerate(fam):
        for h,f in [(g,'z'),(('F',j),'y')]:
            check(ch,{(f,3*j+2)},{(f,3*j+3)},S,(f,3*j+1),h)
            S.add(h)
    assert S==set(ch)
    return len(S)

def exercise_lemma():
    U,W={0,1},{2,3}
    sides=lambda mask: {v for v in range(4) if mask>>v&1}
    count=0
    for masks in product(range(16),repeat=3):
        ch=dict(enumerate(map(sides,masks)))
        expected=False
        whole=size(ch,U,W,set())==2 and size(ch,U,W,{0})<2
        found=False
        for uu in [{0},{1},U]:
            for ww in [{2},{3},W]:
                if len(uu)!=len(ww): continue
                expected |= size(ch,uu,ww,set())==len(uu) and size(ch,uu,ww,{0})<len(uu)
                common={g for g,C in ch.items() if C&uu and C&ww}
                if (0 in common and len(common)==len(uu)
                    and size(ch,uu,ww,set())==len(uu)):
                    found=True
        assert found==expected and (not whole or found)
        count+=1
    return count

def can_certify_brute(ch, pivot, parent, vertices):
    available = [v for v in vertices if v != pivot]
    for coloring in product((0, 1, 2), repeat=len(available)):
        left = {v for v, color in zip(available, coloring) if color == 1}
        right = {v for v, color in zip(available, coloring) if color == 2}
        if left and len(left) == len(right):
            k = len(left)
            if size(ch, left, right, set()) == k and size(ch, left, right, {parent}) < k:
                return True
    return False


def slots_saturate(choices):
    assigned = {}

    def advance(slot, visited):
        for vertex in choices[slot]:
            if vertex in visited:
                continue
            visited.add(vertex)
            if vertex not in assigned or advance(assigned[vertex], visited):
                assigned[vertex] = slot
                return True
        return False

    return all(advance(slot, set()) for slot in range(len(choices)))


def can_certify_labels(ch, pivot, parent, vertices):
    others = [g for g in ch if g != parent]
    for labels in product((0, 1, 2), repeat=len(others)):
        common = [parent, *(g for g, label in zip(others, labels) if label == 0)]
        left_blocked = set().union(*(ch[g] for g, label in zip(others, labels) if label == 2))
        right_blocked = set().union(*(ch[g] for g, label in zip(others, labels) if label == 1))
        choices = [sorted(ch[g] - blocked - {pivot})
                   for g in common for blocked in (left_blocked, right_blocked)]
        if slots_saturate(choices):
            return True
    return False


def eligible(ch, vertices):
    for vertex in vertices:
        parents = [g for g, children in ch.items() if vertex in children]
        if len(parents) == 1:
            yield vertex, parents[0]


def recognize(ch, vertices, local, greedy):
    current = {g: children for g, children in ch.items() if children}
    if not current:
        return True
    for pivot, parent in eligible(current, vertices):
        if local(current, pivot, parent, vertices):
            reduced = {g: children for g, children in current.items() if g != parent}
            if recognize(reduced, vertices, local, greedy):
                return True
            if greedy:
                return False
    return False


def compare_deciders():
    vertices = tuple(range(4))
    child_sets = [{v for v in vertices if (mask >> v) & 1} for mask in range(16)]
    checked = 0
    for first, second in product(child_sets, repeat=2):
        ch = {0: first, 1: second}
        for pivot, parent in eligible(ch, vertices):
            assert can_certify_brute(ch, pivot, parent, vertices) == can_certify_labels(ch, pivot, parent, vertices)
        brute = recognize(ch, vertices, can_certify_brute, greedy=False)
        peeled = recognize(ch, vertices, can_certify_labels, greedy=True)
        assert brute == peeled
        checked += 1
    return checked


def worked_example():
    vertices = tuple("vabcd")
    base = {"h": set("vab"), "r": set("abcd")}
    for decoy in (False, True):
        graph = dict(base)
        if decoy:
            graph["s"] = set("cd")
        assert size(graph, set("ac"), set("bd"), set()) == 2
        assert size(graph, set("vac"), set("vbd"), set()) == 2 + decoy
        for local in (can_certify_brute, can_certify_labels):
            assert local(graph, "v", "h", vertices) == (not decoy)
            assert recognize(graph, vertices, local, greedy=True) == (not decoy)
    print("Worked graphs: 2/2 base matchings; augmented sizes 2/3 and 3/3.")


if __name__=='__main__':
    cases=[(1,[(1,)],(True,)),(2,[(1,2),(-1,2),(-2,-1)],(False,True)),
           (3,[(1,-2,3),(-1,2),(-2,)],(False,False,True))]
    print("Positive full-order flow checks:",[positive(*c) for c in cases])
    print("Exhaustive small matching-lemma networks:",exercise_lemma())

    print("Whole-graph brute force versus latent-label peeling:", compare_deciders())
    worked_example()
