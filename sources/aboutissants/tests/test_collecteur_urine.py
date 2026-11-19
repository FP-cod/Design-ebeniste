# -*- coding: utf-8 -*-
"""Tests hors Fusion du collecteur d'urine (hors pouf Incognito)."""

import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

import hygiene.collecteur_urine as cu
from hygiene.collecteur_urine import (
    calculer_collecteur,
    arbitrages_par_typologie,
    typologies_cibles,
    volume_total_ml,
    normaliser_typologie,
    comparaison_vidanges,
)
from common.params_globaux import Parametres
from catalogues.materiaux import POLYMERES, JOINTS, HABILLAGE_HORS_ZONE_HUMIDE, materiau


def test_module_sans_import_adsk():
    src = Path(cu.__file__).read_text(encoding="utf-8")
    tete, _, _ = src.partition("def construire_fusion")
    for ligne in tete.splitlines():
        s = ligne.strip()
        if s.startswith("import adsk") or s.startswith("from adsk"):
            raise AssertionError("import adsk au niveau module : %s" % ligne)


def test_pouf_vibrant_refuse():
    for typ in ("pouf", "pouf_vibrant", "Pouf Vibrant"):
        with pytest.raises(ValueError, match="pouf"):
            normaliser_typologie("incognito", typ)
        with pytest.raises(ValueError, match="pouf"):
            calculer_collecteur(typologie=typ, gamme="incognito")
    typo_ids = {t["typologie"] for t in typologies_cibles()}
    assert "pouf" not in typo_ids and "pouf_vibrant" not in typo_ids
    assert all("pouf" not in r["typologie"] for r in arbitrages_par_typologie())


def test_volume_utile_sourcé():
    p = Parametres()
    assert p.get("collecteur_urine.volume_utile") == 500.0
    assert p.get("collecteur_urine.coefficient_anti_debordement") == 1.2
    assert volume_total_ml(p) == 600.0
    justif = p.meta("collecteur_urine.volume_utile").justification
    assert "200" in justif and "500" in justif
    assert "UnityPoint" in p.meta("collecteur_urine.volume_utile").source or "UnityPoint" in justif


def test_hygiene_defaut():
    p = Parametres()
    assert p.get("collecteur_urine.pente_min") == 0.02
    assert p.get("collecteur_urine.rayon_interieur_min") == 5.0
    assert p.get("collecteur_urine.materiau_contact") == "inox_316"
    assert p.get("collecteur_urine.joint") == "epdm"
    assert p.get("collecteur_urine.cuir_sangle_zone_humide") is False
    assert p.get("collecteur_urine.vidange") == "reservoir_amovible"
    res = calculer_collecteur(p)
    by = {v["nom"]: v for v in res["verifications"]}
    assert by["materiau_contact_non_poreux"]["ok"]
    assert by["pente_ecoulement"]["ok"]
    assert by["pas_de_vac_u_lock_fluide"]["ok"]
    assert by["modification_meuble"]["ok"]
    assert by["cuir_sangle_hors_zone_humide"]["ok"]


def test_cuir_interdit_zone_humide():
    p = Parametres()
    p.set("collecteur_urine.cuir_sangle_zone_humide", True)
    erreurs = [x for x in p.valider() if x.niveau == "erreur" and "cuir" in x.chemin]
    assert erreurs
    with pytest.raises(ValueError):
        calculer_collecteur(p)


def test_discretion_etat_ferme():
    p = Parametres()
    p.set("collecteur_urine.etat_deploiement", 0)
    res = calculer_collecteur(p, gamme="incognito", typologie="banquette")
    assert res["typologie"] == "banquette"
    by = {v["nom"]: v for v in res["verifications"]}
    assert by["discretion_etat_ferme"]["ok"]
    roles_humides = {"collecte", "reservoir", "siphon", "vidange", "joint"}
    assert not [s for s in res["solides"] if s.get("visible") and s["role"] in roles_humides]


def test_trois_vidanges_et_materiaux():
    modes = comparaison_vidanges()
    for k in ("reservoir_amovible", "gravite_point_bas", "raccord_npt"):
        assert k in modes
    assert modes["reservoir_amovible"]["recommandation"] == "defaut"
    assert "vac_u_lock" in modes
    assert "pp_homopolymere" in POLYMERES and "pehd" in POLYMERES
    assert POLYMERES["pp_homopolymere"]["poreux"] is False
    assert "tenue_uree" in POLYMERES["pp_homopolymere"]
    assert "epdm" in JOINTS
    assert "cuir" in HABILLAGE_HORS_ZONE_HUMIDE
    assert materiau("inox_316")["tenue_uree"]


def test_arbitrages_toutes_typologies():
    cibles = typologies_cibles()
    rows = arbitrages_par_typologie()
    assert len(cibles) == 26
    assert len(rows) == 26
    attendu = {(c["gamme"], c["typologie"]) for c in cibles}
    obtenu = {(r["gamme"], r["typologie"]) for r in rows}
    assert attendu == obtenu
    # Échantillon : Equinox, Néogothique, Incognito hors pouf, aboutissant fixe.
    for g, t in (("equinox", "banc_flore"), ("neogothique", "entrave"),
                 ("incognito", "banquette"), ("aboutissants", "sex_machine_mecanique"),
                 ("tantra", "tantra_chaise_double_courbe"), ("rangement", "ratelier_mural")):
        assert (g, t) in obtenu
    # Chaque ligne a les trois axes d'arbitrage.
    for r in rows:
        assert r["discretion"] and r["volume_utile"] and r["facilite_vidange"] and r["arbitrage"]


def test_calcul_toutes_typologies_sans_modifier():
    for c in typologies_cibles():
        res = calculer_collecteur(gamme=c["gamme"], typologie=c["typologie"])
        assert res["modification_meuble"] is False
        assert res["implantation"]["modification_meuble"] is False
        assert "pouf" not in res["typologie"]
