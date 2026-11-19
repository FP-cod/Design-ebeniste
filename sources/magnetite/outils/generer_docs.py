# -*- coding: utf-8 -*-
"""Genere docs/parametres.md, docs/assortiments.md, docs/rapport_menottes.txt et le patron SVG.

    python outils/generer_docs.py

docs/compromis.md est redige a la main (arbitrages argumentes).
"""

import os
import sys

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, RACINE)

from gamme_cuir import geometrie as geo  # noqa: E402
from gamme_cuir.catalogues import correspondances_meubles as cm  # noqa: E402
from gamme_cuir.catalogues import cuirs, quincaillerie as q  # noqa: E402
from gamme_cuir.fusion_outils import rapport_texte  # noqa: E402
from gamme_cuir.grammaires import menottes  # noqa: E402
from gamme_cuir.parametres import Parametres  # noqa: E402

DOCS = os.path.join(RACINE, "docs")


def _fmt(v):
    if isinstance(v, bool):
        return "oui" if v else "non"
    if isinstance(v, float):
        return ("%g" % v).replace(".", ",")
    if isinstance(v, dict):
        return " ; ".join("%s %s-%s" % (k, _fmt(a), _fmt(b)) for k, (a, b) in v.items())
    return str(v)


def doc_parametres():
    p = Parametres(json_utilisateur=False)
    L = ["# Parametres globaux GammeCuir", "",
         "Genere par `outils/generer_docs.py` depuis `gamme_cuir/parametres_gamme_cuir.defauts.json` "
         "(lui-meme produit par `outils/_generer_defauts_json.py`). Surcharges projet : "
         "`gamme_cuir/parametres_gamme_cuir.json`. Unites internes mm / N ; seul `fusion_outils` convertit en cm.", "",
         "Statuts : `impose` (fixe par Fabien), `a_valider` (proposition a trancher), `derive`, `libre`. "
         "Une source = valeur reprise d'une autre gamme (chemin sous /workspace) ; pas de source = proposition "
         "GammeCuir.", ""]
    section = None
    for chemin, m, v in p.feuilles():
        s = chemin.split(".")[0]
        if s != section:
            section = s
            L += ["", "## `%s`" % s, "", "| Parametre | Valeur | Unite | Plage / choix | Statut | Role | Justification | Source |",
                  "|---|---|---|---|---|---|---|---|"]
        borne = ("%s - %s" % (_fmt(m["plage"][0]), _fmt(m["plage"][1]))) if m.get("plage") else \
            (", ".join(m["choix"]) if m.get("choix") else "")
        L.append("| `%s` | %s | %s | %s | %s | %s | %s | %s |" % (
            chemin, _fmt(v), m["unite"] or "-", borne, m["statut"], m["role"], m["justification"],
            m.get("source") or ""))
    L += ["", "## Grandeurs derivees (defauts)", "",
          "- epaisseur totale (doublure + rembourrage + exterieur) : %s mm" % _fmt(p.epaisseur_totale()),
          "- epaisseur cuir seul (zones percees) : %s mm" % _fmt(p.epaisseur_cuir_seul()),
          "- classe d'epaisseur exterieure : %s" % p.classe_epaisseur(),
          "- points de couture par cm : %.2f" % p.points_par_cm(), ""]
    return "\n".join(L)


def _cellule(teinte, gamme):
    if gamme == "tantra":
        return "a confirmer (aucun catalogue)"
    lignes = []
    for c in cm.meubles_assortis(teinte, gamme):
        typ = "" if c["type"] == "exact" else " *(proche, a valider)*"
        cuir = "" if c["cuir_veritable"] else " [non cuir]"
        lignes.append("`%s` / %s%s%s -> %s" % (c["materiau"], c["coloris"], cuir, typ, ", ".join(c["typologies"])))
    return "<br>".join(lignes) if lignes else "-"


def doc_assortiments():
    L = ["# Assortiments par teinte de cuir", "",
         "Genere par `outils/generer_docs.py` depuis `gamme_cuir/catalogues/correspondances_meubles.py`. "
         "Identifiants = cles REELLES des catalogues meubles (instantane du 18/11/2026, verifie par "
         "`tests/test_correspondances.py` contre les catalogues vivants).", "",
         "Statut : **assortie** = meme coloris sur un cuir veritable meuble ; **assortie_hors_cuir** = meme coloris "
         "seulement sur un revetement non cuir (vegan, tissu) ; **proche** = nuance voisine a valider sur echantillon ; "
         "**non_assortie** = aucun meuble.", "",
         "| Teinte | Statut | Equinox | Neogothique | Incognito | Tantra | Quincaillerie conseillee | Possible (contraste) |",
         "|---|---|---|---|---|---|---|---|"]
    for t, d in cuirs.TEINTES.items():
        L.append("| **%s** | %s | %s | %s | %s | %s | %s | %s |" % (
            t, cm.statut_teinte(t), _cellule(t, "equinox"), _cellule(t, "neogothique"), _cellule(t, "incognito"),
            _cellule(t, "tantra"), ", ".join("`%s`" % m for m in d["quincaillerie_conseillee"]),
            ", ".join("`%s`" % m for m in d["quincaillerie_possible"])))
    L += ["", "## Quincaillerie des meubles (pour accorder les metaux)", ""]
    for g, d in cm.QUINCAILLERIE_MEUBLES.items():
        ids = ", ".join("`%s`" % x for k, v in d.items() if isinstance(v, list) for x in v)
        L.append("- **%s** (%s) : %s %s" % (g, d.get("fichier", "-"), ids, d.get("notes", "")))
    L += ["", "## Metaux GammeCuir", "", "| Cle | Metal | Contact peau | Cout | Reference meuble |", "|---|---|---|---|---|"]
    for k, m in q.METAUX.items():
        L.append("| `%s` | %s | %s | %s | %s |" % (k, m["nom"], m["contact_peau"], m["cout"], m["reference_meuble"] or "-"))
    L += ["", "## Gammes sans catalogue", ""]
    L += ["- **%s** : %s" % (g, txt) for g, txt in cm.GAMMES_SANS_CATALOGUE.items()]
    L += ["", "## Exemples d'ensembles", "",
          "- Banc Flore / croix / tabouret / chaise trone Equinox en `cuir_classique_pleine_fleur` cognac -> menottes "
          "vachette vegetale **cognac**, quincaillerie **laiton massif CW510L**, fil naturel ou ton sur ton.",
          "- Entrave Neogothique (`cuir_sellier_fin_noir`, fer forge cire noire) -> menottes **noir**, quincaillerie "
          "**inox PVD noir** (accord fer forge) ou laiton patine *hors contact peau*.",
          "- Banquette / pouf Incognito (interieur `cuir_cognac`) -> menottes **cognac** ; rangees dans le coffre "
          "(regle 'zero cuir visible' en facade).", ""]
    return "\n".join(L)


def patron_svg(plan):
    """Patron de coupe a l'echelle 1 (mm) : bande, percages, points de couture, passant, patte."""
    def chemin(contour):
        d = []
        for s in contour:
            if s[0] == "ligne":
                d.append("M %.2f %.2f L %.2f %.2f" % (s[1] + s[2]))
            elif s[0] == "arc":
                p0 = geo.point_arc(s[1], s[2], s[3])
                p1 = geo.point_arc(s[1], s[2], s[4])
                d.append("M %.2f %.2f A %.2f %.2f 0 0 1 %.2f %.2f" % (p0 + (s[2], s[2]) + p1))
            else:
                (x, y), r = s[1], s[2]
                d.append("M %.2f %.2f a %.2f %.2f 0 1 0 %.2f 0 a %.2f %.2f 0 1 0 %.2f 0" % (x - r, y, r, r, 2 * r, r, r, -2 * r))
        return " ".join(d)
    prims = [x for x in plan.primitives() if x.type in ("plaque", "percage", "couture")
             and (x.type != "plaque" or x.categorie == "cuir") and x.nom != "patte_anneau_repliee"]
    boites = [geo.boite_englobante(x.contour) for x in prims]
    x0, x1 = min(b[0] for b in boites) - 10, max(b[1] for b in boites) + 10
    y0, y1 = min(b[2] for b in boites) - 10, max(b[3] for b in boites) + 10
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.1fmm" height="%.1fmm" viewBox="%.1f %.1f %.1f %.1f">'
           % (x1 - x0, y1 - y0, x0, y0, x1 - x0, y1 - y0),
           '<title>%s - patron a l\'echelle 1 (mm)</title>' % plan.nom]
    for x in prims:
        if x.type == "couture":
            out += ['<circle cx="%.2f" cy="%.2f" r="0.4" fill="#c00"/>' % pt for pt in x.points]
        elif x.nom.startswith("bande_doublure"):
            continue
        else:
            coul = "#000" if x.type == "plaque" else "#06c"
            out.append('<path d="%s" fill="none" stroke="%s" stroke-width="0.2"><title>%s</title></path>'
                       % (chemin(x.contour), coul, x.nom))
    out.append("</svg>")
    return "\n".join(out)


def main():
    os.makedirs(DOCS, exist_ok=True)
    with open(os.path.join(DOCS, "parametres.md"), "w", encoding="utf-8") as f:
        f.write(doc_parametres())
    with open(os.path.join(DOCS, "assortiments.md"), "w", encoding="utf-8") as f:
        f.write(doc_assortiments())
    plan = menottes.concevoir(params=Parametres(json_utilisateur=False))
    with open(os.path.join(DOCS, "rapport_menottes.txt"), "w", encoding="utf-8") as f:
        f.write(rapport_texte(plan))
    with open(os.path.join(DOCS, "patron_%s.svg" % plan.nom), "w", encoding="utf-8") as f:
        f.write(patron_svg(plan))
    print("docs generees dans", DOCS)


if __name__ == "__main__":
    main()
