# -*- coding: utf-8 -*-
"""Regenere les fichiers derives des parametres et catalogues.

Usage : ``python outils/generer_docs.py`` depuis la racine du projet.

Produit :
- ``rangement/parametres_rangement.defauts.json`` (copie de reference des defauts) ;
- ``rangement/parametres_rangement.json`` s'il n'existe pas (gabarit d'overrides vide) ;
- ``docs/parametres.md`` (tous les parametres : role, unite, plage, defaut, statut, source) ;
- ``docs/systemes.md`` (compromis capacite / discretion / solidite / cout par systeme) ;
- ``docs/a_valider.md`` (tout ce qui reste « À VALIDER » ou TODO) ;
- les tableaux du ``README.md`` entre les marqueurs ``<!-- DEBUT_xxx -->`` / ``<!-- FIN_xxx -->``.
"""

import io
import json
import os
import sys

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from rangement import parametres as P  # noqa: E402
from rangement.catalogues import bois, garnissage, quincaillerie, systemes, jonctions  # noqa: E402
from rangement.grammaires import ratelier_mural  # noqa: E402

LIBELLE_STATUT = {"repris": "repris", "a_valider": "**À VALIDER**", "derive": "dérivé", "todo": "**TODO**",
                  "libre": "libre", "impose": "imposé"}
LIBELLE_CRITERE = (("capacite", "Capacité"), ("discretion", "Discrétion"), ("solidite", "Solidité"),
                   ("cout", "Coût (5 = le moins cher)"))


def _fmt(v):
    if v is None:
        return "—"
    if isinstance(v, bool):
        return "oui" if v else "non"
    if isinstance(v, float):
        return ("%g" % v).replace(".", ",")
    if isinstance(v, (list, tuple)):
        return ", ".join(_fmt(x) for x in v)
    return str(v)


def _cellule(texte):
    return str(texte).replace("|", "\\|").replace("\n", " ")


def _plage(m):
    if m.choix:
        return "choix : " + ", ".join("`%s`" % c for c in m.choix)
    if m.plage:
        return "%s à %s" % (_fmt(m.plage[0]), _fmt(m.plage[1]))
    return "—"


def _ligne_param(chemin, m):
    origine = m.source or m.justification or ""
    if m.source and m.justification:
        origine = "%s — %s" % (m.source, m.justification)
    return "| `%s` | %s | %s | %s | %s | %s | %s |" % (
        chemin, _cellule(m.role), m.unite or "—", _cellule(_plage(m)), _cellule(_fmt(m.valeur)),
        LIBELLE_STATUT.get(m.statut, m.statut), _cellule(origine))


ENTETE = ("| Paramètre | Rôle | Unité | Plage / choix | Défaut | Statut | Source / justification |\n"
          "|---|---|---|---|---|---|---|")


def tableaux_parametres():
    lignes = []
    for section, arbre in P.SCHEMA.items():
        lignes += ["", "#### Section `%s`" % section, "", ENTETE]
        for chemin, m in P._iter_schema(arbre, section + "."):
            lignes.append(_ligne_param(chemin, m))
    lignes += ["", "#### Sous-schéma `ratelier` (grammaire râtelier mural)", "", ENTETE]
    for chemin, m in P._iter_schema(ratelier_mural.SCHEMA_RATELIER, "ratelier."):
        lignes.append(_ligne_param(chemin, m))
    lignes += ["", "#### Surcharges par typologie", "", "| Typologie | Paramètre | Valeur |", "|---|---|---|"]
    for typo in P.TYPOLOGIES:
        surch = P.OVERRIDES_TYPOLOGIE.get(typo) or {}
        plats = []

        def _aplatir(d, pre=""):
            for k, v in d.items():
                if isinstance(v, dict):
                    _aplatir(v, pre + k + ".")
                else:
                    plats.append((pre + k, v))
        _aplatir(surch)
        if not plats:
            lignes.append("| `%s` | — | (défauts communs) |" % typo)
        for c, v in plats:
            lignes.append("| `%s` | `%s` | %s |" % (typo, c, _cellule(_fmt(v))))
    return "\n".join(lignes).strip("\n")


def tableaux_compromis():
    lignes = []
    for fam in systemes.FAMILLES:
        lignes += ["", "#### Famille `%s`" % fam, "",
                   "| Système | Capacité | Discrétion | Solidité | Coût | Compromis | Statut |",
                   "|---|---|---|---|---|---|---|"]
        for cle in systemes.par_famille(fam):
            s = systemes.SYSTEMES[cle]
            c = s["compromis"]
            lignes.append("| `%s` — %s | %d | %d | %d | %d | %s | %s |" % (
                cle, _cellule(s["nom"]), c["capacite"], c["discretion"], c["solidite"], c["cout"],
                _cellule(c["texte"]), "**À VALIDER**" if s["a_valider"] else "sourcé"))
    return "\n".join(lignes).strip("\n")


def liste_a_valider():
    lignes = ["## Paramètres", ""]
    p = P.Parametres.pour_typologie("ratelier_mural", json_utilisateur=False)
    p.etendre("ratelier", ratelier_mural.SCHEMA_RATELIER)
    for chemin, m, _v in p.feuilles():
        if m.statut in ("a_valider", "todo"):
            lignes.append("- `%s` = %s (%s) — %s" % (chemin, _fmt(m.valeur), LIBELLE_STATUT[m.statut],
                                                     _cellule(m.justification or m.source or m.role)))
    lignes += ["", "## Catalogues", ""]
    for cle, e in bois.ESSENCES.items():
        if e["a_valider"]:
            lignes.append("- bois `%s` : champs sans source %s" % (cle, ", ".join(e["a_valider"])))
    for cle, f in bois.FINITIONS_BOIS.items():
        if f["a_valider"]:
            lignes.append("- finition bois `%s`" % cle)
    for cle, f in quincaillerie.FINITIONS_METAL.items():
        if f.get("a_valider"):
            lignes.append("- finition métal `%s`" % cle)
    for nom_cat, cat in (("visserie", quincaillerie.VISSERIE), ("charnière", quincaillerie.CHARNIERES),
                         ("vérin", quincaillerie.VERINS), ("système", systemes.SYSTEMES),
                         ("jonction", jonctions.JONCTIONS)):
        for cle, e in cat.items():
            if e.get("a_valider"):
                lignes.append("- %s `%s` : %s" % (nom_cat, cle, _cellule(e.get("source", ""))))
    for cle, s in systemes.SYSTEMES.items():
        if s.get("capacite_service") is None and s["famille"] not in ("crochet", "barre"):
            lignes.append("- capacité de service de `%s` : fiche fabricant à obtenir" % cle)
    lignes.append("- notes de compromis (1–5) de tous les systèmes : appréciations de conception à valider")
    return "\n".join(lignes)


def _remplacer_bloc(texte, marque, contenu):
    debut, fin = "<!-- DEBUT_%s -->" % marque, "<!-- FIN_%s -->" % marque
    if debut not in texte or fin not in texte:
        return texte
    avant = texte.split(debut)[0]
    apres = texte.split(fin, 1)[1]
    return avant + debut + "\n" + contenu + "\n" + fin + apres


def _ecrire(chemin, contenu):
    with io.open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(contenu)


def main():
    _ecrire(P.CHEMIN_DEFAUTS, json.dumps(P.valeurs_par_defaut(), ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    if not os.path.exists(P.CHEMIN_JSON):
        _ecrire(P.CHEMIN_JSON, json.dumps({"commun": {}, "typologies": {t: {} for t in P.TYPOLOGIES}},
                                          ensure_ascii=False, indent=2) + "\n")
    docs = os.path.join(RACINE, "docs")
    if not os.path.isdir(docs):
        os.makedirs(docs)
    tp, tc = tableaux_parametres(), tableaux_compromis()
    _ecrire(os.path.join(docs, "parametres.md"),
            "# Paramètres de la gamme Rangement (généré)\n\nNe pas éditer : `python outils/generer_docs.py`.\n\n"
            + tp + "\n")
    _ecrire(os.path.join(docs, "systemes.md"),
            "# Systèmes et compromis (généré)\n\nNotes 1 (faible) à 5 (excellent) ; coût : 5 = le moins cher.\n\n"
            + tc + "\n")
    _ecrire(os.path.join(docs, "a_valider.md"), "# Points À VALIDER / TODO (généré)\n\n" + liste_a_valider() + "\n")
    readme = os.path.join(RACINE, "README.md")
    if os.path.exists(readme):
        with io.open(readme, encoding="utf-8") as f:
            texte = f.read()
        texte = _remplacer_bloc(texte, "PARAMETRES", tp)
        texte = _remplacer_bloc(texte, "COMPROMIS", tc)
        _ecrire(readme, texte)
    print("Docs et JSON regeneres.")


if __name__ == "__main__":
    main()
