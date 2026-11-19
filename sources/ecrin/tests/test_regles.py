# -*- coding: utf-8 -*-
"""Regles de coherence (couche 2) : charges, porte-a-faux, ports, discretion."""
import math

import pytest

from rangement import regles as R
from rangement.parametres import Parametres


def _p(typo="armoire_accessoires", **ov):
    return Parametres.pour_typologie(typo, {k.replace("__", "."): v for k, v in ov.items()}, json_utilisateur=False)


def _niv(verifs, nom):
    return {v.nom: v.niveau for v in verifs}[nom]


def test_module_flexion_rond_plein_et_tube():
    assert R.module_flexion_rond(20) == pytest.approx(math.pi * 20 ** 3 / 32)
    assert R.module_flexion_rond(20, 1.5) < R.module_flexion_rond(20)
    assert R.inertie_rond(20, 1.5) == pytest.approx(math.pi * (20 ** 4 - 17 ** 4) / 64)


def test_crochet_defaut_et_surcharge():
    assert _niv(R.verifier_crochet(_p()), "crochet_flexion") == "ok"
    assert _niv(R.verifier_crochet(_p(charges__charge_crochet=30.0)), "crochet_flexion") == "echec"
    # l'effort accidentel n'est qu'une alerte : un ratelier n'est pas un point d'ancrage
    assert _niv(R.verifier_crochet(_p()), "crochet_accidentel") == "alerte"


def test_barre_portee_et_fleche():
    p = _p()
    assert R.portee_barre(p) == pytest.approx(600 - 2 * (20 + 22))
    v = R.verifier_barre(p, R.portee_barre(p))
    assert _niv(v, "barre_flexion") == "ok" and _niv(v, "barre_fleche") == "ok"
    v = R.verifier_barre(_p(systemes__barre="rond_bois_30", charges__charge_lineaire_barre=60.0), 2000.0)
    assert "echec" in {x.niveau for x in v}


def test_etagere_porte_a_faux():
    p = _p()
    assert all(v.niveau == "ok" for v in R.verifier_etagere(p, 564, 420))
    v = R.verifier_etagere(p, 564, 420, porte_a_faux=200.0)
    assert _niv(v, "etagere_porte_a_faux_ratio") == "echec"          # 200/564 > 0,25
    v = R.verifier_etagere(p, 564, 420, porte_a_faux=100.0)
    assert _niv(v, "etagere_porte_a_faux_ratio") == "ok"
    assert _niv(R.verifier_etagere(_p(charges__charge_etagere=400.0), 1200, 420, epaisseur=15.0),
                "etagere_fleche") == "echec"


def test_profondeur_mini_npt():
    p = _p()
    assert R.profondeur_min_npt(p) == pytest.approx(25.006 + 6.0)
    assert R.profondeur_min_npt(p, "port_cache_affleurant") == pytest.approx(25.006 + 6.0 + 10.0)
    assert R.diametre_douille_npt(p) == pytest.approx(33.401 + 8.0)
    assert R.largeur_min_plot(p) == pytest.approx(41.401 + 24.0)
    v = R.verifier_port_npt(p, 30.0, 70.0)
    assert _niv(v, "port_profondeur_npt") == "echec" and _niv(v, "port_largeur_plot") == "ok"
    assert _niv(R.verifier_port_npt(p, 40.0, 60.0), "port_largeur_plot") == "echec"


def test_npt_dans_panneau_signale_sauf_port_filete():
    noms = {v.nom for v in R.verifier_discretion_materiaux(_p())}
    assert "npt_dans_panneau" in noms                       # 22 mm < 31 mm : plots obligatoires
    noms = {v.nom for v in R.verifier_discretion_materiaux(_p(systemes__port="port_vac_u_lock_m8",
                                                              ports__montage_arriere="filete_machine"))}
    assert "npt_dans_panneau" not in noms


def test_port_filete_m8():
    p = _p(systemes__port="port_vac_u_lock_m8", ports__montage_arriere="filete_machine")
    assert all(v.niveau == "ok" for v in R.verifier_port_filete(p, 22.0))
    assert _niv(R.verifier_port_filete(p, 15.0), "port_insert_dans_panneau") == "echec"
    q = _p(ports__filetage_ergot="M10x1.5")
    assert _niv(R.verifier_port_filete(q, 22.0), "port_filetage_insert") == "echec"


def test_montage_port_coherent():
    assert _niv(R.verifier_montage_port(_p()), "port_montage") == "ok"
    assert _niv(R.verifier_montage_port(_p(systemes__port="port_vac_u_lock_m8")), "port_montage") == "alerte"


def test_pas_ports_regle_aboutissants():
    p = _p()
    assert _niv(R.verifier_pas_ports(p, pas=60.0), "ports_pas_vs_ergot") == "alerte"   # < 76,2 mm
    assert _niv(R.verifier_pas_ports(p, pas=200.0, largeur_plot=70.0), "ports_chevauchement") == "ok"
    assert _niv(R.verifier_pas_ports(p, pas=70.0, largeur_plot=70.0), "ports_chevauchement") == "echec"


def test_support_mural_todo_tant_que_mur_inconnu():
    assert R.verifier_support_mural(_p(), 30.0, 80.0, 800.0)[0].niveau == "todo"
    p = _p(pose__capacite_support_mur=2000.0)
    assert R.verifier_support_mural(p, 30.0, 80.0, 800.0)[0].niveau == "ok"
    assert R.verifier_support_mural(p, 300.0, 80.0, 800.0)[0].niveau == "echec"


def test_serrure_rfid_lecture_et_lamage():
    p = _p("armoire_verrouillable")
    v = R.verifier_porte_serrure(p)
    assert _niv(v, "serrure_lecture") == "ok" and _niv(v, "serrure_secours") == "alerte"
    p.set("panneaux.lamage_lecteur", 0.0)
    assert _niv(R.verifier_porte_serrure(p), "serrure_lecture") == "echec"
    p.set("panneaux.lamage_lecteur", 14.0)
    assert _niv(R.verifier_porte_serrure(p), "serrure_lamage_discretion") == "alerte"


def test_tiroir_et_stabilite():
    assert _niv(R.verifier_tiroir(_p()), "tiroir_glissiere") == "ok"
    assert _niv(R.verifier_tiroir(_p(modules__profondeur_armoire=200.0)), "tiroir_glissiere") == "echec"
    assert _niv(R.verifier_stabilite_armoire(_p(pose__anti_basculement=False)), "armoire_anti_basculement") == "echec"


def test_discretion_invisible_et_tanins():
    p = _p("armoire_verrouillable", discretion__cuir_visible_ferme=True)
    assert _niv(R.verifier_discretion_materiaux(p), "discretion_cuir") == "echec"
    p = _p(systemes__barre="rond_fer_forge_20")
    assert _niv(R.verifier_discretion_materiaux(p), "tanins_fer") == "alerte"
    p = _p(bois__essence="erable_sycomore")
    assert _niv(R.verifier_discretion_materiaux(p), "essence_sigma") == "alerte"


def test_coherence_sans_echec_aux_defauts():
    for typo in ("ratelier_mural", "armoire_accessoires", "coffre", "support_exposition", "armoire_verrouillable"):
        assert not [v for v in R.verifier_coherence(_p(typo)) if v.niveau == "echec"], typo


def test_recalcul_derives():
    p = _p(bois__essence="noyer_noir")
    p.set("panneaux.epaisseur_caisson", 30.0)
    R.recalculer_derives(p)
    assert p.get("jonctions.diametre_tourillon") <= 15.0
    assert p.get("jonctions.longueur_tourillon") == pytest.approx(5 * p.get("jonctions.diametre_tourillon"))
