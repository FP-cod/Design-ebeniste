# -*- coding: utf-8 -*-
import pytest

from equinox.grammaires import ancrages, banc_flore, chaise_trone, croix_saint_andre, tabouret
from equinox.parametres import Parametres


def _verif(plan, nom):
    return [v for v in plan.verifications if v.nom == nom][0]


@pytest.fixture(scope="module")
def flore():
    return banc_flore.concevoir()


def test_banc_flore_composants(flore):
    noms = {c.nom for c in flore.composants}
    for attendu in ("plateau", "ceinture", "pied_AR_G", "pied_AV_D", "capuchon_AR_G", "traverse_arriere", "helice_G",
                    "helice_D", "repose_genou_G", "branche_coude_D", "repose_coude_G", "oeillet_bas_AR_G",
                    "oeillet_bas_AR_D", "anneau_arriere"):
        assert attendu in noms, attendu
    assert 15 < flore.masse_structure() < 60


def test_banc_flore_vocabulaire_respecte(flore):
    p = flore.params
    pl = flore.composant("plateau").primitives[1]
    xs = [x for x, _ in pl.contour]
    assert abs(max(xs) - min(xs) - 1150) < 1
    assert pl.angle_y == 2.0 and pl.epaisseur == 30.0
    h = flore.composant("helice_G").primitives[0]
    assert h.diametre == 12.0
    pied = flore.composant("pied_AR_G").primitives
    assert pied[0].d0 == 50.0 and pied[-1].d1 == 30.0
    # sommet du garnissage a 700 mm au point haut (bassin)
    assert abs(max(z for _, _, z in pl.points_3d(True)) - 700.0) < 1.0
    assert p.get("inox.crans_verrouillage") == 2
    piv = [j for j in flore.jonctions if j.nom == "pivot_helice_G"][0]
    assert piv.details["crans"] == 2


def test_banc_flore_orientation_levrette(flore):
    """Genoux a l'arriere (X faible, bas), coudes a l'avant (X fort, plus haut que les genoux)."""
    g, c = flore.repere["genou_G"], flore.repere["coude_G"]
    assert g[0] < 300 and c[0] > 900 and c[2] > g[2]
    # helice : part du pied ARRIERE et avance vers l'avant
    pts = flore.repere["helice_G"]
    pied_ar = flore.repere["pieds"]["AR_G"]["noeud"]
    assert abs(pts[0][0] - pied_ar[0]) < 80
    assert pts[-1][0] > pts[0][0]


def test_banc_flore_helices_symetriques(flore):
    for (xg, yg, zg), (xd, yd, zd) in zip(flore.repere["helice_G"], flore.repere["helice_D"]):
        assert abs(xg - xd) < 1e-6 and abs(yg + yd) < 1e-6 and abs(zg - zd) < 1e-6


def test_banc_flore_signale_lest_et_helice(flore):
    assert _verif(flore, "lest_integrable").niveau == "echec"
    assert "LEST INSUFFISANT" in _verif(flore, "lest_integrable").detail
    assert _verif(flore, "helice_torsion").niveau == "echec"
    assert any("Helice" in n for n in flore.notes)
    assert _verif(flore, "interference_helice_G").niveau == "ok"
    for nom in ("renversement_poussee_vers_avant", "renversement_lateral_G", "pied_flexion_noeud", "longerons",
                "courbure_pieds", "courbure_branche_G"):
        assert _verif(flore, nom).niveau == "ok", nom


def test_banc_flore_jonctions_nommees(flore):
    types = {j.type for j in flore.jonctions}
    assert {"tenon_mortaise", "tourillons", "taraudage", "pivot_crans", "tenon_barillet"} <= types


def test_banc_flore_bassin_epaules_et_tissu():
    plan = banc_flore.concevoir(overrides={"dimensions.mode_longueur": "bassin_epaules",
                                           "garnissage.materiau": "tissu_krypton", "garnissage.couleur": "noir"})
    xs = [x for x, _ in plan.composant("plateau").primitives[1].contour]
    assert abs(max(xs) - min(xs) - 680) < 1
    assert any("raccourci" in n for n in plan.notes)
    assert plan.params.get("garnissage.epaisseur_rembourrage") == 40.0
    assert plan.params.get("garnissage.methode_fixation") == "agrafage_ou_scratch"


def test_banc_flore_parametres_invalides():
    with pytest.raises(ValueError):
        banc_flore.concevoir(overrides={"bois.section_extremite": 80.0})


def test_ancrages_reutilisables():
    p = Parametres()
    comps, jonc, verifs = ancrages.oeillets_sous_semelles(p, [("X", (0, 0), (-1, 0))])
    assert len(comps) == 1 and comps[0].primitives[2].diametre == 8.0 and comps[0].primitives[0].epaisseur == 2.0
    assert verifs[0].niveau == "ok"
    comps, jonc, verifs = ancrages.anneau_traverse(p, (0, 0, 130), (-1, 0, 0))
    assert comps[0].nom == "anneau_arriere" and jonc[0].type == "taraudage"
    p.set("ancrage.oeillets_bas", False)
    assert ancrages.oeillets_sous_semelles(p, [("X", (0, 0), (-1, 0))]) == ([], [], [])


def test_croix_avec_et_sans_plateforme():
    plan = croix_saint_andre.concevoir()
    assert _verif(plan, "renversement_traction_vers_avant").niveau == "ok"
    assert len([c for c in plan.composants if c.nom.startswith("anneau_")]) == 6
    sans = croix_saint_andre.concevoir(overrides={"croix.profondeur_plateforme": 0.0})
    assert _verif(sans, "renversement_traction_vers_avant").niveau == "echec"


def test_tabouret_et_chaise():
    t = tabouret.concevoir()
    assert t.params.get("dimensions.hauteur_assise") == 440.0
    assert _verif(t, "cg_dans_polygone").niveau == "ok"
    c = chaise_trone.concevoir()
    assert len([x for x in c.composants if x.nom.startswith("nervure_")]) == 5
    assert _verif(c, "cg_dans_polygone").niveau == "ok"
