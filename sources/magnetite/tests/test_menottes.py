# -*- coding: utf-8 -*-
"""Geometrie de la grammaire menottes."""

import math

import pytest

from gamme_cuir import geometrie as geo
from gamme_cuir.grammaires import menottes
from gamme_cuir.parametres import Parametres


def plan(**s):
    s = {k.replace("__", "."): v for k, v in s.items()}
    return menottes.concevoir(params=Parametres(s, json_utilisateur=False))


def test_longueur_developpee_tour_plus_recouvrement():
    pl = plan()
    c, p = pl.cotes, pl.params
    assert c["circonference_neutre"] == pytest.approx(170 + 20 + math.pi * p.epaisseur_totale())
    assert c["recouvrement"] == pytest.approx(30 + 2 * 15 + 30)
    assert c["longueur_developpee"] == pytest.approx(c["circonference_neutre"] + c["recouvrement"])
    bande = [x for x in pl.primitives("plaque") if x.nom == "bande_exterieur"][0]
    x0, x1, y0, y1 = geo.boite_englobante(bande.contour)
    assert (x0, x1) == (0.0, pytest.approx(c["longueur_developpee"])) and y1 - y0 == pytest.approx(50.0)


@pytest.mark.parametrize("membre,boucle", [("poignet", "boucle_rouleau_50_laiton"),
                                           ("cheville", "boucle_rouleau_60_laiton")])
@pytest.mark.parametrize("taille", ["S", "M", "L", "XL"])
def test_toutes_tailles_sans_echec(membre, taille, boucle):
    pl = plan(produit__membre=membre, produit__taille=taille, finition__boucle=boucle)
    assert pl.echecs() == []
    c = pl.cotes
    lo, hi = pl.params.plage_taille()
    couvre = c["tour_mini_reglable"] <= lo and c["tour_maxi_reglable"] >= hi
    # la regle signale exactement les cas ou la rangee de trous ne couvre pas la plage de la taille
    assert ("plage_reglage" in {x.code for x in pl.alertes()}) == (not couvre)
    if (membre, taille) != ("cheville", "XL"):
        assert couvre, "5 trous x 15 mm couvrent la plage"


def test_cheville_xl_demande_sept_trous():
    """Plage XL cheville 250-310 mm (asymetrique autour de 270) : 5 trous ne suffisent pas, 7 oui."""
    s = dict(produit__membre="cheville", produit__taille="XL", finition__boucle="boucle_rouleau_60_laiton")
    assert "plage_reglage" in {x.code for x in plan(**s).alertes()}
    assert "plage_reglage" not in {x.code for x in plan(ardillon__nb_trous=7, **s).alertes()}


def test_trous_dans_la_bande_et_hors_couture():
    pl = plan()
    c, p = pl.cotes, pl.params
    w, L, r = c["largeur"], c["longueur_developpee"], c["rayon_extremite"]
    xs = c["x_trous"]
    assert len(xs) == 5 and xs[2] == pytest.approx(c["x_pli_boucle"] + c["circonference_neutre"])
    assert all(b - a == pytest.approx(15.0) for a, b in zip(xs, xs[1:]))
    assert L - xs[-1] == pytest.approx(p.get("ardillon.bout_apres_dernier_trou"))
    marge = p.get("couture.marge_couture_percages")
    for perc in pl.primitives("percage"):
        x0, x1, y0, y1 = geo.boite_englobante(perc.contour)
        for coin in ((x0, y0), (x0, y1), (x1, y0), (x1, y1)):
            assert geo.point_dans_rect_arrondi(coin, 0.0, L, -w / 2, w / 2, r), perc.nom
        centre = ((x0 + x1) / 2, (y0 + y1) / 2)
        rayon = max(x1 - x0, y1 - y0) / 2
        assert geo.distance_point_contour(centre, c["contour_couture"]) - rayon >= marge, perc.nom


def test_rembourrage_hors_percages_et_patte():
    pl = plan()
    c = pl.cotes
    zones = c["zones_rembourrage"]
    assert len(zones) == 2  # interrompu sous la patte d'anneau
    assert zones[0][0] >= 2 * c["x_pli_boucle"]
    assert zones[-1][1] < c["x_trous"][0]
    p0, p1 = c["zone_patte"]
    for a, b in zones:
        assert b <= p0 or a >= p1
    for perc in pl.primitives("percage"):
        x0, x1, _, _ = geo.boite_englobante(perc.contour)
        for a, b in zones:
            assert x1 < a or x0 > b, perc.nom
    plaques = [x for x in pl.primitives("plaque") if x.categorie == "rembourrage"]
    assert len(plaques) == 2 and all(x.z == pytest.approx(1.2) for x in plaques)


def test_sans_rembourrage_ni_doublure():
    pl = plan(cuir__nb_couches=1, cuir__rembourrage=False)
    noms = {x.nom for x in pl.primitives("plaque")}
    assert "bande_doublure" not in noms and not any(n.startswith("rembourrage") for n in noms)
    assert pl.cotes["epaisseur_totale"] == pytest.approx(3.5)


def test_couture_sellier():
    pl = plan()
    p = pl.params
    perim = [x for x in pl.primitives("couture") if x.nom == "couture_perimetre"][0]
    assert perim.pas_reel == pytest.approx(3.2, rel=0.05)
    assert len(perim.points) == round(perim.longueur / perim.pas_reel)
    rb = p.get("couture.retrait_bord")
    bande = [x for x in pl.primitives("plaque") if x.nom == "bande_exterieur"][0]
    for pt in perim.points[::10]:
        assert geo.distance_point_contour(pt, bande.contour) == pytest.approx(rb, abs=1e-6)
    assert pl.cotes["longueur_fil"] == pytest.approx(pl.cotes["longueur_couture"] * 4.0)
    assert {x.nom for x in pl.primitives("couture")} == {"couture_perimetre", "couture_patte"}
    pl2 = plan(jonctions__fixation_repli="rivets_et_couture")
    assert "couture_rabat" in {x.nom for x in pl2.primitives("couture")}


def test_extremites_arrondies():
    pl = plan()
    bande = [x for x in pl.primitives("plaque") if x.nom == "bande_exterieur"][0]
    arcs = [s for s in bande.contour if s[0] == "arc"]
    assert len(arcs) == 4 and all(s[2] == pytest.approx(25.0) for s in arcs)
    assert pl.cotes["rayon_extremite"] >= pl.params.get("securite.rayon_mini_extremite")


def test_anneau_d_et_rivets():
    pl = plan()
    c = pl.cotes
    assert c["x_anneau"] == pytest.approx(c["x_pli_boucle"] + c["circonference_neutre"] / 2)
    for pt in c["rivets_patte"]:
        assert c["zone_patte"][0] < pt[0] < c["zone_patte"][1]
    noms = {x.nom for x in pl.primitives()}
    assert {"anneau_d", "boucle_cadre", "boucle_ardillon", "patte_anneau_repliee", "passant_a_plat",
            "fente_ardillon"} <= noms
    anneau = [x for x in pl.primitives("plaque") if x.nom == "anneau_d"][0]
    assert anneau.apparence == ("metal", "laiton_massif_cw510l") and len(anneau.trous) == 1
    sans = plan(anneau_d__present=False)
    assert "anneau_d" not in {x.nom for x in sans.primitives()} and len(sans.cotes["zones_rembourrage"]) == 1


def test_passant():
    pl = plan()
    p, c = pl.params, pl.cotes
    attendu = 2 * (50 + 2) + 2 * (2 * p.epaisseur_cuir_seul() + 2) + math.pi * 2.0 + 10
    assert c["longueur_passant"] == pytest.approx(attendu)


def test_apparence_selon_teinte():
    pl = plan(finition__teinte="noir", finition__quincaillerie="inox_316", finition__boucle="boucle_rouleau_50_inox",
              anneau_d__reference="anneau_d_inox_soude_6x30")
    ext = [x for x in pl.primitives("plaque") if x.nom == "bande_exterieur"][0]
    assert ext.apparence == ("cuir", "noir")
    assert pl.echecs() == [] and "quincaillerie_depareillee" not in {c.code for c in pl.alertes()}


def test_parametres_invalides_refuses():
    with pytest.raises(ValueError):
        plan(ardillon__nb_trous=4)


def test_geometrie_rect_arrondi_refuse_rayon_trop_grand():
    with pytest.raises(ValueError):
        geo.rect_arrondi(0, 100, -10, 10, 11)
    assert geo.perimetre(geo.contour_bande(0, 300, 50, 25)) == pytest.approx(500 + math.pi * 50)
