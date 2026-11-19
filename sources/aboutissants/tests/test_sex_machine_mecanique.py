# -*- coding: utf-8 -*-
"""Tests hors Fusion de la cinématique et de la géométrie de la machine mécanique."""

import math
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

# Importer la grammaire SANS adsk.
import mouvement.sex_machine_mecanique as sm
from common.params_globaux import Parametres, course_depuis_excentricite
from catalogues.visserie import rapport_m8, charge_admissible_traction, AS_M8_MM2


def test_module_sans_import_adsk():
    src = Path(sm.__file__).read_text(encoding="utf-8")
    # Aucun import adsk au niveau module (seulement dans run / construire_fusion).
    # Aucune instruction d'import adsk avant les fonctions Fusion.
    tete, _, _ = src.partition("def construire_fusion")
    for ligne in tete.splitlines():
        s = ligne.strip()
        if s.startswith("import adsk") or s.startswith("from adsk"):
            raise AssertionError("import adsk au niveau module : %s" % ligne)
    assert sm.position_coulisseau is not None


def test_formule_course_egale_deux_excentricites():
    L = 250.0
    for e in (15.0, 25.0, 40.0, 55.0, 70.0):
        course, xmin, xmax = sm.course_cinematique(e, L, n=720)
        assert abs(course - 2.0 * e) < 0.02, (e, course)
        # Points cardinaux exacts
        assert abs(sm.position_coulisseau(0.0, e, L) - (L + e)) < 1e-9
        assert abs(sm.position_coulisseau(math.pi, e, L) - (L - e)) < 1e-9


def test_bielle_trop_courte_leve():
    with pytest.raises(ValueError):
        sm.position_coulisseau(math.pi / 2, 80.0, 50.0)


def test_calculer_defaut():
    res = sm.calculer(theta_deg=0.0)
    assert res["course"] == 80.0
    assert res["e"] == 40.0
    assert res["L"] == 250.0
    assert abs(res["x_relatif"] - (250.0 + 40.0)) < 1e-9
    assert res["hauteur"] == 700.0  # 350 + 14*25 = 700, cran pour 700
    assert len(res["solides"]) >= 15
    noms = {s["nom"] for s in res["solides"]}
    for requis in (
        "semelle_chassis", "colonne", "disque_excentrique", "bielle", "rail",
        "chariot", "tige_sortie", "manivelle", "bride_joue_g", "vis_serre_bride_m8",
        "platine_moteur_reservee", "butee_proche", "butee_loin", "goupille_debrayage",
    ):
        assert requis in noms, requis
    # Aucune pièce ne « perce » le meuble : la jonction le dit.
    j = next(j for j in res["jonctions"] if j["nom"] == "bride_sur_oeillet_meuble")
    assert j["details"]["modification_meuble"] is False
    assert j["details"]["filetage_serrage"] == "M8"


def test_chariot_reste_dans_les_butees_sur_un_tour():
    p = Parametres()
    for theta in range(0, 360, 15):
        res = sm.calculer(p, theta_deg=theta)
        v = next(v for v in res["verifications"] if v["nom"] == "chariot_dans_butees")
        assert v["ok"], (theta, v["message"])


def test_verifications_course_et_debrayage():
    res = sm.calculer()
    by = {v["nom"]: v for v in res["verifications"]}
    assert by["course_egale_2e"]["ok"]
    assert by["bielle_plus_longue_que_e"]["ok"]
    assert by["debrayage_present"]["ok"]
    assert by["params_sans_erreur"]["ok"]


def test_hauteur_par_cran():
    assert sm.hauteur_au_cran(350, 25, 0) == 350
    assert sm.hauteur_au_cran(350, 25, 14) == 700
    cran = sm.cran_pour_hauteur(690, 350, 25, 900)
    assert sm.hauteur_au_cran(350, 25, cran) in (675, 700)
    res = sm.calculer(cran_hauteur=0)
    assert res["hauteur"] == 350.0
    res2 = sm.calculer(cran_hauteur=22)  # 350+22*25=900
    assert res2["hauteur"] == 900.0


def test_courses_reglables_sur_les_trous():
    p = Parametres()
    for e in p.get("mouvement.trous_excentricite"):
        q = p.copie()
        q.set("mouvement.excentricite", e)
        res = sm.calculer(q, theta_deg=0)
        assert res["course"] == course_depuis_excentricite(e)
        course_num, _, _ = sm.course_cinematique(e, q.get("mouvement.longueur_bielle"))
        assert abs(course_num - res["course"]) < 0.05


def test_m8_charges_hypotheses():
    r = rapport_m8(3.0, "A4-70")
    # Rp0,2 450 × As 36.6 = 16470 N ; /3 = 5490 N
    assert abs(r["traction_elastique_N"] - 450.0 * AS_M8_MM2) < 1e-6
    assert abs(r["traction_admissible_N"] - 16470.0 / 3.0) < 0.2
    # Cisaillement fileté : 0.6 × 16470 / 3 = 3294 N
    assert abs(r["cisaillement_filete_admissible_N"] - (0.6 * 16470.0) / 3.0) < 0.2
    assert r["limite_meuble_oeillet_equinox_N"] == 2000.0
    # La vis est plus « solide » que l'œillet catalogue : le meuble limite.
    assert r["traction_admissible_N"] > r["limite_meuble_oeillet_equinox_N"]
    assert charge_admissible_traction("A4-70", 3.0) == r["traction_admissible_N"]


def test_rapport_texte_contient_formule():
    texte = sm.rapport_texte(sm.calculer())
    assert "course = 2" in texte
    assert "M8" in texte or "bride" in texte.lower() or "œillet" in texte or "oeillet" in texte.lower()


def test_materiaux_catalogues():
    from catalogues.materiaux import METAUX, BOIS, materiau
    for cle in ("inox_316", "laiton_cw614n", "laiton_cw510l", "alu_6082_t6"):
        assert cle in METAUX
        assert METAUX[cle]["limite_elastique"] > 0
        assert METAUX[cle]["source"]
    assert METAUX["alu_6082_t6"].get("a_valider") is True
    assert "frene" in BOIS and "chene" in BOIS and "noyer" in BOIS
    assert materiau("inox_316")["densite"] == 8000.0
