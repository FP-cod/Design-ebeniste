# -*- coding: utf-8 -*-
"""Couche 3 - Grammaire de l'« Entrave cou-poignets » (gamme Neogothique, v0.2 « raffinee »).

Description (repere : X = longueur de la platine, Y = profondeur, Z = haut,
origine au sol, au centre de la platine) :

- PLATINE en noyer massif (800 x 400 x 50 mm, double carre 2:1) a chants
  MOULURES : conge doux sur le dessus (cote corps), BEC-DE-CORBIN (tore +
  gorge + listel, hauteur e/phi) en sous-face qui allege visuellement
  l'epaisseur. Portee par quatre COULISSEAUX (tenons traversants a coins) ;
  deux barres a queue anti-tuilage dessous.
- CEINTURES AJOUREES avant et arriere sous la platine (hauteur ~ e x phi),
  percees d'une arcature (arcs brises, trilobes ou quadrilobes) ; elles
  suivent la platine (mobiles).
- Quatre PIEDS-COLONNES = FOURREAUX creux : PLINTHE (conge + glacis), BAGUE
  forgee au pied du fut, FUT legerement fuselé a CHANFREINS ARRETES (arret
  droit ou langue de boeuf), ASTRAGALE, CHAPITEAU (cavet sous abaque). Partition de la
  hauteur visible selon ``style.proportions`` (nombre d'or : H/phi^4, H/phi,
  H/phi^3). Section carree ou octogonale. Les fourreaux sont tenonnes dans
  deux SEMELLES (quart-de-rond sur les aretes, bouts en cavet) reliees par
  une TRAVERSE basse a tenons a clef.
- Reglage en hauteur : CREMAILLERE LATERALE de calage (fer plat cranté,
  trous de crans modelises, decor lisse / festonne / ajoure) suspendue sous
  la platine, guidee par une bride forgee ; LOQUET A PENE ; HABILLAGE par un
  capot en U ajoure de lancettes ou une plaque a quadrilobes.
- Synchronisation : cremaillere dentee + pignon par pied, arbres bas,
  renvois d'angle (mode ``quatre_points``).
- Manilles en cuir sellier fin (point sellier double, doublure agneau,
  rembourrage fin) sur pivots ; COUSSIN d'appui avant matelasse en losanges
  (ou capitonne).
- Ferrures forgees affinees : PENTURES d'angle 28 x 4 a TERMINAISONS forgees
  (fleur de lys, queue d'aronde, trilobe), rivets a TETE GOUTTE DE SUIF
  (revolutions), platines de pivot a coins abattus. Zero vis apparente.

Hauteur (variable derivee, convention ``cremaillere.convention``) ::

    hauteur_platine = hauteur_mini + cran_courant x pas

Usage hors Fusion ::

    from neogothique.grammaires import entrave
    res = entrave.calculer_entrave()
    print(entrave.rapport_texte(res))

Dans Fusion : ``run(context)`` (voir scripts_fusion/Entrave/Entrave.py).
"""

import math
import traceback

from ..parametres import Parametres
from ..catalogues import BOIS, METAUX, GARNISSAGE, TERMINAISONS, DECORS_BARRE
from ..catalogues.attaches import dimensionner, capacite_cheville_n
from .. import fusion_outils as fo
from .. import profils as pf
from ..fusion_outils import Solide, BlocProfile, Revolution, rectangle, cercle, octogone, polygone, chemin

TYPOLOGIE = "entrave"

#: Facteur de forme de Lewis (angle de pression 20 deg, denture normale).
FACTEUR_LEWIS = {12: 0.245, 13: 0.261, 14: 0.277, 15: 0.290, 16: 0.296, 17: 0.303, 18: 0.309, 19: 0.314,
                 20: 0.322, 21: 0.328, 22: 0.331, 24: 0.337, 26: 0.346, 28: 0.353, 30: 0.359, 34: 0.371,
                 38: 0.384, 43: 0.397, 50: 0.409}

#: Verifications des ferrures affinees soumises a la marge mini ``charges.marge_mini_ferrures``.
FERRURES_AFFINEES = ("cisaillement_pene", "matage_cran", "ligament_crans", "traction_barre_cran", "dent_lewis",
                     "torsion_arbre", "axe_pivot", "rivets_pivot", "gond")

#: Debordement (mm) des tranches diagonales non coupantes (evite les faces coincidentes).
EPS_DIAG = 0.5


def facteur_lewis(z):
    cles = sorted(FACTEUR_LEWIS)
    if z <= cles[0]:
        return FACTEUR_LEWIS[cles[0]]
    if z >= cles[-1]:
        return FACTEUR_LEWIS[cles[-1]]
    for a, b in zip(cles, cles[1:]):
        if a <= z <= b:
            return FACTEUR_LEWIS[a] + (FACTEUR_LEWIS[b] - FACTEUR_LEWIS[a]) * (z - a) / float(b - a)


class Verification(object):
    """Resultat d'un controle.

    :ivar niveau: "ok", "alerte" (acceptable sous condition) ou "insuffisant".
    :ivar sens: "max" (valeur <= limite) ou "min" (valeur >= limite).
    :ivar marge: limite / valeur (sens max) ou valeur / limite (sens min) ;
        > 1 : verifie, avec cette reserve.
    """

    def __init__(self, ident, nom, valeur, limite, unite, ok, detail, recommandation="", niveau=None, sens="max"):
        self.ident, self.nom, self.valeur, self.limite, self.unite = ident, nom, valeur, limite, unite
        self.ok, self.detail, self.recommandation = ok, detail, recommandation
        self.niveau = niveau or ("ok" if ok else "insuffisant")
        self.sens = sens
        if sens == "max":
            self.marge = (limite / valeur) if valeur else float("inf")
        else:
            self.marge = (valeur / limite) if limite else float("inf")

    def __repr__(self):
        return "<Verif %s %s>" % (self.ident, self.niveau)

    def ligne(self):
        sym = {"ok": "OK ", "alerte": "!! ", "insuffisant": "XX "}[self.niveau]
        marge = ("marge x%.2f" % self.marge) if self.marge != float("inf") else "marge infinie"
        txt = "%s%s : %.4g %s (limite %.4g %s, %s) - %s" % (sym, self.nom, self.valeur, self.unite, self.limite,
                                                            self.unite, marge, self.detail)
        if self.recommandation and self.niveau != "ok":
            txt += "\n      -> " + self.recommandation
        return txt


class ResultatEntrave(object):
    """Conteneur des resultats de la grammaire."""

    def __init__(self):
        self.params = None
        self.cran = 0
        self.hauteur = 0.0
        self.cotes = {}
        self.solides = []
        self.jonctions = []
        self.verifications = []
        self.masses = {}
        self.problemes = []
        self.alertes = []
        self.nomenclature = []
        self.parametres_derives = []

    def solide(self, nom):
        for s in self.solides:
            if s.nom == nom:
                return s
        raise KeyError(nom)

    def verification(self, ident):
        for v in self.verifications:
            if v.ident == ident:
                return v
        raise KeyError(ident)

    def insuffisances(self):
        return [v for v in self.verifications if v.niveau == "insuffisant"]


class ErreurGeometrie(ValueError):
    """Geometrie impossible avec les parametres donnes."""


# ---------------------------------------------------------------------------
# Proportions et profils
# ---------------------------------------------------------------------------
def partition_pied(p, H):
    """Hauteurs (plinthe, fut, chapiteau) de la partie visible H du pied selon ``style.proportions``.

    - nombre_or  : H/phi^4, H/phi, H/phi^3 (1/phi + 1/phi^3 + 1/phi^4 = 1) ;
    - harmonique : 1 : 5 : 2 (H/8, 5H/8, 2H/8 : octave plinthe/chapiteau, dixieme majeure chapiteau/fut) ;
    - libre      : parts ``style.part_plinthe`` / ``style.part_chapiteau``.
    """
    mode = p.get("style.proportions")
    if mode == "nombre_or":
        parts = (1 / pf.PHI ** 4, 1 / pf.PHI, 1 / pf.PHI ** 3)
    elif mode == "harmonique":
        parts = (1 / 8.0, 5 / 8.0, 2 / 8.0)
    else:
        a, c = p.get("style.part_plinthe"), p.get("style.part_chapiteau")
        parts = (a, 1.0 - a - c, c)
    return tuple(H * k for k in parts)


def chant_spec(type_, taille, hauteur=None, profondeur=None):
    """Argument ``chant_*`` de ``profils.trace_bloc`` pour un type de chant."""
    if type_ == "bec_de_corbin":
        return (type_, profondeur, hauteur, profondeur)
    return (type_, taille)


def traces_pied(p, c):
    """Traces (d, z) du pied-colonne : trace des faces (droite) et trace des aretes (diagonale).

    :return: dict(face=segments, diag=segments ou None, a=demi-largeur maxi,
        a_diag, zones=...). ``diag`` vaut None si pas de chanfrein arrete.
    """
    g = p.get
    A = c["a_max"] / 2.0
    deb, fus = g("entrave.pied.debord_base"), g("entrave.pied.fuselage")
    ra, rc, rp = g("entrave.pied.rayon_astragale"), g("entrave.pied.rayon_cavet"), g("entrave.pied.rayon_conge_plinthe")
    ch = min(g("bois.chanfrein_aretes"), 3.0)
    z_ft, hs = c["z_haut_fourreau"], c["semelle_h"]
    h_p, h_c = c["h_plinthe"], c["h_chapiteau"]
    z_ph, z_cb = hs + h_p, z_ft - h_c          # haut de plinthe, bas de chapiteau (= haut du fut)
    h_ab = g("entrave.pied.part_abaque") * h_c
    filet = 2.0
    d_haut_fut, d_bas_fut = deb + fus, deb
    # --- trace des faces
    tr = pf.Trace(ch, z_ft)
    tr.ligne(0.0, z_ft - ch)
    tr.vers(z_ft - h_ab)
    tr.palier(filet)
    tr.quart(filet + rc, z_ft - h_ab - rc, convexe=False)          # cavet sous l'abaque
    z_corb_bas = z_cb + 2 * ra
    if z_corb_bas > tr.p[1] + 1e-9:
        raise ErreurGeometrie("Chapiteau trop bas (%.1f mm) pour abaque + cavet R%g + astragale R%g : "
                              "reduire les rayons ou changer style.proportions" % (h_c, rc, ra))
    tr.vers(z_corb_bas)                                              # corbeille
    if ra > 0:
        tr.palier(d_haut_fut)
        tr.arc((d_haut_fut - ra, z_cb + ra), (d_haut_fut, z_cb))     # astragale (boudin)
    else:
        tr.palier(d_haut_fut)
        tr.vers(z_cb)
    tr.ligne(d_bas_fut, z_ph)                                        # fut fuselé
    if rp > deb + 1e-9 or deb > h_p - 1e-9:
        raise ErreurGeometrie("Plinthe trop basse (%.1f mm) ou conge R%g > debord %g" % (h_p, rp, deb))
    tr.quart(d_bas_fut - rp, z_ph - rp, convexe=False)               # conge fut / plinthe
    tr.ligne(0.0, z_ph - deb)                                        # glacis a 45 deg
    tr.vers(hs)
    face = tr.segments
    res = {"face": face, "a": A, "diag": None, "a_diag": None, "z_haut_plinthe": z_ph, "z_bas_chapiteau": z_cb}
    # --- chanfreins arretes (section carree)
    cw = g("entrave.pied.chanfrein_arrete")
    if c["section"] == "carre" and cw > 0:
        ad = A * math.sqrt(2.0) + EPS_DIAG
        w = lambda z: A - pf.evaluer(face, z)
        stop = g("entrave.pied.longueur_arret")
        z_s_haut = z_cb - stop
        z_s_bas = z_ph + c["frette_h"] + stop          # la bague forgee ceinture le pied du fut
        if z_s_haut - z_s_bas < 3 * cw:
            raise ErreurGeometrie("Fut trop court pour des chanfreins arretes (%.0f mm utiles)" % (z_s_haut - z_s_bas))
        k = (w(z_s_bas) - w(z_s_haut)) / (z_s_haut - z_s_bas)        # dw / d(-z)
        r2 = math.sqrt(2.0)
        # d_vis : la tranche diagonale affleure l'arete a EPS_DIAG pres (pas de face coincidente)
        d_vis = lambda z: ad - r2 * w(z) - EPS_DIAG
        dh = (cw / 2.0 + EPS_DIAG) / (1.0 + r2 * k)
        db = (cw / 2.0 + EPS_DIAG) / (1.0 - r2 * k)
        langue = g("entrave.pied.type_arret") == "langue_de_boeuf"
        t = pf.Trace(0.0, z_ft)
        t.vers(z_s_haut)
        t.palier(d_vis(z_s_haut))
        p1 = (d_vis(z_s_haut) + dh, z_s_haut - dh)
        if langue:
            t.quart(p1[0], p1[1], convexe=False)
        else:
            t.ligne(*p1)
        p2 = (d_vis(z_s_bas) + db, z_s_bas + db)
        t.ligne(*p2)
        if langue:
            t.quart(d_vis(z_s_bas), z_s_bas, convexe=False)
        else:
            t.ligne(d_vis(z_s_bas), z_s_bas)
        t.palier(0.0)
        t.vers(hs)
        res.update(diag=t.segments, a_diag=ad, z_arret_haut=z_s_haut, z_arret_bas=z_s_bas)
    return res


def bloc_pied(nom, c, tp, sx, sy):
    """BlocProfile d'un pied (fourreau) avec alesage et lumiere de cremaillere dentee."""
    xp, yp = c["x_pied"], c["y_pied"]
    A, al = tp["a"], c["alesage_fourreau"]
    dirs = [(0.0, A, tp["face"]), (90.0, A, tp["face"])]
    if c["section"] == "octogonal":
        dirs += [(45.0, A, tp["face"]), (135.0, A, tp["face"])]
    elif tp["diag"]:
        dirs += [(45.0, tp["a_diag"], tp["diag"]), (135.0, tp["a_diag"], tp["diag"])]
    ld = c["largeur_denture"]
    xa, xb = sorted((-sx * (A + 1.0), -sx * al / 2.0))
    lumiere = (xa, xb, -ld / 2.0 - 1.0, ld / 2.0 + 1.0, c["semelle_h"], c["z_haut_fourreau"])
    return BlocProfile(nom, "pied_colonne", (sx * xp, sy * yp), dirs,
                       alesage=(al, al, c["semelle_h"], c["z_haut_fourreau"]), enlevements=[lumiere],
                       materiau="bois")


def _cercle_chemin(cx, cz, r):
    return [("A", (cx + r, cz), (cx, cz + r), (cx - r, cz)), ("A", (cx - r, cz), (cx, cz - r), (cx + r, cz))]


def _transformer_profil(segs, f):
    return pf.transformer(segs, f)


# ---------------------------------------------------------------------------
# Calcul des cotes
# ---------------------------------------------------------------------------
def _cotes(p, cran):
    g = p.get
    c = {}
    L, W, e = g("entrave.platine.longueur"), g("entrave.platine.largeur"), g("entrave.platine.epaisseur")
    sec, a = g("entrave.pied.section"), g("entrave.pied.cote")
    deb, fus = g("entrave.pied.debord_base"), g("entrave.pied.fuselage")
    a_max, a_haut = a + 2 * deb, a - 2 * fus
    c.update(L=L, W=W, e=e, section=sec, cote_pied=a, a_max=a_max, a_fut_haut=a_haut, a_fut_bas=a)
    # le retrait est mesure depuis la partie la plus large (chapiteau / plinthe)
    c["x_pied"] = L / 2.0 - g("entrave.pied.retrait_bord") - a_max / 2.0
    c["y_pied"] = W / 2.0 - g("entrave.pied.retrait_bord") - a_max / 2.0
    jeu, paroi = g("tolerances.jeu_coulisseau"), g("entrave.fourreau.paroi")
    pdm = g("entrave.fourreau.paroi_diagonale_min")
    r2 = math.sqrt(2.0)
    al = a_haut - 2 * paroi                     # paroi mesuree au plus fin : haut du fut
    if sec == "octogonal":
        al = min(al, 2.0 * (a_haut / 2.0 - pdm) / r2)
    elif g("entrave.pied.chanfrein_arrete") > 0:
        # arete chanfreinee : distance diagonale = w.r2 - cw/2 ; alesage limite par paroi_diagonale_min
        al = min(al, 2.0 * (a_haut / 2.0 * r2 - g("entrave.pied.chanfrein_arrete") / 2.0 - pdm) / r2)
    cc = math.floor(al - 2 * jeu)
    if cc < g("bois.section_mini"):
        raise ErreurGeometrie("Coulisseau %g mm < section mini %g mm : augmenter entrave.pied.cote "
                              "(section %s)" % (cc, g("bois.section_mini"), sec))
    c["coulisseau"] = cc
    c["alesage_fourreau"] = al = cc + 2 * jeu
    if sec == "octogonal":
        c["paroi_diagonale"] = a_haut / 2.0 - al / 2.0 * r2
    elif g("entrave.pied.chanfrein_arrete") > 0:
        c["paroi_diagonale"] = a_haut / 2.0 * r2 - g("entrave.pied.chanfrein_arrete") / 2.0 - al / 2.0 * r2
    else:
        c["paroi_diagonale"] = (a_haut - al) / 2.0 * r2
    c["paroi_plats"] = (a_haut - al) / 2.0
    # Hauteurs et crans
    hm, hM, pas = g("cremaillere.hauteur_mini"), g("cremaillere.hauteur_maxi"), g("cremaillere.pas")
    npos = p.nombre_positions()
    if not 0 <= cran <= npos - 1:
        raise ErreurGeometrie("cran %s hors [0 ; %d]" % (cran, npos - 1))
    h = hm + cran * pas
    c.update(hauteur_mini=hm, hauteur_maxi=hM, pas=pas, positions=npos, cran=cran, hauteur=h,
             debattement=hM - hm, course_crans=(npos - 1) * pas,
             hauteurs_crans=[hm + k * pas for k in range(npos)])
    c["course_courante"] = cran * pas
    # Semelles, fourreaux, coulisseaux
    hs, ws, Ls = g("entrave.semelle.hauteur"), g("entrave.semelle.largeur"), g("entrave.semelle.longueur")
    c.update(semelle_h=hs, semelle_l=ws, semelle_L=Ls)
    zb_min, zb_max = hm - e, hM - e
    zb = h - e
    z_ft = zb_min - g("entrave.fourreau.jeu_haut")
    Hf = z_ft - hs
    if Hf < 2 * g("bois.section_mini"):
        raise ErreurGeometrie("Fourreau trop court (%g mm) : hauteur_mini trop faible pour l'epaisseur de "
                              "platine et la semelle" % Hf)
    h_p, h_f, h_c = partition_pied(p, Hf)
    c.update(h_plinthe=h_p, h_fut=h_f, h_chapiteau=h_c, frette_h=g("entrave.fourreau.frette_hauteur"))
    z_cb_min = hs - g("entrave.semelle.profondeur_logement") + g("entrave.coulisseau.garde_bas")
    Lc = zb_min - z_cb_min
    z_cb_max = zb_max - Lc
    rec = z_ft - max(z_cb_max, hs)
    c.update(z_dessous_platine=zb, z_dessous_platine_min=zb_min, z_dessous_platine_max=zb_max,
             z_haut_fourreau=z_ft, fourreau_hauteur=Hf, coulisseau_longueur=Lc,
             z_bas_coulisseau=zb - Lc, z_bas_coulisseau_min=z_cb_min, z_bas_coulisseau_max=z_cb_max,
             recouvrement_haut=rec, largeur_denture=g("cremaillere.largeur_denture"))
    if rec <= 0:
        raise ErreurGeometrie("Le coulisseau sort du fourreau en position haute (recouvrement %g mm)" % rec)
    tp = traces_pied(p, c)
    c["traces_pied"] = tp
    c["z_haut_plinthe"], c["z_bas_chapiteau"] = tp["z_haut_plinthe"], tp["z_bas_chapiteau"]
    w_fut = lambda z: tp["a"] - pf.evaluer(tp["face"], z)
    c["demi_largeur_fut"] = w_fut
    # Synchronisation : cremaillere dentee + pignon (references a la partie la plus large du pied)
    m = g("cremaillere.module")
    z_dents = max(int(g("cremaillere.dents_mini")), int(math.ceil((hM - hm) / (math.pi * m) - 1e-9)))
    rp = m * z_dents / 2.0
    c.update(module=m, pignon_dents=z_dents, pignon_d_primitif=2 * rp, pignon_d_tete=2 * rp + 2 * m,
             pas_denture=math.pi * m, course_par_tour=math.pi * m * z_dents,
             tours_course_totale=(hM - hm) / (math.pi * m * z_dents),
             dents_cremaillere=int(math.ceil((Lc - 2 * m) / (math.pi * m))))
    c["x_ligne_primitive"] = c["x_pied"] - a_max / 2.0 - m - 2.0
    c["x_arbre"] = c["x_ligne_primitive"] - rp
    c["z_arbre"] = z_cb_max + g("cremaillere.marge_engrenement")
    contact_rel_min = c["z_arbre"] - z_cb_min
    if contact_rel_min > Lc - g("cremaillere.marge_engrenement") + 1e-9:
        raise ErreurGeometrie("Denture trop courte : contact a %g mm du bas du coulisseau en position basse" %
                              contact_rel_min)
    if c["z_arbre"] + rp + m >= zb_min:
        raise ErreurGeometrie("Pignon (z=%g, R tete=%g) touche la platine en position basse" %
                              (c["z_arbre"], rp + m))
    # Cremaillere laterale de calage + loquet : la barre passe a l'exterieur de la plinthe, du chapiteau
    # ET de la semelle, ce qui lui permet de descendre pres du sol (barre plus longue => loquet sur le fut).
    fe, fl = g("ferrures.fer_plat_epaisseur"), g("ferrures.fer_plat_largeur")
    tb = g("cremaillere.barre_epaisseur")
    x_bar_in = c["x_pied"] + max(a_max, ws) / 2.0 + 2.0
    c["x_barre_calage"] = x_bar_in + tb / 2.0
    garde = 10.0 if x_bar_in > c["x_pied"] + ws / 2.0 else hs + 5.0
    Lbar = zb_min - fe - garde
    c["barre_calage_longueur"] = Lbar
    bh = g("loquet.boitier_hauteur")
    h_loq = max(bh, fl)
    lo = max(zb_max - fe - Lbar + pas / 2.0, hs + bh / 2.0,
             tp["z_haut_plinthe"] + c["frette_h"] + h_loq / 2.0 + 2.0)
    hi = min(zb_min - fe - pas / 2.0, z_ft - bh / 2.0, tp["z_bas_chapiteau"] - h_loq / 2.0 - 2.0)
    if lo > hi:
        raise ErreurGeometrie("Pas de fenetre commune pour le loquet sur le fut (%g > %g) : course trop grande "
                              "pour des pieds si courts, ou chapiteau/plinthe trop hauts" % (lo, hi))
    z_loq = round((lo + hi) / 2.0)
    c["z_loquet"] = z_loq
    c["fenetre_loquet"] = (lo, hi)
    c["trous_crans"] = sorted(z_loq - (hm + k * pas - e - fe - Lbar) for k in range(npos))
    # Manilles
    epm = g("garnissage.epaisseur_manille")
    c["manille_cou_d_ext"] = g("garnissage.diametre_int_cou") + 2 * epm
    c["manille_poignet_d_ext"] = g("garnissage.diametre_int_poignet") + 2 * epm
    c["z_pivot"] = h + g("ferrures.platine_pivot_epaisseur") + g("entrave.manilles.hauteur_pivot")
    c["z_manille_cou"] = c["z_pivot"] + c["manille_cou_d_ext"] / 2.0
    c["z_manille_poignet"] = c["z_pivot"] + c["manille_poignet_d_ext"] / 2.0
    c["z_manille_cou_max"] = c["z_manille_cou"] - h + hM
    # Mortaise oblongue (dilatation transversale de la platine, fil selon X)
    ess = BOIS[g("bois.essence")]
    mvt = 2 * c["y_pied"] * ess["retrait_tangentiel_coef"] / 100.0 * g("bois.variation_humidite")
    c["dilatation_platine"] = mvt
    c["jeu_mortaise_oblongue"] = max(g("tolerances.jeu_mortaise_oblongue"), math.ceil(mvt * 2) / 2.0)
    # Platine moulee : section reelle (flexion selon X, section dans le plan Y-Z)
    tr_pl = pf.trace_bloc(h, h - e,
                          chant_spec(g("entrave.platine.chant_dessus"), g("entrave.platine.chant_dessus_taille")),
                          chant_spec(g("entrave.platine.chant_dessous"), g("entrave.platine.chant_dessous_profondeur"),
                                     g("entrave.platine.chant_dessous_hauteur"),
                                     g("entrave.platine.chant_dessous_profondeur"))).segments
    c["trace_platine"] = tr_pl
    c["section_platine"] = pf.proprietes_section(W / 2.0, tr_pl)
    # Ceinture ajouree
    c["ceinture"] = g("entrave.ceinture.active")
    if c["ceinture"]:
        ret, ep_c = g("entrave.ceinture.retrait"), g("entrave.ceinture.epaisseur")
        c["ceinture_y"] = W / 2.0 - ret - ep_c / 2.0
        c["ceinture_demi_longueur"] = c["x_pied"] - a_max / 2.0 - 2.0
        if ret < g("entrave.platine.chant_dessous_profondeur") + 2.0:
            raise ErreurGeometrie("Ceinture sous la moulure de platine : retrait >= profondeur du chant + 2 mm")
        if c["ceinture_y"] + ep_c / 2.0 > c["y_pied"] + a_max / 2.0 + 1e-9 and \
                c["ceinture_demi_longueur"] > c["x_pied"] - a_max / 2.0:
            raise ErreurGeometrie("Ceinture en collision avec les chapiteaux")
    return c


# ---------------------------------------------------------------------------
# Solides
# ---------------------------------------------------------------------------
def _pentures(p, c, S, h):
    """Pentures d'angle a terminaisons forgees + rivets goutte de suif."""
    g = p.get
    L, W = c["L"], c["W"]
    fe, fl = g("ferrures.fer_plat_epaisseur"), g("ferrures.fer_plat_largeur")
    Lp, nr = g("entrave.pentures.longueur"), int(g("entrave.pentures.rivets_par_branche"))
    term = g("ferrures.terminaison_pentures")
    dr, dt, ht = g("ferrures.rivet_diametre"), g("ferrures.tete_rivet_diametre"), g("ferrures.tete_rivet_hauteur")
    segs = pf.penture(Lp, fl, term)
    vmax = max(abs(q[1]) for q in pf.echantillonner(segs, 12))
    inset = max(vmax + g("entrave.pentures.recul_bord"), fl / 2.0 + g("entrave.platine.chant_dessus_taille") + 1.0)
    c0 = inset - fl / 2.0
    lt = TERMINAISONS[term]["longueur_relative"] * fl
    zone = Lp - lt - fl
    if zone < nr * 3 * dr:
        raise ErreurGeometrie("Penture trop courte : %.0f mm de bande droite pour %d rivets (>= 3 d chacun) - "
                              "allonger entrave.pentures.longueur" % (zone, nr))
    c.update(penture_inset=inset, penture_envergure=vmax, penture_bande_droite=zone)
    us = [fl + zone * (k + 0.5) / nr for k in range(nr)]
    rivets = []
    for nx, sx in (("D", 1), ("G", -1)):
        for ny, sy in (("AR", 1), ("AV", -1)):
            suf = "%s_%s" % (ny, nx)
            # branche le long de X
            cx, cy = sx * (L / 2.0 - c0 - Lp / 2.0), sy * (W / 2.0 - inset)
            fx = lambda q, sx=sx, cx=cx: (sx * (L / 2.0 - c0 - q[0]) - cx, q[1])
            S.append(Solide("penture_x_" + suf, "penture_angle", "z", (cx, cy, h + fe / 2.0), fe,
                            chemin(pf.transformer(segs, fx)), materiau="metal", mobile=True))
            # branche le long de Y
            cx2, cy2 = sx * (L / 2.0 - inset), sy * (W / 2.0 - c0 - Lp / 2.0)
            fy = lambda q, sy=sy, cy2=cy2: (q[1], sy * (W / 2.0 - c0 - q[0]) - cy2)
            S.append(Solide("penture_y_" + suf, "penture_angle", "z", (cx2, cy2, h + fe / 2.0), fe,
                            chemin(pf.transformer(segs, fy)), materiau="metal", mobile=True))
            rivets.append(("rivet_pc_" + suf, sx * (L / 2.0 - inset), sy * (W / 2.0 - inset)))
            for k, u in enumerate(us):
                rivets.append(("rivet_px_%s_%d" % (suf, k), sx * (L / 2.0 - c0 - u), sy * (W / 2.0 - inset)))
                rivets.append(("rivet_py_%s_%d" % (suf, k), sx * (L / 2.0 - inset), sy * (W / 2.0 - c0 - u)))
    prof = fo.tete_goutte_de_suif(h + fe, dt, ht)
    for nom, x, y in rivets:
        S.append(Revolution(nom, "tete_rivet_goutte_de_suif", (x, y), prof, materiau="metal", mobile=True))


def _coussin(p, c, S, h):
    """Coussin d'appui avant : bloc a conge, ou cellules en losange (matelassage) + boutons (capiton)."""
    g = p.get
    W = c["W"]
    ce = g("sellerie.coussin_epaisseur")
    ym = g("entrave.manilles.position_y")
    lm = max(g("garnissage.largeur_manille_cou"), g("ferrures.platine_pivot_cote"))
    y0, y1 = -W / 2.0 + 30.0, ym - lm / 2.0 - 8.0
    # le coussin s'arrete 8 mm avant le bout des pentures (branche X)
    xmax = min(240.0, c["L"] / 2.0 - (c["penture_inset"] - g("ferrures.fer_plat_largeur") / 2.0) -
               g("entrave.pentures.longueur") - 8.0)
    if xmax < 100.0:
        raise ErreurGeometrie("Pentures trop longues : plus de place pour le coussin d'appui")
    if y1 - y0 < 40.0:
        raise ErreurGeometrie("Pas de place pour le coussin d'appui devant les manilles")
    Ax, Ay, cy = xmax, (y1 - y0) / 2.0, (y0 + y1) / 2.0
    rc = min(6.0, ce * 0.4)
    t_pad = pf.trace_bloc(h + ce, h, ("conge", rc)).segments
    c.update(coussin=(-xmax, xmax, y0, y1))
    mode = g("sellerie.matelassage_platine")
    if mode == "aucun":
        S.append(BlocProfile("coussin_avant", "coussin_cuir", (0.0, cy), [(0.0, Ax, t_pad), (90.0, Ay, t_pad)],
                             materiau="coussin", mobile=True))
        return
    pm = g("sellerie.matelassage_pas")
    ac = pm / (2.0 * math.sqrt(2.0))           # demi-largeur d'une cellule (losange carre de diagonale pm)
    rcel = min(5.0, ce / 3.0)
    t_cel = pf.trace_bloc(h + ce, h, ("conge", rcel)).segments
    pas = pm / 2.0
    n_i, n_j = int(math.ceil(Ax / pas)) + 1, int(math.ceil(Ay / pas)) + 1
    plein = pm * pm / 2.0
    k = 0
    for j in range(-n_j, n_j + 1):
        for i in range(-n_i, n_i + 1):
            if (i + j) % 2:
                continue
            x, y = i * pas, cy + j * pas
            dirs = [(45.0, ac, t_cel), (135.0, ac, t_cel), (0.0, Ax, t_pad, -x), (90.0, Ay, t_pad, cy - y)]
            bloc = BlocProfile("coussin_cellule_%02d" % k, "coussin_cellule_cuir", (x, y), dirs,
                               materiau="coussin", mobile=True)
            if bloc._aire_z(h + 0.5 * ce) < 0.15 * plein:
                continue
            S.append(bloc)
            k += 1
    c["coussin_cellules"] = k
    if mode == "capitonne":
        bd = g("sellerie.bouton_diametre")
        prof = fo.tete_goutte_de_suif(h + ce - rcel, bd, bd / 3.0)
        n = 0
        for j in range(-n_j, n_j + 1):
            for i in range(-n_i, n_i + 1):
                if (i + j) % 2 == 0:
                    continue
                x, y = i * pas, cy + j * pas
                if abs(x) <= Ax - pas / 2.0 and abs(y - cy) <= Ay - pas / 2.0:
                    S.append(Revolution("bouton_capiton_%02d" % n, "bouton_capiton", (x, y), prof,
                                        materiau="cuir", mobile=True))
                    n += 1
        c["coussin_boutons"] = n


def _barre_calage_profil(p, c):
    """Profil (u = Y local, v = Z local) de la barre crantee : rives (festons), trous de crans, ajours."""
    g = p.get
    lb, Lbar, pas = g("cremaillere.barre_largeur"), c["barre_calage_longueur"], c["pas"]
    d = g("loquet.pene_diametre") + 0.5
    decor = g("cremaillere.decor_barre")
    taux = DECORS_BARRE[decor]["taux_enlevement"]
    vb = -Lbar / 2.0
    trous_v = [vb + t for t in c["trous_crans"]]
    a = lb / 2.0
    if decor == "festonnee":
        f = taux * a                     # profondeur des festons
        mids = [(v1 + v2) / 2.0 for v1, v2 in zip(trous_v, trous_v[1:])]
        demi = 0.4 * pas
        segs = [("L", (-a, -Lbar / 2.0), (a, -Lbar / 2.0))]
        cur = -Lbar / 2.0
        for vm in mids:                  # rive droite, de bas en haut
            segs.append(("L", (a, cur), (a, vm - demi)))
            segs.append(("A", (a, vm - demi), (a - f, vm), (a, vm + demi)))
            cur = vm + demi
        segs.append(("L", (a, cur), (a, Lbar / 2.0)))
        segs.append(("L", (a, Lbar / 2.0), (-a, Lbar / 2.0)))
        cur = Lbar / 2.0
        for vm in reversed(mids):        # rive gauche, de haut en bas
            segs.append(("L", (-a, cur), (-a, vm + demi)))
            segs.append(("A", (-a, vm + demi), (-a + f, vm), (-a, vm - demi)))
            cur = vm - demi
        segs.append(("L", (-a, cur), (-a, -Lbar / 2.0)))
        ext = chemin([s for s in segs if s[0] == "A" or abs(s[1][1] - s[2][1]) + abs(s[1][0] - s[2][0]) > 1e-9])
    else:
        ext = chemin(pf.rectangle_chemin(-a, -Lbar / 2.0, a, Lbar / 2.0))
    trous = [chemin(_cercle_chemin(0.0, v, d / 2.0)) for v in trous_v]
    if decor == "ajouree":
        r = min((pas - d) / 2.0 - 2.5, a - 4.0)
        if r > 1.5:
            trous += [chemin(pf.lobes(0.0, (v1 + v2) / 2.0, r, 4, 45.0)) for v1, v2 in zip(trous_v, trous_v[1:])]
    return ext, trous


def _habillage(p, c, S, nx, sx, ny, sy):
    """Capot en U (ajoure de lancettes) ou plaque a quadrilobes devant la barre de calage (fixe)."""
    g = p.get
    hab = g("cremaillere.habillage")
    if hab == "aucun":
        return
    tb, lb = g("cremaillere.barre_epaisseur"), g("cremaillere.barre_largeur")
    ep = g("cremaillere.capot_epaisseur")
    fl, bh = g("ferrures.fer_plat_largeur"), g("loquet.boitier_hauteur")
    xb, yp, xp = c["x_barre_calage"], c["y_pied"], c["x_pied"]
    z0 = c["z_loquet"] + max(fl, bh) / 2.0 + 3.0
    z1 = c["z_haut_fourreau"] - 4.0
    hc = z1 - z0
    if hc < 25.0:
        return
    larg = lb + 16.0
    xf = xb + tb / 2.0 + 2.0 + ep / 2.0
    suf = "%s_%s" % (ny, nx)
    if hab == "capot_ajoure":
        n = 1 if larg < 45 else 2
        boucles, _, _ = pf.ajours_arcature(larg, hc, n, "ogive", marge=6.0, ratio_largeur=0.5, ratio_rayon=1.3)
    else:
        rq = min(larg / 2.0 - 5.0, 12.0)
        nq = max(1, int((hc - 10.0) // (2 * rq + 4.0)))
        boucles = [pf.lobes(0.0, 5.0 + (2 * rq + 4.0) * (k + 0.5), rq, 4, 45.0) for k in range(nq)]
    trous = [chemin(pf.transformer(b, lambda q: (q[0], q[1] - hc / 2.0))) for b in boucles]
    S.append(Solide("capot_cremaillere_" + suf, "capot_cremaillere", "x", (sx * xf, sy * yp, (z0 + z1) / 2.0), ep,
                    rectangle(larg, hc), materiau="metal", trous=trous))
    x_dos = xp + c["a_max"] / 2.0
    xj0, xj1 = x_dos, xf + ep / 2.0
    for k, dy in enumerate((-larg / 2.0 + ep / 2.0, larg / 2.0 - ep / 2.0)):
        S.append(Solide("joue_capot_%s_%d" % (suf, k), "capot_cremaillere", "y",
                        (sx * (xj0 + xj1) / 2.0, sy * yp + dy, (z0 + z1) / 2.0), ep, rectangle(xj1 - xj0, hc),
                        materiau="metal"))


def _solides(p, c):
    g = p.get
    S = []
    L, W, h = c["L"], c["W"], c["hauteur"]
    zb = c["z_dessous_platine"]
    cc, sec = c["coulisseau"], c["section"]
    xp, yp = c["x_pied"], c["y_pied"]
    hs, ws, Ls = c["semelle_h"], c["semelle_l"], c["semelle_L"]
    fe, fl = g("ferrures.fer_plat_epaisseur"), g("ferrures.fer_plat_largeur")
    m, ld = c["module"], g("cremaillere.largeur_denture")
    za = c["z_arbre"]
    A = c["a_max"] / 2.0
    tp = c["traces_pied"]
    cotes_x = (("D", 1), ("G", -1))
    cotes_y = (("AR", 1), ("AV", -1))

    # --- Mobile : platine moulee, ceintures ajourees, barres a queue, coulisseaux, cremailleres
    tr_pl = c["trace_platine"]
    S.append(BlocProfile("platine", "platine", (0.0, 0.0), [(0.0, L / 2.0, tr_pl), (90.0, W / 2.0, tr_pl)],
                         materiau="bois", mobile=True))
    hb, wb = 22.0, 50.0
    xbq = c["x_arbre"] - g("synchro.carter_cote") / 2.0 - 30.0 - wb / 2.0
    lbq = W - 60.0
    if c["ceinture"]:
        ep_c, hc = g("entrave.ceinture.epaisseur"), g("entrave.ceinture.hauteur")
        lbq = 2 * (c["ceinture_y"] - ep_c / 2.0) - 2.0
        xc = c["ceinture_demi_longueur"]
        boucles, w_baie, montant = pf.ajours_arcature(2 * xc, hc, int(g("entrave.ceinture.nombre_arcades")),
                                                     g("style.motif_ajours"), g("entrave.ceinture.marge"),
                                                     g("entrave.ceinture.ratio_largeur"), g("style.ratio_rayon_ogive"))
        c.update(ceinture_baie=w_baie, ceinture_montant=montant)
        t_droit = pf.trace_bloc(zb, zb - hc).segments
        t_ep = pf.trace_bloc(zb, zb - hc, ("droit", 0), ("chanfrein", g("entrave.ceinture.chanfrein_bas"))).segments
        ajours = [chemin(pf.transformer(b, lambda q: (q[0], q[1] + zb - hc))) for b in boucles]
        for ny, sy in cotes_y:
            S.append(BlocProfile("ceinture_" + ny, "ceinture_ajouree", (0.0, sy * c["ceinture_y"]),
                                 [(0.0, xc, t_droit), (90.0, ep_c / 2.0, t_ep)], materiau="bois", mobile=True,
                                 ajours=(1, ajours)))
    for nx, sx in cotes_x:
        S.append(Solide("barre_queue_%s" % nx, "barre_a_queue", "z", (sx * xbq, 0, zb - hb / 2.0), hb,
                        rectangle(wb, lbq), materiau="bois", mobile=True))
    c["x_barres_queue"] = xbq
    Lc = c["coulisseau_longueur"]
    ext_bar, trous_bar = _barre_calage_profil(p, c)
    Lbar = c["barre_calage_longueur"]
    tb, lb = g("cremaillere.barre_epaisseur"), g("cremaillere.barre_largeur")
    xb = c["x_barre_calage"]
    for nx, sx in cotes_x:
        for ny, sy in cotes_y:
            suf = "%s_%s" % (ny, nx)
            S.append(Solide("coulisseau_" + suf, "coulisseau", "z", (sx * xp, sy * yp, zb - Lc / 2.0), Lc,
                            rectangle(cc, cc), materiau="bois", mobile=True))
            x_tip = c["x_ligne_primitive"] - m
            x_in = xp - cc / 2.0 + 6.0
            S.append(Solide("cremaillere_dentee_" + suf, "cremaillere_dentee", "z",
                            (sx * (x_tip + x_in) / 2.0, sy * yp, zb - Lc / 2.0), Lc,
                            rectangle(x_in - x_tip, ld), materiau="acier", mobile=True))
            S.append(Solide("cremaillere_calage_" + suf, "cremaillere_calage", "x",
                            (sx * xb, sy * yp, zb - fe - Lbar / 2.0), tb, ext_bar,
                            materiau="metal", mobile=True, trous=trous_bar))
            x0, x1 = xb - tb / 2.0, min(xb + tb / 2.0 + 20.0, L / 2.0 - 3.0)
            S.append(Solide("equerre_calage_" + suf, "equerre_calage", "z",
                            (sx * (x0 + x1) / 2.0, sy * yp, zb - fe / 2.0), fe, rectangle(x1 - x0, lb),
                            materiau="metal", mobile=True))
    _pentures(p, c, S, h)
    # manilles
    ym = g("entrave.manilles.position_y")
    ec = g("entrave.manilles.ecartement_poignets")
    cp, ep_p = g("ferrures.platine_pivot_cote"), g("ferrures.platine_pivot_epaisseur")
    dax, hp, dg = g("ferrures.axe_pivot_diametre"), g("entrave.manilles.hauteur_pivot"), g("ferrures.gond_diametre")
    epm = g("garnissage.epaisseur_manille")
    ca = 0.15 * cp
    q = cp / 2.0
    plat = polygone([(-q + ca, -q), (q - ca, -q), (q, -q + ca), (q, q - ca), (q - ca, q), (-q + ca, q), (-q, q - ca),
                     (-q, -q + ca)])
    prof_rivet = fo.tete_goutte_de_suif(h + ep_p, g("ferrures.tete_rivet_diametre"), g("ferrures.tete_rivet_hauteur"))
    manilles = [("cou", 0.0, g("garnissage.diametre_int_cou"), g("garnissage.largeur_manille_cou"),
                 g("entrave.manilles.pivot_cou")),
                ("poignet_G", -ec / 2.0, g("garnissage.diametre_int_poignet"), g("garnissage.largeur_manille_poignet"),
                 g("entrave.manilles.pivot_poignets")),
                ("poignet_D", ec / 2.0, g("garnissage.diametre_int_poignet"), g("garnissage.largeur_manille_poignet"),
                 g("entrave.manilles.pivot_poignets"))]
    dri = q - 12.0
    for nom, xm, di, lm, piv in manilles:
        S.append(Solide("platine_pivot_" + nom, "platine_pivot", "z", (xm, ym, h + ep_p / 2.0), ep_p,
                        plat, materiau="metal", mobile=True))
        for k, (dx, dy) in enumerate(((-dri, -dri), (dri, -dri), (dri, dri), (-dri, dri))):
            S.append(Revolution("rivet_pivot_%s_%d" % (nom, k), "tete_rivet_goutte_de_suif", (xm + dx, ym + dy),
                                prof_rivet, materiau="metal", mobile=True))
        z0 = h + ep_p
        if piv == "axe_vertical_chape":
            S.append(Solide("axe_pivot_" + nom, "axe_pivot", "z", (xm, ym, z0 + hp / 2.0), hp, cercle(dax),
                            materiau="metal", mobile=True))
            S.append(Solide("chape_" + nom, "chape", "z", (xm, ym, z0 + hp - 5.0), 10.0,
                            rectangle(dax + 12.0, lm), materiau="metal", mobile=True))
        elif piv == "rotule":
            S.append(Solide("coquille_rotule_" + nom, "coquille_rotule", "z", (xm, ym, z0 + hp / 2.0), hp,
                            octogone(2.2 * dax), materiau="metal", mobile=True))
        else:  # charniere_basculante : deux noeuds + axe horizontal (Y)
            for k, dy in enumerate((-lm / 2.0 + 5.0, lm / 2.0 - 5.0)):
                S.append(Solide("noeud_charniere_%s_%d" % (nom, k), "noeud_charniere", "z",
                                (xm, ym + dy, z0 + hp / 2.0), hp, rectangle(dax + 10.0, 10.0),
                                materiau="metal", mobile=True))
            S.append(Solide("axe_charniere_" + nom, "axe_pivot", "y", (xm, ym, z0 + hp - dax / 2.0 - 2.0), lm,
                            cercle(dax), materiau="metal", mobile=True))
        dext = di + 2 * epm
        zc = z0 + hp + dext / 2.0
        S.append(Solide("manille_" + nom, "manille_cuir", "y", (xm, ym, zc), lm, octogone(dext), octogone(di),
                        materiau="cuir", mobile=True))
        S.append(Solide("gond_" + nom, "gond", "y", (xm - dext / 2.0 - dg / 2.0, ym, zc), lm, cercle(dg),
                        materiau="metal", mobile=True))
        S.append(Solide("fermoir_" + nom, "fermoir_ouverture_rapide" if nom == "cou" else "fermoir", "y",
                        (xm + dext / 2.0 + 5.0, ym, zc), lm * 0.6, rectangle(10.0, 20.0),
                        materiau="metal", mobile=True))
    if g("sellerie.coussin_avant"):
        _coussin(p, c, S, h)

    # --- Fixe : semelles moulurees, ancrages, traverse a clefs, pieds-colonnes, bagues, brides, loquets, synchro
    R_cav = hs - g("entrave.semelle.garde_cavet")
    t_long = pf.trace_bloc(hs, 0.0, chant_spec(g("entrave.semelle.chant"), g("entrave.semelle.chant_taille"))).segments
    t_bout = pf.Trace(R_cav, hs).quart(0.0, hs - R_cav, convexe=False).vers(0.0).segments
    al = c["alesage_fourreau"]
    lg = g("entrave.semelle.profondeur_logement")
    for nx, sx in cotes_x:
        enl = []
        for ny, sy in cotes_y:
            enl.append((-al / 2.0, al / 2.0, sy * yp - al / 2.0, sy * yp + al / 2.0, hs - lg, hs + 1.0))  # logement
            xa, xb2 = sorted((-sx * (A + 1.0), -sx * al / 2.0))
            enl.append((xa, xb2, sy * yp - ld / 2.0 - 1.0, sy * yp + ld / 2.0 + 1.0,
                        c["z_bas_coulisseau_min"] - 2.0, hs + 1.0))                                       # lumiere
        S.append(BlocProfile("semelle_" + nx, "semelle", (sx * xp, 0.0),
                             [(0.0, ws / 2.0, t_long), (90.0, Ls / 2.0, t_bout)], materiau="bois",
                             enlevements=enl))
        if g("ancrage.anneaux_sol"):
            for ny, sy in cotes_y:
                S.append(Solide("ancrage_sol_%s_%s" % (ny, nx), "plaque_ancrage_sol", "z",
                                (sx * xp, sy * (Ls / 2.0 - R_cav - 30.0), 3.0), 6.0, rectangle(36.0, 36.0),
                                materiau="metal"))
    tw, th, gs = g("entrave.traverse.largeur"), g("entrave.traverse.hauteur"), g("entrave.traverse.garde_sol")
    xi = xp - ws / 2.0
    S.append(Solide("traverse_basse", "traverse_basse", "x", (0, 0, gs + th / 2.0), 2 * xi, rectangle(tw, th),
                    materiau="bois"))
    jt = dimensionner(g("jonctions.type_traverse_semelle"), tw, ws, th, p)
    ht = min(jt["tenon_largeur"], hs - 20.0)
    sail = jt.get("saillie", g("jonctions.saillie_tenon_clavete"))
    c["tenon_traverse"] = dict(jt, hauteur_retenue=ht)
    for nx, sx in cotes_x:
        lt = ws + sail
        S.append(Solide("tenon_traverse_" + nx, "tenon_traverse", "x", (sx * (xi + lt / 2.0), 0, hs / 2.0), lt,
                        rectangle(jt["tenon_epaisseur"], ht), materiau="bois"))
        if "clef_epaisseur" in jt:
            S.append(Solide("clef_" + nx, "clef_chene", "z", (sx * (xp + ws / 2.0 + sail * 0.45), 0,
                                                             (2.0 + hs + 15.0) / 2.0), hs + 13.0,
                            rectangle(jt["clef_epaisseur"], jt["tenon_epaisseur"] + 12.0), materiau="bois"))
    zl, bh = c["z_loquet"], g("loquet.boitier_hauteur")
    dpe = g("loquet.pene_diametre")
    fh = c["frette_h"]
    z_fh = c["z_haut_plinthe"] + fh            # bague forgee au pied du fut, au-dessus du conge de plinthe
    w_fut = c["demi_largeur_fut"]
    for nx, sx in cotes_x:
        for ny, sy in cotes_y:
            suf = "%s_%s" % (ny, nx)
            S.append(bloc_pied("fourreau_" + suf, c, tp, sx, sy))
            if fh > 0:
                wf = w_fut(z_fh - fh / 2.0)
                prof_int = octogone(2 * wf) if sec == "octogonal" else rectangle(2 * wf, 2 * wf)
                prof_ext = octogone(2 * wf + 2 * fe) if sec == "octogonal" else rectangle(2 * wf + 2 * fe, 2 * wf + 2 * fe)
                S.append(Solide("frette_" + suf, "bague_forgee", "z", (sx * xp, sy * yp, z_fh - fh / 2.0), fh,
                                prof_ext, prof_int, materiau="metal"))
            wl = w_fut(zl)
            xb0, xb1 = xp + wl, xb + tb / 2.0 + fe
            S.append(Solide("bride_calage_" + suf, "bride_calage", "z", (sx * (xb0 + xb1) / 2.0, sy * yp, zl), fl,
                            rectangle(xb1 - xb0, lb + 24.0), materiau="metal"))
            xl0 = xb1
            S.append(Solide("loquet_boitier_" + suf, "loquet_boitier", "z", (sx * (xl0 + 11.0), sy * yp, zl), bh,
                            rectangle(22.0, 40.0), materiau="metal"))
            xpe0 = xp + wl - g("loquet.engagement")
            xpe1 = xl0 + 22.0
            S.append(Solide("pene_" + suf, "pene", "x", (sx * (xpe0 + xpe1) / 2.0, sy * yp, zl), xpe1 - xpe0,
                            cercle(dpe), materiau="metal"))
            _habillage(p, c, S, nx, sx, ny, sy)
            S.append(Solide("pignon_" + suf, "pignon", "y", (sx * c["x_arbre"], sy * yp, za), ld,
                            cercle(c["pignon_d_tete"]), materiau="acier"))
            yp_pal = yp + ld / 2.0 + 7.0
            xa0, xa1 = c["x_arbre"] - 16.0, xp - w_fut(za)
            S.append(Solide("palier_" + suf, "palier", "z", (sx * (xa0 + xa1) / 2.0, sy * yp_pal, za), 40.0,
                            rectangle(xa1 - xa0, 6.0), materiau="metal"))
    da = g("synchro.arbre_diametre")
    Lt = 2 * (yp + ld / 2.0 + 20.0)
    for nx, sx in cotes_x:
        S.append(Solide("arbre_transversal_" + nx, "arbre_transversal", "y", (sx * c["x_arbre"], 0, za), Lt,
                        cercle(da), materiau="acier"))
    if g("synchro.mode") == "quatre_points":
        ct = g("synchro.carter_cote")
        S.append(Solide("arbre_longitudinal", "arbre_longitudinal", "x", (0, 0, za), 2 * c["x_arbre"] - ct,
                        cercle(da), materiau="acier"))
        for nx, sx in cotes_x:
            S.append(Solide("renvoi_angle_" + nx, "renvoi_angle", "z", (sx * c["x_arbre"], 0, za), ct,
                            rectangle(ct, ct), materiau="metal"))
    return S


# ---------------------------------------------------------------------------
# Masses
# ---------------------------------------------------------------------------
#: Densite apparente du coussin (cuir + mousse latex), kg/m3.
DENSITE_COUSSIN = 300.0


def _masses(p, solides):
    dens = {"bois": BOIS[p.get("bois.essence")]["densite_kg_m3"],
            "metal": METAUX[p.get("ferrures.metal")]["densite_kg_m3"],
            "acier": METAUX["fer_forge_mat"]["densite_kg_m3"],
            "cuir": GARNISSAGE[p.get("garnissage.cuir_manilles")]["densite_kg_m3"],
            "coussin": DENSITE_COUSSIN}
    m = {"mobile": 0.0, "fixe": 0.0, "par_materiau": {}}
    sx = sy = 0.0
    for s in solides:
        kg = s.volume_mm3() * 1e-9 * dens[s.materiau]
        m["mobile" if s.mobile else "fixe"] += kg
        m["par_materiau"][s.materiau] = m["par_materiau"].get(s.materiau, 0.0) + kg
        sx += kg * s.centre[0]
        sy += kg * s.centre[1]
    m["lest"] = p.get("ancrage.lest")
    m["total"] = m["mobile"] + m["fixe"] + m["lest"]
    m["cdg_xy"] = (sx / (m["total"] or 1.0), sy / (m["total"] or 1.0))
    return m


# ---------------------------------------------------------------------------
# Jonctions
# ---------------------------------------------------------------------------
def _jonctions(p, c):
    g = p.get
    J = []
    jc = dimensionner(g("jonctions.type_coulisseau_platine"), c["coulisseau"], c["e"], c["coulisseau"], p)
    jc.update(nom_jonction="coulisseau -> platine", quantite=4,
              remarque="Mortaises des 2 coulisseaux arriere OBLONGUES en Y (+%.1f mm) : dilatation transversale "
                       "de la platine massive (%.2f mm calcules) ; tenons avant fixes." %
                       (c["jeu_mortaise_oblongue"], c["dilatation_platine"]))
    J.append(jc)
    paroi = c["paroi_plats"]
    jf = dimensionner(g("jonctions.type_fourreau_semelle"), c["cote_pied"], c["semelle_h"], c["cote_pied"], p)
    if "tenon_epaisseur" in jf:
        ep = min(jf["tenon_epaisseur"], math.floor(paroi))
        jf.update(tenon_epaisseur=ep, mortaise_epaisseur=ep + g("tolerances.jeu_mortaise"),
                  epaulement=0.0, nombre_tenons_jumeles=2)
        if "cheville_diametre" in jf:
            jf["cheville_diametre"] = min(jf["cheville_diametre"], math.floor(ep / 2.0))
    jf.update(nom_jonction="fourreau -> semelle", quantite=4,
              remarque="Pied-colonne creux : deux tenons jumeles (un par joue pleine, epaisseur = paroi) sous la "
                       "plinthe, traversant la semelle ; le coulisseau descend entre eux dans le logement.")
    J.append(jf)
    jt = dict(c["tenon_traverse"])
    jt.update(nom_jonction="traverse basse -> semelles", quantite=2,
              remarque="Tenon a clef : demontage de l'Entrave en 3 sous-ensembles sans outil.")
    J.append(jt)
    jj = dimensionner(g("jonctions.type_joues_fourreau"), paroi, paroi, None, p)
    n = 2 * max(2, int(math.ceil(c["fourreau_hauteur"] / 70.0)))
    jj.update(nom_jonction="demi-fourreaux (joues rainurees)", quantite=4, par_piece=n,
              remarque="Deux demi-colonnes rainurees collees + %d tourillons par pied ; la moulure (plinthe, "
                       "astragale, chapiteau) est usinee APRES collage pour des onglets continus." % n)
    J.append(jj)
    if c["ceinture"]:
        J.append({"type": "tenon_mortaise_borgne", "nom": "Ceinture embrevee + tourillons",
                  "nom_jonction": "ceinture -> platine", "quantite": 2,
                  "diametre": g("jonctions.tourillon_diametre"),
                  "remarque": "Ceinture embrevee de 6 mm dans une rainure de sous-face et tourillonnee ; trous "
                              "oblongs vers l'avant/arriere (dilatation de la platine). Pas de colle sur la longueur."})
    J.append({"type": "rivet_forge", "nom": "Rivets forges a tete goutte de suif et contre-plaque",
              "nom_jonction": "ferrures -> bois", "diametre": g("ferrures.rivet_diametre"), "quantite": None,
              "remarque": "Toutes les ferrures (pentures, platines de pivot, brides, paliers, equerres, capots) : "
                          "rivets traversants, tete %g x %g mm bouterollee, zero vis." %
                          (g("ferrures.tete_rivet_diametre"), g("ferrures.tete_rivet_hauteur"))})
    return J


# ---------------------------------------------------------------------------
# Verifications
# ---------------------------------------------------------------------------
def _verifications(p, c, mas, J=None):
    g = p.get
    V = []
    gr = g("charges.g")
    ess, met = BOIS[g("bois.essence")], METAUX[g("ferrures.metal")]
    acier = METAUX["fer_forge_mat"]
    cuir = GARNISSAGE[g("garnissage.cuir_manilles")]
    kd = g("charges.coef_dynamique")
    F = g("charges.traction_manille") * kd
    zF = c["z_manille_cou_max"]
    W = mas["total"] * gr
    xg, yg = mas["cdg_xy"]
    gm = g("charges.gamma_m_metal")
    # 1-2. Renversement (sans le poids de l'utilisateur, cas defavorable)
    for axe, levier, dist_ancr in (("y", c["semelle_L"] / 2.0 - abs(yg), c["semelle_L"] - 90.0),
                                   ("x", c["x_pied"] + c["semelle_l"] / 2.0 - abs(xg), 2 * c["x_pied"])):
        Ms, Mr = W * levier / 1000.0, F * zF / 1000.0
        ratio = Ms / Mr
        lest_req = max(0.0, (Mr * 1000.0 / levier) / gr - mas["total"])
        T = max(0.0, Mr - Ms) / (dist_ancr / 1000.0) / 2.0
        ancre = g("ancrage.anneaux_sol")
        if ratio >= 1.0:
            niv, det = "ok", "stable sans ancrage"
        elif ancre and T <= g("ancrage.capacite_point"):
            niv, det = "alerte", "stable UNIQUEMENT ancre : %.0f N par anneau (capacite %.0f N)" % (T, g("ancrage.capacite_point"))
        else:
            niv, det = "insuffisant", "basculement : ni le poids propre ni l'ancrage ne suffisent"
        V.append(Verification("renversement_" + axe, "Renversement (traction %g N x %.2f, direction %s, a z=%.0f mm)"
                              % (g("charges.traction_manille"), kd, axe.upper(), zF),
                              ratio, 1.0, "(Ms/Mr)", ratio >= 1.0,
                              "Ms=%.0f N.m (masse %.1f kg, levier %.0f mm) / Mr=%.0f N.m ; %s" %
                              (Ms, mas["total"], levier, Mr, det),
                              "Ancrer au sol (anneaux sous semelles) ou ajouter %.0f kg de lest bas ; elargir les "
                              "semelles aide aussi." % lest_req, niveau=niv, sens="min"))
    # 3. Glissement
    Fg = g("charges.coef_frottement_sol") * W
    niv = "ok" if Fg >= F else ("alerte" if g("ancrage.anneaux_sol") else "insuffisant")
    V.append(Verification("glissement", "Glissement au sol", F, Fg, "N", Fg >= F,
                          "frottement mu=%.2f x %.0f N" % (g("charges.coef_frottement_sol"), W),
                          "Patins antiderapants ou ancrage au sol.", niveau=niv))
    # 4-5. Flexion / fleche de la platine MOULUREE (section reelle, poutre sur 2 appuis, charge centree)
    Lx = 2 * c["x_pied"]
    P = g("charges.verticale_service") * kd
    M = P * Lx / 4.0
    sp = c["section_platine"]
    wel = min(sp["w_inf"], sp["w_sup"])
    sig = M / wel
    fmd = g("charges.kmod_bois") * ess["resistance_flexion_calcul_mpa"] / g("charges.gamma_m_bois")
    perte = 1.0 - wel / (c["W"] * c["e"] ** 2 / 6.0)
    V.append(Verification("flexion_platine", "Flexion platine moulee (%s, portee %.0f mm)" % (g("bois.essence"), Lx),
                          sig, fmd, "MPa", sig <= fmd,
                          "M=P.L/4, P=%.0f N ; module de section reel %.0f cm3 (-%.1f %% vs rectangle : chants "
                          "%s / %s)" % (P, wel / 1000.0, 100 * perte, g("entrave.platine.chant_dessus"),
                                        g("entrave.platine.chant_dessous")),
                          "Augmenter l'epaisseur de platine ou reduire la moulure de sous-face."))
    I = sp["inertie"]
    f = P * Lx ** 3 / (48.0 * ess["module_elasticite_mpa"] * I)
    flim = Lx / g("charges.fleche_limite_ratio")
    V.append(Verification("fleche_platine", "Fleche platine moulee", f, flim, "mm", f <= flim,
                          "f = P.L^3/(48.E.I), E=%.0f MPa, I reel %.3g mm4" % (ess["module_elasticite_mpa"], I),
                          "Epaisseur +5 mm."))
    # 6-9. Pene du loquet, matage, ligament, traction de la barre au droit d'un cran (section nette)
    n = int(g("loquet.loquets_porteurs_min"))
    Fp = (P + mas["mobile"] * gr) / n
    d = g("loquet.pene_diametre")
    tau = Fp / (2 * math.pi * d ** 2 / 4.0)
    tadm = met["limite_elastique_mpa"] / (math.sqrt(3) * gm)
    V.append(Verification("cisaillement_pene", "Cisaillement du pene (%d loquets porteurs, %s)" % (n, g("ferrures.metal")),
                          tau, tadm, "MPa", tau <= tadm, "F=%.0f N par pene, double cisaillement barre/gache" % Fp,
                          "Augmenter le diametre du pene."))
    tb, lb = g("cremaillere.barre_epaisseur"), g("cremaillere.barre_largeur")
    smat = Fp / (d * tb)
    madm = 2.0 * met["limite_elastique_mpa"] / gm
    V.append(Verification("matage_cran", "Matage du cran dans la barre de calage", smat, madm, "MPa", smat <= madm,
                          "sigma = F/(d.t), admissible ~2 Re/gamma", "Barre plus epaisse."))
    lig = g("cremaillere.pas") - d
    tlig = Fp / (2 * lig * tb) if lig > 0 else float("inf")
    V.append(Verification("ligament_crans", "Ligament entre deux crans", tlig, tadm, "MPa", tlig <= tadm,
                          "2 plans de cisaillement de %.1f x %.0f mm" % (lig, tb), "Augmenter le pas ou reduire le pene."))
    taux = DECORS_BARRE[g("cremaillere.decor_barre")]["taux_enlevement"]
    joue = (lb * (1.0 - taux) - d) / 2.0
    st = Fp / (2 * joue * tb) if joue > 0 else float("inf")
    sadm = met["limite_elastique_mpa"] / gm
    V.append(Verification("traction_barre_cran", "Traction de la barre au droit d'un cran (decor %s)" %
                          g("cremaillere.decor_barre"), st, sadm, "MPa", st <= sadm,
                          "2 joues nettes de %.1f mm x %.0f mm (largeur %g, -%d %% de decor)" %
                          (joue, tb, lb, round(100 * taux)), "Elargir la barre (regle minimum_section_nette)."))
    # 10. Dent de pignon (Lewis) en manoeuvre (loquets ouverts)
    z = c["pignon_dents"]
    Y = facteur_lewis(z)
    Ft = mas["mobile"] * gr * kd / 2.0
    sl = Ft / (g("cremaillere.largeur_denture") * c["module"] * Y)
    ladm = acier["limite_elastique_mpa"] / (gm * 1.5)
    V.append(Verification("dent_lewis", "Dent de pignon (Lewis, z=%d, m=%g)" % (z, c["module"]), sl, ladm, "MPa",
                          sl <= ladm, "Ft=%.0f N, Y=%.3f ; pignons/cremailleres dentees toujours en acier" % (Ft, Y),
                          "Module ou largeur de denture superieurs."))
    # 11. Torsion de l'arbre
    T = Ft * c["pignon_d_primitif"] / 2.0
    da = g("synchro.arbre_diametre")
    tt = 16 * T / (math.pi * da ** 3)
    tadm_a = acier["limite_elastique_mpa"] / (math.sqrt(3) * gm)
    V.append(Verification("torsion_arbre", "Torsion arbre de synchronisation", tt, tadm_a, "MPa", tt <= tadm_a,
                          "T=%.1f N.m" % (T / 1000.0), "Arbre plus gros."))
    # 12. Recouvrement coulisseau / fourreau en position haute + matage du bois
    rec, cc = c["recouvrement_haut"], c["coulisseau"]
    rmin = g("charges.recouvrement_ratio_mini") * cc
    ratio = rec / cc
    hm_req = (rmin + g("entrave.fourreau.jeu_haut") + c["z_dessous_platine_max"] + c["z_bas_coulisseau_min"]) / 2.0 + c["e"]
    hm_req = math.ceil(hm_req / 5.0) * 5.0
    Mleg = F / 4.0 * (zF - (c["z_haut_fourreau"] - rec / 2.0))
    Fc = Mleg / (2.0 / 3.0 * rec)
    pc = Fc / (cc * rec / 3.0)
    pc_adm = g("charges.kmod_bois") * ess["compression_perp_mpa"] / g("charges.gamma_m_bois")
    V.append(Verification("recouvrement", "Recouvrement coulisseau/fourreau en position haute", ratio,
                          g("charges.recouvrement_ratio_mini"), "x section", ratio >= g("charges.recouvrement_ratio_mini"),
                          "%.0f mm pour un coulisseau de %.0f mm (jeu %.1f mm => ballant %.2f deg) ; matage %.2f MPa "
                          "(adm. %.2f)" % (rec, cc, g("tolerances.jeu_coulisseau"),
                                           math.degrees(math.atan(2 * g("tolerances.jeu_coulisseau") / rec)), pc, pc_adm),
                          "Pieds courts + course 150 mm : passer hauteur_mini a >= %.0f mm (course %.0f mm) OU "
                          "ajouter des patins laiton reglables dans le fourreau (jeu ~0,3 mm). Les loquets engages "
                          "reprennent une partie du ballant." % (hm_req, c["hauteur_maxi"] - hm_req),
                          niveau="ok" if ratio >= g("charges.recouvrement_ratio_mini") and pc <= pc_adm else "alerte",
                          sens="min"))
    c["hauteur_mini_pour_recouvrement"] = hm_req
    # 13. Paroi diagonale des pieds (chanfrein arrete / octogone)
    pdm = g("entrave.fourreau.paroi_diagonale_min")
    V.append(Verification("paroi_diagonale", "Paroi du pied dans l'arete (%s%s)" % (
        c["section"], ", chanfrein %g" % g("entrave.pied.chanfrein_arrete") if c["section"] == "carre" else ""),
        c["paroi_diagonale"], pdm, "mm", c["paroi_diagonale"] >= pdm - 1e-9,
        "au haut du fut (section la plus fine) ; paroi sur plats %.1f mm" % c["paroi_plats"],
        "Reduire le chanfrein arrete ou augmenter entrave.pied.cote.", sens="min"))
    # 14. Montants de la ceinture ajouree (section nette)
    if c["ceinture"]:
        mm_ = g("style.montant_mini")
        V.append(Verification("montants_ceinture", "Montants de la ceinture ajouree (%s)" % g("style.motif_ajours"),
                              c["ceinture_montant"], mm_, "mm", c["ceinture_montant"] >= mm_ - 1e-9,
                              "%d baies de %.1f mm sur %.0f mm" % (int(g("entrave.ceinture.nombre_arcades")),
                                                                 c["ceinture_baie"], 2 * c["ceinture_demi_longueur"]),
                              "Moins de baies ou ratio_largeur plus faible.", sens="min"))
    # 15. Manille (traction)
    for nom, larg in (("cou", g("garnissage.largeur_manille_cou")), ("poignet", g("garnissage.largeur_manille_poignet"))):
        if cuir["ame_porteuse_n"] > 0:
            adm = cuir["ame_porteuse_n"] / g("charges.gamma_cuir")
            V.append(Verification("manille_" + nom, "Manille %s (ame porteuse)" % nom, F, adm, "N", F <= adm,
                                  "ame textile %.0f N / gamma %.1f" % (cuir["ame_porteuse_n"], g("charges.gamma_cuir")),
                                  "Ame plus large."))
        else:
            s = F / (larg * g("garnissage.epaisseur_manille"))
            adm = cuir["resistance_traction_mpa"] / g("charges.gamma_cuir")
            V.append(Verification("manille_" + nom, "Manille %s (cuir seul)" % nom, s, adm, "MPa", s <= adm,
                                  "section %.0f x %.1f mm" % (larg, g("garnissage.epaisseur_manille")),
                                  "Largeur ou ame porteuse."))
    # 16. Axe de pivot (flexion a la base, effort lateral au centre de la manille)
    dax = g("ferrures.axe_pivot_diametre")
    lev = g("entrave.manilles.hauteur_pivot") + c["manille_cou_d_ext"] / 2.0
    Mp = F * lev
    spv = 32 * Mp / (math.pi * dax ** 3)
    V.append(Verification("axe_pivot", "Axe de pivot de la manille de cou (%s)" % g("entrave.manilles.pivot_cou"),
                          spv, sadm, "MPa", spv <= sadm, "M=%.1f N.m (levier %.0f mm), d=%g mm" % (Mp / 1000.0, lev, dax),
                          "Axe plus gros ou pivot plus bas."))
    # 17. Rivets de la platine de pivot (traction par le moment)
    dr = g("ferrures.rivet_diametre")
    Tr = Mp / (0.7 * g("ferrures.platine_pivot_cote")) / 2.0
    sr = Tr / (math.pi * dr ** 2 / 4.0)
    V.append(Verification("rivets_pivot", "Rivets traversants de la platine de pivot", sr, sadm, "MPa", sr <= sadm,
                          "4 rivets, 2 tendus, %.0f N chacun" % Tr, "Rivets plus gros ou platine plus grande."))
    # 18. Gond de manille (cisaillement double de l'axe sous la traction F)
    dg = g("ferrures.gond_diametre")
    tg = F / (2 * math.pi * dg ** 2 / 4.0)
    V.append(Verification("gond", "Axe du gond de manille (double cisaillement)", tg, tadm, "MPa", tg <= tadm,
                          "F=%.0f N, d=%g mm" % (F, dg), "Gond plus gros."))
    # 19. Chevilles de la jonction fourreau/semelle (arrachement en renversement)
    jf = next((j for j in (J or []) if j.get("nom_jonction") == "fourreau -> semelle"), {})
    dch = jf.get("cheville_diametre", min(g("jonctions.cheville_diametre"), math.floor(c["paroi_plats"] / 2.0)))
    nch = 2 * int(jf.get("nombre_chevilles", 1))          # 2 tenons jumeles x n chevilles
    Fch = capacite_cheville_n(dch) / g("charges.gamma_m_bois") * nch
    Tarr = max(0.0, F * zF / (2 * c["y_pied"]) / 2.0)
    V.append(Verification("chevilles_pied", "Chevilles fourreau/semelle (arrachement, %d x d=%g mm)" % (nch, dch),
                          Tarr, Fch, "N", Tarr <= Fch,
                          "effort de soulevement par pied %.0f N, capacite %.0f N (paroi %.0f mm => cheville <= "
                          "paroi/2)" % (Tarr, Fch, c["paroi_plats"]),
                          "Chevilles plus grosses ou tenons a coins."))
    # Marges des ferrures affinees
    mmini = g("charges.marge_mini_ferrures")
    for v in V:
        if v.ident in FERRURES_AFFINEES and v.niveau == "ok" and v.marge < mmini:
            v.niveau = "alerte"
            v.recommandation = ("Marge x%.2f < x%.2f exigee pour une ferrure affinee : revenir a la section "
                                "superieure. " % (v.marge, mmini)) + v.recommandation
    fer = [v for v in V if v.ident in FERRURES_AFFINEES]
    vmin = min(fer, key=lambda v: v.marge)
    V.append(Verification("marges_ferrures", "Marge mini des ferrures affinees (%s)" % vmin.ident, vmin.marge, mmini,
                          "", vmin.marge >= mmini, "%d verifications de ferrures" % len(fer),
                          "Voir la verification %s." % vmin.ident, sens="min",
                          niveau="ok" if vmin.marge >= mmini else ("alerte" if vmin.marge >= 1.0 else "insuffisant")))
    return V


# ---------------------------------------------------------------------------
# Point d'entree pur
# ---------------------------------------------------------------------------
def parametres_derives(p, c):
    """User Parameters derives (expressions Fusion liees) : le cran pilote la hauteur."""
    pre = p.get("gamme.prefixe_fusion")
    n = lambda chemin: Parametres.nom_fusion(chemin, pre)
    return [
        (pre + "course_courante", "%s * %s" % (n("cremaillere.cran_courant"), n("cremaillere.pas")), "mm",
         "Course au cran courant = cran x pas (pilote le deplacement des corps mobiles)"),
        (pre + "hauteur_platine", "%s + %s" % (n("cremaillere.hauteur_mini"), pre + "course_courante"), "mm",
         "Hauteur du dessus de platine = hauteur_mini + cran x pas"),
        (pre + "debattement", "%s - %s" % (n("cremaillere.hauteur_maxi"), n("cremaillere.hauteur_mini")), "mm",
         "Debattement total"),
        (pre + "pignon_dents", "%d" % c["pignon_dents"], "", "Nombre de dents du pignon (calcule)"),
        (pre + "pignon_d_primitif", "%s * %s" % (n("cremaillere.module"), pre + "pignon_dents"), "mm",
         "Diametre primitif du pignon = m.z"),
        (pre + "coulisseau_section", "%g mm" % c["coulisseau"], "mm", "Section du coulisseau (calculee)"),
        (pre + "z_arbre", "%g mm" % c["z_arbre"], "mm", "Hauteur des arbres de synchronisation"),
        (pre + "pied_plinthe", "%.2f mm" % c["h_plinthe"], "mm", "Hauteur de plinthe (%s)" % p.get("style.proportions")),
        (pre + "pied_fut", "%.2f mm" % c["h_fut"], "mm", "Hauteur du fut (%s)" % p.get("style.proportions")),
        (pre + "pied_chapiteau", "%.2f mm" % c["h_chapiteau"], "mm",
         "Hauteur du chapiteau, astragale comprise (%s)" % p.get("style.proportions")),
    ]


def calculer_entrave(params=None, cran=None, strict=True):
    """Calcule la geometrie, les jonctions et les verifications de l'Entrave.

    :param params: ``Parametres`` (defaut : ``Parametres.pour_typologie('entrave')``).
    :param cran: cran a representer (defaut : ``cremaillere.cran_courant``).
    :param strict: lever ``ErreurParametres`` si la validation trouve des erreurs.
    :return: ``ResultatEntrave``.
    """
    p = params or Parametres.pour_typologie(TYPOLOGIE)
    r = ResultatEntrave()
    r.params = p
    r.problemes = p.verifier() if strict else p.valider()
    r.cran = int(p.get("cremaillere.cran_courant") if cran is None else cran)
    c = _cotes(p, r.cran)
    r.cotes = c
    r.hauteur = c["hauteur"]
    r.solides = _solides(p, c)
    noms = [s.nom for s in r.solides]
    if len(noms) != len(set(noms)):
        raise ErreurGeometrie("noms de corps en double")
    r.masses = _masses(p, r.solides)
    r.jonctions = _jonctions(p, c)
    r.verifications = _verifications(p, c, r.masses, r.jonctions)
    r.parametres_derives = parametres_derives(p, c)
    noms_pieces = {}
    for s in r.solides:
        k = (s.piece, s.materiau)
        noms_pieces[k] = noms_pieces.get(k, 0) + 1
    r.nomenclature = sorted((pc, mat, q) for (pc, mat), q in noms_pieces.items())
    r.alertes = [str(pb) for pb in r.problemes if pb.niveau == "alerte"] + \
                [v.ligne() for v in r.verifications if v.niveau != "ok"]
    return r


def rapport_texte(r):
    c, p = r.cotes, r.params
    g = p.get
    L = []
    L.append("ENTRAVE COU-POIGNETS - gamme Neogothique (v%s, style raffine)" % g("gamme.version"))
    L.append("Essence %s | cuir %s | ferrures %s (%s) | pieds %s %g mm | pivot cou %s" % (
        g("bois.essence"), g("garnissage.cuir_manilles"), g("ferrures.metal"), g("ferrures.finition"),
        c["section"], c["cote_pied"], g("entrave.manilles.pivot_cou")))
    L.append("Cran %d / %d -> hauteur platine %g mm (crans : %s)" % (r.cran, c["positions"] - 1, r.hauteur,
                                                                    ", ".join("%g" % x for x in c["hauteurs_crans"])))
    L.append("Debattement %g mm = %d intervalles x %g mm (convention '%s')" % (
        c["debattement"], c["positions"] - 1, c["pas"], g("cremaillere.convention")))
    L.append("STYLE : proportions '%s' -> pied visible %.0f mm = plinthe %.1f + fut %.1f + chapiteau %.1f mm ; "
             "colonne %g (fut bas) / %g (fut haut) / %g (plinthe, abaque) mm" % (
                 g("style.proportions"), c["fourreau_hauteur"], c["h_plinthe"], c["h_fut"], c["h_chapiteau"],
                 c["a_fut_bas"], c["a_fut_haut"], c["a_max"]))
    if c["section"] == "carre" and g("entrave.pied.chanfrein_arrete") > 0:
        L.append("       chanfreins arretes %g mm, arret %s a %g mm des extremites du fut" % (
            g("entrave.pied.chanfrein_arrete"), g("entrave.pied.type_arret"), g("entrave.pied.longueur_arret")))
    L.append("       platine : chant dessus %s %g, dessous %s %g x %g mm ; ceinture %s" % (
        g("entrave.platine.chant_dessus"), g("entrave.platine.chant_dessus_taille"),
        g("entrave.platine.chant_dessous"), g("entrave.platine.chant_dessous_hauteur"),
        g("entrave.platine.chant_dessous_profondeur"),
        ("%d baies '%s' de %.0f mm, montants %.1f mm" % (int(g("entrave.ceinture.nombre_arcades")),
                                                         g("style.motif_ajours"), c["ceinture_baie"],
                                                         c["ceinture_montant"])) if c["ceinture"] else "aucune"))
    L.append("       ferrures : fer plat %g x %g, pentures %g mm en '%s', rivets %g a tete goutte de suif %g x %g, "
             "habillage cremaillere '%s', barre '%s'" % (
                 g("ferrures.fer_plat_largeur"), g("ferrures.fer_plat_epaisseur"), g("entrave.pentures.longueur"),
                 g("ferrures.terminaison_pentures"), g("ferrures.rivet_diametre"), g("ferrures.tete_rivet_diametre"),
                 g("ferrures.tete_rivet_hauteur"), g("cremaillere.habillage"), g("cremaillere.decor_barre")))
    L.append("       sellerie : point %s, pas %g mm, fil %s %g mm, filet a %g mm, tranches %s, rembourrage %g mm ; "
             "coussin %s (matelassage %s%s)" % (
                 g("sellerie.point"), g("sellerie.pas_point"), g("sellerie.fil"), g("sellerie.fil_diametre"),
                 g("sellerie.filet_bordure"), g("sellerie.tranches"), g("sellerie.rembourrage_manille"),
                 "oui" if g("sellerie.coussin_avant") else "non", g("sellerie.matelassage_platine"),
                 (", %d cellules" % c["coussin_cellules"]) if "coussin_cellules" in c else ""))
    L.append("Coulisseau %g mm, longueur %g mm ; fourreau %g mm de haut ; recouvrement en haut %g mm" % (
        c["coulisseau"], c["coulisseau_longueur"], c["fourreau_hauteur"], c["recouvrement_haut"]))
    L.append("Synchro : module %g, pignon z=%d (d primitif %g mm), %.1f mm de course par tour (%.2f tour pour la "
             "course), arbres a z=%g mm, mode %s" % (c["module"], c["pignon_dents"], c["pignon_d_primitif"],
                                                     c["course_par_tour"], c["tours_course_totale"], c["z_arbre"],
                                                     g("synchro.mode")))
    L.append("Calage : barre %g mm (passe hors semelle), loquet sur le fut a z=%g mm, trous de crans a %s mm du bas "
             "de barre" % (c["barre_calage_longueur"], c["z_loquet"], ", ".join("%g" % t for t in c["trous_crans"])))
    L.append("Masses : mobile %.1f kg, fixe %.1f kg, lest %.1f kg, total %.1f kg" % (
        r.masses["mobile"], r.masses["fixe"], r.masses["lest"], r.masses["total"]))
    L.append("Corps : %d (%d blocs moulures, %d revolutions)" % (
        len(r.solides), sum(1 for s in r.solides if isinstance(s, BlocProfile)),
        sum(1 for s in r.solides if isinstance(s, Revolution))))
    L.append("Jonctions :")
    for j in r.jonctions:
        cotes = ", ".join("%s=%s" % (k, ("%g" % v) if isinstance(v, float) else v) for k, v in sorted(j.items())
                          if k not in ("nom", "nom_jonction", "remarque", "type", "quantite"))
        L.append("  - %s : %s (x%s) %s" % (j["nom_jonction"], j["nom"], j.get("quantite"), cotes))
        if j.get("remarque"):
            L.append("      %s" % j["remarque"])
    L.append("Verifications :")
    for v in r.verifications:
        L.append("  " + v.ligne())
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Construction Fusion
# ---------------------------------------------------------------------------
def construire_fusion(design, params=None, nom_composant="Entrave_Neogothique"):
    """Construit l'Entrave dans ``design`` (Fusion) et lie la hauteur au cran.

    1. Exporte tous les parametres numeriques + les derives (expressions liees).
    2. Construit les corps fixes et mobiles AU CRAN 0 dans deux composants.
    3. Deplace les corps mobiles de ``neo_course_courante`` (MoveFeature a
       expression) : changer ``neo_cremaillere_cran_courant`` dans Fusion met
       le modele a jour. Si la MoveFeature n'est pas disponible, les corps
       mobiles sont construits directement au cran courant (non lies).

    :return: dict (resultat, crees, mis_a_jour, corps_fixes, corps_mobiles, lie).
    """
    import adsk.core
    import adsk.fusion
    p = params or Parametres.pour_typologie(TYPOLOGIE)
    r0 = calculer_entrave(p, cran=0)
    rc = calculer_entrave(p)
    crees, maj = p.exporter_user_parameters(design, rc.parametres_derives)
    racine = design.rootComponent
    occ = racine.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = nom_composant
    occ_f = comp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ_f.component.name = "Fixe"
    occ_m = comp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ_m.component.name = "Mobile"
    cf = fo.ConstructeurFusion(occ_f.component)
    cm = fo.ConstructeurFusion(occ_m.component)
    corps_f = cf.construire_tous([s for s in r0.solides if not s.mobile])
    lie = True
    try:
        corps_m = cm.construire_tous([s for s in r0.solides if s.mobile])
        cm.deplacer_z(corps_m, p.get("gamme.prefixe_fusion") + "course_courante")
    except Exception:  # API indisponible : repli non lie
        lie = False
        for b in list(occ_m.component.bRepBodies):
            b.deleteMe()
        corps_m = cm.construire_tous([s for s in rc.solides if s.mobile])
    return {"resultat": rc, "crees": crees, "mis_a_jour": maj, "corps_fixes": corps_f,
            "corps_mobiles": corps_m, "lie": lie}


def run(context):
    """Point d'entree du script Fusion 360."""
    ui = None
    try:
        import adsk.core
        import adsk.fusion
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Ouvrir un document Fusion (espace Design) avant de lancer le script.")
            return
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        p = Parametres.pour_typologie(TYPOLOGIE)
        # Conserver le cran deja regle dans Fusion (re-execution du script)
        nom_cran = Parametres.nom_fusion("cremaillere.cran_courant", p.get("gamme.prefixe_fusion"))
        cran = fo.lire_user_parameter(design, nom_cran)
        if cran is not None:
            p.set("cremaillere.cran_courant", int(round(cran)))
        res = construire_fusion(design, p)
        r = res["resultat"]
        msg = ["Entrave construite : %d corps fixes, %d mobiles." % (len(res["corps_fixes"]), len(res["corps_mobiles"])),
               "Hauteur platine : %g mm (cran %d)." % (r.hauteur, r.cran),
               "Parametres : %d crees, %d mis a jour." % (len(res["crees"]), len(res["mis_a_jour"])),
               ("Hauteur LIEE a %s (Modifier > Changer les parametres)." % nom_cran) if res["lie"]
               else "ATTENTION : deplacement parametrique indisponible, corps mobiles figes au cran courant."]
        ins = [v.ligne() for v in r.verifications if v.niveau != "ok"]
        if ins:
            msg.append("\nPoints de vigilance :\n" + "\n".join(ins))
        ui.messageBox("\n".join(msg))
    except Exception:
        if ui:
            ui.messageBox("Echec Entrave :\n%s" % traceback.format_exc())
        else:
            raise
