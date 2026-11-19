# -*- coding: utf-8 -*-
"""Genere docs/parametres.md, docs/regles_materiaux.md, docs/rapport_entrave.txt et docs/ajustements_v2.md.

Usage : python outils/generer_docs.py
"""
import json
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

from neogothique.parametres import Parametres, tableau_markdown, OVERRIDES_TYPOLOGIE  # noqa: E402
from neogothique.catalogues import CATEGORIES, SELECTIONS  # noqa: E402
from neogothique import regles  # noqa: E402
from neogothique.grammaires import entrave as E  # noqa: E402

DOCS = os.path.join(RACINE, "docs")


def doc_parametres():
    p = Parametres.pour_typologie("entrave", json_utilisateur=False)
    r = E.calculer_entrave(p)
    L = ["# Parametres de la gamme Neogothique (couche 1)", "",
         "Genere par `outils/generer_docs.py` depuis `neogothique/parametres.py` (source de verite).", "",
         "Unites internes : mm, kg, deg, N, MPa. Valeurs affichees : typologie `entrave` (override : %s)." %
         OVERRIDES_TYPOLOGIE["entrave"], "",
         "Statuts : **impose** (fixe par Fabien), **a_valider** (propose, voir points_a_trancher.md), "
         "**derive** (peut etre recalcule par les regles materiaux), **libre** (reference de gamme).", "",
         "Nom Fusion : `neo_` + chemin avec `_` (ex. `cremaillere.pas` -> `neo_cremaillere_pas`). Les textes et "
         "booleens ne sont pas exportes (Fusion ne gere que des valeurs numeriques).", "",
         tableau_markdown(p), "",
         "## Grandeurs derivees (calculees par la grammaire Entrave, cran %d)" % r.cran, "",
         "| Grandeur | Valeur | Unite | Role |", "|---|---|---|---|"]
    c = r.cotes
    derives = [("hauteur", "mm", "Dessus de platine = hauteur_mini + cran x pas"),
               ("hauteurs_crans", "mm", "Hauteurs des 7 positions"),
               ("coulisseau", "mm", "Section du coulisseau (pied - 2 parois - 2 jeux ; octogone : limite par les pans)"),
               ("coulisseau_longueur", "mm", "Longueur du coulisseau sous la platine"),
               ("fourreau_hauteur", "mm", "Hauteur du fourreau (pied visible)"),
               ("recouvrement_haut", "mm", "Recouvrement coulisseau/fourreau en position haute"),
               ("pignon_dents", "", "Dents du pignon = max(dents_mini, course/(pi.m))"),
               ("pignon_d_primitif", "mm", "m.z"), ("course_par_tour", "mm", "pi.m.z"),
               ("z_arbre", "mm", "Hauteur des arbres bas"), ("z_loquet", "mm", "Hauteur des penes"),
               ("trous_crans", "mm", "Trous de crans depuis le bas de la barre de calage"),
               ("barre_calage_longueur", "mm", "Longueur des cremailleres laterales"),
               ("dilatation_platine", "mm", "Mouvement transversal calcule de la platine"),
               ("jeu_mortaise_oblongue", "mm", "Jeu retenu (mortaises arriere)"),
               ("hauteur_mini_pour_recouvrement", "mm", "hauteur_mini mini pour un recouvrement de 1,5 x section"),
               ("h_plinthe", "mm", "Plinthe = H/phi^4 (style.proportions)"),
               ("h_fut", "mm", "Fut = H/phi"), ("h_chapiteau", "mm", "Chapiteau + astragale = H/phi^3"),
               ("a_max", "mm", "Largeur de plinthe et d'abaque = cote + 2 x debord_base"),
               ("a_fut_haut", "mm", "Largeur du haut du fut = cote - 2 x fuselage"),
               ("paroi_plats", "mm", "Paroi du fourreau sur les plats (haut du fut)"),
               ("paroi_diagonale", "mm", "Paroi dans l'arete chanfreinee / le pan coupe"),
               ("ceinture_baie", "mm", "Largeur des baies de la ceinture"),
               ("ceinture_montant", "mm", "Montant de bois entre deux baies"),
               ("penture_inset", "mm", "Axe des pentures depuis le bord (terminaison + recul)"),
               ("penture_bande_droite", "mm", "Partie droite des pentures (rivets)"),
               ("coussin_cellules", "", "Cellules du matelassage en losange")]
    for k, u, role in derives:
        if k not in c:
            continue
        v = c[k]
        v = ", ".join("%g" % x for x in v) if isinstance(v, list) else ("%g" % v)
        L.append("| `%s` | %s | %s | %s |" % (k, v, u, role))
    L += ["", "User Parameters a expression liee crees en plus dans Fusion :", "",
          "| Nom | Expression | Unite | Commentaire |", "|---|---|---|---|"]
    for nom, expr, u, com in r.parametres_derives:
        L.append("| `%s` | `%s` | %s | %s |" % (nom, expr, u, com))
    L += ["", "## Overrides", "",
          "- Par typologie : `OVERRIDES_TYPOLOGIE` dans `parametres.py` (fusion profonde).",
          "- Par fichier : copier `neogothique/parametres_neogothique.exemple.json` en "
          "`neogothique/parametres_neogothique.json` (charge automatiquement : `commun` puis `typologies.<nom>`).",
          "- Par code : `Parametres.pour_typologie('entrave', {'cremaillere.pas': 30.0})` (cles pointees ou dict imbrique)."]
    with open(os.path.join(DOCS, "parametres.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def doc_regles():
    with open(os.path.join(DOCS, "regles_materiaux_intro.md"), "r", encoding="utf-8") as f:
        L = [f.read().rstrip(), ""]
    L += ["## Catalogue des regles (genere)", ""]
    sel_par_cat = {}
    for chemin, cat in SELECTIONS.items():
        sel_par_cat.setdefault(cat, []).append(chemin)
    for cat, dico in CATEGORIES.items():
        L += ["### Categorie `%s` (selection : %s)" % (cat, ", ".join("`%s`" % s for s in sel_par_cat.get(cat, []))), ""]
        for cle, ent in dico.items():
            rs = ent.get("regles", [])
            L.append("**`%s`** - %s : %d regle(s)" % (cle, ent.get("nom", ""), len(rs)))
            L.append("")
            if rs:
                L += ["| id | operation | cibles | propriete / valeur | explication |", "|---|---|---|---|---|"]
                for r in rs:
                    pv = r.get("propriete") or r.get("valeur", "")
                    if "exposant" in r:
                        pv = "%s ^ %.3g" % (pv, r["exposant"])
                    if "facteur" in r or "ajout" in r:
                        pv = "defaut x %g + %g" % (r.get("facteur", 1.0), r.get("ajout", 0.0))
                    if r["operation"] == "minimum_section_nette":
                        pv = "(%s + %g) / (1 - %g)" % (" + ".join(r.get("bases", [])), r.get("constante", 0.0),
                                                       r.get("taux", 0.0))
                    L.append("| %s | %s | %s | %s | %s |" % (r["id"], r["operation"], ", ".join(r.get("cibles", [])) or "-",
                                                          pv, r["explication"].replace("|", "/")))
                L.append("")
    L += ["## Exemples executes (typologie entrave)", ""]
    p = Parametres.pour_typologie("entrave", json_utilisateur=False)
    for chemin, cle in (("bois.essence", "chene"), ("ferrures.metal", "laiton_mat"),
                        ("garnissage.cuir_manilles", "cuir_harnais_noir"), ("entrave.manilles.pivot_cou", "rotule"),
                        ("bois.essence", "chene_fume"), ("ferrures.finition", "galvanisation_peinture_mate"),
                        ("cremaillere.decor_barre", "festonnee"), ("cremaillere.decor_barre", "ajouree"),
                        ("ferrures.terminaison_pentures", "queue_d_aronde"),
                        ("garnissage.cuir_manilles", "cuir_synthetique_pu_noir")):
        q, aj = regles.changer_materiau(p, chemin, cle)
        L += ["### `%s` -> `%s`" % (chemin, cle), "", "```", regles.rapport(aj), "```", ""]
    with open(os.path.join(DOCS, "regles_materiaux.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def rapport():
    p = Parametres.pour_typologie("entrave", json_utilisateur=False)
    txt = [E.rapport_texte(E.calculer_entrave(p, cran=0)), "", "=" * 78, "",
           E.rapport_texte(E.calculer_entrave(p, cran=p.nombre_positions() - 1))]
    with open(os.path.join(DOCS, "rapport_entrave.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(txt) + "\n")


def json_defauts():
    p = Parametres.pour_typologie("entrave", json_utilisateur=False)
    p.vers_json(os.path.join(DOCS, "parametres_entrave_defauts.json"))


PREFIXES_STYLE = ("style.", "sellerie.", "entrave.pied.", "entrave.ceinture.", "entrave.pentures.",
                  "entrave.platine.chant", "entrave.semelle.", "entrave.fourreau.", "ferrures.", "cremaillere.barre",
                  "cremaillere.habillage", "cremaillere.decor", "cremaillere.capot", "garnissage.", "bois.chanfrein",
                  "charges.marge_mini")


def doc_style():
    p = Parametres.pour_typologie("entrave", json_utilisateur=False)
    with open(os.path.join(DOCS, "style_intro.md"), "r", encoding="utf-8") as f:
        L = [f.read().rstrip(), "", "## Reference : tous les parametres de style (genere)", "",
             "| Chemin | Defaut | Unite | Plage / choix | Statut | Role |", "|---|---|---|---|---|---|"]
    for k, v in sorted(_aplatir(p.valeurs).items()):
        if not k.startswith(PREFIXES_STYLE):
            continue
        m = p.meta(k)
        if m is None:
            continue
        pl = ", ".join(str(x) for x in m.choix) if m.choix else (
            "%g - %g" % tuple(m.plage) if m.plage else "")
        L.append("| `%s` | %s | %s | %s | %s | %s |" % (k, _fmt(v), m.unite, pl, m.statut, m.role.replace("|", "/")))
    with open(os.path.join(DOCS, "style.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def _aplatir(d, prefixe=""):
    res = {}
    for k, v in d.items():
        ch = prefixe + k
        if isinstance(v, dict):
            res.update(_aplatir(v, ch + "."))
        else:
            res[ch] = v
    return res


def _fmt(v):
    return ("%g" % v) if isinstance(v, float) else str(v)


AJUSTEMENTS_INTRO = """# Ajustements v0.1 -> v0.2 : Neogothique « raffine »

Genere par `outils/generer_docs.py` (comparaison automatique de
`docs/parametres_entrave_defauts_v1.json` et `docs/resultats_entrave_v1.json`,
instantanes de la v0.1, avec les defauts et resultats actuels).

Direction : toujours medieval / neogothique (angles francs, sections carrees,
ferrures apparentes, zero vis) mais finition elegante : proportions au nombre
d'or, moulures reelles sur les chants (conge, bec-de-corbin, quart-de-rond,
cavet), colonnes a plinthe / fut a chanfreins arretes / astragale / chapiteau,
ceintures ajourees d'une arcature, ferrures forgees plus fines a terminaisons,
rivets goutte de suif, sellerie fine. La regle « zero courbe organique »
devient : *pas de courbes organiques type Equinox, mais des moulures et
chanfreins travailles sur les chants* (arcs de cercle et droites uniquement).
"""


def ajustements():
    p = Parametres.pour_typologie("entrave", json_utilisateur=False)
    with open(os.path.join(DOCS, "parametres_entrave_defauts_v1.json"), "r", encoding="utf-8") as f:
        v1 = _aplatir(json.load(f))
    v2 = _aplatir(p.valeurs)
    L = [AJUSTEMENTS_INTRO, "## Parametres modifies (avant -> apres)", "",
         "| Chemin | v0.1 | v0.2 | Unite | Role |", "|---|---|---|---|---|"]
    for k in sorted(v1):
        if k in v2 and v1[k] != v2[k]:
            m = p.meta(k)
            L.append("| `%s` | %s | **%s** | %s | %s |" % (k, _fmt(v1[k]), _fmt(v2[k]), m.unite if m else "",
                                                      (m.role if m else "").replace("|", "/")))
    L += ["", "## Parametres ajoutes", "", "| Chemin | Valeur | Unite | Role |", "|---|---|---|---|"]
    for k in sorted(v2):
        if k not in v1:
            m = p.meta(k)
            L.append("| `%s` | %s | %s | %s |" % (k, _fmt(v2[k]), m.unite if m else "",
                                                (m.role if m else "").replace("|", "/")))
    retires = [k for k in sorted(v1) if k not in v2]
    L += ["", "## Parametres retires", ""] + (["- `%s` (v0.1 : %s)" % (k, _fmt(v1[k])) for k in retires] or ["- aucun"])
    with open(os.path.join(DOCS, "resultats_entrave_v1.json"), "r", encoding="utf-8") as f:
        r1 = json.load(f)
    r = E.calculer_entrave(p)
    c = r.cotes
    L += ["", "## Resultats de la grammaire (cran 0, defauts)", "",
          "| Grandeur | v0.1 | v0.2 |", "|---|---|---|",
          "| Masse totale | %.1f kg | %.1f kg |" % (r1["masse_totale_kg"], r.masses["total"]),
          "| Masse mobile / fixe | %.1f / %.1f kg | %.1f / %.1f kg |" % (r1["masse_mobile_kg"], r1["masse_fixe_kg"],
                                                                     r.masses["mobile"], r.masses["fixe"]),
          "| Corps Fusion | %d | %d (dont %d blocs moulures, %d revolutions) |" % (
              r1["nombre_corps"], len(r.solides), sum(1 for s in r.solides if isinstance(s, E.BlocProfile)),
              sum(1 for s in r.solides if isinstance(s, E.Revolution))),
          "| Coulisseau | %g mm | %g mm |" % (r1["coulisseau_mm"], c["coulisseau"]),
          "| Recouvrement en position haute | %g mm | %g mm |" % (r1["recouvrement_haut_mm"], c["recouvrement_haut"]),
          "| Barre de calage / loquet | %g mm, z=%g | %g mm, z=%g |" % (r1["barre_calage_longueur_mm"], r1["z_loquet_mm"],
                                                                       c["barre_calage_longueur"], c["z_loquet"]),
          "", "| Verification | v0.1 (valeur / limite, niveau) | v0.2 (valeur / limite, marge, niveau) |",
          "|---|---|---|"]
    for v in r.verifications:
        a = r1["verifications"].get(v.ident)
        avant = ("%.4g / %.4g, %s" % (a["valeur"], a["limite"], a["niveau"])) if a else "(nouvelle)"
        L.append("| %s | %s | %.4g / %.4g, x%.2f, %s |" % (v.ident, avant, v.valeur, v.limite, v.marge, v.niveau))
    with open(os.path.join(DOCS, "ajustements_v2.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    json_defauts()
    ajustements()
    doc_style()
    doc_parametres()
    doc_regles()
    rapport()
    print("docs generees")
