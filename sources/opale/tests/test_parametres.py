# -*- coding: utf-8 -*-
"""Tests de la couche 1 : paramètres globaux Incognito."""

from dataclasses import FrozenInstanceError

import pytest

from incognito.parametres import (
    ANCRE_DEFAUT,
    BANQUETTE,
    CHARGES_DEFAUT,
    CHENE,
    COEFFICIENT_SECURITE_MIN_RECOMMANDE,
    CUIR_COGNAC,
    CUIR_NOIR,
    CUIR_SOBRE_FACADE,
    DISCRETION_DEFAUT,
    ESSENCES_BASE,
    HETRE,
    MERISIER,
    NIVEAU_ESSAI_REQUIS,
    NIVEAU_NON_CONFORME,
    PARAMETRES_DEFAUT,
    PLAGE_HAUTEUR_ASSISE,
    PLAGE_HAUTEUR_TABLE_BASSE,
    TABLE_BASSE,
    TYPOLOGIES,
    VELOURS,
    Cote,
    Essence,
    GeometrieAncre,
    ParametresCharge,
    ParametresGlobaux,
    Plage,
    typologie_par_nom,
    valider_ancrage,
    valider_charges,
    vers_parametres_fusion,
)


def test_dataclasses_figees():
    with pytest.raises(FrozenInstanceError):
        CHENE.masse_volumique_kg_m3 = 1.0  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        DISCRETION_DEFAUT.jeu_mecanique_mm = 0.0  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        CHARGES_DEFAUT.coefficient_securite = 1.0  # type: ignore[misc]


def test_plage_et_cote_valides():
    plage = Plage(420.0, 450.0)
    assert plage.contient(430.0)
    assert not plage.contient(400.0)
    assert plage.borner(400.0) == 420.0
    with pytest.raises(ValueError):
        Plage(10.0, 1.0)
    with pytest.raises(ValueError):
        Cote("x", 10.0, Plage(0.0, 5.0), "hors plage")


def test_typologies_salon_completes():
    attendues = {
        "canape", "fauteuil", "table_basse", "banc_entree",
        "pouf", "bibliotheque", "banquette",
    }
    assert set(TYPOLOGIES) == attendues
    for typo in TYPOLOGIES.values():
        assert typo.cotes
        for cote in typo.cotes:
            assert cote.plage.contient(cote.valeur)
            assert cote.valeur > 0 or cote.nom == "hauteur_dossier"


def test_hauteurs_assise_et_table_basse_dans_plages_demandees():
    for nom in ("canape", "fauteuil", "banc_entree", "pouf", "banquette"):
        typo = typologie_par_nom(nom)
        # pouf utilise "hauteur", les autres "hauteur_assise"
        nom_cote = "hauteur" if nom == "pouf" else "hauteur_assise"
        cote = typo.cote(nom_cote)
        assert PLAGE_HAUTEUR_ASSISE.contient(cote.valeur)
        assert cote.plage.minimum == PLAGE_HAUTEUR_ASSISE.minimum
        assert cote.plage.maximum == PLAGE_HAUTEUR_ASSISE.maximum
    assert PLAGE_HAUTEUR_TABLE_BASSE.contient(TABLE_BASSE.cote("hauteur").valeur)


def test_cotes_banc_banquette_hypotheses():
    assert BANQUETTE.cote("hauteur_appui_banc").valeur == 700.0
    assert BANQUETTE.cote("longueur_appui_banc").valeur == 1150.0
    assert BANQUETTE.cote("longueur").valeur >= 1150.0 + 2 * 22.0


def test_essences_proprietes_positives_et_sources():
    assert set(ESSENCES_BASE) == {"chene", "noyer", "hetre", "frene", "merisier"}
    for essence in ESSENCES_BASE.values():
        assert essence.masse_volumique_kg_m3 > 0
        assert essence.module_elasticite_mpa > 0
        assert essence.contrainte_admissible_flexion_mpa > 0
        assert essence.contrainte_admissible_cisaillement_mpa > 0
        assert essence.contrainte_admissible_flexion_mpa < essence.contrainte_caracteristique_flexion_mpa
        assert "Wood Handbook" in essence.source or "NF EN 338" in essence.source
        assert "essai" in essence.hypotheses.lower()
    with pytest.raises(ValueError):
        Essence(
            nom="x", nom_affiche="X", nom_latin="X",
            masse_volumique_kg_m3=0, module_elasticite_mpa=1,
            contrainte_caracteristique_flexion_mpa=1,
            contrainte_admissible_flexion_mpa=1,
            contrainte_admissible_cisaillement_mpa=1,
            source="s", hypotheses="h",
        )


def test_revetements_cuir_cache_par_defaut():
    assert VELOURS.conforme_discretions_defaut()
    assert CUIR_COGNAC.usage == "interieur_cache"
    assert CUIR_NOIR.usage == "interieur_cache"
    assert not CUIR_SOBRE_FACADE.conforme_discretions_defaut()
    assert PARAMETRES_DEFAUT.revetement_exterieur is VELOURS
    assert PARAMETRES_DEFAUT.revetement_interieur is CUIR_COGNAC


def test_charges_defaut_et_rupture_visee():
    assert CHARGES_DEFAUT.coefficient_securite >= COEFFICIENT_SECURITE_MIN_RECOMMANDE
    assert CHARGES_DEFAUT.charge_rupture_visee_ancrage_n == pytest.approx(4500.0)
    rapport = valider_charges(ParametresCharge(coefficient_securite=2.0))
    assert not rapport.conforme
    assert any(s.code == "cs_insuffisant" for s in rapport.signalements)


def test_valider_ancrage_defaut_acceptable_mais_essai_requis():
    rapport = valider_ancrage(CHENE, ANCRE_DEFAUT, CHARGES_DEFAUT, DISCRETION_DEFAUT)
    assert rapport.conforme
    assert any(s.niveau == NIVEAU_ESSAI_REQUIS for s in rapport.signalements)
    assert any(s.code == "essai_charge_reel" for s in rapport.signalements)


def test_valider_ancrage_signle_compromis_section_insuffisante():
    ancre_mince = GeometrieAncre(
        diametre_insert_mm=12.0,
        longueur_encastrement_mm=20.0,
        epaisseur_bloc_mm=22.0,
        largeur_bloc_mm=30.0,
        longueur_bloc_mm=30.0,
        epaisseur_recouvrement_mm=10.0,
        recouvrement_est_structurel=False,
        nombre_plans_cisaillement=2,
        distance_au_bord_mm=5.0,
    )
    rapport = valider_ancrage(MERISIER, ancre_mince, CHARGES_DEFAUT, DISCRETION_DEFAUT)
    assert not rapport.conforme
    codes = {s.code for s in rapport.signalements}
    assert "paroi_cisaillement_insuffisante" in codes or "section_restante_nulle" in codes
    assert any(s.compromis for s in rapport.signalements)
    assert any(s.niveau == NIVEAU_NON_CONFORME for s in rapport.signalements)


def test_valider_ancrage_retrait_discretion():
    ancre = GeometrieAncre(
        epaisseur_recouvrement_mm=2.0,
        epaisseur_bloc_mm=80.0,
        distance_au_bord_mm=40.0,
        longueur_encastrement_mm=80.0,
        largeur_bloc_mm=80.0,
        longueur_bloc_mm=80.0,
    )
    rapport = valider_ancrage(HETRE, ancre, CHARGES_DEFAUT, DISCRETION_DEFAUT)
    assert not rapport.conforme
    assert any(s.code == "retrait_discretion_insuffisant" and s.compromis for s in rapport.signalements)


def test_derogation_cuir_facade_signalee():
    params = ParametresGlobaux(revetement_exterieur=CUIR_SOBRE_FACADE)
    rapport = params.valider()
    assert any(s.code == "cuir_visible_derogation" and s.compromis for s in rapport.signalements)


def test_vers_parametres_fusion_structure_et_unites():
    dico = vers_parametres_fusion()
    assert dico
    for nom, (valeur, unite, commentaire) in dico.items():
        assert nom.startswith("inc_")
        assert isinstance(valeur, float)
        assert isinstance(unite, str)
        assert commentaire
    assert dico["inc_charge_service_ancrage"][0] == 1500.0
    assert dico["inc_charge_service_ancrage"][1] == "N"
    assert dico["inc_coefficient_securite"][0] == 3.0
    assert dico["inc_coefficient_securite"][1] == ""
    assert dico["inc_banquette_hauteur_appui_banc"][0] == 700.0
    assert dico["inc_banquette_hauteur_appui_banc"][1] == "mm"
    assert "inc_canape_hauteur_assise" in dico
    assert "inc_bibliotheque_hauteur" in dico
    assert typologie_par_nom("banquette") is BANQUETTE
    with pytest.raises(KeyError):
        typologie_par_nom("inexistant")


def test_parametres_sybian_fusion():
    from incognito.parametres import (
        ParametresSybian, GAMME_SYBIAN_ENTREE, vers_parametres_fusion,
    )
    assert ParametresSybian().code_fusion == 1
    assert ParametresSybian.depuis_code_fusion(0).gamme == GAMME_SYBIAN_ENTREE
    dico = vers_parametres_fusion()
    assert dico["inc_sybian_gamme"][0] in (0.0, 1.0)
    assert dico["inc_sybian_tension"][0] == 24.0
