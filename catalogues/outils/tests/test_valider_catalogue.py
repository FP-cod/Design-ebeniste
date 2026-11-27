#!/usr/bin/env python3
"""Tests unittest du validateur de catalogue produits (stdlib uniquement)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

OUTILS = Path(__file__).resolve().parents[1]
if str(OUTILS) not in sys.path:
    sys.path.insert(0, str(OUTILS))

from valider_catalogue import ETAPES_ATTENDUES, main, valider

CIRCUIT = [
    {"numero": n, "etape": e, "statut": s} for n, e, s in ETAPES_ATTENDUES
]

DATE = "2026-01-15"


def _lien(gamme, typologie, numero, etape, date=DATE, reference=None, pad=False):
    num = f"{numero:02d}" if pad else str(numero)
    nom = f"{num}_{etape}_{date}.md"
    parties = ["preuves", gamme, typologie]
    if reference:
        parties.append(reference)
    parties.append(nom)
    return "/".join(parties)


def _preuve(numero, etape=None, date=DATE, valide_par="Fabien Petrot",
            gamme="obsidienne", typologie="demo", reference=None, pad=False,
            preuve=None):
    etape = etape or ETAPES_ATTENDUES[numero - 1][1]
    return {
        "numero_etape": numero,
        "etape": etape,
        "preuve": preuve or _lien(gamme, typologie, numero, etape, date, reference, pad),
        "date": date,
        "valide_par": valide_par,
    }


class TestsValidateurCatalogue(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.racine = Path(self.tmp.name)
        (self.racine / "catalogues").mkdir()
        self.chemin = self.racine / "catalogues" / "produits.json"

    def tearDown(self):
        self.tmp.cleanup()

    def ecrire(self, data, fichiers=None):
        self.chemin.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        for rel, contenu in (fichiers or {}).items():
            p = self.racine / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(contenu, encoding="utf-8")

    def creer_fichiers_preuves(self, *liens, extra=None):
        fichiers = {lien: f"preuve {lien}\n" for lien in liens}
        if extra:
            fichiers.update(extra)
        return fichiers

    def catalogue_valide(self):
        """Catalogue minimal : typologies null, design_valide, produit, plus une référence OK."""
        p_design = [_preuve(1, typologie="chaise_demo"), _preuve(2, typologie="chaise_demo")]
        p_produit = [_preuve(n, typologie="table_demo", pad=(n == 3)) for n in range(2, 9)]
        p_ref = [_preuve(2, typologie="etagere_demo", reference="ref_a")]
        data = {
            "gammes": {
                "obsidienne": {
                    "nom": "Obsidienne",
                    "series": [
                        {
                            "id": "serie-demo",
                            "nom": "Démo",
                            "typologies": [
                                {
                                    "id": "tabouret_demo",
                                    "nom": "Tabouret démo",
                                    "statut": None,
                                    "preuves": [],
                                },
                                {
                                    "id": "chaise_demo",
                                    "nom": "Chaise démo",
                                    "statut": "design_valide",
                                    "preuves": p_design,
                                },
                                {
                                    "id": "table_demo",
                                    "nom": "Table démo",
                                    "statut": "produit",
                                    "preuves": p_produit,
                                    "dossier_gpsr": "preuves/obsidienne/table_demo/dossier_gpsr/dossier_technique.md",
                                },
                                {
                                    "id": "etagere_demo",
                                    "nom": "Étagère démo",
                                    "statut": None,
                                    "preuves": [],
                                    "references": [
                                        {
                                            "id": "ref_a",
                                            "statut": "design_valide",
                                            "preuves": p_ref,
                                        }
                                    ],
                                },
                            ],
                        }
                    ],
                }
            },
            "circuit_etapes": CIRCUIT,
        }
        liens = [p["preuve"] for p in p_design + p_produit + p_ref]
        extra = {
            "preuves/obsidienne/table_demo/dossier_gpsr/dossier_technique.md": "Dossier GPSR complet.\n"
        }
        return data, self.creer_fichiers_preuves(*liens, extra=extra)

    def erreurs_valide_mute(self, mutateur, fichiers=None):
        data, fichiers_ok = self.catalogue_valide()
        mutateur(data)
        self.ecrire(data, fichiers if fichiers is not None else fichiers_ok)
        return valider(self.chemin, self.racine)

    def typo(self, data, ident):
        for t in data["gammes"]["obsidienne"]["series"][0]["typologies"]:
            if t["id"] == ident:
                return t
        raise KeyError(ident)

    # --- cas valide ---

    def test_catalogue_valide(self):
        data, fichiers = self.catalogue_valide()
        self.ecrire(data, fichiers)
        erreurs = valider(self.chemin, self.racine)
        self.assertEqual(erreurs, [], msg="\n".join(erreurs))
        self.assertEqual(main(["--catalogue", str(self.chemin), "--racine", str(self.racine)]), 0)

    # --- refus ---

    def test_statut_absent(self):
        def mute(data):
            typo = self.typo(data, "tabouret_demo")
            del typo["statut"]
        erreurs = self.erreurs_valide_mute(mute)
        self.assertTrue(erreurs)
        self.assertTrue(any("statut" in e and "absente" in e for e in erreurs), erreurs)

    def test_valeur_inconnue(self):
        def mute(data):
            self.typo(data, "tabouret_demo")["statut"] = "presque_fini"
        erreurs = self.erreurs_valide_mute(mute)
        self.assertTrue(any("inconnue" in e and "presque_fini" in e for e in erreurs), erreurs)

    def test_en_cours(self):
        def mute(data):
            self.typo(data, "tabouret_demo")["statut"] = "en_cours"
        erreurs = self.erreurs_valide_mute(mute)
        self.assertTrue(any("en_cours" in e for e in erreurs), erreurs)

    def test_preuves_absente(self):
        def mute(data):
            del self.typo(data, "tabouret_demo")["preuves"]
        erreurs = self.erreurs_valide_mute(mute)
        self.assertTrue(any("preuves" in e and "absente" in e for e in erreurs), erreurs)

    def test_preuves_pas_liste(self):
        def mute(data):
            self.typo(data, "tabouret_demo")["preuves"] = {"oops": True}
        erreurs = self.erreurs_valide_mute(mute)
        self.assertTrue(any("preuves" in e and "liste" in e for e in erreurs), erreurs)

    def test_statut_sans_preuve(self):
        def mute(data):
            typo = self.typo(data, "tabouret_demo")
            typo["statut"] = "faisabilite_ok"
            typo["preuves"] = []
        erreurs = self.erreurs_valide_mute(mute)
        self.assertTrue(any("sans preuve" in e for e in erreurs), erreurs)

    def test_trou_dans_les_etapes(self):
        def mute(data):
            typo = self.typo(data, "chaise_demo")
            typo["statut"] = "normes_ok"
            typo["preuves"] = [
                _preuve(2, typologie="chaise_demo"),
                _preuve(4, typologie="chaise_demo"),
            ]
        data, _f = self.catalogue_valide()
        mute(data)
        liens = [p["preuve"] for t in data["gammes"]["obsidienne"]["series"][0]["typologies"]
                 for p in t.get("preuves", [])]
        for ref in self.typo(data, "etagere_demo")["references"]:
            liens.extend(p["preuve"] for p in ref["preuves"])
        extra = {
            "preuves/obsidienne/table_demo/dossier_gpsr/dossier_technique.md": "GPSR\n"
        }
        # include preuves of table_demo too (unchanged)
        self.ecrire(data, self.creer_fichiers_preuves(*liens, extra=extra))
        erreurs = valider(self.chemin, self.racine)
        self.assertTrue(any("trou" in e for e in erreurs), erreurs)

    def test_statut_inferieur_a_derniere_etape_continue(self):
        def mute(data):
            typo = self.typo(data, "chaise_demo")
            typo["statut"] = "design_valide"
            typo["preuves"] = [
                _preuve(2, typologie="chaise_demo"),
                _preuve(3, typologie="chaise_demo"),
            ]
        data, _f = self.catalogue_valide()
        mute(data)
        liens = [p["preuve"] for t in data["gammes"]["obsidienne"]["series"][0]["typologies"]
                 for p in t.get("preuves", [])]
        for ref in self.typo(data, "etagere_demo")["references"]:
            liens.extend(p["preuve"] for p in ref["preuves"])
        extra = {
            "preuves/obsidienne/table_demo/dossier_gpsr/dossier_technique.md": "GPSR\n"
        }
        self.ecrire(data, self.creer_fichiers_preuves(*liens, extra=extra))
        erreurs = valider(self.chemin, self.racine)
        self.assertTrue(any("inférieur" in e for e in erreurs), erreurs)

    def test_benchmark_seul_avec_statut(self):
        def mute(data):
            typo = self.typo(data, "tabouret_demo")
            typo["statut"] = "design_valide"
            typo["preuves"] = [_preuve(1, typologie="tabouret_demo")]
        data, fichiers = self.catalogue_valide()
        mute(data)
        fichiers[_preuve(1, typologie="tabouret_demo")["preuve"]] = "benchmark\n"
        self.ecrire(data, fichiers)
        erreurs = valider(self.chemin, self.racine)
        self.assertTrue(any("benchmark" in e for e in erreurs), erreurs)

    def test_numero_etape_incoherents(self):
        def mute(data):
            typo = self.typo(data, "chaise_demo")
            typo["preuves"][1]["etape"] = "benchmark"  # numero 2 vs etape 1
        erreurs = self.erreurs_valide_mute(mute)
        self.assertTrue(any("incohérents" in e for e in erreurs), erreurs)

    def test_date_invalide(self):
        def mute(data):
            typo = self.typo(data, "chaise_demo")
            typo["preuves"][1]["date"] = "26/01/2026"
        erreurs = self.erreurs_valide_mute(mute)
        self.assertTrue(any("date invalide" in e for e in erreurs), erreurs)

    def test_valide_par_manquant(self):
        def mute(data):
            typo = self.typo(data, "chaise_demo")
            typo["preuves"][1]["valide_par"] = "  "
        erreurs = self.erreurs_valide_mute(mute)
        self.assertTrue(any("valide_par" in e for e in erreurs), erreurs)

    def test_design_valide_par_un_autre(self):
        def mute(data):
            typo = self.typo(data, "chaise_demo")
            typo["preuves"][1]["valide_par"] = "Alice Dupont"
        erreurs = self.erreurs_valide_mute(mute)
        self.assertTrue(any("Fabien" in e and "Alice Dupont" in e for e in erreurs), erreurs)

    def test_fichier_preuve_inexistant(self):
        data, fichiers = self.catalogue_valide()
        lien = self.typo(data, "chaise_demo")["preuves"][1]["preuve"]
        del fichiers[lien]
        self.ecrire(data, fichiers)
        erreurs = valider(self.chemin, self.racine)
        self.assertTrue(any("n'existe pas" in e for e in erreurs), erreurs)

    def test_chemin_hors_arborescence(self):
        data, fichiers = self.catalogue_valide()
        typo = self.typo(data, "chaise_demo")
        mauvais = "preuves/hors_arbre.md"
        typo["preuves"][1]["preuve"] = mauvais
        fichiers[mauvais] = "existe mais hors arborescence\n"
        self.ecrire(data, fichiers)
        erreurs = valider(self.chemin, self.racine)
        self.assertTrue(any("arborescence" in e for e in erreurs), erreurs)

    def test_produit_sans_dossier_gpsr(self):
        def mute(data):
            del self.typo(data, "table_demo")["dossier_gpsr"]
        erreurs = self.erreurs_valide_mute(mute)
        self.assertTrue(any("dossier_gpsr" in e for e in erreurs), erreurs)

    def test_dossier_gpsr_inexistant(self):
        def mute(data):
            self.typo(data, "table_demo")["dossier_gpsr"] = (
                "preuves/obsidienne/table_demo/dossier_gpsr/absent.md"
            )
        erreurs = self.erreurs_valide_mute(mute)
        self.assertTrue(any("dossier_gpsr" in e and "n'existe pas" in e for e in erreurs), erreurs)

    def test_serie_avec_statut(self):
        def mute(data):
            data["gammes"]["obsidienne"]["series"][0]["statut"] = None
        erreurs = self.erreurs_valide_mute(mute)
        self.assertTrue(any("série" in e and "statut" in e for e in erreurs), erreurs)

    def test_id_duplique(self):
        def mute(data):
            typologies = data["gammes"]["obsidienne"]["series"][0]["typologies"]
            typologies.append(
                {"id": "tabouret_demo", "nom": "Doublon", "statut": None, "preuves": []}
            )
        erreurs = self.erreurs_valide_mute(mute)
        self.assertTrue(any("dupliqué" in e for e in erreurs), erreurs)

    def test_json_invalide(self):
        self.chemin.write_text("{ pas du json", encoding="utf-8")
        erreurs = valider(self.chemin, self.racine)
        self.assertTrue(erreurs)
        self.assertTrue(any("JSON invalide" in e for e in erreurs), erreurs)
        self.assertEqual(main(["--catalogue", str(self.chemin), "--racine", str(self.racine)]), 1)

    def test_reference_fautive(self):
        def mute(data):
            ref = self.typo(data, "etagere_demo")["references"][0]
            del ref["statut"]
        erreurs = self.erreurs_valide_mute(mute)
        self.assertTrue(
            any("references[0]" in e and "statut" in e and "absente" in e for e in erreurs),
            erreurs,
        )


if __name__ == "__main__":
    unittest.main()
