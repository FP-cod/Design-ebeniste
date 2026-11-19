# -*- coding: utf-8 -*-
"""Tests hors Fusion du port Vac-U-Lock, des cales, des filetages et de la machine."""

import math
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

import interfaces.port_vac_u_lock as vul
from interfaces.port_vac_u_lock import calculer_port, adaptateur_ancrage, profil_enveloppe
from catalogues.vac_u_lock import (
    rapport_arrachement, compatible_ergot, compatible_cale,
    FILETAGES_COTE_MACHINE, filetage_cote_machine,
)
from common.params_globaux import Parametres, jeu_radial_variantes, diametre_tete_actif
import mouvement.sex_machine_mecanique as sm


ATTENDUS_FILETAGES = (
    "M6x1", "M8x1", "M8x1.25", "M10x1", "M10x1.5", "M12x1.75", "M16x2",
    "3/8-16 UNC", "3/4-10 UNC", "5/16-18 UNC", "1/4-20 UNC", "G1/8",
)


def test_module_sans_import_adsk():
    src = Path(vul.__file__).read_text(encoding="utf-8")
    tete, _, _ = src.partition("def construire_fusion")
    for ligne in tete.splitlines():
        s = ligne.strip()
        if s.startswith("import adsk") or s.startswith("from adsk"):
            raise AssertionError("import adsk au niveau module : %s" % ligne)


def test_cotes_et_variantes_tete():
    p = Parametres()
    assert p.get("vac_u_lock.plug_longueur") == 76.2
    assert p.get("vac_u_lock.plug_diametre_tete_brevet") == 31.75
    assert p.get("vac_u_lock.plug_diametre_tete_boutique") == 27.94
    assert p.get("vac_u_lock.plug_diametre_tete_source_alternative") == 27.94
    assert p.get("vac_u_lock.plug_diametre_tige_max") == 19.05
    assert p.get("vac_u_lock.variante_tete") == "brevet"
    assert p.get("vac_u_lock.plug_diametre_tete_max") == 31.75
    assert diametre_tete_actif(p) == 31.75
    p.set("vac_u_lock.variante_tete", "boutique")
    assert p.get("vac_u_lock.plug_diametre_tete_max") == 27.94
    assert diametre_tete_actif(p) == 27.94
    assert jeu_radial_variantes(p) == pytest.approx((31.75 - 27.94) / 2.0)
    # Les deux variantes restent accessibles ; on ne tranche pas.
    assert p.get("vac_u_lock.plug_diametre_tete_brevet") == 31.75


def test_todos_etoile_cone_milieu():
    p = Parametres()
    for chemin in (
        "vac_u_lock.plug_diametre_milieu_max",
        "vac_u_lock.plug_longueur_tete",
        "vac_u_lock.plug_longueur_milieu",
        "vac_u_lock.plug_longueur_tige",
        "vac_u_lock.conicite_angle_deg",
        "vac_u_lock.cavite_interference",
        "vac_u_lock.collerette_epaisseur",
    ):
        assert p.get(chemin) is None, chemin
        assert p.meta(chemin).statut == "todo"
        assert p.meta(chemin).justification
    forme = p.meta("vac_u_lock.forme").justification.lower()
    assert "étoil" in forme or "etoil" in forme


def test_cales_parametrees():
    p = Parametres()
    assert p.get("vac_u_lock.cales_epaisseurs") == [0.25, 0.5, 1.0, 2.0]
    assert p.get("vac_u_lock.cales_materiau") == "inox_316"
    assert p.get("vac_u_lock.cales_actives") is True
    assert compatible_cale("inox_316")
    assert compatible_cale("pp_homopolymere")
    assert compatible_cale("pehd")
    assert not compatible_cale("cuir")
    p.set("vac_u_lock.cales_materiau", "bois")
    erreurs = [x for x in p.valider() if x.niveau == "erreur" and "cales_materiau" in x.chemin]
    assert erreurs
    p.set("vac_u_lock.cales_materiau", "pehd")
    res = calculer_port(p)
    noms = {s["nom"] for s in res["solides"]}
    assert "vul_cales_ajustement" in noms
    cale = next(s for s in res["solides"] if s["nom"] == "vul_cales_ajustement")
    assert cale["materiau"] == "pehd"
    assert res["cales"]["jeu_radial_variantes_mm"] == pytest.approx(1.905)


def test_filetages_cote_machine_catalogue():
    p = Parametres()
    assert p.get("vac_u_lock.filetage_cote_machine") == "M8x1.25"
    assert p.get("vac_u_lock.montage_arriere") == "filete_machine"
    for cle in ATTENDUS_FILETAGES:
        assert cle in FILETAGES_COTE_MACHINE, cle
        f = filetage_cote_machine(cle)
        assert "vaculocks.com" in f["source"]
        assert f["diametre_mm"] > 0
    assert FILETAGES_COTE_MACHINE["M8x1.25"].get("defaut") is True
    assert FILETAGES_COTE_MACHINE["M8x1.25"]["As_mm2"] == pytest.approx(36.6)
    assert FILETAGES_COTE_MACHINE["G1/8"]["As_mm2"] is None  # pas un filetage de traction
    res = calculer_port()
    noms = {s["nom"] for s in res["solides"]}
    assert "vul_filetage_cote_machine" in noms
    assert res["filetage_cote_machine"] == "M8x1.25"
    fil = next(s for s in res["solides"] if s["nom"] == "vul_filetage_cote_machine")
    assert fil["diametre"] == 8.0


def test_npt_asme_non_ajoute_aux_meubles():
    p = Parametres()
    assert p.get("npt_1.norme") == "ASME B1.20.1"
    assert p.get("npt_1.tpi") == 11.5
    assert abs(p.get("npt_1.diametre_exterieur") - 33.401) < 1e-6
    assert abs(p.get("npt_1.conicite") - 0.0625) < 1e-9
    assert p.get("npt_1.angle_filet") == 60.0
    assert abs(p.get("npt_1.longueur_utile_L2") - 17.343) < 1e-6
    # Décision : pas d'ajout rétroactif Equinox / Néogothique.
    assert p.get("npt_1.present_equinox") is False
    assert p.get("npt_1.present_neogothique") is False
    assert p.get("npt_1.present_incognito") is True
    assert p.get("npt_1.present_tantra") is False
    assert p.get("npt_1.present_rangement") is True
    # NPT optionnel, plus le défaut.
    assert "vul_raccord_npt" not in {s["nom"] for s in calculer_port(p)["solides"]}
    q = p.copie()
    q.set("vac_u_lock.montage_arriere", "filete_et_npt")
    assert "vul_raccord_npt" in {s["nom"] for s in calculer_port(q)["solides"]}
    assert "vul_filetage_cote_machine" in {s["nom"] for s in calculer_port(q)["solides"]}


def test_poussee_400_validee():
    p = Parametres()
    meta = p.meta("securite.charge_service_poussee_machine")
    assert p.get("securite.charge_service_poussee_machine") == 400.0
    just = meta.justification.lower()
    assert "valid" in just
    assert "attente" not in just
    assert "800" in meta.justification and "2400" in meta.justification
    d = p.get("vac_u_lock.plug_diametre_tete_max")
    r = rapport_arrachement(d, 400.0, 2.0, "collier_serrage", "M4", 2, 3.0)
    assert r["vide_theorique_max_N"] < 100
    assert r["effort_calcul_N"] == 800.0
    assert r["vide_theorique_max_N"] < r["effort_calcul_N"]
    assert "validée" in r["hypotheses"] or "validee" in r["hypotheses"].lower() or "valid" in r["hypotheses"].lower()
    assert "à valider" not in r["hypotheses"]
    assert compatible_ergot("inox_316")
    assert not compatible_ergot("bois")


def test_port_defaut_collier_et_filetage():
    res = calculer_port()
    noms = {s["nom"] for s in res["solides"]}
    assert "vul_ergot_enveloppe_tete" in noms
    assert "vul_collier_serrage" in noms
    assert "vul_filetage_cote_machine" in noms
    assert res["verrouillage"] == "collier_serrage"
    assert res["variante_tete"] == "brevet"
    profil = str(res["profil"]).lower() + " ".join(res["notes"]).lower()
    assert "étoil" in profil or "etoil" in profil
    # On documente l'absence de cote, on n'invente pas la forme.
    assert "todo" in profil


def test_adaptateurs_sans_modifier_meuble():
    for gamme in ("equinox", "neogothique", "incognito", "tantra", "rangement"):
        a = adaptateur_ancrage(gamme)
        assert a["jonctions"]
        for j in a["jonctions"]:
            assert j["modification_meuble"] is False
    inc = adaptateur_ancrage("incognito")
    assert inc["jonctions"][0]["filetage"] is None  # TODO
    neo = adaptateur_ancrage("neogothique")
    assert neo["jonctions"][0]["filetage"] is None
    assert neo["jonctions"][0]["plaque_mm"] == (40.0, 40.0, 6.0)
    tan = adaptateur_ancrage("tantra")
    assert tan["jonctions"][0]["filetage"] == "M12"
    assert tan["jonctions"][0]["diametre_insert_mm"] == 16.0
    assert tan["jonctions"][0]["diametre_interieur_anneau"] is None  # TODO
    ran = adaptateur_ancrage("rangement")
    assert ran["jonctions"][0]["type"] == "port_natif"
    assert ran["jonctions"][0]["filetage_insert"] == "M8"


def test_integration_machine_bout_de_tige():
    res = sm.calculer()
    noms = {s["nom"] for s in res["solides"]}
    assert "tige_sortie" in noms
    assert "raccord_filete_tige_vul" in noms
    assert "vul_ergot_enveloppe_tete" in noms
    assert "vul_filetage_cote_machine" in noms
    assert "vul_collier_serrage" in noms
    j = next(j for j in res["jonctions"] if j["nom"] == "port_vac_u_lock_bout_de_tige")
    assert j["details"]["modification_meuble"] is False
    assert j["details"]["filetage_cote_machine"] == "M8x1.25"
    assert res["port_vac_u_lock"]["longueur_ergot"] == 76.2
    texte = sm.rapport_texte(res)
    assert "attente" not in texte.lower()
