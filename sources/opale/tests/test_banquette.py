# -*- coding: utf-8 -*-
"""Tests de la grammaire de la banquette Incognito."""

import pytest

from incognito.grammaires.banquette import (
    Etat,
    ParametresBanquette,
    caisson_interieur,
    calculer,
    calculer_deux_etats,
    deriver,
    encombrement_banc_replie,
    encombrement_bequille_repliee,
    parametres_banquette_defaut,
    vers_parametres_fusion_banquette,
)
from incognito.parametres import (
    BANQUETTE,
    NIVEAU_ESSAI_REQUIS,
    NIVEAU_NON_CONFORME,
    PLAGE_HAUTEUR_ASSISE,
    ParametresCharge,
)
from incognito.fusion_outils import cm_vers_mm, mm_vers_cm


def test_deux_etats_depuis_les_memes_parametres():
    params = parametres_banquette_defaut()
    etats = calculer_deux_etats(params)
    assert set(etats) == {Etat.FERMEE, Etat.DEPLOYEE}
    fermee = etats[Etat.FERMEE]
    deployee = etats[Etat.DEPLOYEE]
    assert fermee.parametres is params
    assert deployee.parametres is params
    assert fermee.etat is Etat.FERMEE
    assert deployee.etat is Etat.DEPLOYEE
    # Mêmes identifiants de pièces structurelles dans les deux états.
    communs = set(p.nom for p in fermee.pieces) & set(p.nom for p in deployee.pieces)
    for nom in (
        "assise_couvercle", "caisson_fond", "banc_panneau", "banc_joue_g",
        "banc_joue_d", "banc_coussin_cuir", "pied_avg", "panneau_arriere_dossier",
    ):
        assert nom in communs
    # Le couvercle et le banc ont bougé.
    assert fermee.piece("assise_couvercle").boite != deployee.piece("assise_couvercle").boite
    assert fermee.piece("banc_panneau").boite.z != deployee.piece("banc_panneau").boite.z


def test_cotes_salon_etat_ferme():
    geo = calculer(Etat.FERMEE)
    typo = BANQUETTE
    assert geo.piece("coussin_assise").boite.z + geo.piece("coussin_assise").boite.dz == pytest.approx(
        typo.cote("hauteur_assise").valeur
    )
    assert PLAGE_HAUTEUR_ASSISE.contient(typo.cote("hauteur_assise").valeur)
    assert geo.parametres.longueur == typo.cote("longueur").valeur
    assert geo.parametres.profondeur == typo.cote("profondeur_hors_tout").valeur
    # Encombrement fermé : pas de débord avant (y >= 0), hauteur dossier.
    enc = geo.encombrement()
    assert enc.y >= -0.1
    assert enc.x >= -0.1
    assert enc.z >= -0.1
    assert enc.z + enc.dz == pytest.approx(typo.cote("hauteur_dossier").valeur)
    assert geo.conforme


def test_cotes_banc_deploye():
    geo = calculer(Etat.DEPLOYEE)
    coussin = geo.piece("banc_coussin_cuir")
    z_appui = coussin.boite.z + coussin.boite.dz
    assert z_appui == pytest.approx(700.0, abs=1.0)
    assert coussin.boite.dx == pytest.approx(1150.0, abs=1.0)
    assert coussin.boite.dy == pytest.approx(320.0, abs=1.0)
    codes = {v.code: v for v in geo.verifications}
    assert codes["cotes_appui_deploye"].ok


def test_banc_replié_rentre_dans_le_caisson():
    params = parametres_banquette_defaut()
    derivees = deriver(params)
    interieur = caisson_interieur(params, derivees)
    pack = encombrement_banc_replie(params, derivees)
    assert pack.rentre_dans(interieur, jeu=params.discretion.jeu_repli_mm)
    geo = calculer(Etat.FERMEE, params)
    verif = next(v for v in geo.verifications if v.code == "banc_rentre_dans_caisson")
    assert verif.ok
    # Les pièces du banc rangé sont bien à l'intérieur du caisson.
    for nom in ("banc_panneau", "banc_coussin_cuir", "banc_joue_g", "banc_joue_d"):
        boite = geo.piece(nom).boite
        assert boite.x >= interieur.x - 1.0
        assert boite.y >= interieur.y - 1.0
        assert boite.z >= interieur.z - 1.0
        assert boite.x + boite.dx <= interieur.x + interieur.dx + 1.0
        assert boite.y + boite.dy <= interieur.y + interieur.dy + 1.0
        assert boite.z + boite.dz <= interieur.z + interieur.dz + 1.0


def test_bequille_repliée_rentre():
    params = parametres_banquette_defaut()
    interieur = caisson_interieur(params)
    beq = encombrement_bequille_repliee(params)
    assert beq.dx <= interieur.dx
    assert beq.dy <= interieur.dy
    geo = calculer(Etat.FERMEE, params)
    verif = next(v for v in geo.verifications if v.code == "bequille_rentre_dans_caisson")
    assert verif.ok
    # Déployée, la béquille déborde en avant (y < 0).
    dep = calculer(Etat.DEPLOYEE, params)
    assert dep.piece("appuie_genoux").boite.y < 0
    enc = dep.encombrement()
    assert enc.y < 0


def test_ancrages_invisibles_en_fermee():
    geo = calculer(Etat.FERMEE)
    for piece in geo.pieces:
        if piece.role in {"ancrage", "coussin_interieur", "bequille"}:
            assert piece.visible_exterieur_si_fermee is False
    for assemblage in geo.assemblages:
        if assemblage.type in {"ancre", "charniere_soss", "verin"}:
            assert assemblage.visible_etat_ferme is False
    verif = next(v for v in geo.verifications if v.code == "ancrages_invisibles_en_fermee")
    assert verif.ok
    # Le cuir du banc n'est pas un revêtement de façade.
    assert geo.piece("banc_coussin_cuir").visible_exterieur_si_fermee is False
    assert geo.parametres.revetement_banc.usage == "interieur_cache"


def test_assemblages_bois_sans_vis_apparente():
    geo = calculer(Etat.FERMEE)
    types = {a.type for a in geo.assemblages}
    assert "tourillon" in types
    assert "mortaise_tenon" in types
    assert "charniere_soss" in types
    assert "ancre" in types
    assert "lumiere_fond" in types
    assert "vis" not in types


def test_compromis_rail_et_essai_requis():
    for etat in Etat:
        geo = calculer(etat)
        codes = {v.code: v for v in geo.verifications}
        assert codes["rail_necessite_bloc_local"].compromis
        assert any(v.niveau == NIVEAU_ESSAI_REQUIS for v in geo.verifications)
        assert any(v.code.startswith("essai") for v in geo.verifications)


def test_stabilite_deployee_avec_et_sans_bequille():
    avec = calculer(Etat.DEPLOYEE, parametres_banquette_defaut())
    sans = calculer(
        Etat.DEPLOYEE,
        parametres_banquette_defaut(avec_bequille_avant=False),
    )
    assert any(v.code == "stabilite_verticale" and v.ok for v in avec.verifications)
    # Sans béquille, la traction horizontale est signalée comme compromis.
    horiz_sans = next(v for v in sans.verifications if v.code == "stabilite_horizontale_sans_bequille")
    assert horiz_sans.compromis
    assert horiz_sans.niveau in {NIVEAU_NON_CONFORME, "avertissement"}
    horiz_avec = next(v for v in avec.verifications if v.code == "stabilite_horizontale_avec_bequille")
    assert horiz_avec is not None


def test_longueur_insuffisante_rejetee():
    with pytest.raises(ValueError):
        ParametresBanquette(longueur=1100.0, longueur_appui=1150.0)


def test_export_fusion_banquette_contient_etat():
    dico = vers_parametres_fusion_banquette()
    assert dico["inc_etat_deploiement"][0] == 0.0
    assert dico["inc_etat_deploiement"][1] == ""
    assert dico["inc_banq_hauteur_appui"][0] == 700.0
    assert dico["inc_banq_longueur_appui"][0] == 1150.0
    assert "inc_banq_hauteur_interieure" in dico


def test_conversion_mm_cm():
    assert mm_vers_cm(100.0) == 10.0
    assert cm_vers_mm(10.0) == 100.0


def test_cs_insuffisant_non_conforme():
    params = parametres_banquette_defaut(
        charges=ParametresCharge(coefficient_securite=2.0),
    )
    # Le recalage refuse un CS < 3, donc calculer doit remonter l'erreur.
    with pytest.raises(ValueError):
        calculer(Etat.FERMEE, params)


def test_nom_pieces_stables_pour_le_script_fusion():
    """Le script Fusion s'appuie sur ces noms : on les fige par un test."""
    geo = calculer(Etat.FERMEE)
    attendues = {
        "pied_avg", "pied_avd", "pied_arg", "pied_ard",
        "caisson_panneau_av", "caisson_panneau_g", "caisson_panneau_d",
        "panneau_arriere_dossier", "caisson_fond",
        "assise_couvercle", "coussin_assise", "coussin_dossier",
        "banc_panneau", "banc_coussin_cuir", "banc_joue_g", "banc_joue_d",
        "banc_traverse", "lest",
    }
    noms = {p.nom for p in geo.pieces}
    assert attendues <= noms
