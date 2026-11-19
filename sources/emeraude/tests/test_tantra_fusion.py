# -*- coding: utf-8 -*-
"""Scripts Fusion : importables sans adsk, plan de construction cohérent."""
import importlib
import os

import pytest

import tantra_commun as TC
from tantra import registre

DOSSIER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts_fusion")


@pytest.mark.parametrize("fichier", sorted(f for f in os.listdir(DOSSIER) if f.endswith(".py")))
def test_scripts_importables_et_run(fichier):
    m = importlib.import_module(fichier[:-3])
    if fichier != "tantra_commun.py":
        assert callable(getattr(m, "run"))


def test_un_script_par_typologie():
    for nom in registre.REGISTRE:
        f = nom if nom.startswith("tantra_") else f"tantra_{nom}"
        assert os.path.exists(os.path.join(DOSSIER, f + ".py")), nom


@pytest.mark.parametrize("nom,etat", [(n, e) for n, x in registre.REGISTRE.items() for e in x.etats])
def test_plan_piece_restitue_aabb(nom, etat):
    for p in registre.geometrie(nom, etat).pieces:
        base, milieu, pts = TC.plan_piece(p)
        assert base == TC.PLAN_DE_BASE[p.axe]
        assert all(TC.composante_axe(q, p.axe) == pytest.approx(milieu) for q in pts)
        b = p.aabb
        lo = {"x": b[0], "y": b[2], "z": b[4]}[p.axe]
        hi = {"x": b[1], "y": b[3], "z": b[5]}[p.axe]
        assert milieu - p.epaisseur / 2 == pytest.approx(lo) and milieu + p.epaisseur / 2 == pytest.approx(hi)


def test_expression_fusion():
    assert TC.expression_fusion(0, "") == "0"
    assert TC.expression_fusion(12.5, "mm") == "12.5 mm"


def test_tous_les_parametres():
    import tantra_parametres_fusion as T
    d = T.tous_les_parametres()
    assert "tan_desserte_etat" in d and "tan_canape_etat" in d


def test_rapport_markdown(tmp_path):
    from tantra import rapport
    b = rapport.bloc_markdown("cadre_desserte_genoux")
    assert rapport.DEBUT in b and "CADRE" in b and "novembre 2026" in b
    (tmp_path / "camo_canape.md").write_text("# Canapé\n\ntexte main\n\n" + rapport.DEBUT + "\nvieux\n" + rapport.FIN)
    rapport.mettre_a_jour(str(tmp_path))
    t = (tmp_path / "camo_canape.md").read_text()
    assert "texte main" in t and "vieux" not in t
    assert "| camo_canape |" in rapport.tableau_chiffrages_markdown()
