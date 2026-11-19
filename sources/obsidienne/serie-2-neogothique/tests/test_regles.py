# -*- coding: utf-8 -*-
import pytest

from neogothique import regles


def _a(ajust, chemin):
    return next(a for a in ajust if a.chemin == chemin)


def test_noyer_vers_chene(params):
    q, aj = regles.changer_materiau(params, "bois.essence", "chene")
    assert q.get("bois.essence") == "chene" and params.get("bois.essence") == "noyer"  # original intact
    assert _a(aj, "entrave.platine.epaisseur").apres == 48.0
    assert any(a.statut == "recalcul" and a.regle == "bois_masse" for a in aj)
    assert q.get("tolerances.jeu_mortaise_oblongue") > params.get("tolerances.jeu_mortaise_oblongue")
    assert any("tanins" in a.explication for a in aj if a.statut == "alerte")


def test_fer_vers_laiton_sections_augmentees(params):
    q, aj = regles.changer_materiau(params, "ferrures.metal", "laiton_mat")
    for chemin in ("loquet.pene_diametre", "ferrures.axe_pivot_diametre", "synchro.arbre_diametre",
                   "ferrures.fer_plat_epaisseur", "cremaillere.barre_epaisseur"):
        assert q.get(chemin) > params.get(chemin), chemin
    assert q.get("cremaillere.module") == 4.0           # serie normalisee
    assert q.get("ferrures.finition") == "laiton_brosse_vernis_mat"
    assert not q.erreurs()
    assert any("engrenages" in a.explication or "pignons" in a.explication for a in aj if a.statut == "alerte")


def test_aller_retour_quasi_reversible(params):
    q, _ = regles.changer_materiau(params, "ferrures.metal", "laiton_mat")
    r, _ = regles.changer_materiau(q, "ferrures.metal", "fer_forge_mat")
    for chemin in ("loquet.pene_diametre", "ferrures.axe_pivot_diametre", "synchro.arbre_diametre"):
        assert abs(r.get(chemin) - params.get(chemin)) <= 1.0  # arrondis superieurs
    assert r.get("ferrures.finition") == "cire_noire"


def test_cuir_harnais_puis_retour(params):
    q, aj = regles.changer_materiau(params, "garnissage.cuir_manilles", "cuir_harnais_noir")
    assert q.get("garnissage.epaisseur_manille") == 4.0
    assert q.get("garnissage.largeur_manille_cou") == 75.0
    r, _ = regles.changer_materiau(q, "garnissage.cuir_manilles", "cuir_renforce_double_noir")
    assert r.get("garnissage.largeur_manille_cou") == 60.0 and r.get("garnissage.epaisseur_manille") == 6.5


def test_pivot_rotule(params):
    q, aj = regles.changer_materiau(params, "entrave.manilles.pivot_cou", "rotule")
    assert q.get("entrave.manilles.hauteur_pivot") == 40.0
    assert q.get("ferrures.axe_pivot_diametre") >= 20.0


def test_chene_fume_finition_et_alerte(params):
    q, aj = regles.changer_materiau(params, "bois.essence", "chene_fume")
    assert q.get("bois.finition") == "fumage_ammoniac"
    assert any("avant fumage" in a.explication for a in aj)


def test_cascade_finition_bois():
    from neogothique.parametres import Parametres
    p = Parametres.pour_typologie("entrave", {"bois.essence": "chene", "bois.finition": "teinte_acetate_fer"},
                                  json_utilisateur=False)
    q, aj = regles.changer_materiau(p, "bois.essence", "noyer")
    assert q.get("bois.finition") in ("huile_cire_noire", "cire_naturelle")
    assert any(a.regle == "cascade_finition_bois" for a in aj)


def test_galvanisation_jeu(params):
    q, aj = regles.changer_materiau(params, "ferrures.finition", "galvanisation_peinture_mate")
    assert q.get("tolerances.jeu_axes") == 0.5


def test_jonction_tourillons_alerte(params):
    q, aj = regles.changer_materiau(params, "jonctions.type_joues_fourreau", "chevillage")
    assert q.get("jonctions.type_joues_fourreau") == "chevillage"


def test_selection_inconnue(params):
    with pytest.raises(KeyError):
        regles.changer_materiau(params, "bois.inconnu", "chene")
    with pytest.raises(KeyError):
        regles.changer_materiau(params, "bois.essence", "ebene")


def test_meme_materiau_sans_ajustement(params):
    q, aj = regles.changer_materiau(params, "bois.essence", "noyer")
    assert [a for a in aj if a.statut == "ajuste"] == []


def test_rapport_lisible(params):
    _, aj = regles.changer_materiau(params, "ferrures.metal", "laiton_mat")
    txt = regles.rapport(aj)
    assert "AJUSTE loquet.pene_diametre : 12 mm -> 14 mm" in txt
    assert regles.rapport([]) == "Aucun ajustement."


def test_operation_inconnue(params):
    with pytest.raises(ValueError):
        regles.appliquer_regle(params, {"id": "x", "operation": "magie", "cibles": ["bois.essence"]}, {}, {}, "t")
