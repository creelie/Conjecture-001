"""Checks every number printed in the paper against a direct computation, by reading the tables, the
pair list of Lemma 4.1 and the cycle (4.1) out of preprint/main.tex.  Independent of the C program
and of Lean: K is rebuilt from its covering pairs, and L from the definition x <= y <= phi(x).

usage: python3 -I check_paper.py path/to/main.tex"""
import re
import sys
from itertools import product

COVERS = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 4), (2, 7), (3, 5), (3, 6), (4, 9), (5, 10), (6, 8), (6, 9),
          (7, 12), (8, 10), (8, 11), (9, 12), (10, 13), (11, 13), (12, 11)]
n = 14
K = range(n)
le = [[i == j for j in K] for i in K]
for a, b in COVERS:
    le[a][b] = True
for k, i, j in product(K, K, K):
    if le[i][k] and le[k][j]:
        le[i][j] = True


def join(a, b):
    ub = [u for u in K if le[a][u] and le[b][u]]
    least = [u for u in ub if all(le[u][w] for w in ub)]
    assert len(least) == 1
    return least[0]


def meet(a, b):
    lb = [u for u in K if le[u][a] and le[u][b]]
    greatest = [u for u in lb if all(le[w][u] for w in lb)]
    assert len(greatest) == 1
    return greatest[0]


J = [[join(a, b) for b in K] for a in K]
M = [[meet(a, b) for b in K] for a in K]
lower = {x: [y for y in K if y != x and le[y][x] and not any(z not in (x, y) and le[y][z] and le[z][x] for z in K)]
         for x in K}
upper = {x: [y for y in K if y != x and le[x][y] and not any(z not in (x, y) and le[x][z] and le[z][y] for z in K)]
         for x in K}
JI = [x for x in K if len(lower[x]) == 1]
MI = [x for x in K if len(upper[x]) == 1]

tex = open(sys.argv[1]).read()
fails = 0


def check(cond, what):
    global fails
    if not cond:
        fails += 1
        print('FAIL:', what)


def ints(s):
    return [int(t) for t in re.findall(r'\d+', s)]


# covering pairs and irreducibles as printed in Section 3
printed = re.findall(r'(\d+)\\prec(\d+)', tex)
check(sorted((int(a), int(b)) for a, b in printed) == sorted(COVERS), 'covering pairs of K')
check(f"join-irreducible elements are ${','.join(map(str, JI))}$" in tex, f'join-irreducibles {JI}')
check(f"meet-irreducible elements are ${','.join(map(str, MI))}$" in tex, f'meet-irreducibles {MI}')

# Table 1: j, j_*, up j_* - up j, kappa(j), m, m^*, down m^* - down m, kappa^d(m)
t1 = tex[tex.index(r'$j$ & $j_*$'):]
t1 = t1[t1.index(r'\midrule') + 8:t1.index(r'\bottomrule')]
rows = [r for r in t1.split(r'\\') if r.strip()]
check(len(rows) == 7, 'Table 1 has seven rows')
for r, j, m in zip(rows, JI, MI):
    c = [x.strip() for x in r.split('&')]
    jj, js, A, kj, mm, ms, B, km = c
    check(ints(jj) == [j] and ints(mm) == [m], f'Table 1 row order at {j}, {m}')
    check(ints(js) == lower[j], f'j_* for j = {j}')
    Aset = sorted(x for x in K if le[lower[j][0]][x] and not le[j][x])
    check(ints(A) == Aset, f'up j_* - up j for j = {j}: {Aset}')
    top = [x for x in Aset if all(le[y][x] for y in Aset)]
    check(top == ints(kj), f'kappa({j}) = {top}')
    check(ints(ms) == upper[m], f'm^* for m = {m}')
    Bset = sorted(x for x in K if le[x][upper[m][0]] and not le[x][m])
    check(ints(B) == Bset, f'down m^* - down m for m = {m}: {Bset}')
    bot = [x for x in Bset if all(le[x][y] for y in Bset)]
    check(bot == ints(km), f'kappa^d({m}) = {bot}')

# semidistributivity of K, directly
sd = all(J[a][b] != J[a][c] or J[a][b] == J[a][M[b][c]] for a, b, c in product(K, K, K)) and \
     all(M[a][b] != M[a][c] or M[a][b] == M[a][J[b][c]] for a, b, c in product(K, K, K))
check(sd, 'K is semidistributive')

# Table 2: phi, psi and the intervals [x, phi(x)]
t2 = tex[tex.index(r'$x$ & $0$ & $1$'):]
t2 = t2[:t2.index(r'\bottomrule')]
phi = ints(re.search(r'\$\\varphi\(x\)\$(.*?)\\\\', t2).group(1))
psi = ints(re.search(r'\$\\psi\(x\)\$(.*?)\\\\', t2).group(1))
ivs = [ints(c) for c in re.search(r'\$\[x,\\varphi\(x\)\]\$(.*?)\\\\', t2).group(1).split('&')[1:]]
check(len(phi) == n and len(psi) == n and len(ivs) == n, 'Table 2 has fourteen columns')
check(all(le[x][phi[x]] for x in K), 'x <= phi(x)')
check(all(phi[M[a][b]] == M[phi[a]][phi[b]] for a, b in product(K, K)), 'phi preserves meets')
for y in K:
    check(sorted(x for x in K if le[y][phi[x]]) == sorted(x for x in K if le[psi[y]][x]), f'psi({y})')
for x in K:
    check(sorted(ivs[x]) == sorted(y for y in K if le[x][y] and le[y][phi[x]]), f'interval [{x}, phi({x})]')
check('$K\\setminus\\{0,2,7\\}=\\up1$' in tex and sorted(x for x in K if le[6][phi[x]]) == [x for x in K if le[1][x]]
      and sorted(set(K) - {0, 2, 7}) == [x for x in K if le[1][x]], 'example in the proof of Lemma 4.1')

# L, D, C
Lset = [(x, y) for x in K for y in K if le[x][y] and le[y][phi[x]]]
check(len(Lset) == 26, 'L has 26 elements')
Cset = [p for p in Lset if p[0] != p[1]]
lem = tex[tex.index(r'and the twelve pairs'):]
lem = lem[:lem.index(r'\]')]
pairs = [tuple(map(int, t)) for t in re.findall(r'\((\d+),(\d+)\)', lem)]
check(sorted(pairs) == sorted(Cset), 'the twelve pairs of Lemma 4.1')
pj = lambda p, q: (J[p[0]][q[0]], J[p[1]][q[1]])
pm = lambda p, q: (M[p[0]][q[0]], M[p[1]][q[1]])
Ls = set(Lset)
check(all(pj(p, q) in Ls and pm(p, q) in Ls for p in Lset for q in Lset), 'L is a sublattice of K x K')

# the cycle (4.1) and footnote 2
cyc = tex[tex.index(r'\label{eq:cycle}'):]
cyc = cyc[:cyc.index(r'\end{aligned}')]
steps = re.findall(r'\((\d+),(\d+)\)\\(vee|wedge)\\(?:bar(\d)|overline\{(\d+)\})&=\((\d+),(\d+)\)', cyc)
check(len(steps) == 12, 'twelve steps in (4.1)')
chain = []
for a, b, op, d1, d2, c, e in steps:
    p, d, q = (int(a), int(b)), int(d1 or d2), (int(c), int(e))
    got = (pj if op == 'vee' else pm)(p, (d, d))
    check(got == q, f'{p} {op} {d} = {q} (computed {got})')
    chain.append((p, q))
check(all(chain[i][1] == chain[(i + 1) % 12][0] for i in range(12)), '(4.1) is a closed chain')
check(sorted(p for p, q in chain) == sorted(Cset), '(4.1) passes through all of C')
foot = tex[tex.index(r'In the first coordinate'):]
foot = foot[:foot.index('The remaining')]
for a, op, b, c in re.findall(r'(\d+)\\(vee|wedge)(\d+)=(\d+)', foot):
    a, b, c = int(a), int(b), int(c)
    check((J if op == 'vee' else M)[a][b] == c, f'footnote: {a} {op} {b} = {c}')

# maximality of D by generation, and the shape of C


def gen(S):
    S = set(S)
    while True:
        new = {pj(p, q) for p in S for q in S} | {pm(p, q) for p in S for q in S}
        if new <= S:
            return S
        S |= new


Dset = [(x, x) for x in K]
check(all(gen(Dset + [c]) == Ls for c in Cset), 'D is maximal in L')
check(gen(Dset + [(1, 3)]) == Ls, 'L is generated by D and (1,3)')
ple = lambda p, q: le[p[0]][q[0]] and le[p[1]][q[1]]
mins = sorted(c for c in Cset if not any(d != c and ple(d, c) for d in Cset))
maxs = sorted(c for c in Cset if not any(d != c and ple(c, d) for d in Cset))
check(mins == [(1, 3), (2, 7)], f'minimal elements of C: {mins}')
check(maxs == [(5, 10), (12, 11)], f'maximal elements of C: {maxs}')
check(pm((1, 3), (2, 7)) == (0, 0), '(1,3) ^ (2,7) = (0,0)')
check(ple((1, 3), (3, 3)) and ple((3, 3), (3, 6)) and (3, 6) in Cset, '(1,3) < (3,3) < (3,6)')
below13 = sorted(p for p in Lset if ple(p, (1, 3)))
below27 = sorted(p for p in Lset if ple(p, (2, 7)))
above510 = sorted(p for p in Lset if ple((5, 10), p))
above1211 = sorted(p for p in Lset if ple((12, 11), p))
check(below13 == [(0, 0), (1, 1), (1, 3)] and below27 == [(0, 0), (2, 2), (2, 7)], 'elements below (1,3), (2,7)')
check(above510 == [(5, 10), (10, 10), (13, 13)] and above1211 == [(11, 11), (12, 11), (13, 13)],
      'elements above (5,10), (12,11)')

# Remark 3.2 (D-cycle) and Remark 5.2 (self-duality)
for p, q, x in ((6, 7, 1), (7, 8, 2), (8, 6, 5)):
    check(le[p][J[q][x]] and not le[p][J[lower[q][0]][x]], f'{p} D {q} with witness {x}')
dmap = ints(re.search(r'\\mapsto([\d,]+)\$', tex).group(1))
check(sorted(dmap) == list(K) and all(le[i][j] == le[dmap[j]][dmap[i]] for i in K for j in K), 'self-duality map')
# the transposed example generated by D and (3,1)
T = gen(Dset + [(3, 1)])
check(T == {(y, x) for x, y in Ls}, 'D and (3,1) generate the transpose of L')

if fails:
    sys.exit(f'{fails} checks FAILED')
print('paper: covering pairs, Table 1, Table 2, Lemma 4.1, (4.1), footnote 2, Proposition 4.2, Theorem 4.3,')
print('Remarks 3.2, 5.1 and 5.2 agree with direct computation; all checks passed')
