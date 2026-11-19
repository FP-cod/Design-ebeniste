# -*- coding: utf-8 -*-
"""Tests de la grammaire du pouf vibrant, des deux gammes et de l'export STL."""

import pytest

from incognito.export_fabrication import exporter_tout
from incognito.grammaires.pouf_vibrant import (
    Etat,
    calculer,
    calculer_deux_etats,
    caisson_interieur,
    parametres_pouf_defaut,
    vers_parametres_fusion_pouf,
)
from incognito.parametres import (
    GAMME_SYBIAN_ENTREE,
    GAMME_SYBIAN_HAUT,
    NIVEAU_NON_CONFORME,
    ParametresGlobaux,
    ParametresSybian,
)
from incognito.regles import (
    ARCHITECTURE_PARALLELE,
    ARCHITECTURE_SERIE,
    recaler_module_vibrant,
)


def test_deux_etats_memes_parametres():
    params = parametres_pouf_defaut()
    etats = calculer_deux_etats(params)
    assert set(etats) == {Etat.POUF, Etat.MODULE}
    assert etats[Etat.POUF].parametres is params
    assert etats[Etat.MODULE].parametres is params
    assert "coussin_amovible" in {p.nom for p in etats[Etat.POUF].pieces}
    assert "coussin_amovible" not in {p.nom for p in etats[Etat.MODULE].pieces}
    assert "selle_peau" in {p.nom for p in etats[Etat.MODULE].pieces}
    assert "embout_npt" in {p.nom for p in etats[Etat.POUF].pieces}
    assert "capuchon_npt" in {p.nom for p in etats[Etat.POUF].pieces}


def test_gamme_change_recalcule_logement_et_silentblocs():
    haut = recaler_module_vibrant(GAMME_SYBIAN_HAUT, 0.75)
    entree = recaler_module_vibrant(GAMME_SYBIAN_ENTREE, 0.75)
    assert haut.logement.largeur_mm != entree.logement.largeur_mm or haut.logement.hauteur_mm != entree.logement.hauteur_mm
    assert haut.choix_silentblocs.silentbloc.materiau == "silicone"
    assert entree.choix_silentblocs.silentbloc.materiau == "caoutchouc"
    assert haut.fixations.entraxe_x_mm != 0
    assert entree.choix_silentblocs.frequence_propre_hz != haut.choix_silentblocs.frequence_propre_hz


def test_defauts_deux_gammes_conformes_et_logement_dans_caisson():
    for gamme in (GAMME_SYBIAN_HAUT, GAMME_SYBIAN_ENTREE):
        params = parametres_pouf_defaut(gamme=gamme)
        geo = calculer(Etat.POUF, params)
        assert geo.conforme
        interieur = caisson_interieur(params)
        rec = recaler_module_vibrant(gamme, params.masse_housse_kg)
        assert rec.logement.largeur_mm + 4 <= interieur.dx
        assert rec.logement.profondeur_mm + 4 <= interieur.dy
        verif = next(v for v in geo.verifications if v.code == "logement_rentre_dans_caisson")
        assert verif.ok
        trans = next(v for v in geo.verifications if v.code == "transmissibilite_isolation")
        assert trans.ok or trans.niveau != NIVEAU_NON_CONFORME


def test_module_invisible_en_pouf():
    geo = calculer(Etat.POUF, parametres_pouf_defaut())
    for p in geo.pieces:
        if p.role in {"interface", "selle", "actionneur", "capuchon", "silentbloc", "module"}:
            assert p.visible_exterieur_si_pouf is False
    assert next(v for v in geo.verifications if v.code == "module_invisible_en_pouf").ok
    enc = geo.encombrement()
    assert enc.z + enc.dz == pytest.approx(430.0, abs=2.0)


def test_housse_un_kg_hors_capacite_haut():
    geo = calculer(Etat.MODULE, parametres_pouf_defaut(gamme=GAMME_SYBIAN_HAUT, masse_housse_kg=1.0))
    v = next(x for x in geo.verifications if x.code == "masse_housse_capacite")
    assert v.ok is False
    assert v.compromis is True
    # 0,5 kg reste dans la capacité typique 15 Hz / 8 mm
    geo_ok = calculer(Etat.MODULE, parametres_pouf_defaut(masse_housse_kg=0.50))
    v_ok = next(x for x in geo_ok.verifications if x.code == "masse_housse_capacite")
    assert v_ok.ok is True


def test_architecture_serie_non_conforme_parallele_ok():
    ok = calculer(Etat.POUF, parametres_pouf_defaut(architecture=ARCHITECTURE_PARALLELE))
    ko = calculer(Etat.POUF, parametres_pouf_defaut(architecture=ARCHITECTURE_SERIE))
    assert ok.conforme
    assert not ko.conforme
    assert any(v.code == "architecture_masses" and not v.ok for v in ko.verifications)
    assert any(v.code == "encombrement_vertical" and not v.ok for v in ko.verifications)


def test_activation_modules_change_les_pieces():
    tout = calculer(Etat.MODULE, parametres_pouf_defaut(
        module_vibration=True, module_piston=True, module_rotation=True,
    ))
    vib_seul = calculer(Etat.MODULE, parametres_pouf_defaut(
        module_vibration=True, module_piston=False, module_rotation=False,
    ))
    noms_tout = {p.nom for p in tout.pieces}
    noms_v = {p.nom for p in vib_seul.pieces}
    assert "module_vibration" in noms_tout and "module_piston" in noms_tout
    assert "module_vibration" in noms_v
    assert "module_piston" not in noms_v
    assert "module_rotation" not in noms_v


def test_entree_n_a_pas_les_trois_etages():
    geo = calculer(Etat.MODULE, parametres_pouf_defaut(gamme=GAMME_SYBIAN_ENTREE))
    noms = {p.nom for p in geo.pieces}
    assert "carter_balourd" in noms
    assert "moteur_balourd" in noms
    assert "module_piston" not in noms


def test_globaux_sybian_basculent_la_grammaire():
    globaux = ParametresGlobaux(sybian=ParametresSybian(gamme=GAMME_SYBIAN_ENTREE))
    geo = calculer(Etat.POUF, parametres_pouf_defaut(globaux))
    assert geo.parametres.gamme == GAMME_SYBIAN_ENTREE
    assert geo.conforme


def test_export_fusion_et_stl(tmp_path):
    dico = vers_parametres_fusion_pouf()
    assert dico["inc_sybian_gamme"][0] in (0.0, 1.0)
    assert "inc_pouf_etat" in dico
    assert "inc_module_vibration" in dico
    assert dico["inc_masse_housse"][1] == "kg"
    fichiers = exporter_tout(tmp_path)
    noms = {f.name for f in fichiers}
    assert "silentbloc_tpu.stl" in noms
    assert "moule_selle_partie_basse.stl" in noms
    assert "moule_selle_partie_haute.stl" in noms
    for f in fichiers:
        texte = f.read_text(encoding="ascii")
        assert texte.startswith("solid ")
        assert "endsolid" in texte
        assert "vertex" in texte


def test_tension_230_rejetee():
    with pytest.raises(ValueError):
        parametres_pouf_defaut(tension_v=230.0)



def test_pilotage_au_cellules_panneaux_dans_la_grammaire():
    params = parametres_pouf_defaut()
    geo = calculer(Etat.POUF, params)
    noms = {p.nom for p in geo.pieces}
    assert "boitier_electronique" in noms
    assert "arret_urgence" in noms
    assert "cellule_charge_1" in noms and "butee_surcharge_4" in noms
    assert "panneau_acoustique_av" in noms
    assert "capot_acoustique_module" in noms
    boitier = geo.piece("boitier_electronique")
    assert boitier.visible_exterieur_si_pouf is False
    assert boitier.boite.rentre_dans(caisson_interieur(params))
    assert next(v for v in geo.verifications if v.code == "au_independant_esp32").ok
    assert next(v for v in geo.verifications if v.code == "presence_cellules_butees").ok
    assert next(v for v in geo.verifications if v.code == "treillis_pas_silentbloc").ok
    assert geo.conforme
    dico = vers_parametres_fusion_pouf()
    assert dico["inc_esp32"][0] == 1.0
    assert dico["inc_au_physique"][0] == 1.0
    assert dico["inc_presence_cellules"][0] == 1.0
    assert dico["inc_panneau_acoustique_epaisseur"][0] == 12.0


def test_export_contient_panneau_et_boitier(tmp_path):
    fichiers = exporter_tout(tmp_path)
    noms = {f.name for f in fichiers}
    assert "panneau_acoustique_labyrinthe.stl" in noms
    assert "boitier_electronique.stl" in noms
    assert "butee_surcharge.stl" in noms
