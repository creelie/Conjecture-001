"""Writes the TikZ sources preprint/figures/k14.tex (the lattice K) and preprint/figures/l26.tex (the lattice L
with the diagonal D and its complement C). Run from the repository root: python3 scripts/gen_figures.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gen_lean import order, tables, build, NK, K_COVERS

POS = {0: (0, 0), 1: (-1, 1), 2: (1, 1), 3: (-2, 2), 4: (0, 2), 7: (2, 2), 5: (-3, 3), 6: (-1, 3),
       8: (-2, 4), 9: (0, 4), 10: (-3, 5), 12: (1, 5), 11: (0, 6), 13: (-1, 7)}

STYLE = r"""\documentclass[tikz,border=6pt]{standalone}
\usepackage{amsmath,amssymb}
\definecolor{inD}{RGB}{31,94,165}\definecolor{inC}{RGB}{214,96,33}
\tikzset{
  m/.style={circle,inner sep=0pt,minimum size=9pt,ball color=inD!85,draw=inD!60!black,line width=0.3pt},
  c/.style={circle,inner sep=0pt,minimum size=9pt,ball color=inC!90,draw=inC!60!black,line width=0.3pt},
  lab/.style={font=\small,fill=white,fill opacity=0.85,text opacity=1,inner sep=1.2pt,rounded corners=1pt},
  e/.style={line width=0.75pt,black!55},
  ec/.style={line width=1.4pt,inC!80!black},
  ex/.style={line width=0.6pt,black!35,densely dashed}}
\begin{document}
"""


def covers(n, le):
    return [(a, b) for a in range(n) for b in range(n) if a != b and le[a][b]
            and not any(c not in (a, b) and le[a][c] and le[c][b] for c in range(n))]


def k_figure():
    le = order(NK, K_COVERS)
    out = [STYLE, r"\begin{tikzpicture}[x=1.25cm,y=1.05cm]",
           r"\fill[black!4,rounded corners=10pt] (-3.7,-0.55) rectangle (2.7,7.55);"]
    for x, (a, b) in POS.items():
        out.append(rf"\coordinate (k{x}) at ({a},{b});")
    for a, b in covers(NK, le):
        out.append(rf"\draw[e] (k{a}) -- (k{b});")
    for x in POS:
        side = "below" if x == 0 else "above" if x == 13 else ("left" if POS[x][0] < 0 or x in (4, 9, 11) else "right")
        out.append(rf"\node[m] at (k{x}) {{}}; \node[lab,{side}=4pt] at (k{x}) {{${x}$}};")
    out += [r"\end{tikzpicture}", r"\end{document}"]
    return "\n".join(out) + "\n"


def l_figure():
    le, ks, ki, P, idx, n, sup, inf = build()
    lle = [[le[a][c] and le[b][d] for (c, d) in P] for (a, b) in P]

    def pos(p):
        a, b = p
        x = (POS[a][0] + POS[b][0]) / 2
        y = (POS[a][1] + POS[b][1]) / 2
        return x, y

    out = [STYLE, r"\begin{tikzpicture}[x=1.9cm,y=1.45cm]",
           r"\fill[black!4,rounded corners=10pt] (-3.7,-0.6) rectangle (2.75,7.6);"]
    for p in P:
        x, y = pos(p)
        out.append(rf"\coordinate ({name(p)}) at ({x:.3f},{y:.3f});")
    cov = covers(n, lle)
    # draw back sheet first, then cross edges, then the diagonal
    for a, b in cov:
        pa, pb = P[a], P[b]
        offa, offb = pa[0] != pa[1], pb[0] != pb[1]
        if offa and offb:
            out.append(rf"\draw[ec] ({name(pa)}) -- ({name(pb)});")
    for a, b in cov:
        pa, pb = P[a], P[b]
        if (pa[0] != pa[1]) != (pb[0] != pb[1]):
            out.append(rf"\draw[ex] ({name(pa)}) -- ({name(pb)});")
    for a, b in cov:
        pa, pb = P[a], P[b]
        if pa[0] == pa[1] and pb[0] == pb[1]:
            out.append(rf"\draw[e] ({name(pa)}) -- ({name(pb)});")
    for p in P:
        st = "m" if p[0] == p[1] else "c"
        lab = f"{p[0]}" if p[0] == p[1] else f"({p[0]},{p[1]})"
        side = SIDE.get(p, "left" if pos(p)[0] < 0 else "right")
        out.append(rf"\node[{st}] at ({name(p)}) {{}}; \node[lab,{side}=4pt] at ({name(p)}) {{${lab}$}};")
    out += [r"\end{tikzpicture}", r"\end{document}"]
    return "\n".join(out) + "\n", cov, P


SIDE = {}


def name(p):
    return f"d{p[0]}" if p[0] == p[1] else f"p{p[0]}x{p[1]}"


if __name__ == "__main__":
    os.makedirs("preprint/figures", exist_ok=True)
    open("preprint/figures/k14.tex", "w").write(k_figure())
    s, cov, P = l_figure()
    open("preprint/figures/l26.tex", "w").write(s)
    print("covers of L:", len(cov))
