#!/usr/bin/env python3
"""Valide catalogues/produits.json (statuts, preuves, circuit d'étapes).

Stdlib uniquement. Code de sortie : 0 si le catalogue est conforme, 1 sinon.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

NOM_CATALOGUE_DEFAUT = Path("catalogues") / "produits.json"

ETAPES_ATTENDUES = (
    (1, "benchmark", None),
    (2, "design_valide", "design_valide"),
    (3, "faisabilite_ok", "faisabilite_ok"),
    (4, "normes_ok", "normes_ok"),
    (5, "script_ok", "script_ok"),
    (6, "debit_ok", "debit_ok"),
    (7, "go_marche", "go_marche"),
    (8, "produit", "produit"),
)
NUMERO_VERS_ETAPE = {n: e for n, e, _s in ETAPES_ATTENDUES}
ETAPE_VERS_NUMERO = {e: n for n, e, _s in ETAPES_ATTENDUES}
STATUTS_ADMIS = {s for _n, _e, s in ETAPES_ATTENDUES if s is not None}
STATUT_VERS_NUMERO = {s: n for n, _e, s in ETAPES_ATTENDUES if s is not None}

RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_NUMERO_FICHIER = re.compile(r"^(0?[1-8])$")
NOMS_FABIEN = frozenset({"fabien", "fabien petrot"})


def racine_defaut() -> Path:
    """Racine du dépôt : deux niveaux au-dessus de ce fichier (catalogues/outils/)."""
    return Path(__file__).resolve().parents[2]


def chemin_json(*parts: str) -> str:
    return "".join(parts) if parts else "$"


def _cle(nom: str) -> str:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nom):
        return nom
    return "[{0}]".format(json.dumps(nom, ensure_ascii=False))


class Validateur:
    def __init__(self, catalogue: Path, racine: Path) -> None:
        self.catalogue = catalogue
        self.racine = racine.resolve()
        self.erreurs: list[str] = []

    def erreur(self, chemin: str, message: str) -> None:
        if chemin:
            self.erreurs.append(f"{chemin} : {message}")
        else:
            self.erreurs.append(message)

    def valider(self) -> list[str]:
        try:
            texte = self.catalogue.read_text(encoding="utf-8")
        except OSError as exc:
            self.erreur("", f"Impossible de lire le catalogue {self.catalogue} : {exc}")
            return self.erreurs
        try:
            data = json.loads(texte)
        except json.JSONDecodeError as exc:
            self.erreur(
                "",
                "JSON invalide dans {0} : {1} (ligne {2}, colonne {3}).".format(
                    self.catalogue, exc.msg, exc.lineno, exc.colno
                ),
            )
            return self.erreurs
        if not isinstance(data, dict):
            self.erreur("$", "Le catalogue doit être un objet JSON.")
            return self.erreurs
        if not self._circuit_conforme(data.get("circuit_etapes"), "$.circuit_etapes"):
            # On continue quand même le reste avec l'échelle attendue.
            pass
        gammes = data.get("gammes")
        if not isinstance(gammes, dict):
            self.erreur("$.gammes", "La clé « gammes » doit être un objet.")
            return self.erreurs
        vus: dict[str, str] = {}
        for cle_gamme, gamme in gammes.items():
            self._valider_gamme(cle_gamme, gamme, vus)
        return self.erreurs

    def _circuit_conforme(self, circuit, chemin: str) -> bool:
        if not isinstance(circuit, list) or len(circuit) != 8:
            self.erreur(
                chemin,
                "le référentiel des étapes est absent ou non conforme "
                "(attendu : une liste de 8 objets {numero, etape, statut}, "
                "benchmark=1 … produit=8).",
            )
            return False
        ok = True
        for i, attendu in enumerate(ETAPES_ATTENDUES):
            numero, etape, statut = attendu
            obj = circuit[i]
            if not isinstance(obj, dict):
                self.erreur(f"{chemin}[{i}]", "chaque étape doit être un objet.")
                ok = False
                continue
            if obj.get("numero") != numero or obj.get("etape") != etape or obj.get("statut") != statut:
                self.erreur(
                    f"{chemin}[{i}]",
                    "étape non conforme (attendu : numero={0}, etape={1!r}, statut={2!r} ; "
                    "trouvé : numero={3}, etape={4!r}, statut={5!r}).".format(
                        numero, etape, statut, obj.get("numero"), obj.get("etape"), obj.get("statut")
                    ),
                )
                ok = False
        return ok

    def _valider_gamme(self, cle_gamme: str, gamme, vus: dict[str, str]) -> None:
        chemin = chemin_json("$.gammes.", _cle(cle_gamme))
        if not isinstance(gamme, dict):
            self.erreur(chemin, "une gamme doit être un objet.")
            return
        series = gamme.get("series", [])
        if not isinstance(series, list):
            self.erreur(f"{chemin}.series", "« series » doit être une liste.")
            return
        for i, serie in enumerate(series):
            self._valider_serie(cle_gamme, serie, f"{chemin}.series[{i}]", vus)

    def _valider_serie(self, cle_gamme: str, serie, chemin: str, vus: dict[str, str]) -> None:
        if not isinstance(serie, dict):
            self.erreur(chemin, "une série doit être un objet.")
            return
        if "statut" in serie:
            self.erreur(chemin, "une série ne doit pas porter de clé « statut ».")
        typologies = serie.get("typologies", [])
        if not isinstance(typologies, list):
            self.erreur(f"{chemin}.typologies", "« typologies » doit être une liste.")
            return
        for j, typo in enumerate(typologies):
            self._valider_typologie(cle_gamme, typo, f"{chemin}.typologies[{j}]", vus)

    def _valider_typologie(self, cle_gamme: str, typo, chemin: str, vus: dict[str, str]) -> None:
        if not isinstance(typo, dict):
            self.erreur(chemin, "une typologie doit être un objet.")
            return
        ident = typo.get("id")
        if not isinstance(ident, str) or not ident:
            self.erreur(f"{chemin}.id", "identifiant de typologie absent ou vide.")
            ident_effectif = None
        else:
            if ident in vus:
                self.erreur(
                    f"{chemin}.id",
                    "identifiant de typologie dupliqué « {0} » (déjà vu en {1}).".format(ident, vus[ident]),
                )
            else:
                vus[ident] = chemin
            ident_effectif = ident
        self._valider_entree(typo, chemin, cle_gamme, ident_effectif, reference=None)
        references = typo.get("references")
        if references is None:
            return
        if not isinstance(references, list):
            self.erreur(f"{chemin}.references", "« references » doit être une liste.")
            return
        refs_vues: dict[str, str] = {}
        for k, ref in enumerate(references):
            c_ref = f"{chemin}.references[{k}]"
            if not isinstance(ref, dict):
                self.erreur(c_ref, "une référence doit être un objet.")
                continue
            rid = ref.get("id")
            if not isinstance(rid, str) or not rid:
                self.erreur(f"{c_ref}.id", "identifiant de référence absent ou vide.")
                rid_effectif = None
            else:
                if rid in refs_vues:
                    self.erreur(
                        f"{c_ref}.id",
                        "identifiant de référence dupliqué « {0} » (déjà vu en {1}).".format(rid, refs_vues[rid]),
                    )
                else:
                    refs_vues[rid] = c_ref
                rid_effectif = rid
            self._valider_entree(ref, c_ref, cle_gamme, ident_effectif, reference=rid_effectif)

    def _valider_entree(self, entree: dict, chemin: str, gamme: str, typologie, reference) -> None:
        if "statut" not in entree:
            self.erreur(chemin, "clé « statut » absente.")
            statut = "__absent__"
        else:
            statut = entree["statut"]
            if statut is not None and statut not in STATUTS_ADMIS:
                if statut == "en_cours":
                    self.erreur(
                        f"{chemin}.statut",
                        "valeur interdite « en_cours » (valeurs admises : null, "
                        + ", ".join(s for _n, _e, s in ETAPES_ATTENDUES if s)
                        + ").",
                    )
                else:
                    self.erreur(
                        f"{chemin}.statut",
                        "valeur inconnue {0!r} (valeurs admises : null, {1}).".format(
                            statut, ", ".join(s for _n, _e, s in ETAPES_ATTENDUES if s)
                        ),
                    )
                statut = "__invalide__"

        if "preuves" not in entree:
            self.erreur(chemin, "clé « preuves » absente.")
            preuves = None
        else:
            preuves = entree["preuves"]
            if not isinstance(preuves, list):
                self.erreur(f"{chemin}.preuves", "« preuves » doit être une liste.")
                preuves = None

        etapes_prouvees: set[int] = set()
        if isinstance(preuves, list):
            for i, preuve in enumerate(preuves):
                numero = self._valider_preuve(
                    preuve, f"{chemin}.preuves[{i}]", gamme, typologie, reference
                )
                if numero is not None and numero >= 2:
                    etapes_prouvees.add(numero)

        if statut in ("__absent__", "__invalide__"):
            pass
        else:
            self._coherence_statut(chemin, statut, etapes_prouvees, preuves)

        if statut == "produit":
            self._valider_dossier_gpsr(entree, chemin, gamme, typologie, reference)

    def _coherence_statut(self, chemin: str, statut, etapes_prouvees: set[int], preuves) -> None:
        derniere = None
        for k in range(2, 9):
            if k in etapes_prouvees:
                derniere = k
            else:
                break

        if statut is None:
            if derniere is not None:
                self.erreur(
                    chemin,
                    "le statut déclaré est null alors que des preuves contiguës vont jusqu'à "
                    "l'étape {0} ({1}).".format(derniere, NUMERO_VERS_ETAPE[derniere]),
                )
            return

        declare = STATUT_VERS_NUMERO[statut]
        seulement_benchmark = (
            derniere is None
            and isinstance(preuves, list)
            and any(
                isinstance(p, dict) and p.get("numero_etape") in (1, 1.0) or
                (isinstance(p, dict) and p.get("etape") == "benchmark")
                for p in preuves
            )
        )
        if derniere is None:
            if seulement_benchmark:
                self.erreur(
                    chemin,
                    "statut « {0} » alors que seules des preuves d'étape 1 (benchmark) "
                    "sont présentes ; le benchmark ne confère aucun statut.".format(statut),
                )
            else:
                self.erreur(
                    chemin,
                    "statut « {0} » sans preuve d'étape 2 (aucun statut sans preuve ; "
                    "l'étape 1 n'entre pas dans le calcul).".format(statut),
                )
            return

        manquantes = [k for k in range(2, declare + 1) if k not in etapes_prouvees]
        if manquantes:
            self.erreur(
                chemin,
                "trou dans les preuves pour le statut « {0} » : étape(s) {1} manquante(s) "
                "(une preuve est exigée pour chaque étape 2 à {2}, sans trou).".format(
                    statut,
                    ", ".join("{0} ({1})".format(k, NUMERO_VERS_ETAPE[k]) for k in manquantes),
                    declare,
                ),
            )
        if derniere > declare:
            self.erreur(
                chemin,
                "le statut déclaré « {0} » est inférieur à la dernière étape continue "
                "prouvée ({1}, étape {2}).".format(
                    statut, NUMERO_VERS_ETAPE[derniere], derniere
                ),
            )

    def _valider_preuve(self, preuve, chemin: str, gamme: str, typologie, reference):
        if not isinstance(preuve, dict):
            self.erreur(chemin, "une preuve doit être un objet.")
            return None
        numero = preuve.get("numero_etape")
        if isinstance(numero, bool) or not isinstance(numero, int) or numero < 1 or numero > 8:
            self.erreur(
                f"{chemin}.numero_etape",
                "« numero_etape » doit être un entier de 1 à 8 (trouvé : {0!r}).".format(numero),
            )
            numero_ok = None
        else:
            numero_ok = numero

        etape = preuve.get("etape")
        if etape not in ETAPE_VERS_NUMERO:
            self.erreur(
                f"{chemin}.etape",
                "étape inconnue {0!r} (attendu : {1}).".format(
                    etape, ", ".join(e for _n, e, _s in ETAPES_ATTENDUES)
                ),
            )
            etape_ok = None
        else:
            etape_ok = etape

        if numero_ok is not None and etape_ok is not None and ETAPE_VERS_NUMERO[etape_ok] != numero_ok:
            self.erreur(
                chemin,
                "numero_etape ({0}) et etape (« {1} ») sont incohérents avec circuit_etapes "
                "(l'étape {0} est « {2} »).".format(
                    numero_ok, etape_ok, NUMERO_VERS_ETAPE[numero_ok]
                ),
            )

        date_ok = self._date_valide(preuve.get("date"), f"{chemin}.date")

        valide_par = preuve.get("valide_par")
        if not isinstance(valide_par, str) or not valide_par.strip():
            self.erreur(chemin, "« valide_par » est absent ou vide.")
            valide_ok = False
        else:
            valide_ok = True
            if etape_ok == "design_valide" or numero_ok == 2:
                if valide_par.strip().casefold() not in NOMS_FABIEN:
                    self.erreur(
                        chemin,
                        "l'étape design_valide doit être validée par Fabien "
                        "(« Fabien » ou « Fabien Petrot ») ; trouvé : {0!r}.".format(valide_par),
                    )

        lien = preuve.get("preuve")
        if not isinstance(lien, str) or not lien.strip():
            self.erreur(f"{chemin}.preuve", "le lien « preuve » est absent ou vide.")
            return numero_ok

        self._valider_lien_preuve(
            lien.strip(),
            chemin,
            gamme,
            typologie,
            reference,
            numero_ok,
            etape_ok,
            date_ok,
        )
        return numero_ok

    def _date_valide(self, valeur, chemin: str):
        if not isinstance(valeur, str) or not RE_DATE.match(valeur):
            self.erreur(chemin, "date invalide {0!r} (attendu : AAAA-MM-JJ).".format(valeur))
            return None
        try:
            date.fromisoformat(valeur)
        except ValueError:
            self.erreur(chemin, "date invalide {0!r} (jour inexistant).".format(valeur))
            return None
        return valeur

    def _valider_lien_preuve(
        self, lien, chemin, gamme, typologie, reference, numero, etape, date_iso
    ) -> None:
        if Path(lien).is_absolute() or "\\" in lien:
            self.erreur(
                f"{chemin}.preuve",
                "le lien « {0} » doit être un chemin relatif POSIX depuis la racine du dépôt.".format(lien),
            )
            return
        parties = Path(lien).parts
        if ".." in parties:
            self.erreur(
                f"{chemin}.preuve",
                "le lien « {0} » ne doit pas contenir de segment « .. ».".format(lien),
            )
            return
        cible = (self.racine / lien).resolve()
        try:
            cible.relative_to(self.racine)
        except ValueError:
            self.erreur(
                f"{chemin}.preuve",
                "le lien « {0} » sort de la racine du dépôt.".format(lien),
            )
            return
        if not cible.is_file():
            self.erreur(
                f"{chemin}.preuve",
                "le fichier de preuve « {0} » n'existe pas.".format(lien),
            )
            # On signale aussi l'arborescence si le motif est faux, même si le fichier manque.
        if typologie is None:
            return
        if not self._arborescence_preuve_ok(lien, gamme, typologie, reference, numero, etape, date_iso):
            attendu = self._modele_preuve(gamme, typologie, reference)
            self.erreur(
                f"{chemin}.preuve",
                "le chemin « {0} » n'obéit pas à l'arborescence {1} "
                "(numero, etape et date doivent coïncider avec l'entrée ; "
                "numéro accepté : 1..8 ou 01..08).".format(lien, attendu),
            )

    def _modele_preuve(self, gamme, typologie, reference) -> str:
        if reference:
            return "preuves/{0}/{1}/{2}/<numero>_<etape>_<date>.md".format(gamme, typologie, reference)
        return "preuves/{0}/{1}/<numero>_<etape>_<date>.md".format(gamme, typologie)

    def _arborescence_preuve_ok(self, lien, gamme, typologie, reference, numero, etape, date_iso) -> bool:
        attendu_pref = ["preuves", gamme, typologie]
        if reference:
            attendu_pref.append(reference)
        parties = Path(lien).parts
        if len(parties) != len(attendu_pref) + 1:
            return False
        if list(parties[:-1]) != attendu_pref:
            return False
        nom = parties[-1]
        if not nom.endswith(".md"):
            return False
        corps = nom[:-3]
        bits = corps.split("_")
        # <numero>_<etape>_<date> : etape may contain underscores (none currently)
        # Format: numero, then etape (known token), then date
        if len(bits) < 3:
            return False
        num_s, date_s = bits[0], bits[-1]
        etape_s = "_".join(bits[1:-1])
        if not RE_NUMERO_FICHIER.match(num_s):
            return False
        num_int = int(num_s)
        if num_int < 1 or num_int > 8:
            return False
        if numero is not None and num_int != numero:
            return False
        if etape is not None and etape_s != etape:
            return False
        if date_iso is not None and date_s != date_iso:
            return False
        if etape_s not in ETAPE_VERS_NUMERO:
            return False
        if ETAPE_VERS_NUMERO[etape_s] != num_int:
            return False
        return True

    def _valider_dossier_gpsr(self, entree, chemin, gamme, typologie, reference) -> None:
        if "dossier_gpsr" not in entree:
            self.erreur(
                chemin,
                "statut « produit » sans champ « dossier_gpsr » "
                "(chemin relatif vers un fichier existant du dossier technique GPSR).",
            )
            return
        lien = entree["dossier_gpsr"]
        c = f"{chemin}.dossier_gpsr"
        if not isinstance(lien, str) or not lien.strip():
            self.erreur(c, "« dossier_gpsr » doit être un chemin relatif non vide.")
            return
        lien = lien.strip()
        if Path(lien).is_absolute() or ".." in Path(lien).parts or "\\" in lien:
            self.erreur(c, "« dossier_gpsr » doit être un chemin relatif POSIX sous la racine du dépôt.")
            return
        cible = (self.racine / lien).resolve()
        try:
            cible.relative_to(self.racine)
        except ValueError:
            self.erreur(c, "le chemin « {0} » sort de la racine du dépôt.".format(lien))
            return
        if not cible.is_file():
            self.erreur(c, "le fichier « {0} » n'existe pas.".format(lien))
        if typologie is None:
            return
        parties_ok = ["preuves", gamme, typologie]
        if reference:
            parties_ok.append(reference)
        parties_ok.append("dossier_gpsr")
        pref = "/".join(parties_ok)
        normalise = Path(lien).as_posix()
        if not (normalise == pref or normalise.startswith(pref + "/") or normalise.startswith(pref + ".")):
            self.erreur(
                c,
                "le chemin « {0} » doit se trouver sous {1}/ "
                "(ou être un fichier {1}.md).".format(lien, pref),
            )


def valider(catalogue: str | Path, racine: str | Path) -> list[str]:
    """Valide le catalogue et retourne la liste des messages d'erreur (vide si OK)."""
    return Validateur(Path(catalogue), Path(racine)).valider()


def analyser_arguments(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Valide catalogues/produits.json (statuts, preuves, circuit d'étapes)."
    )
    parser.add_argument(
        "--catalogue",
        default=None,
        help="Chemin du catalogue JSON (défaut : <racine>/catalogues/produits.json).",
    )
    parser.add_argument(
        "--racine",
        default=None,
        help="Racine du dépôt, pour résoudre les liens de preuves (défaut : racine déduite du script).",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = analyser_arguments(argv)
    racine = Path(args.racine) if args.racine else racine_defaut()
    catalogue = Path(args.catalogue) if args.catalogue else racine / NOM_CATALOGUE_DEFAUT
    erreurs = valider(catalogue, racine)
    if erreurs:
        for message in erreurs:
            print(message, file=sys.stderr)
        print(
            "Catalogue invalide : {0} erreur(s).".format(len(erreurs)),
            file=sys.stderr,
        )
        return 1
    print("Catalogue valide : {0}".format(catalogue))
    return 0


if __name__ == "__main__":
    sys.exit(main())
