# -*- coding: utf-8 -*-
import math

import pytest

from neogothique import fusion_outils as fo
from neogothique.parametres import Parametres
from neogothique.grammaires import entrave as E


def test_conversion_et_profils():
    assert fo.mm_vers_cm(25.0) == 2.5
    o = fo.octogone(100.0)
    us = [p[0] for p in o.points()]
    assert max(us) == pytest.approx(50.0)                 # sur plats
    assert o.aire() == pytest.approx(2 * (math.sqrt(2) - 1) * 100 ** 2, rel=1e-6)
    s = fo.Solide("t", "t", "z", (0, 0, 10), 20, fo.rectangle(10, 10), fo.rectangle(4, 4))
    assert s.volume_mm3() == pytest.approx((100 - 16) * 20)
    assert len(s.facettes()) == 4 + 4 + 2 * 4  # bouchons annulaires
    assert len(fo.Solide("p", "p", "z", (0, 0, 0), 5, fo.rectangle(3, 3)).facettes()) == 6
    with pytest.raises(ValueError):
        fo.Solide("t", "t", "w", (0, 0, 0), 1, fo.rectangle(1, 1))


def test_construction_fusion_mock(adsk_mock, params):
    adsk, design, app = adsk_mock
    res = E.construire_fusion(design, params)
    r = res["resultat"]
    n_fixes = len([s for s in r.solides if not s.mobile])
    assert len(res["corps_fixes"]) == n_fixes
    assert len(res["corps_mobiles"]) == len(r.solides) - n_fixes
    assert res["lie"] is True
    ups = design.userParameters.items
    assert "neo_cremaillere_cran_courant" in ups and "neo_hauteur_platine" in ups
    assert ups["neo_hauteur_platine"].expression == "neo_cremaillere_hauteur_mini + neo_course_courante"
    comp = design.rootComponent.occurrences.liste[0].component
    mobile = comp.occurrences.liste[1].component
    mv = mobile.features.moveFeatures.liste
    assert len(mv) == 1 and mv[0].translation[2].texte == "neo_course_courante"
    noms = [b.name for b in mobile.bRepBodies]
    assert "platine" in noms and "manille_cou" in noms
    # re-export : mise a jour sans doublon
    crees, maj = params.exporter_user_parameters(design, r.parametres_derives)
    assert crees == [] and len(maj) == len(ups)


def test_corps_mobiles_construits_au_cran_0(adsk_mock):
    adsk, design, app = adsk_mock
    p = Parametres.pour_typologie("entrave", {"cremaillere.cran_courant": 4}, json_utilisateur=False)
    res = E.construire_fusion(design, p)
    assert res["resultat"].hauteur == 400.0
    mobile = design.rootComponent.occurrences.liste[0].component.occurrences.liste[1].component
    # la platine (bloc moulure) est esquissee au cran 0 : dessus a 300 mm = 30 cm, dessous a 25 cm
    esq = [e for e in mobile.sketches.liste if e.name == "esq_platine_t0"][0]
    zs = [p[2] for l in esq.lignes for p in (l.a, l.b)] + [p[2] for a in esq.arcs for p in a]
    assert max(zs) == pytest.approx(30.0) and min(zs) == pytest.approx(25.0)


def test_repli_sans_move_feature(params):
    import sys
    import fake_adsk
    mods = {}
    adsk, design, app = fake_adsk.installer(mods, fake_adsk.Design(moves_disponible=False))
    anciens = {k: sys.modules.get(k) for k in mods}
    sys.modules.update(mods)
    try:
        params.set("cremaillere.cran_courant", 2)
        res = E.construire_fusion(design, params)
        assert res["lie"] is False
        mobile = design.rootComponent.occurrences.liste[0].component.occurrences.liste[1].component
        assert len(mobile.bRepBodies.liste) == len(res["corps_mobiles"])
    finally:
        for k, v in anciens.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


def test_correction_sens_plan_xz(adsk_mock):
    adsk, design, app = adsk_mock
    comp = design.rootComponent
    c = fo.ConstructeurFusion(comp)
    s = fo.Solide("arbre", "arbre", "y", (10.0, 50.0, 30.0), 40.0, fo.cercle(20.0))
    c.construire(s)  # le mock leve si un point d'esquisse sort du plan
    plan = comp.sketches.liste[0].plan
    assert plan.coordonnee() == pytest.approx(5.0)


def test_run_context(adsk_mock):
    adsk, design, app = adsk_mock
    E.run(None)
    assert app.userInterface.messages
    assert "Entrave construite" in app.userInterface.messages[-1], app.userInterface.messages[-1]
    # re-execution : le cran regle dans Fusion est conserve
    design.userParameters.items["neo_cremaillere_cran_courant"].expression = "3"
    E.run(None)
    assert "cran 3" in app.userInterface.messages[-1]


def test_lanceur_script(adsk_mock):
    import importlib.util
    import os
    chemin = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "scripts_fusion", "Entrave", "Entrave.py")
    spec = importlib.util.spec_from_file_location("Entrave_lanceur", chemin)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert os.path.isdir(os.path.join(mod._chemin_paquet(), "neogothique"))
    mod.run(None)
    assert "Entrave construite" in adsk_mock[2].userInterface.messages[-1]


@pytest.mark.parametrize("angle", [45.0, 135.0, 30.0])
def test_plan_vertical_incline_corrige(adsk_mock, angle):
    adsk, design, app = adsk_mock
    c = fo.ConstructeurFusion(design.rootComponent)
    plan = c.plan_vertical(angle, 120.0, -40.0)
    a = math.radians(angle)
    assert abs(plan.n[0] * math.cos(a) + plan.n[1] * math.sin(a)) < 1e-9      # contient la direction
    assert plan.n[2] == 0.0
    assert plan.distance((12.0, -4.0, 7.0)) == pytest.approx(0.0, abs=1e-9)   # passe par le centre (cm)
    assert c.plan_vertical(angle, 120.0, -40.0) is plan                         # cache


def _toutes_features(comp):
    ex, rv = list(comp.features.extrudeFeatures.liste), list(comp.features.revolveFeatures.liste)
    for occ in comp.occurrences.liste:
        e2, r2 = _toutes_features(occ.component)
        ex += e2
        rv += r2
    return ex, rv


def test_blocs_par_intersections_et_enlevements(adsk_mock, params):
    adsk, design, app = adsk_mock
    res = E.construire_fusion(design, params)
    r = res["resultat"]
    ex, rv = _toutes_features(design.rootComponent)
    blocs = [s for s in r.solides if isinstance(s, fo.BlocProfile)]
    n_inter = sum(len(b.directions) - 1 for b in blocs)
    assert sum(1 for f in ex if f.entree.op == "Intersect") == n_inter
    assert len(rv) == sum(1 for s in r.solides if isinstance(s, fo.Revolution))
    cuts = [f for f in ex if f.entree.op == "Cut"]
    assert cuts and all(f.entree.participantBodies for f in cuts)
    # les ceintures sont ajourees par un enlevement multi-boucles (1 profil a 5 trous)
    assert any(len(getattr(f.entree.profil, "boucles", [])) >= 5 or getattr(f.entree.profil, "n", 0) >= 5
               for f in cuts) or len(cuts) >= 2
    assert len(res["corps_fixes"]) + len(res["corps_mobiles"]) == len(r.solides)


@pytest.mark.parametrize("ov", [
    {"entrave.pied.section": "octogonal", "entrave.pied.cote": 110.0},
    {"entrave.pied.type_arret": "langue_de_boeuf", "style.proportions": "harmonique"},
    {"ferrures.terminaison_pentures": "trilobe", "style.motif_ajours": "trilobe",
     "cremaillere.habillage": "plaque_decoupee", "sellerie.matelassage_platine": "capitonne"},
    {"ferrures.terminaison_pentures": "queue_d_aronde", "style.motif_ajours": "quadrilobe",
     "cremaillere.habillage": "aucun", "cremaillere.decor_barre": "festonnee", "cremaillere.barre_largeur": 30.0},
    {"cremaillere.decor_barre": "ajouree", "cremaillere.barre_largeur": 35.0, "cremaillere.barre_epaisseur": 10.0,
     "entrave.ceinture.active": False, "sellerie.coussin_avant": False},
    {"entrave.platine.chant_dessous": "cavet", "entrave.platine.chant_dessus": "chanfrein",
     "entrave.semelle.chant": "droit", "cremaillere.cran_courant": 6},
])
def test_variantes_construites_dans_le_mock(adsk_mock, ov):
    adsk, design, app = adsk_mock
    p = Parametres.pour_typologie("entrave", ov, json_utilisateur=False)
    assert not p.erreurs(), p.erreurs()
    res = E.construire_fusion(design, p)
    assert len(res["corps_fixes"]) + len(res["corps_mobiles"]) == len(res["resultat"].solides)
