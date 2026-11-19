# -*- coding: utf-8 -*-
"""Tests des catalogues essences, revêtements et fixations."""

import pytest

from incognito.catalogues import (
    ESSENCES,
    FIXATIONS,
    REVETEMENTS,
    essence_par_nom,
    fixation_par_nom,
    revetement_par_nom,
)
from incognito.catalogues.revetements import (
    revetements_exterieurs_conformes,
    revetements_interieurs,
)


def test_catalogue_essences():
    for nom in ("chene", "noyer", "hetre", "frene", "merisier"):
        essence = essence_par_nom(nom)
        assert essence.nom == nom
        assert essence is ESSENCES[nom]
    with pytest.raises(KeyError):
        essence_par_nom("pin")


def test_catalogue_revetements_discret():
    noms_tissus = {r.nom for r in revetements_exterieurs_conformes()}
    assert noms_tissus == {"velours", "lin", "laine_bouclee", "tissu_chine"}
    interieurs = {r.nom for r in revetements_interieurs()}
    assert "cuir_cognac" in interieurs
    assert "cuir_noir" in interieurs
    assert revetement_par_nom("cuir_cognac").usage == "interieur_cache"
    with pytest.raises(KeyError):
        revetement_par_nom("vinyle")


def test_catalogue_fixations_invisibles_en_fermee():
    assert set(FIXATIONS) >= {
        "tourillon_10", "tourillon_12", "mortaise_tenon",
        "insert_ancre_noye", "cache_affleurant",
        "charniere_soss", "verin_compas",
    }
    for fixation in FIXATIONS.values():
        assert fixation.visible_etat_ferme is False
    soss = fixation_par_nom("charniere_soss")
    assert soss.cotes_mm["epaisseur_min_bois"] <= 22.0
    with pytest.raises(KeyError):
        fixation_par_nom("vis_apparente")


def test_catalogues_pouf_vibrant():
    from incognito.catalogues.silentblocs import silentblocs_pour_gamme, silentbloc_par_nom
    from incognito.catalogues.moteurs import variante_par_gamme, VCAR_0105, PISTON_VCAR_0110, ROTATION_EC45
    from incognito.catalogues.housses import FILETAGE_1_NPT, COMPATIBILITES, ADAPTATEURS
    from incognito.catalogues.impression import PIECES_IMPRIMABLES, NOTE_ACOUSTIQUE_TREILLIS
    from incognito.parametres import GAMME_SYBIAN_HAUT, GAMME_SYBIAN_ENTREE

    assert any(s.materiau == "silicone" for s in silentblocs_pour_gamme(GAMME_SYBIAN_HAUT))
    assert any(s.materiau == "caoutchouc" for s in silentblocs_pour_gamme(GAMME_SYBIAN_ENTREE))
    silentbloc_par_nom("silicone_tres_souple_m6")
    assert VCAR_0105.force_crete_n == 105.0
    assert 16.0 <= VCAR_0105.course_totale_mm <= 16.5
    assert PISTON_VCAR_0110.course_totale_mm == 38.0
    assert ROTATION_EC45.tension_v == 24.0
    assert FILETAGE_1_NPT.conique is True
    assert FILETAGE_1_NPT.tpi == 11.5
    # Aucune housse officielle listée n'est native 1" NPT
    assert any(c.compatible_1_npt_natif is False for c in COMPATIBILITES)
    assert all(c.sources for c in COMPATIBILITES)
    assert any(a.nom == "npt_vers_platine_levre_sybian" for a in ADAPTATEURS)
    assert any(p.piece == "selle_peau" and "Dragon Skin" in p.materiau for p in PIECES_IMPRIMABLES)
    assert "10.1007/s00170-026-17663-z" in NOTE_ACOUSTIQUE_TREILLIS
    assert "10.1088/2631-8695/ae1791" in NOTE_ACOUSTIQUE_TREILLIS
    assert "20,6" in NOTE_ACOUSTIQUE_TREILLIS and "16,9" in NOTE_ACOUSTIQUE_TREILLIS
    assert "fournis par Fabien" in NOTE_ACOUSTIQUE_TREILLIS
    from incognito.catalogues.electronique import ESP32_S3_WROOM1, NOTE_FSR_ECARTE, ADS1220
    assert ESP32_S3_WROOM1.famille.startswith("ESP32")
    assert "FSR" in NOTE_FSR_ECARTE
    assert ADS1220.recommande is True
    assert any(p.piece == "panneau_acoustique" for p in PIECES_IMPRIMABLES)
    v = variante_par_gamme(GAMME_SYBIAN_HAUT)
    assert v.prix_vente.origine == "vente_fabien"
    assert v.cout_matiere_estime.origine == "estimation_matiere"
