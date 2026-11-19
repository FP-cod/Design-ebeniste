# -*- coding: utf-8 -*-
"""Apercus matplotlib de l'Entrave -> docs/*.png.

- ``apercu_entrave*.png``        : vues 3D (positions basse et haute) + faces X-Z ;
- ``apercu_entrave_profil*.png`` : profils Y-Z ;
- ``apercu_entrave_details*.png``: details de style (pied-colonne a chanfreins
  arretes, ceinture ajouree, angle de platine avec penture forgee et coussin
  matelasse, traces des moulures).

Les ajours (arcatures, lancettes, trous de crans) sont peints en couleur de
fond devant la face qui les porte.

Usage : python outils/generer_apercu.py
"""
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

from neogothique.parametres import Parametres  # noqa: E402
from neogothique.grammaires import entrave as E  # noqa: E402
from neogothique import profils as pf  # noqa: E402

FOND = "#f4f1ea"
COULEURS = {"bois": "#4b2e1e", "metal": "#2a2a2a", "acier": "#5d646b", "cuir": "#0d0d0d", "coussin": "#161616"}
ARETES = {"bois": "#9a7258", "metal": "#8a8a8a", "acier": "#9aa3ab", "cuir": "#555555", "coussin": "#5a5a5a"}


def vue_3d(ax, res, titre):
    for s in res.solides:
        poly = Poly3DCollection(s.facettes(), facecolor=COULEURS[s.materiau], edgecolor=ARETES[s.materiau],
                                linewidths=0.25, alpha=0.96)
        ax.add_collection3d(poly)
        trous = s.facettes_trous()
        if trous:
            ax.add_collection3d(Poly3DCollection(trous, facecolor=FOND, edgecolor=ARETES[s.materiau],
                                                 linewidths=0.3))
    ax.set_xlim(-450, 450)
    ax.set_ylim(-450, 450)
    ax.set_zlim(0, 650)
    ax.set_box_aspect((900, 900, 650))
    ax.view_init(elev=22, azim=-58)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_zlabel("Z (mm)")
    ax.set_title(titre, fontsize=10)


def vue_plan(ax, res, titre, axe_h=0, axe_v=2, axe_prof=1, depuis_moins=True, lims=None, filtre=None,
             annoter=True):
    """Projection orthogonale sur (axe_h, axe_v), algorithme du peintre selon axe_prof.

    ``depuis_moins`` : observateur du cote des axe_prof negatifs (face avant) ; sinon positifs (vue de dessus
    quand axe_prof = 2).
    """
    sgn = 1.0 if depuis_moins else -1.0
    faces = []
    for s in res.solides:
        if filtre and not filtre(s):
            continue
        for f in s.facettes():
            prof = sum(p[axe_prof] for p in f) / len(f)
            faces.append((sgn * prof, [(p[axe_h], p[axe_v]) for p in f], COULEURS[s.materiau], ARETES[s.materiau]))
        for f in s.facettes_trous():
            prof = sum(p[axe_prof] for p in f) / len(f)
            faces.append((sgn * prof - 1e-3, [(p[axe_h], p[axe_v]) for p in f], FOND, ARETES[s.materiau]))
    faces.sort(key=lambda t: -t[0])
    pc = PolyCollection([f[1] for f in faces], facecolors=[f[2] for f in faces], edgecolors=[f[3] for f in faces],
                        linewidths=0.3)
    ax.add_collection(pc)
    if lims is None:
        lim = 450 if axe_h == 0 else 320
        lims = (-lim, lim, -10, 640)
    ax.set_xlim(lims[0], lims[1])
    ax.set_ylim(lims[2], lims[3])
    ax.set_aspect("equal")
    ax.set_facecolor(FOND)
    if axe_v == 2 and annoter:
        ax.axhline(0, color="#999999", lw=0.8)
        ax.axhline(res.hauteur, color="#b03030", lw=0.6, ls="--")
        ax.text(lims[0] + 10, res.hauteur + 8, "dessus platine %g mm (cran %d)" % (res.hauteur, res.cran),
                color="#b03030", fontsize=7)
    ax.set_xlabel("XYZ"[axe_h] + " (mm)")
    ax.set_ylabel("XYZ"[axe_v] + " (mm)")
    ax.set_title(titre, fontsize=10)


def vue_traces(ax, res):
    """Traces (d, z) des moulures : pied (faces + aretes) et chant de platine."""
    c = res.cotes
    tp = c["traces_pied"]
    for segs, coul, lab in ((tp["face"], "#4b2e1e", "pied : faces"),
                            (tp["diag"], "#b07040", "pied : aretes (chanfrein arrete)")):
        if not segs:
            continue
        pts = pf.echantillonner(segs, 16)
        a = tp["a"] if segs is tp["face"] else tp["a_diag"] / 2 ** 0.5
        k = 1.0 if segs is tp["face"] else 2 ** 0.5
        xs, zs = [a - d / k for d, z in pts], [z for d, z in pts]
        ax.plot(xs, zs, color=coul, lw=1.4, label=lab)
        if segs is tp["face"]:
            ax.fill_betweenx(zs, c["alesage_fourreau"] / 2.0, xs, color="#7a4a2e", alpha=0.35, lw=0)
    ax.axvline(c["alesage_fourreau"] / 2.0, color="#777777", lw=0.8, ls=":", label="alesage")
    tr = c["trace_platine"]
    pts = pf.echantillonner(tr, 16)
    z0 = c["hauteur"]
    xs, zs = [100 - d for d, z in pts], [z - z0 + 330 for d, z in pts]
    ax.plot(xs, zs, color="#2a2a2a", lw=1.4, label="chant de platine (decale)")
    ax.fill_betweenx(zs, 60, xs, color="#7a4a2e", alpha=0.35, lw=0)
    ax.set_aspect("equal")
    ax.set_facecolor(FOND)
    ax.set_xlim(0, 115)
    ax.set_ylim(40, 345)
    ax.set_xlabel("demi-largeur (mm)")
    ax.set_ylabel("z (mm)")
    ax.legend(fontsize=7, loc="lower left")
    ax.set_title("Traces des moulures (demi-profils)", fontsize=10)


def generer(dossier=None, overrides=None, suffixe=""):
    dossier = dossier or os.path.join(RACINE, "docs")
    p = Parametres.pour_typologie("entrave", overrides, json_utilisateur=False)
    n = p.nombre_positions() - 1
    bas, haut = E.calculer_entrave(p, cran=0), E.calculer_entrave(p, cran=n)
    sec = p.get("entrave.pied.section")
    fig = plt.figure(figsize=(14, 11))
    vue_3d(fig.add_subplot(2, 2, 1, projection="3d"), bas, "Position basse - cran 0 (%g mm)" % bas.hauteur)
    vue_3d(fig.add_subplot(2, 2, 2, projection="3d"), haut, "Position haute - cran %d (%g mm)" % (n, haut.hauteur))
    vue_plan(fig.add_subplot(2, 2, 3), bas, "Face (X-Z) - basse")
    vue_plan(fig.add_subplot(2, 2, 4), haut, "Face (X-Z) - haute")
    fig.suptitle("Entrave cou-poignets - Neogothique raffine (pieds %s %g mm, %s, %s, pentures %s)" % (
        sec, p.get("entrave.pied.cote"), p.get("bois.essence"), p.get("ferrures.metal"),
        p.get("ferrures.terminaison_pentures")), fontsize=12)
    fig.tight_layout()
    f1 = os.path.join(dossier, "apercu_entrave%s.png" % suffixe)
    fig.savefig(f1, dpi=110)
    plt.close(fig)
    fig, axs = plt.subplots(1, 2, figsize=(12, 5.5))
    vue_plan(axs[0], bas, "Profil (Y-Z) - basse", axe_h=1, axe_prof=0, depuis_moins=False)
    vue_plan(axs[1], haut, "Profil (Y-Z) - haute", axe_h=1, axe_prof=0, depuis_moins=False)
    fig.suptitle("Entrave - profils (semelles a bouts en cavet, colonnes moulurees, capots ajoures)")
    fig.tight_layout()
    f2 = os.path.join(dossier, "apercu_entrave_profil%s.png" % suffixe)
    fig.savefig(f2, dpi=110)
    plt.close(fig)
    # details
    c = bas.cotes
    xp = c["x_pied"]
    fig, axs = plt.subplots(2, 2, figsize=(13, 11))
    vue_plan(axs[0][0], bas, "Pied-colonne et ceinture ajouree (face X-Z, cran 0)",
             lims=(xp - 260, xp + 110, -5, 330))
    vue_plan(axs[0][1], bas, "Calage : barre crantee, loquet, capot (profil Y-Z, cote droit)", axe_h=1,
             axe_prof=0, depuis_moins=False, lims=(c["y_pied"] - 90, c["y_pied"] + 110, -5, 330))
    vue_plan(axs[1][0], bas, "Angle de platine vu de dessus : penture '%s', rivets goutte de suif, coussin %s" % (
        p.get("ferrures.terminaison_pentures"), p.get("sellerie.matelassage_platine")),
        axe_h=0, axe_v=1, axe_prof=2, depuis_moins=False, lims=(80, 410, -210, 10),
        filtre=lambda s: s.boite_englobante()[1][2] >= bas.hauteur - 1.0)
    vue_traces(axs[1][1], bas)
    fig.suptitle("Details de style : plinthe / fut a chanfreins arretes / astragale / chapiteau, arcature, "
                 "pentures forgees", fontsize=11)
    fig.tight_layout()
    f3 = os.path.join(dossier, "apercu_entrave_details%s.png" % suffixe)
    fig.savefig(f3, dpi=110)
    plt.close(fig)
    return f1, f2, f3


if __name__ == "__main__":
    print(generer())
    print(generer(overrides={"entrave.pied.section": "octogonal", "entrave.pied.cote": 110.0,
                             "ferrures.terminaison_pentures": "trilobe", "style.motif_ajours": "quadrilobe",
                             "cremaillere.habillage": "plaque_decoupee", "sellerie.matelassage_platine": "capitonne"},
                  suffixe="_octogonal"))
