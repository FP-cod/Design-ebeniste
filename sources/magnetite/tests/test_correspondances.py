# -*- coding: utf-8 -*-
"""Coherence du mapping teintes cuir <-> materiaux des catalogues meubles."""

import os

import pytest

from gamme_cuir.catalogues import correspondances_meubles as cm
from gamme_cuir.catalogues.cuirs import TEINTES

from conftest import WORKSPACE

GAMMES_PRESENTES = all(os.path.isdir(os.path.join(WORKSPACE, g)) for g in ("equinox", "neogothique", "incognito"))


def test_coherence_interne():
    assert cm.verifier_coherence_interne() == []


@pytest.mark.parametrize("teinte", sorted(TEINTES))
def test_chaque_teinte_mappee_ou_marquee_non_assortie(teinte):
    statut = cm.statut_teinte(teinte)
    reels = [c for c in cm.CORRESPONDANCES[teinte] if c["type"] in ("exact", "proche")]
    if statut == "non_assortie":
        assert reels == []
    else:
        assert reels, teinte
        for c in reels:
            assert (c["gamme"], c["materiau"]) in cm.MATERIAUX_MEUBLES


@pytest.mark.parametrize("teinte", sorted(TEINTES))
def test_tantra_a_confirmer(teinte):
    t = [c for c in cm.CORRESPONDANCES[teinte] if c["gamme"] == "tantra"]
    assert len(t) == 1 and t[0]["type"] == "a_confirmer" and t[0]["materiau"] is None
    assert "tantra" in cm.GAMMES_SANS_CATALOGUE


def test_exemple_banc_cognac_et_entrave_noire():
    cognac = {(c["gamme"], c["materiau"]) for c in cm.meubles_assortis("cognac", types=("exact",))}
    assert ("equinox", "cuir_classique_pleine_fleur") in cognac and ("incognito", "cuir_cognac") in cognac
    noir = {(c["gamme"], c["materiau"]) for c in cm.meubles_assortis("noir", types=("exact",))}
    assert ("neogothique", "cuir_sellier_fin_noir") in noir
    assert cm.statut_teinte("cognac") == "assortie" and cm.statut_teinte("bordeaux") == "assortie_hors_cuir"


def test_statut_non_assortie_et_proche():
    assert cm.statut_teinte("inconnue", {"inconnue": []}) == "non_assortie"
    assert cm.statut_teinte("tan") == "proche"


def test_exact_impose_meme_identifiant_de_coloris():
    fausse = {"cognac": [cm._c("equinox", "cuir_classique_pleine_fleur", "havane")]}
    sauvegarde = cm.CORRESPONDANCES
    try:
        cm.CORRESPONDANCES = dict(sauvegarde, **fausse)
        assert any("meme identifiant" in a for a in cm.verifier_coherence_interne())
    finally:
        cm.CORRESPONDANCES = sauvegarde


@pytest.mark.skipif(not GAMMES_PRESENTES, reason="catalogues meubles absents de la machine")
def test_instantane_conforme_aux_catalogues_vivants():
    anomalies, gammes = cm.verifier_contre_catalogues(WORKSPACE)
    assert gammes == ["equinox", "incognito", "neogothique"]
    assert anomalies == []


@pytest.mark.skipif(not GAMMES_PRESENTES, reason="catalogues meubles absents de la machine")
def test_tous_les_cuirs_meubles_sont_couverts():
    """Chaque materiau cuir des meubles (vivant) doit apparaitre dans au moins une correspondance."""
    vivants = cm.coloris_vivants(WORKSPACE)
    utilises = {(c["gamme"], c["materiau"]) for corr in cm.CORRESPONDANCES.values() for c in corr}
    for cle in cm.MATERIAUX_MEUBLES:
        assert cle in vivants
        if cm.MATERIAUX_MEUBLES[cle]["cuir_veritable"]:
            assert cle in utilises, cle


@pytest.mark.skipif(not GAMMES_PRESENTES, reason="catalogues meubles absents de la machine")
def test_quincaillerie_meubles_identifiants_reels():
    eq = cm._importer(WORKSPACE, "equinox", "equinox.catalogues.metaux")
    neo = cm._importer(WORKSPACE, "neogothique", "neogothique.catalogues.ferrures")
    d = cm.QUINCAILLERIE_MEUBLES
    assert set(d["equinox"]["inox"] + d["equinox"]["laiton"]) <= set(eq.METAUX)
    assert set(d["neogothique"]["fer"] + d["neogothique"]["laiton"]) <= set(neo.METAUX)
    assert set(d["neogothique"]["finitions"]) <= set(neo.FINITIONS)
    assert neo.FINITIONS["laiton_patine_vieilli"]["contact_peau"] != "ok"
