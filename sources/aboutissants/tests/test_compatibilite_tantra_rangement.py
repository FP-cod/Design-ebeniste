# -*- coding: utf-8 -*-
"""Fidélité des cotes Tantra / Rangement, TODO, et matrices de compatibilité."""

import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from common.params_globaux import Parametres, GAMMES_ANCRAGES, TODO
from catalogues.compatibilite import (
    GAMMES, INTERFACES, STATUTS, matrice_interfaces_gammes, decisions_a_trancher,
)
from cadres.cadre_modulaire import matrice_compatibilite, ANCRAGES_MEUBLES_MATRICE, TYPOLOGIES
import catalogues.compatibilite as compat_mod
import common.params_globaux as pg


def test_aucun_import_adsk_dans_les_modules_ajoutes():
    src = Path(compat_mod.__file__).read_text(encoding="utf-8")
    assert "import adsk" not in src and "from adsk" not in src
    # La couche 1 n'importe adsk qu'à l'export Fusion.
    src1 = Path(pg.__file__).read_text(encoding="utf-8")
    assert "import adsk" not in src1.split("def exporter_user_parameters")[0]


def test_gammes_ancrages_etendues():
    assert GAMMES_ANCRAGES == ("equinox", "neogothique", "incognito", "tantra", "rangement")
    assert GAMMES == GAMMES_ANCRAGES
    assert ANCRAGES_MEUBLES_MATRICE == GAMMES_ANCRAGES
    p = Parametres()
    for g in GAMMES_ANCRAGES:
        d = p.interface_gamme(g)
        assert d and isinstance(d, dict)


def test_tantra_cotes_fideles_aux_scripts():
    p = Parametres()
    t = p.interface_gamme("tantra")
    assert t["filetage"] == "M12"
    assert t["filetage_diametre"] == 12.0
    assert t["diametre_insert"] == 16.0
    assert t["longueur_encastrement"] == 60.0
    assert t["charge_service"] == 1500.0
    assert t["coefficient_securite"] == 3.0
    assert t["charge_rupture_visee"] == 4500.0
    assert t["poids_personne"] == 1100.0
    assert t["facteur_dynamique"] == 1.5
    assert t["retrait_ancre_sous_surface"] == 10.0
    assert t["cache_diametre"] == 40.0
    assert t["cache_epaisseur"] == 10.0
    assert t["anneau_diametre_cuvette"] == 50.0
    assert t["anneau_profondeur_cuvette"] == 12.0
    assert t["bloc_min_epaisseur"] == 50.0
    assert t["bloc_min_longueur"] == 80.0
    assert t["bloc_epaisseur_defaut"] == 50.0
    assert t["bloc_largeur_defaut"] == 80.0
    assert t["bloc_longueur_defaut"] == 80.0
    assert t["distance_bord_min"] == 25.0
    assert t["tourillon_liaison_diametre"] == 12.0
    assert t["tourillon_liaison_longueur"] == 50.0
    assert t["pas"] == 1.75  # ISO, pas une cote inventée de meuble
    assert t["presence_npt"] is False
    assert t["presence_vac_u_lock"] is False
    assert p.get("npt_1.present_tantra") is False
    # Typologies livrées : comptes d'ancrages sourcés.
    assert t["chaise_double_courbe_nombre"] == 4
    assert t["chaise_double_courbe_positions_y"] == [760.0, 1560.0]
    assert t["fauteuil_lombaire_nombre"] == 2
    assert t["banquette_deux_niveaux_nombre"] == 6
    assert t["siege_repose_genoux_nombre"] == 4
    assert t["camo_canape_nombre"] == 6
    assert t["camo_fauteuil_nombre"] == 4
    assert t["cadre_desserte_nombre"] == 4
    assert t["cadre_desserte_hauteur_meuble"] == 750.0
    assert t["cadre_desserte_hauteur_cadre"] == 1150.0
    # Sources citées.
    assert "INSERT_ANCRE_M12" in p.meta("ancrages.tantra.diametre_insert").source
    assert p.meta("ancrages.tantra.filetage").source.endswith("filetage'] = 12.0)") or \
           "filetage" in p.meta("ancrages.tantra.filetage").source


def test_tantra_todos_non_inventes():
    p = Parametres()
    t = p.interface_gamme("tantra")
    for cle in (
        "diametre_interieur_anneau",
        "diametre_fil",
        "emplacement_collecteur",
        "emplacement_machine",
        "cadre_table_inclinee_nombre",
    ):
        assert t[cle] is None, cle
        meta = p.meta("ancrages.tantra." + cle)
        assert meta.statut == TODO
        assert meta.justification
        assert "TODO" in meta.justification


def test_rangement_cotes_fideles_aux_scripts():
    p = Parametres()
    r = p.interface_gamme("rangement")
    assert r["filetage_insert"] == "M8"
    assert r["longueur_insert"] == 20.0
    assert r["cmu_insert_m8"] == 2500.0
    assert r["point_ancrage_personne"] is False
    assert r["effort_accidentel"] == 300.0
    assert r["ports_vac_u_lock"] is True
    assert r["ports_npt"] is True
    assert r["montage_arriere_defaut"] == "npt_1_male"
    assert r["systeme_port_defaut"] == "port_vac_u_lock_npt"
    assert r["filetage_ergot"] == "M8x1.25"
    assert r["filetage_ergot_longueur"] == 16.0
    assert r["pas_ports"] == 200.0
    assert r["epaisseur_panneau_mural"] == 22.0
    assert r["epaisseur_cache"] == 10.0
    assert r["plot_largeur"] == 70.0
    assert r["plot_profondeur"] == 40.0
    assert r["ports_par_module"] == 2
    assert r["hauteur_ports"] == 130.0
    assert r["crochets_par_module"] == 4
    assert r["hauteur_crochets"] == 400.0
    assert r["hauteur_pose"] == 900.0
    assert r["module_largeur"] == 600.0
    assert r["module_hauteur"] == 320.0
    assert r["nombre_barres"] == 2
    assert r["hauteur_premiere_barre"] == 680.0
    assert p.get("npt_1.present_rangement") is True
    assert "filetage_insert" in p.meta("ancrages.rangement.filetage_insert").source
    assert "ratelier" in p.meta("ancrages.rangement.point_ancrage_personne").justification.lower()


def test_rangement_todos_non_inventes():
    p = Parametres()
    r = p.interface_gamme("rangement")
    for cle in (
        "capacite_support_mur",
        "emplacement_collecteur",
        "emplacement_machine",
        "diametre_interieur_anneau",
        "diametre_fil",
    ):
        assert r[cle] is None, cle
        meta = p.meta("ancrages.rangement." + cle)
        assert meta.statut == TODO
        assert meta.justification
        assert "TODO" in meta.justification


def test_sources_citent_les_depots_sans_les_inventer():
    p = Parametres()
    for chemin, meta, val in p.feuilles():
        if not chemin.startswith("ancrages.tantra.") and not chemin.startswith("ancrages.rangement."):
            continue
        if val is None:
            assert meta.statut == TODO
            assert meta.justification
        else:
            assert meta.statut != TODO
            assert meta.source, chemin


def test_matrice_interfaces_complete_et_statuts():
    m = matrice_interfaces_gammes()
    for interface in INTERFACES:
        for g in GAMMES:
            c = m["interfaces"][interface][g]
            assert c["statut"] in STATUTS
            assert c["note"]
    # Décisions clés, fondées sur les scripts (rien d'inventé).
    itf = m["interfaces"]
    assert itf["interface_oeillet_m8"]["equinox"]["statut"] == "compatible"
    assert itf["interface_oeillet_m8"]["tantra"]["statut"] == "compatible_adaptateur"
    assert itf["interface_oeillet_m8"]["rangement"]["statut"] == "incompatible"
    assert itf["port_vac_u_lock"]["rangement"]["statut"] == "compatible"
    assert itf["port_vac_u_lock"]["tantra"]["statut"] == "limite"
    assert itf["npt_1"]["tantra"]["statut"] == "incompatible"
    assert itf["npt_1"]["rangement"]["statut"] == "compatible"
    assert itf["collecteur_urine"]["rangement"]["statut"] == "incompatible"
    assert itf["collecteur_urine"]["tantra"]["statut"] == "limite"
    assert itf["sex_machine_mecanique"]["rangement"]["statut"] == "incompatible"
    assert itf["sex_machine_mecanique"]["tantra"]["statut"] == "limite"
    # Notes : M12, pas un ancrage de personne, ports natifs.
    assert "M12" in itf["interface_oeillet_m8"]["tantra"]["note"]
    note_ran = itf["interface_oeillet_m8"]["rangement"]["note"].lower()
    assert "pas un point d'ancrage" in note_ran or "n'est pas un point d'ancrage" in note_ran
    assert "natif" in itf["port_vac_u_lock"]["rangement"]["note"].lower()


def test_matrice_cadres_inclut_tantra_et_rangement():
    m = matrice_compatibilite()
    for typ in TYPOLOGIES:
        for g in ("tantra", "rangement"):
            c = m["meubles"][typ][g]
            assert c["statut"] in m["statuts"]
            assert c["note"]
    assert m["meubles"]["cadre_sol"]["tantra"]["statut"] == "compatible_adaptateur"
    assert m["meubles"]["cadre_sol"]["rangement"]["statut"] == "limite"
    assert "M12" in m["meubles"]["cadre_sol"]["tantra"]["note"]
    assert "ancrage de personne" in m["meubles"]["cadre_sol"]["rangement"]["note"]


def test_decisions_a_trancher_sont_documentees():
    decisions = decisions_a_trancher()
    ids = {d["id"] for d in decisions}
    assert "tantra_di_fil_anneau" in ids
    assert "tantra_m12_vs_m8" in ids
    assert "rangement_montage_arriere" in ids
    assert "rangement_ancrage_personne" in ids
    for d in decisions:
        assert d["sujet"] and d["question"]
    # Les cellules marquées decision_fabien correspondent à un vrai choix.
    m = matrice_interfaces_gammes()
    marques = [
        (i, g) for i in INTERFACES for g in GAMMES
        if m["interfaces"][i][g]["decision_fabien"]
    ]
    assert ("interface_oeillet_m8", "tantra") in marques
    assert ("port_vac_u_lock", "rangement") in marques
    assert ("npt_1", "rangement") in marques


def test_validation_defaut_reste_sans_erreur():
    p = Parametres()
    erreurs = [x for x in p.valider() if x.niveau == "erreur"]
    assert erreurs == [], erreurs
    todos = p.todos()
    chemins = [c for c, _ in todos]
    assert any(c.startswith("ancrages.tantra.") for c in chemins)
    assert any(c.startswith("ancrages.rangement.") for c in chemins)
