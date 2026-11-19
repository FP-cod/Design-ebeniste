# -*- coding: utf-8 -*-
"""Catalogues : contenu, tracabilite, et reprise EXACTE des autres gammes."""

import importlib
import os
import sys

import pytest

from rangement.catalogues import bois, garnissage, quincaillerie, systemes, jonctions, entree
from rangement import sources as S

from conftest import WORKSPACE


def _importer(gamme, module):
    """Importe un module d'une autre gamme (sans la modifier) ; skip si absent."""
    racine = os.path.join(WORKSPACE, gamme)
    if not os.path.isdir(racine):
        pytest.skip("gamme %s absente" % gamme)
    sys.path.insert(0, racine)
    try:
        return importlib.import_module(module)
    finally:
        sys.path.remove(racine)


# --- essences ------------------------------------------------------------------
def test_essences_union_exacte_des_autres_gammes():
    eq = _importer("equinox", "equinox.catalogues.bois").BOIS
    neo = _importer("neogothique", "neogothique.catalogues.bois").BOIS
    inc = _importer("incognito", "incognito.parametres").ESSENCES_BASE
    abo = _importer("aboutissants", "catalogues.materiaux").BOIS
    tan = _importer("tantra", "tantra.parametres").ESSENCES
    tan_lib = _importer(os.path.join("tantra", "TantraGamme"), "lib.params_globaux").ESSENCES
    assert set(bois.ESSENCES) == set(eq) | set(neo) | set(inc) | set(abo) | set(tan) | set(tan_lib)


def test_essences_tantra_reprises():
    tan = _importer("tantra", "tantra.parametres").ESSENCES
    for cle in ("lamelle_hetre", "contreplaque_bouleau"):
        e = tan[cle]
        assert bois.ESSENCES[cle]["densite"] == e.masse_volumique_kg_m3
        assert bois.ESSENCES[cle]["module_elasticite"] == e.module_elasticite_mpa
        assert bois.ESSENCES[cle]["valeurs_autres_gammes"]["Tantra"]["fm_k"] == e.fm_k_mpa


def test_essences_valeurs_reprises_d_equinox():
    eq = _importer("equinox", "equinox.catalogues.bois").BOIS
    for cle, ent in eq.items():
        r = bois.ESSENCES[cle]
        for champ in ("densite", "module_elasticite", "resistance_flexion", "teinte"):
            assert r[champ] == ent[champ], (cle, champ)


def test_sigma_adm_reprise_d_incognito():
    inc = _importer("incognito", "incognito.parametres").ESSENCES_BASE
    for cle, ess in inc.items():
        assert bois.ESSENCES[cle]["sigma_adm_flexion"] == ess.contrainte_admissible_flexion_mpa


def test_essences_tracabilite():
    for cle, ent in bois.ESSENCES.items():
        assert ent["source"] and ent["gammes"], cle
        for champ in ent["a_valider"]:
            assert ent[champ] is None, (cle, champ)


def test_sigma_adm_repli_prudent():
    v, methode = bois.sigma_adm("erable_sycomore")
    assert methode == "repli_min_catalogue" and v == 10.0
    assert bois.sigma_adm("chene") == (14.0, "incognito")


def test_finitions():
    assert bois.finition_compatible("chene", "fumage_ammoniac")
    assert not bois.finition_compatible("noyer", "teinte_acetate_fer")
    neo = _importer("neogothique", "neogothique.catalogues.bois").FINITIONS_BOIS
    tan = _importer(os.path.join("tantra", "TantraGamme"), "lib.params_globaux").FINITIONS
    assert set(bois.FINITIONS_BOIS) == set(neo) | set(tan)
    assert not any(f["a_valider"] for f in bois.FINITIONS_BOIS.values())


# --- cuirs et teintes ------------------------------------------------------------
def test_teintes_cuir_union_exacte():
    eq = _importer("equinox", "equinox.catalogues.garnissage").GARNISSAGES
    neo = _importer("neogothique", "neogothique.catalogues.garnissage").GARNISSAGE
    inc = _importer("incognito", "incognito.parametres").REVETEMENTS_BASE
    attendu = set()
    for cle in eq:  # iteration sans alias
        if eq[cle]["famille"] != "tissu" and not eq[cle]["famille"].startswith("tissu"):
            attendu |= set(eq[cle]["coloris"])
    for ent in neo.values():
        attendu |= set(ent["coloris"])
    for r in inc.values():
        if r.famille == "cuir":
            attendu |= set(r.couleurs_typiques)
    gc = _importer("gamme_cuir", "gamme_cuir.catalogues.cuirs")
    for ent in list(gc.CUIRS.values()) + list(gc.DOUBLURES.values()):
        attendu |= set(ent["teintes"])
    assert set(gc.TEINTES) <= attendu
    attendu |= {"cognac", "noir"}  # Tantra : cuir_cognac / cuir_noir
    assert set(garnissage.TEINTES_CUIR) == attendu
    assert garnissage.TEINTES_CUIR["tan"] and all(s.startswith("GammeCuir:") for s in garnissage.TEINTES_CUIR["tan"])


def test_familles_reprises_avec_coloris_identiques():
    eq = _importer("equinox", "equinox.catalogues.garnissage").GARNISSAGES
    neo = _importer("neogothique", "neogothique.catalogues.garnissage").GARNISSAGE
    inc = _importer("incognito", "incognito.parametres").REVETEMENTS_BASE
    for cle in eq:
        assert garnissage.GARNISSAGES[cle]["coloris"] == eq[cle]["coloris"]
    for cle, ent in neo.items():
        assert garnissage.GARNISSAGES[cle]["coloris"] == ent["coloris"]
    for cle, r in inc.items():
        assert tuple(garnissage.GARNISSAGES[cle]["coloris"]) == r.couleurs_typiques
    gc = _importer("gamme_cuir", "gamme_cuir.catalogues.cuirs")
    for cle, ent in list(gc.CUIRS.items()) + list(gc.DOUBLURES.items()):
        assert garnissage.GARNISSAGES[cle]["coloris"] == ent["teintes"]
        assert garnissage.GARNISSAGES[cle]["epaisseur_plage"] == ent["epaisseur_plage"]
    tan = _importer("tantra", "tantra.parametres").REVETEMENTS
    for cle in tan:
        nous = garnissage.GARNISSAGES.get(cle if cle not in inc else "tantra_" + cle)
        assert nous is not None and nous["gamme"] == "Tantra", cle


def test_teintes_sources():
    assert "noir" in garnissage.TEINTES_CUIR and len(garnissage.TEINTES_CUIR["noir"]) >= 3
    assert {s.split(":")[0] for s in garnissage.TEINTES_CUIR["noir"]} == {"Equinox", "Neogothique", "Incognito", "Tantra", "GammeCuir"}
    assert not garnissage.est_cuir("velours") and garnissage.est_cuir("cuir_harnais_noir")


# --- quincaillerie, ports Aboutissants --------------------------------------------
def test_metaux_repris():
    abo = _importer("aboutissants", "catalogues.materiaux").METAUX
    for cle in ("inox_316", "inox_304", "laiton_cw614n", "laiton_cw510l"):
        for champ in ("densite", "module_elasticite", "limite_elastique"):
            assert quincaillerie.METAUX[cle][champ] == abo[cle][champ]


def test_cotes_ports_identiques_a_aboutissants():
    from rangement.parametres import Parametres
    pg = _importer("aboutissants", "common.params_globaux")
    a = pg.Parametres()
    r = Parametres()
    paires = {"ports.plug_longueur": "vac_u_lock.plug_longueur",
              "ports.plug_diametre_tete": "vac_u_lock.plug_diametre_tete_max",
              "ports.plug_diametre_tige": "vac_u_lock.plug_diametre_tige_max",
              "ports.npt_diametre_exterieur": "npt_1.diametre_exterieur",
              "ports.npt_longueur_utile": "npt_1.longueur_utile_L2",
              "ports.npt_longueur_totale": "npt_1.longueur_totale_L4",
              "ports.npt_depassement": "npt_1.depassement_recommande",
              "ports.pas_ports": "cadre_modulaire.pas_ports",
              "discretion.epaisseur_cache": "vac_u_lock.cache_epaisseur"}
    for nous, eux in paires.items():
        assert r.get(nous) == a.get(eux), nous
    assert r.meta("ports.montage_arriere").choix == a.meta("vac_u_lock.montage_arriere").choix
    assert r.meta("ports.filetage_ergot").choix == a.meta("vac_u_lock.filetage_cote_machine").choix
    assert r.get("ports.filetage_ergot") == a.get("vac_u_lock.filetage_cote_machine")
    assert r.get("ports.filetage_ergot_longueur") == a.get("vac_u_lock.filetage_cote_machine_longueur")


def test_insert_et_attaches_equinox():
    att = _importer("equinox", "equinox.catalogues.attaches").ATTACHES
    for cle in ("vis_bois_inox", "insert_filete_m8", "vis_barillet_m8"):
        assert quincaillerie.VISSERIE[cle]["capacite_service"] == att[cle]["capacite_service"]
    assert jonctions.JONCTIONS["tenon_mortaise"]["capacite_service"] == att["tenon_mortaise"]["capacite_service"]
    assert jonctions.DIAMETRES_TOURILLON == att["tourillon_hetre"]["diametres"]


# --- systemes ----------------------------------------------------------------------
def test_systemes_complets():
    for cle, ent in systemes.SYSTEMES.items():
        assert ent["famille"] in systemes.FAMILLES, cle
        assert ent["source"], cle
        c = ent["compromis"]
        for k in ("capacite", "discretion", "solidite", "cout"):
            assert 1 <= c[k] <= 5, (cle, k)
        assert c["texte"]
        if S.A_VALIDER in ent["source"] and not ent["source"].count("/"):
            assert ent["a_valider"], cle
    for fam in systemes.FAMILLES:
        assert len(systemes.par_famille(fam)) >= 3, fam


def test_entree_catalogue():
    assert entree("bois", "chene")["nom_latin"].startswith("Quercus")
    with pytest.raises(KeyError):
        entree("bois", "teck")


# --- jonctions ---------------------------------------------------------------------
@pytest.mark.parametrize("e,d", [(12.0, 6.0), (18.0, 8.0), (22.0, 10.0), (30.0, 14.0)])
def test_diametre_tourillon(e, d):
    assert jonctions.diametre_tourillon(e) == d
    c = jonctions.cotes_tourillon(e)
    assert c["longueur"] == 5 * d and c["alesage_chant"] == 2.5 * d


def test_cotes_tenon():
    c = jonctions.cotes_tenon(22.0, 22.0)
    assert c["epaisseur_tenon"] == 7.0 and abs(c["profondeur_mortaise"] - 17.6) < 1e-9
    assert jonctions.distance_barillet() == 25.0
