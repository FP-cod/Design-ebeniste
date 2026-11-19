# -*- coding: utf-8 -*-
"""Apercu matplotlib 3D d'un ``Plan`` (hors Fusion), pour relecture rapide.

Usage : ``python -m equinox.apercu banc_flore docs/apercu_banc.png``
"""

import math
import sys

from .geometrie import Boite, Disque, Fuseau, PlaqueContour, TubeCarre, TubeSpline

COULEURS = {"bois": "#d9b98a", "inox": "#8a9199", "laiton": "#b5892e", "garnissage": "#9a5b2e", "lest": "#444444"}


def _cercle(c, d, n=24):
    return ([c[0] + d / 2 * math.cos(2 * math.pi * i / n) for i in range(n + 1)],
            [c[1] + d / 2 * math.sin(2 * math.pi * i / n) for i in range(n + 1)])


def tracer(plan, ax, mise_en_avant=("helice",)):
    for comp in plan.composants:
        fort = any(m in comp.nom for m in mise_en_avant)
        for prim in comp.primitives:
            col = COULEURS.get(prim.categorie, "k")
            if isinstance(prim, Fuseau):
                ax.plot(*zip(prim.p0, prim.p1), color=col, lw=max(1.0, (prim.d0 + prim.d1) / 2 / 5.0),
                        solid_capstyle="round")
            elif isinstance(prim, TubeSpline):
                pts = prim.points + ([prim.points[0]] if prim.ferme else [])
                ax.plot(*zip(*pts), color="#c0392b" if fort else col, lw=3.0 if fort else 1.5)
            elif isinstance(prim, (Boite,)):
                s = prim.sommets()
                aretes = [(0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7)]
                for i, j in aretes:
                    ax.plot(*zip(s[i], s[j]), color=col, lw=0.9)
            elif isinstance(prim, PlaqueContour):
                for haut in (False, True):
                    pts = prim.points_3d(haut)
                    pts.append(pts[0])
                    ax.plot(*zip(*pts), color=col, lw=1.2)
            elif isinstance(prim, Disque):
                xs, ys = _cercle(prim.centre, prim.diametre)
                ax.plot(xs, ys, [prim.centre[2]] * len(xs), color=col, lw=1.5)
            elif isinstance(prim, TubeCarre):
                ax.plot(*zip(prim.p0, prim.p1), color=col, lw=3.0)


def _egaliser(ax, plan):
    xs, ys, zs = [], [], []
    for comp in plan.composants:
        for prim in comp.primitives:
            c = prim.centroide()
            xs.append(c[0]); ys.append(c[1]); zs.append(c[2])
    zs.append(0.0)
    cx, cy, cz = [(max(v) + min(v)) / 2 for v in (xs, ys, zs)]
    r = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)) / 2 + 80
    ax.set_xlim(cx - r, cx + r); ax.set_ylim(cy - r, cy + r); ax.set_zlim(0, 2 * r)
    ax.set_xlabel("X (mm) -> avant"); ax.set_ylabel("Y (mm)"); ax.set_zlabel("Z (mm)")


def generer_png(plan, chemin, titre=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(15, 6.5))
    vues = [(18, -60, "Vue 3/4 arriere"), (0, -90, "Profil (cote D)"), (90, -90, "Dessus")]
    for i, (elev, azim, nom) in enumerate(vues):
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        tracer(plan, ax)
        _egaliser(ax, plan)
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(nom, fontsize=10)
    fig.suptitle(titre or "Equinox - %s (helice en rouge)" % plan.nom)
    fig.tight_layout()
    fig.savefig(chemin, dpi=130)
    plt.close(fig)
    return chemin


def generer_helice_png(plan, chemin):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(11, 5))
    for i, (elev, azim) in enumerate(((25, -50), (90, -90))):
        ax = fig.add_subplot(1, 2, i + 1, projection="3d")
        for cote in ("G", "D"):
            pts = plan.repere["helice_" + cote]
            ax.plot(*zip(*pts), color="#c0392b", lw=2)
            ax.scatter(*pts[0], color="k", s=20)
            info = plan.repere["pieds"]["AR_" + cote]
            ax.plot(*zip(*info["axe"]), color=COULEURS["bois"], lw=6)
        ax.view_init(elev=elev, azim=azim)
        ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
        ax.set_title("Helices (point noir = collier pivotant)" if i == 0 else "Dessus")
    fig.tight_layout()
    fig.savefig(chemin, dpi=130)
    plt.close(fig)
    return chemin


if __name__ == "__main__":  # pragma: no cover
    import importlib
    typo = sys.argv[1] if len(sys.argv) > 1 else "banc_flore"
    sortie = sys.argv[2] if len(sys.argv) > 2 else "apercu_%s.png" % typo
    mod = importlib.import_module("equinox.grammaires." + typo)
    print(generer_png(mod.concevoir(), sortie))
