# -*- coding: utf-8 -*-
from gamme_cuir.catalogues import cuirs, fermetures, finitions, quincaillerie as q
from gamme_cuir.parametres import Parametres


def test_teintes_cuir():
    assert {"cognac", "noir", "tan"} <= set(cuirs.TEINTES)
    for t, d in cuirs.TEINTES.items():
        assert all(0 <= v <= 255 for v in d["rgb"]) and len(d["rgb"]) == 3, t
        assert d["apparences"], t
        for m in d["quincaillerie_conseillee"] + d["quincaillerie_possible"]:
            assert m in q.METAUX, (t, m)
        assert any(t in c["teintes"] for c in cuirs.CUIRS.values()), "teinte %s introuvable dans les cuirs" % t


def test_cuirs_pleine_fleur_et_sources():
    for k, c in cuirs.CUIRS.items():
        assert c["epaisseur_plage"][0] < c["epaisseur_plage"][1]
        if c["resistance_traction_mpa"] is not None:
            assert c["source_traction"], "%s : resistance sans source" % k


def test_aucune_charge_presentee_comme_sourcee():
    for cat, pieces in q.TOUTES.items():
        for k, pc in pieces.items():
            assert pc["statut_charge"] == q.EST, (cat, k)
            if pc.get("metal"):
                assert pc["metal"] in q.METAUX, (cat, k)
            for m in pc.get("metaux", []):
                assert m in q.METAUX or m == "cuivre", (cat, k, m)


def test_choix_des_parametres_existent_dans_les_catalogues():
    p = Parametres(json_utilisateur=False)
    assert set(p.meta("finition.teinte")["choix"]) == set(cuirs.TEINTES)
    assert set(p.meta("finition.quincaillerie")["choix"]) == set(q.METAUX)
    assert set(p.meta("finition.boucle")["choix"]) <= set(q.BOUCLES)
    assert set(p.meta("anneau_d.reference")["choix"]) <= set(q.ANNEAUX)
    assert set(p.meta("jonctions.rivet")["choix"]) <= set(q.RIVETS)
    assert set(p.meta("finition.tranche")["choix"]) == set(finitions.TRANCHES)
    assert set(p.meta("couture.fil")["choix"]) == set(finitions.FILS)
    assert set(p.meta("finition.fermeture")["choix"]) == set(fermetures.FERMETURES)
    assert set(p.meta("cuir.matiere")["choix"]) == set(cuirs.CUIRS)
    assert set(p.meta("cuir.doublure_matiere")["choix"]) == set(cuirs.DOUBLURES)
    assert set(p.meta("cuir.rembourrage_materiau")["choix"]) == set(cuirs.REMBOURRAGES)


def test_fermetures_et_jonctions():
    assert set(fermetures.FERMETURES) == {"boucle_ardillon", "boucle_ardillon_cadenas", "mousqueton", "scratch"}
    assert fermetures.FERMETURES["scratch"]["tenue_contention"] == 0
    assert {"couture_sellier", "rivets", "oeillets"} <= set(fermetures.JONCTIONS)
    assert finitions.TRANCHES["brute"]["arete_vive"] is True
    assert not any(t["arete_vive"] for k, t in finitions.TRANCHES.items() if k != "brute")
