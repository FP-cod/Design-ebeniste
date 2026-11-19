# -*- coding: utf-8 -*-
"""Grammaires (couche 3) : toutes les typologies, tous les états."""
import dataclasses

import pytest

from tantra import registre
from tantra.chiffrage import chiffrer
from tantra.grammaires import (cadre_desserte_genoux as DG, camo_canape as CC, camo_fauteuil as CF,
                               tantra_banquette_deux_niveaux as BQ, tantra_chaise_double_courbe as CH,
                               tantra_fauteuil_lombaire as FL, tantra_siege_repose_genoux as SG)

TOUS = [(n, e) for n, ent in registre.REGISTRE.items() for e in ent.etats]


@pytest.mark.parametrize("nom,etat", TOUS)
def test_conforme_par_defaut(nom, etat):
    g = registre.geometrie(nom, etat)
    assert g.conforme, [v.message for v in g.verifications if v.niveau == "non_conforme"]
    assert g.pieces and g.ancrages
    assert g.essais_requis, "chaque typologie doit exiger essais réels et visa d'ingénieur"
    assert any(v.code == "visa_ingenieur" for v in g.verifications)


@pytest.mark.parametrize("nom,etat", TOUS)
def test_pieces_au_sol_et_volumes_positifs(nom, etat):
    g = registre.geometrie(nom, etat)
    assert min(p.aabb[4] for p in g.pieces) == pytest.approx(0, abs=1)
    assert all(p.volume_m3 > 0 for p in g.pieces)
    assert len({p.nom for p in g.pieces}) == len(g.pieces)


@pytest.mark.parametrize("nom", list(registre.REGISTRE))
def test_chiffrage_coherent(nom):
    c = registre.entree(nom).chiffrage()
    assert c.date.endswith("2026")
    assert c.fourchette_ttc[0] < c.prix_vente_ttc < c.fourchette_ttc[1]
    assert c.prix_prototype_ttc > c.prix_vente_ttc
    assert 1000 < c.prix_vente_ttc < 15000


def test_registre_parametre_etat():
    assert registre.nom_parametre_etat("camo_canape") == "tan_canape_etat"
    assert registre.nom_parametre_etat("tantra_chaise_double_courbe") is None
    with pytest.raises(KeyError):
        registre.entree("nimporte")
    noms = [n for e in registre.REGISTRE for n in registre.parametres_fusion(e)]
    assert len(noms) == len(set(noms)), "collision de noms de paramètres Fusion"


# --- Volet 1 ---------------------------------------------------------------
def test_chaise_profil_et_rayon():
    g = CH.calculer()
    assert g.dimensions_hors_tout[1] == pytest.approx(1850, abs=5)
    assert g.verification("coque_cintrage").ok


def test_chaise_rayon_trop_serre_detecte():
    p = dataclasses.replace(CH.ParametresChaiseDoubleCourbe(), position_creux=420.0, position_petite_bosse=250.0,
                            retombee=240.0)
    g = CH.calculer(p)
    assert not g.verification("coque_cintrage").ok


def test_chaise_ordre_des_points_cles():
    with pytest.raises(ValueError):
        CH.ParametresChaiseDoubleCourbe(position_creux=200.0)


def test_fauteuil_lombaire_ergonomie():
    g = FL.calculer()
    assert any(v.code.startswith("ergo") for v in g.verifications)


def test_banquette_deux_niveaux_flasques_recalcules():
    p = BQ.ParametresBanquetteDeuxNiveaux()
    n1 = BQ.n_flasques_requis(p)
    n2 = BQ.n_flasques_requis(dataclasses.replace(p, largeur=1900.0)) if hasattr(p, "largeur") else n1
    assert n2 >= n1 >= 3


def test_siege_repose_genoux_patin_court_bascule():
    g = SG.calculer(dataclasses.replace(SG.ParametresSiegeReposeGenoux(), longueur_patin=900.0))
    assert not g.verification("stabilite_bascule_arriere").ok


# --- Volet 2 ---------------------------------------------------------------
@pytest.mark.parametrize("M", [CC, CF])
def test_camouflable_zero_visible_en_salon(M):
    g = M.calculer(None, "SALON")
    disc = [v for v in g.verifications if v.code.startswith("discretion_")]
    assert len(disc) == len(g.ancrages) and all(v.ok for v in disc)
    assert all(not a.visible for a in g.ancrages)


@pytest.mark.parametrize("M", [CC, CF])
def test_camouflable_acces_en_revele(M):
    g = M.calculer(None, "REVELE")
    acces = [v for v in g.verifications if v.code.startswith("acces_")]
    assert acces and all(v.ok for v in acces)


def test_canape_traverse_trop_mince_non_conforme(monkeypatch):
    from tantra.grammaires import _salon
    orig = _salon.ParametresSalon
    s = dataclasses.replace(CC.ParametresCanape().salon(), epaisseur_traverse_avant=50.0)
    monkeypatch.setattr(CC.ParametresCanape, "salon", lambda self: s)
    g = CC.calculer()
    assert not g.verification("insert_traverse_avant").ok
    assert orig is _salon.ParametresSalon


def test_fauteuil_bequilles_touchent_le_sol_en_revele():
    g = CF.calculer(None, 1)
    beq = g.pieces_role("bequille")
    assert len(beq) == g.derivees["nombre_bequilles"] >= 2
    assert all(b.aabb[4] == pytest.approx(0) for b in beq)
    assert g.derivees["z_repose_genoux"] == pytest.approx(140 + 25 + 50)
    assert g.verification("stabilite_a_genoux").ok


# --- Volet 3 ---------------------------------------------------------------
def test_desserte_course_et_recouvrement():
    p = DG.ParametresDesserteGenoux()
    assert p.course == pytest.approx(400)
    assert p.recouvrement_cadre >= 3 * p.section_montant
    m, c = DG.calculer(p, 0), DG.calculer(p, 1)
    assert c.piece("desserte_barre_haute").aabb[5] == pytest.approx(p.hauteur_cadre)
    assert m.piece("desserte_barre_haute").aabb[5] == pytest.approx(p.hauteur_meuble)
    assert {x.nom for x in m.pieces} == {x.nom for x in c.pieces}, "aucune pièce ajoutée ni retirée"


def test_desserte_barre_trop_haute_non_conforme():
    g = DG.calculer(dataclasses.replace(DG.ParametresDesserteGenoux(), hauteur_cadre=1250.0), 1)
    assert not g.verification("telescope_recouvrement").ok


def test_desserte_agenouilloir_retourne_devant():
    m, c = DG.calculer(None, 0), DG.calculer(None, 1)
    tm, tc = m.piece("desserte_tablette_mousse"), c.piece("desserte_tablette_mousse")
    assert tc.aabb[3] < 50 < tm.aabb[3]
    assert tc.aabb[4] > c.piece("desserte_tablette").aabb[4], "mousse au-dessus en CADRE"


def test_desserte_double_verrouillage_et_pincement():
    g = DG.calculer(None, 1)
    for code in ("telescope_double_securite", "agenouilloir_double_securite", "telescope_auto_enclenchement",
                 "pincement_barre_fourreau_fin_course", "pincement_barre_plateau_cisaillement",
                 "telescope_deverrouillage_sous_charge"):
        assert g.verification(code).ok


def test_desserte_sans_tirant_mural_non_conforme():
    g = DG.calculer(dataclasses.replace(DG.ParametresDesserteGenoux(), fixation_murale=False), 1)
    assert not g.verification("stabilite_vide_traction_barre").ok


def test_desserte_jeu_dangereux_detecte():
    g = DG.calculer(dataclasses.replace(DG.ParametresDesserteGenoux(), jeu_fin_course=15.0), 1)
    assert not g.verification("pincement_barre_fourreau_fin_course").ok
