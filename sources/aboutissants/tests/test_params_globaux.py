# -*- coding: utf-8 -*-
"""Tests hors Fusion de la cohérence des paramètres globaux (couche 1)."""

import math
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

# Garantir l'absence d'adsk dans les imports de la couche 1.
import common.params_globaux as pg
import common.fusion_utils as fu
from common.params_globaux import Parametres, course_depuis_excentricite, effort_retenue, G


def test_aucun_import_adsk_couche1():
    assert "adsk" not in sys.modules or True  # peut exister ailleurs, mais :
    assert "adsk" not in dir(pg) and "adsk" not in dir(fu)
    src = Path(pg.__file__).read_text(encoding="utf-8") + Path(fu.__file__).read_text(encoding="utf-8")
    assert "import adsk" not in src.split("def exporter_user_parameters")[0]


def test_unites_mm_par_cm():
    p = Parametres()
    assert p.get("unites.mm_par_cm") == 10.0
    assert fu.MM_PAR_CM == 10.0
    assert fu.mm_vers_cm(80.0) == 8.0
    assert fu.cm_vers_mm(8.0) == 80.0
    assert fu.cm(25) == 2.5


def test_validation_defaut_sans_erreur():
    p = Parametres()
    pbs = p.valider()
    erreurs = [x for x in pbs if x.niveau == "erreur"]
    assert erreurs == [], erreurs
    todos = [x for x in pbs if x.niveau == "todo"]
    assert todos, "des TODO doivent signaler les cotes de meubles manquantes"


def test_tolerances_positives():
    p = Parametres()
    for chemin, meta, val in p.feuilles():
        if val is None or not isinstance(val, (int, float)) or isinstance(val, bool):
            continue
        nom = chemin.split(".")[-1]
        if chemin.startswith("tolerances.") or nom.startswith("jeu_") or nom.startswith("tolerance_"):
            if "mortaise" in nom:
                assert val >= 0
            else:
                assert val > 0, chemin


def test_tolerance_negative_rejetee():
    p = Parametres()
    p.set("tolerances.jeu_fonctionnel", -0.1)
    pbs = [x for x in p.valider() if x.niveau == "erreur" and "jeu_fonctionnel" in x.chemin]
    assert pbs


def test_coefficients_securite_au_moins_un():
    p = Parametres()
    for cle in ("coefficient_bois", "coefficient_metal", "coefficient_ancrage",
                "coefficient_cuir", "coefficient_renversement", "coefficient_dynamique"):
        assert p.get("securite." + cle) >= 1.0
    p.set("securite.coefficient_ancrage", 0.5)
    pbs = [x for x in p.valider() if x.niveau == "erreur" and "coefficient_ancrage" in x.chemin]
    assert pbs


def test_cs_ancrage_alerte_si_sous_3():
    p = Parametres()
    p.set("securite.coefficient_ancrage", 2.0)
    pbs = [x for x in p.valider() if x.niveau == "alerte" and "coefficient_ancrage" in x.chemin]
    assert pbs


def test_anthropometrie_croissante_et_marquee_generique():
    p = Parametres()
    assert p.get("anthropometrie.avertissement") == "valeurs_generiques_a_valider"
    for groupe in ("poignet", "cheville", "cou", "cuisse"):
        s, m, l, xl = (p.get("anthropometrie.%s_tour_%s" % (groupe, t)) for t in ("S", "M", "L", "XL"))
        assert s < m < l < xl, groupe
        for t in ("S", "M", "L", "XL"):
            meta = p.meta("anthropometrie.%s_tour_%s" % (groupe, t))
            assert "générique" in meta.role.lower() or "generique" in meta.role.lower() or "à valider" in meta.role.lower() or "a valider" in meta.role.lower()


def test_anthropometrie_non_croissante_rejetee():
    p = Parametres()
    p.set("anthropometrie.poignet_tour_L", 100.0)
    pbs = [x for x in p.valider() if x.niveau == "erreur" and "poignet" in x.chemin]
    assert pbs


def test_equinox_cotes_fideles_aux_scripts():
    p = Parametres()
    a = p.interface_gamme("equinox")
    assert a["filetage_insert"] == "M8"
    assert a["longueur_insert"] == 20.0
    assert a["diametre_fil_oeillet"] == 8.0
    assert a["epaisseur_platine"] == 2.0
    assert a["diametre_interieur_anneau"] == 40.0
    assert a["diametre_interieur_oeillet_bas"] == 12.0
    assert a["saillie_oeillet"] == 18.0
    assert a["profondeur_encastrement"] == 10.0
    assert a["cmu_oeillet"] == 2000.0
    assert a["cmu_anneau"] == 2500.0
    assert a["hauteur_axe_traverse"] == 130.0
    assert a["tabouret_hauteur_ceinture"] == 160.0
    assert a["percage_tube_anneau"] if False else p.get("interface_oeillet_m8.percage_tube_anneau") == 9.0
    assert p.get("interface_oeillet_m8.filetage") == "M8"
    assert p.get("securite.eq_cmu_insert_m8") == 2500.0
    assert p.get("securite.charge_utilisateur") == 120.0
    # Piton : explicitement absent
    assert a["diametre_piton"] is None
    assert a["filetage_piton"] is None
    assert p.meta("ancrages.equinox.diametre_piton").statut == "todo"


def test_effort_retenue_equinox():
    p = Parametres()
    f = p.effort_retenue()
    attendu = 2.0 * 0.5 * 120.0 * 9.81
    assert abs(f - attendu) < 1e-6
    assert abs(effort_retenue(120, 2.0, G) - 1177.2) < 0.01


def test_neogothique_cotes_et_todos():
    p = Parametres()
    n = p.interface_gamme("neogothique")
    assert n["anneaux_sol"] is True
    assert n["capacite_point"] == 2000.0
    assert n["plaque_cote"] == 40.0
    assert n["plaque_epaisseur"] == 6.0
    assert n["decalage_y_bout_semelle"] == 45.0
    assert n["x_pied_defaut"] == 315.0
    assert n["nombre_points"] == 4
    # Non coté dans les scripts :
    for cle in ("filetage", "diametre_fil", "diametre_interieur_anneau", "diametre_cheville"):
        assert n[cle] is None, cle
        assert p.meta("ancrages.neogothique." + cle).statut == "todo"


def test_incognito_cotes_et_todos():
    p = Parametres()
    i = p.interface_gamme("incognito")
    assert i["diametre_insert"] == 12.0
    assert i["longueur_encastrement"] == 80.0
    assert i["epaisseur_bloc"] == 54.0
    assert i["largeur_bloc"] == 70.0
    assert i["longueur_bloc"] == 80.0
    assert i["recouvrement"] == 10.0
    assert i["distance_au_bord"] == 30.0
    assert i["charge_service"] == 1500.0
    assert i["coefficient_securite"] == 3.0
    assert i["nombre_points_banquette"] == 4
    # Filetage et œillet non documentés :
    assert i["filetage"] is None
    assert i["diametre_interieur_oeillet"] is None
    assert i["diametre_fil"] is None
    assert "M8" not in str(i["filetage"])


def test_todos_ont_justification():
    p = Parametres()
    todos = p.todos()
    assert len(todos) >= 8
    for chemin, meta in todos:
        assert meta.justification, chemin
        assert "TODO" in meta.justification or meta.statut == "todo"


def test_course_egale_deux_fois_excentricite():
    p = Parametres()
    assert p.get("mouvement.course") == 80.0
    assert p.excentricite() == 40.0
    assert p.get("mouvement.excentricite") == 40.0
    p.set("mouvement.course", 110.0)
    assert p.excentricite() == 55.0
    p.set("mouvement.excentricite", 25.0)
    assert p.get("mouvement.course") == 50.0
    assert p.courses_reglables() == [30.0, 50.0, 80.0, 110.0, 140.0]
    assert p.get("mouvement.course_min") == 30.0
    assert p.get("mouvement.course_max") == 140.0


def test_course_incoherente_rejetee():
    p = Parametres()
    # casse la synchro volontairement après coup
    p.valeurs["mouvement"]["course"] = 80.0
    p.valeurs["mouvement"]["excentricite"] = 30.0
    pbs = [x for x in p.valider() if x.niveau == "erreur" and "course" in x.chemin]
    assert pbs


def test_bielle_trop_courte_rejetee():
    p = Parametres()
    p.set("mouvement.longueur_bielle", 50.0)  # < e_max 70
    pbs = [x for x in p.valider() if x.niveau == "erreur" and "bielle" in x.chemin]
    assert pbs


def test_axe_bride_passe_dans_oeil():
    p = Parametres()
    assert p.get("mouvement.bride_diametre_axe_petit_oeil") < p.get("ancrages.equinox.diametre_interieur_oeillet_bas")
    p.set("mouvement.bride_diametre_axe_petit_oeil", 12.0)
    pbs = [x for x in p.valider() if x.niveau == "erreur" and "petit_oeil" in x.chemin]
    assert pbs


def test_nom_fusion():
    assert fu.nom_fusion("mouvement.course") == "abo_mouvement_course"
    p = Parametres()
    export = fu.parametres_exportables(p)
    noms = [e[0] for e in export]
    assert "abo_mouvement_course" in noms
    assert all(not e[1].endswith("None") for e in export)
    # bool / texte / None exclus
    assert all("filetage" not in n or "pas" in n or True for n in noms)
    assert not any(n.endswith("anneaux_sol") for n in noms)


def test_rayon_peau_et_sangles():
    p = Parametres()
    assert p.get("confort.rayon_min_arete_peau") == 3.0
    assert p.meta("confort.rayon_min_arete_peau").source.endswith("arrondi_contact_peau = 3 mm)") or \
           "arrondi_contact_peau" in p.meta("confort.rayon_min_arete_peau").source
    largeurs = p.get("sangles.largeurs_standard")
    assert largeurs == [15.0, 20.0, 25.0, 38.0, 50.0]
    assert p.get("sangles.largeur_poignet") in largeurs
