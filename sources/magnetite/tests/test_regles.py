# -*- coding: utf-8 -*-
import pytest

from gamme_cuir import regles
from gamme_cuir.parametres import Parametres


def constats(**surcharges):
    s = {k.replace("__", "."): v for k, v in surcharges.items()}
    return regles.evaluer(Parametres(s, json_utilisateur=False), {})


def codes(cs, niveau):
    return {c.code for c in cs if c.niveau == niveau}


def test_defauts_sans_echec():
    assert codes(constats(), "ECHEC") == set()


def test_effort_requis():
    assert regles.effort_requis(Parametres(json_utilisateur=False)) == pytest.approx(500 * 1.5 * 4)


@pytest.mark.parametrize("teinte,metal,attendu", [
    ("cognac", "laiton_massif_cw510l", "conseille"), ("tan", "laiton_massif_cw510l", "conseille"),
    ("noir", "inox_316", "conseille"), ("cognac", "inox_316", "possible"),
    ("noir", "laiton_massif_cw510l", "possible"), ("bleu_nuit", "laiton_patine", "inhabituel"),
])
def test_accord_metal_teinte(teinte, metal, attendu):
    assert regles.accord_metal_teinte(teinte, metal) == attendu


def test_scratch_deconseille_en_contention():
    assert "scratch" in codes(constats(finition__fermeture="scratch", produit__usage="contention"), "ECHEC")
    assert "scratch" in codes(constats(finition__fermeture="scratch", produit__usage="jeu_leger"), "ALERTE")


def test_cadenas():
    cs = constats(finition__fermeture="boucle_ardillon_cadenas")
    assert "cadenas_boucle" in codes(cs, "ECHEC")
    cs = constats(finition__fermeture="boucle_ardillon_cadenas", finition__boucle="boucle_verrouillable_50_inox",
                  finition__quincaillerie="inox_316", anneau_d__reference="anneau_d_inox_soude_6x30")
    assert codes(cs, "ECHEC") == set() and "cadenas_cle" in codes(cs, "ALERTE")
    cs = constats(finition__fermeture="boucle_ardillon_cadenas", finition__boucle="boucle_verrouillable_50_inox",
                  securite__deverrouillage_rapide=False)
    assert "cadenas_sans_secours" in codes(cs, "ECHEC")


def test_deverrouillage_rapide_recommande():
    assert "deverrouillage" in codes(constats(securite__deverrouillage_rapide=False), "ALERTE")


def test_pas_d_arete_vive():
    assert "arete_vive" in codes(constats(finition__tranche="brute"), "ECHEC")
    assert "rayon_tranche" in codes(constats(extremites__rayon_tranche=0.3), "ALERTE")


def test_coin_vif():
    assert "coin_vif" in codes(constats(extremites__rayon_ratio=0.1, sangles__largeur_menotte_poignet=40.0,
                                        anneau_d__largeur_patte=25.0), "ECHEC")


def test_quincaillerie_dimensions():
    assert "passage_boucle" in codes(constats(produit__membre="cheville"), "ECHEC")  # bande 60 / boucle 50
    assert "trou_ardillon" in codes(constats(ardillon__diametre_trou=4.2), "ECHEC")
    assert "passage_anneau" in codes(constats(anneau_d__largeur_patte=30.0), "ECHEC")
    assert "boucle_trop_large" in codes(constats(sangles__largeur_menotte_poignet=40.0,
                                                 anneau_d__largeur_patte=25.0), "ALERTE")


def test_materiaux():
    assert "tranche_matiere" in codes(constats(cuir__matiere="vachette_chrome_pleine_fleur",
                                               cuir__epaisseur_exterieure=3.0, finition__teinte="noir"), "ECHEC")
    assert "teinte_matiere" in codes(constats(cuir__matiere="cuir_harnais_vegetal", finition__teinte="tan"), "ECHEC")
    assert "contact_peau" in codes(constats(finition__quincaillerie="acier_nickele"), "ALERTE")
    assert "quincaillerie_depareillee" in codes(constats(finition__quincaillerie="inox_316"), "ALERTE")
    assert "cintrage" in codes(constats(cuir__epaisseur_exterieure=5.0, produit__taille="S"), "ALERTE")


def test_estimations_jamais_conformes():
    cs = constats()
    charges = [c for c in cs if c.code in ("charge_estimee", "charge")]
    assert charges and all(c.niveau == "ALERTE" and "fournisseur" in c.message for c in charges)
    assert "essai_patte" in codes(cs, "ALERTE")
    seuls_rivets = constats(anneau_d__fixation_patte="rivets")
    assert any("rivets de patte" in c.message and "insuffisant" in c.message for c in seuls_rivets)


def test_resistance_cuir():
    cs = constats(cuir__epaisseur_exterieure=2.0, sangles__largeur_menotte_poignet=40.0,
                  finition__boucle="boucle_rouleau_50_laiton")
    assert "resistance_cuir" in codes(cs, "ECHEC")


def test_rivet_longueur_introuvable():
    cs = constats(jonctions__rivet="rivet_double_calotte_9")
    assert "rivet_longueur" in codes(cs, "ECHEC")
