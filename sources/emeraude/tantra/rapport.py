# -*- coding: utf-8 -*-
"""Génère la partie chiffrée des fiches ``docs/<typologie>.md`` (Python pur).

Usage : ``python -m tantra.rapport`` depuis la racine du projet. Le texte
rédigé à la main est conservé ; seul le bloc compris entre les marqueurs
``<!-- DEBUT GENERE -->`` et ``<!-- FIN GENERE -->`` est remplacé.
"""

from __future__ import annotations

import os

from tantra import registre

DEBUT, FIN = "<!-- DEBUT GENERE -->", "<!-- FIN GENERE -->"
ICONE = {"ok": "ok", "avertissement": "AVERTISSEMENT", "essai_requis": "essai requis", "non_conforme": "NON CONFORME"}


def bloc_markdown(nom: str) -> str:
    e = registre.entree(nom)
    lignes = [DEBUT, "", "## Résultats calculés (générés par `python -m tantra.rapport`)", ""]
    lignes += ["| État | Hors-tout l × p × h (mm) | Masse (kg) | Pièces | Ancrages | Conforme |", "|---|---|---|---|---|---|"]
    for s in e.etats:
        g = e.geometrie(s)
        l, p, h = g.dimensions_hors_tout
        lignes.append(f"| {s} | {l:.0f} × {p:.0f} × {h:.0f} | {g.derivees['masse_kg']:.1f} | {len(g.pieces)} | "
                      f"{len(g.ancrages)} | {'oui' if g.conforme else 'NON'} |")
    for s in e.etats:
        g = e.geometrie(s)
        lignes += ["", f"### Vérifications — état {s}", "", "| Niveau | Code | Détail |", "|---|---|---|"]
        for v in g.verifications:
            lignes.append(f"| {ICONE.get(v.niveau, v.niveau)}{' (compromis)' if v.compromis else ''} | `{v.code}` | "
                          f"{v.message.replace('|', '/')} |")
        lignes += ["", f"Ancrages ({s}) :", ""]
        for a in g.ancrages:
            x, y, z = a.position
            lignes.append(f"* `{a.nom}` — ({x:.0f}, {y:.0f}, {z:.0f}) mm, dans `{a.piece_support}` : {a.commentaire}")
    c = e.chiffrage()
    lignes += ["", "### Chiffrage indicatif (estimation datée de novembre 2026, HT sauf mention)", "",
               "| Poste | Montant |", "|---|---|",
               f"| Bois (pertes comprises) | {c.bois_eur:.0f} € |", f"| Mousses | {c.mousse_eur:.0f} € |",
               f"| Revêtements (+25 % de chutes) | {c.revetement_eur:.0f} € |",
               f"| Quincaillerie | {c.quincaillerie_eur:.0f} € |",
               f"| Finition + emballage | {c.finition_emballage_eur:.0f} € |",
               f"| Amortissement moules | {c.moules_eur:.0f} € |",
               f"| Main-d'œuvre ({c.heures_ebenisterie:.1f} h ébénisterie + {c.heures_tapisserie:.1f} h tapisserie) | "
               f"{c.main_oeuvre_eur:.0f} € |",
               f"| **Coût de revient** | **{c.cout_revient_ht:.0f} € HT** |",
               f"| Prix de vente indicatif (× 1,45) | {c.prix_vente_ht:.0f} € HT — **{c.prix_vente_ttc:.0f} € TTC** "
               f"(fourchette {c.fourchette_ttc[0]:.0f}–{c.fourchette_ttc[1]:.0f} €) |",
               f"| Prototype unitaire | ≈ {c.prix_prototype_ttc:.0f} € TTC |", "",
               "### Paramètres Fusion propres à la typologie", ""]
    for n, (val, unite, com) in registre.parametres_fusion(nom).items():
        lignes.append(f"* `{n}` = {val:g} {unite} — {com}")
    if registre.nom_parametre_etat(nom):
        lignes.append(f"\nChanger `{registre.nom_parametre_etat(nom)}` puis relancer le script régénère l'autre état.")
    lignes += ["", FIN]
    return "\n".join(lignes)


def mettre_a_jour(dossier_docs: str) -> list[str]:
    ecrits = []
    for nom in registre.REGISTRE:
        chemin = os.path.join(dossier_docs, f"{nom}.md")
        texte = open(chemin, encoding="utf-8").read() if os.path.exists(chemin) else f"# {nom}\n\n"
        bloc = bloc_markdown(nom)
        if DEBUT in texte and FIN in texte:
            texte = texte[:texte.index(DEBUT)] + bloc + texte[texte.index(FIN) + len(FIN):]
        else:
            texte = texte.rstrip() + "\n\n" + bloc + "\n"
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(texte)
        ecrits.append(chemin)
    return ecrits


def tableau_chiffrages_markdown() -> str:
    lignes = ["| Typologie | Volet | Prix indicatif TTC | Fourchette | Prototype |", "|---|---|---|---|---|"]
    for nom, volet, ttc, (a, b), proto in registre.tableau_chiffrages():
        lignes.append(f"| {nom} | {volet} | {ttc:.0f} € | {a:.0f}–{b:.0f} € | ≈ {proto:.0f} € |")
    return "\n".join(lignes)


if __name__ == "__main__":
    racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for c in mettre_a_jour(os.path.join(racine, "docs")):
        print("écrit", c)
    print(tableau_chiffrages_markdown())
