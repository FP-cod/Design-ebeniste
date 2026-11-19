# -*- coding: utf-8 -*-
"""Style v0.2 « raffine » : proportions, colonnes, moulures, ajours, ferrures fines, sellerie."""
import math

import pytest

from neogothique.parametres import Parametres, ErreurParametres
from neogothique.grammaires import entrave as E
from neogothique import profils as pf
from neogothique import regles
from neogothique.fusion_outils import BlocProfile, Revolution


def params(**ov):
    return Parametres.pour_typologie("entrave", {k.replace("__", "."): v for k, v in ov.items()},
                                     json_utilisateur=False)


def calc(**ov):
    return E.calculer_entrave(params(**ov))


@pytest.mark.parametrize("mode,parts", [("nombre_or", (1 / pf.PHI ** 4, 1 / pf.PHI, 1 / pf.PHI ** 3)),
                                        ("harmonique", (1 / 8.0, 5 / 8.0, 2 / 8.0))])
def test_partition_du_pied(mode, parts):
    p = params(style__proportions=mode)
    h = E.partition_pied(p, 186.0)
    assert sum(h) == pytest.approx(186.0)
    for a, b in zip(h, parts):
        assert a == pytest.approx(186.0 * b)


def test_nombre_or_identite():
    phi = pf.PHI
    assert 1 / phi + 1 / phi ** 3 + 1 / phi ** 4 == pytest.approx(1.0)
    p = params()
    assert p.get("entrave.semelle.hauteur") == pytest.approx(p.get("entrave.semelle.largeur") / phi ** 2, abs=1.0)
    assert p.get("entrave.semelle.longueur") == pytest.approx(p.get("entrave.platine.largeur") * math.sqrt(2), abs=1.0)


def test_colonne_plinthe_fut_chapiteau():
    r = calc()
    c = r.cotes
    pied = r.solide("fourreau_AV_D")
    assert isinstance(pied, BlocProfile) and len(pied.directions) == 4      # 2 faces + 2 aretes chanfreinees
    w = lambda z: (max(p[0] for p in pied.section_a(z)) - min(p[0] for p in pied.section_a(z))) / 2.0
    zs = c["semelle_h"]
    assert w(zs + 2) == pytest.approx(c["a_max"] / 2.0)                     # plinthe
    assert w(c["z_haut_fourreau"] - 5) == pytest.approx(c["a_max"] / 2.0)   # abaque
    z_haut_fut = c["z_bas_chapiteau"] - 0.5
    z_bas_fut = c["z_haut_plinthe"] + 0.5
    assert w(z_haut_fut) < w(z_bas_fut) < c["a_max"] / 2.0                  # fut fusele, plus fin que la base
    assert w(z_haut_fut) == pytest.approx(c["a_fut_haut"] / 2.0, abs=0.2)
    # chanfrein arrete : 8 sommets au milieu du fut, 4 dans la zone d'arret et dans le chapiteau
    zm = (c["traces_pied"]["z_arret_haut"] + c["traces_pied"]["z_arret_bas"]) / 2.0
    assert len(pied.section_a(zm)) == 8
    assert len(pied.section_a(c["traces_pied"]["z_arret_haut"] + 3.0)) == 4
    assert len(pied.section_a(c["z_haut_fourreau"] - 2.0)) >= 4
    # astragale : boudin en saillie sur le haut du fut
    assert w(c["z_bas_chapiteau"] + 3.0) > w(z_haut_fut) + 2.0


def test_arret_langue_de_boeuf_et_sans_chanfrein():
    r = calc(entrave__pied__type_arret="langue_de_boeuf")
    diag = r.cotes["traces_pied"]["diag"]
    assert sum(1 for s in diag if s[0] == "A") == 2
    r0 = calc(entrave__pied__chanfrein_arrete=0.0)
    assert len(r0.solide("fourreau_AV_D").directions) == 2
    assert r0.cotes["paroi_diagonale"] > r.cotes["paroi_diagonale"]


def test_paroi_diagonale_pilote_le_coulisseau():
    r = calc(entrave__pied__chanfrein_arrete=20.0)
    mini = r.params.get("entrave.fourreau.paroi_diagonale_min")
    assert mini <= r.cotes["paroi_diagonale"] < mini + 1.5        # coulisseau arrondi au mm
    assert r.cotes["coulisseau"] < calc().cotes["coulisseau"]


def test_chapiteau_trop_bas():
    with pytest.raises(E.ErreurGeometrie):
        calc(entrave__pied__rayon_cavet=20.0, entrave__pied__part_abaque=0.6)


def test_platine_moulee_flexion_recalculee():
    r = calc()
    v = r.verification("flexion_platine")
    assert "module de section reel" in v.detail and v.ok
    r_droit = calc(entrave__platine__chant_dessous="droit", entrave__platine__chant_dessus="droit")
    assert r_droit.verification("flexion_platine").valeur < v.valeur
    pl = r.solide("platine")
    bb = pl.boite_englobante()
    assert bb[1][0] - bb[0][0] == pytest.approx(800.0) and bb[1][2] == pytest.approx(300.0)


def test_validation_moulure_et_rivet():
    with pytest.raises(ErreurParametres):
        calc(entrave__platine__chant_dessous_profondeur=26.0)       # > retrait_bord - 5
    with pytest.raises(ErreurParametres):
        calc(ferrures__tete_rivet_diametre=7.0)                     # < 1,5 x 5
    with pytest.raises(ErreurParametres):
        calc(entrave__platine__chant_dessous_hauteur=42.0)          # chants > e - 6


@pytest.mark.parametrize("motif", ["ogive", "trilobe", "quadrilobe"])
def test_ceinture_ajouree(motif):
    r = calc(style__motif_ajours=motif)
    cein = r.solide("ceinture_AV")
    assert cein.mobile and cein.ajours and len(cein.ajours[1]) == 5
    assert cein.volume_mm3() < 2 * r.cotes["ceinture_demi_longueur"] * 80 * 20
    assert r.verification("montants_ceinture").ok
    # la ceinture s'arrete avant les chapiteaux
    bb = cein.boite_englobante()
    assert bb[1][0] < r.cotes["x_pied"] - r.cotes["a_max"] / 2.0


def test_montants_trop_fins_signales():
    r = calc(entrave__ceinture__nombre_arcades=9, entrave__ceinture__ratio_largeur=0.8)
    assert r.verification("montants_ceinture").niveau == "insuffisant"


def test_sans_ceinture():
    r = calc(entrave__ceinture__active=False)
    assert not any(s.piece == "ceinture_ajouree" for s in r.solides)
    assert r.solide("barre_queue_D").boite_englobante()[1][1] == pytest.approx(170.0)


@pytest.mark.parametrize("term", ["fleur_de_lys", "queue_d_aronde", "trilobe", "droite"])
def test_pentures_terminaisons(term):
    r = calc(ferrures__terminaison_pentures=term)
    pen = r.solide("penture_x_AV_D")
    assert pen.ext.type == "chemin"
    bb = pen.boite_englobante()
    assert bb[1][0] <= 400.0 and bb[0][1] >= -200.0                         # dans la platine
    rivets = [s for s in r.solides if s.piece == "tete_rivet_goutte_de_suif"]
    assert len(rivets) == 4 * 7 + 3 * 4 and all(isinstance(s, Revolution) for s in rivets)


def test_penture_trop_courte():
    with pytest.raises(E.ErreurGeometrie):
        calc(entrave__pentures__longueur=90.0)


def test_barre_crantee_trous_et_decor():
    r = calc()
    bar = r.solide("cremaillere_calage_AV_D")
    assert len(bar.trous) == r.cotes["positions"]
    p = params(cremaillere__decor_barre="festonnee")
    assert any(pb.chemin == "cremaillere.barre_largeur" for pb in p.erreurs())   # section nette insuffisante
    q, aj = regles.changer_materiau(params(), "cremaillere.decor_barre", "festonnee")
    assert q.get("cremaillere.barre_largeur") == 30.0 and not q.erreurs()
    rq = E.calculer_entrave(q)
    assert any(s[0] == "A" for s in rq.solide("cremaillere_calage_AV_D").ext.donnees)   # festons
    assert rq.verification("traction_barre_cran").ok
    q2, _ = regles.changer_materiau(params(), "cremaillere.decor_barre", "ajouree")
    assert q2.get("cremaillere.barre_largeur") == math.ceil(24 / 0.7) and q2.get("cremaillere.barre_epaisseur") == 10
    assert len(E.calculer_entrave(q2).solide("cremaillere_calage_AV_D").trous) > r.cotes["positions"]


def test_section_nette_suit_le_pene():
    p = params(cremaillere__decor_barre="festonnee", cremaillere__barre_largeur=30.0)
    q, aj = regles.changer_materiau(p, "ferrures.metal", "laiton_mat")
    assert q.get("cremaillere.barre_largeur") * 0.8 >= q.get("loquet.pene_diametre") + 12.0 - 1e-9
    assert not q.erreurs()


@pytest.mark.parametrize("hab,motif_lobes", [("capot_ajoure", False), ("plaque_decoupee", True)])
def test_habillage_cremaillere(hab, motif_lobes):
    r = calc(cremaillere__habillage=hab)
    cap = r.solide("capot_cremaillere_AV_D")
    assert cap.trous and not cap.mobile
    assert all(s[0] == "A" for s in cap.trous[0].donnees) == motif_lobes
    assert not any(s.piece == "capot_cremaillere" for s in calc(cremaillere__habillage="aucun").solides)


def test_loquet_sur_le_fut():
    r = calc()
    c = r.cotes
    assert c["z_haut_plinthe"] + c["frette_h"] < c["z_loquet"] < c["z_bas_chapiteau"]
    bar = r.solide("cremaillere_calage_AV_D").boite_englobante()
    sem = r.solide("semelle_D").boite_englobante()
    assert bar[0][0] > sem[1][0]                  # la barre passe a l'exterieur de la semelle


@pytest.mark.parametrize("cran", [0, 6])
def test_pas_de_collision_ceinture_mecanique(cran):
    r = calc(cremaillere__cran_courant=cran)
    cein = r.solide("ceinture_AV").boite_englobante()
    for nom in ("arbre_transversal_D", "pignon_AV_D", "renvoi_angle_D"):
        b = r.solide(nom).boite_englobante()
        recouvre = all(b[0][i] < cein[1][i] and cein[0][i] < b[1][i] for i in range(3))
        assert not recouvre, nom


@pytest.mark.parametrize("mode", ["aucun", "losange", "capitonne"])
def test_coussin_matelasse(mode):
    r = calc(sellerie__matelassage_platine=mode)
    cells = [s for s in r.solides if s.piece in ("coussin_cuir", "coussin_cellule_cuir")]
    boutons = [s for s in r.solides if s.piece == "bouton_capiton"]
    if mode == "aucun":
        assert len(cells) == 1 and not boutons
    else:
        assert len(cells) > 20
        x0, x1, y0, y1 = r.cotes["coussin"]
        aire = sum(c._aire_z(r.hauteur + 7.0) for c in cells)
        assert aire == pytest.approx((x1 - x0) * (y1 - y0), rel=0.06)    # les cellules pavent le coussin
        assert (len(boutons) > 0) == (mode == "capitonne")
    assert not any(s.piece.startswith("coussin") for s in calc(sellerie__coussin_avant=False).solides)


def test_sellerie_suit_le_cuir():
    p = params()
    q, aj = regles.changer_materiau(p, "garnissage.cuir_manilles", "cuir_harnais_noir")
    assert q.get("sellerie.pas_point") == 4.0 and q.get("sellerie.rembourrage_manille") == 0.0
    q2, _ = regles.changer_materiau(p, "garnissage.cuir_manilles", "cuir_synthetique_pu_noir")
    assert q2.get("sellerie.point") == "piqure_machine"
    q3, _ = regles.changer_materiau(q, "garnissage.cuir_manilles", "cuir_sellier_fin_noir")
    assert q3.get("sellerie.pas_point") == 3.2 and q3.get("garnissage.epaisseur_manille") == 7.5


def test_terminaison_impose_longueur():
    p = params(entrave__pentures__longueur=135.0, ferrures__terminaison_pentures="queue_d_aronde")
    q, aj = regles.changer_materiau(p, "ferrures.terminaison_pentures", "fleur_de_lys")
    assert q.get("entrave.pentures.longueur") == 150.0


def test_marges_ferrures_affinees():
    r = calc()
    v = r.verification("marges_ferrures")
    assert v.ok and v.valeur >= r.params.get("charges.marge_mini_ferrures")
    r16 = calc(ferrures__axe_pivot_diametre=16.0)        # ancien axe : passe, mais marge x1,13
    a = r16.verification("axe_pivot")
    assert a.ok and a.niveau == "alerte" and "Marge" in a.recommandation
    assert r16.verification("marges_ferrures").niveau == "alerte"


def test_finitions_renommees():
    from neogothique.catalogues import FINITIONS
    assert FINITIONS["cire_noire"]["nom"].lower().startswith("fer forge cire noir")
    assert FINITIONS["huile_brunie"]["nom"].lower().startswith("bruni")
    assert FINITIONS["laiton_patine_vieilli"]["nom"].lower().startswith("laiton vieilli")


def test_masse_et_volumes_coherents():
    r = calc()
    assert 30 < r.masses["total"] < 60
    for s in r.solides:
        assert s.volume_mm3() > 0, s.nom
