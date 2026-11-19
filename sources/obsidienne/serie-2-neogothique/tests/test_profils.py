# -*- coding: utf-8 -*-
"""Geometrie pure : chants moulures, traces, sections, motifs gothiques, terminaisons, blocs."""
import math

import pytest

from neogothique import profils as pf
from neogothique import fusion_outils as fo
from neogothique.catalogues import TERMINAISONS


@pytest.mark.parametrize("type_", pf.TYPES_CHANT)
def test_chants_locaux_continus(type_):
    segs, face, cote = pf.chant_local(type_, 6.0, 20.0, 10.0)
    if type_ == "droit":
        assert segs == []
        return
    pts = pf.echantillonner(segs, 8)
    assert pts[0] == pytest.approx(face) and pts[-1] == pytest.approx(cote)
    for a, b in zip(segs, segs[1:]):
        assert a[-1] == pytest.approx(b[1])
    assert cote[0] == 0.0 and face[1] == 0.0


def test_quart_de_cercle_controle():
    with pytest.raises(ValueError):
        pf.quart((0, 0), (3, -5), True)
    convexe = pf.quart((0.0, 10.0), (5.0, 5.0), True)
    creux = pf.quart((0.0, 10.0), (5.0, 5.0), False)
    # convexe : milieu de l'arc cote exterieur (d plus petit) ; creux : cote matiere
    assert convexe[2][0] < creux[2][0]


def test_section_rectangulaire_exacte_et_bec_de_corbin():
    droit = pf.trace_bloc(50.0, 0.0).segments
    s = pf.proprietes_section(200.0, droit)
    assert s["aire"] == pytest.approx(400 * 50, rel=1e-6)
    assert s["inertie"] == pytest.approx(400 * 50 ** 3 / 12.0, rel=1e-3)
    moul = pf.trace_bloc(50.0, 0.0, ("conge", 4), ("bec_de_corbin", 14, 31, 14)).segments
    m = pf.proprietes_section(200.0, moul)
    perte = 1 - min(m["w_inf"], m["w_sup"]) / (400 * 50 ** 2 / 6.0)
    assert 0.02 < perte < 0.10                     # la moulure allege sans affaiblir (< 10 %)
    assert pf.evaluer(moul, 50.0) == pytest.approx(4.0) and pf.evaluer(moul, 0.0) == pytest.approx(14.0)


def test_chants_trop_hauts():
    with pytest.raises(ValueError):
        pf.trace_bloc(30.0, 0.0, ("conge", 10), ("bec_de_corbin", 14, 25, 14))


def test_ogive_et_arcature():
    o = pf.ogive(0.0, 0.0, 40.0, 60.0)
    assert pf.chemin_ferme(o)
    pts = pf.echantillonner(o, 16)
    assert max(p[1] for p in pts) == pytest.approx(60.0)
    assert max(p[0] for p in pts) == pytest.approx(20.0)
    for motif in ("ogive", "trilobe", "quadrilobe"):
        boucles, w, montant = pf.ajours_arcature(480.0, 80.0, 5, motif, 10.0, 0.55)
        assert len(boucles) == 5 and all(pf.chemin_ferme(b) for b in boucles)
        assert montant == pytest.approx(96.0 - w)
        for b in boucles:
            ps = pf.echantillonner(b, 16)
            assert min(p[1] for p in ps) >= 10.0 - 1e-6 and max(p[1] for p in ps) <= 70.0 + 1e-6


@pytest.mark.parametrize("term", pf.TERMINAISONS_FORMES)
def test_terminaisons_fermees_et_dans_l_envergure(term):
    segs = pf.penture(160.0, 28.0, term)
    assert pf.chemin_ferme(segs)
    pts = pf.echantillonner(segs, 16)
    assert max(p[0] for p in pts) == pytest.approx(160.0, abs=0.5)
    assert max(abs(p[1]) for p in pts) <= TERMINAISONS[term]["envergure_relative"] * 28.0 + 1.0
    # la bande droite (rivets) garde toute sa largeur avant la terminaison
    lt = TERMINAISONS[term]["longueur_relative"] * 28.0
    prof = fo.chemin(segs)
    assert prof.aire() > 0.97 * (160.0 - lt) * 28.0


def test_tete_goutte_de_suif_volume_calotte():
    rev = fo.Revolution("r", "r", (0, 0), fo.tete_goutte_de_suif(10.0, 8.0, 3.0))
    a, h = 4.0, 3.0
    calotte = math.pi * h * (3 * a * a + h * h) / 6.0
    assert rev.volume_mm3() == pytest.approx(calotte, rel=0.02)
    assert rev.boite_englobante()[1][2] == pytest.approx(13.0)


def test_bloc_profile_volumes():
    t = pf.trace_bloc(30.0, 0.0).segments
    b = fo.BlocProfile("b", "b", (5.0, 7.0), [(0.0, 50.0, t), (90.0, 20.0, t)])
    assert b.volume_mm3() == pytest.approx(100 * 40 * 30, rel=1e-6)
    bb = b.boite_englobante()
    assert list(bb[0]) == pytest.approx([-45.0, -13.0, 0.0]) and list(bb[1]) == pytest.approx([55.0, 27.0, 30.0])
    oct_ = fo.BlocProfile("o", "o", (0, 0), [(a, 50.0, t) for a in (0.0, 45.0, 90.0, 135.0)])
    assert oct_.volume_mm3() == pytest.approx(fo.octogone(100.0).aire() * 30, rel=1e-6)
    # enlevement (boite) et alesage
    c = fo.BlocProfile("c", "c", (0, 0), [(0.0, 50.0, t), (90.0, 20.0, t)], alesage=(10.0, 10.0, 0.0, 30.0),
                       enlevements=[(40.0, 60.0, -5.0, 5.0, 10.0, 20.0)])
    assert c.volume_mm3() == pytest.approx(100 * 40 * 30 - 10 * 10 * 30 - 10 * 10 * 10, rel=1e-6)
    # tranche decentree (cellule rognee par le contour)
    d = fo.BlocProfile("d", "d", (0, 0), [(0.0, 50.0, t, 30.0), (90.0, 20.0, t)])
    assert d.boite_englobante()[0][0] == pytest.approx(-20.0) and d.boite_englobante()[1][0] == pytest.approx(80.0)
    for k in range(2):
        assert pf.chemin_ferme(d.contour_section(k))


def test_bloc_moulure_onglets_exacts():
    tr = pf.trace_bloc(50.0, 0.0, ("conge", 4), ("bec_de_corbin", 14, 31, 14)).segments
    b = fo.BlocProfile("pl", "pl", (0, 0), [(0.0, 400.0, tr), (90.0, 200.0, tr)])
    # a mi-hauteur de la gorge, section rectangulaire retrecie identiquement sur les 4 cotes
    z = 10.0
    d = pf.evaluer(tr, z)
    sec = b.section_a(z)
    xs, ys = [p[0] for p in sec], [p[1] for p in sec]
    assert max(xs) == pytest.approx(400.0 - d) and max(ys) == pytest.approx(200.0 - d)
    assert b.volume_mm3() < 800 * 400 * 50
