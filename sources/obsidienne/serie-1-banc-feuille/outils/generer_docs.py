# -*- coding: utf-8 -*-
"""Regenere docs/parametres.md, docs/regles_materiaux.md et les apercus PNG.

Usage : python outils/generer_docs.py   (depuis la racine du projet)
"""

import os
import sys

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, RACINE)

from equinox import regles  # noqa: E402
from equinox.catalogues import attaches, bois, garnissage, metaux  # noqa: E402
from equinox.grammaires import banc_flore, chaise_trone, croix_saint_andre, tabouret  # noqa: E402
from equinox.parametres import Parametres  # noqa: E402

DOCS = os.path.join(RACINE, "docs")
STATUT = {"impose": "**impose**", "a_valider": "a valider", "derive": "derive", "libre": "libre"}


def _v(v):
    if isinstance(v, float):
        return "%g" % v
    return "`%s`" % v if isinstance(v, str) else str(v)


def _table(params, racines=None):
    lignes = ["| Chemin | Valeur | Unite | Role | Plage / choix | Statut | Utilise par |",
              "|---|---|---|---|---|---|---|"]
    for chemin, meta, val in params.feuilles():
        if racines and chemin.split(".")[0] not in racines:
            continue
        plage = ("%g - %g" % meta.plage) if meta.plage else (", ".join(meta.choix) if meta.choix else "")
        lignes.append("| `%s` | %s | %s | %s | %s | %s | %s |" % (
            chemin, _v(val), meta.unite, meta.role.replace("|", "/"), plage, STATUT[meta.statut],
            ", ".join(meta.utilise_par) or "-"))
    return "\n".join(lignes)


def parametres_md():
    p = Parametres()
    out = ["# Parametres Equinox (couche 1)", "",
           "Genere par `outils/generer_docs.py` depuis `equinox/parametres.py` et les schemas specifiques des "
           "grammaires. Unites internes mm / kg / deg (l'export Fusion ecrit des expressions `700 mm`, `7 deg`, "
           "Fusion convertit en cm internes).", "",
           "Statuts : **impose** = valeur donnee par Fabien ; *a valider* = proposition a trancher ; *derive* = "
           "recalcule par les regles materiaux (`equinox/regles.py`).", "",
           "Overrides : `equinox/parametres_equinox.json` (`commun` et `typologies.<nom>`), "
           "`OVERRIDES_TYPOLOGIE` dans `parametres.py`, ou `concevoir(overrides={'bois.section_noeud': 52})`.", "",
           "Nom Fusion d'un parametre : `eq_` + chemin avec `_` (ex. `eq_bois_section_noeud`).", "",
           "## Vocabulaire commun", "", _table(p), ""]
    for titre, mod, racine, schema in (("Banc Flore (`flore.*`)", banc_flore, "flore", banc_flore.SCHEMA_FLORE),
                                       ("Croix de Saint-Andre (`croix.*`)", croix_saint_andre, "croix",
                                        croix_saint_andre.SCHEMA_CROIX),
                                       ("Tabouret (`tabouret.*`)", tabouret, "tabouret", tabouret.SCHEMA_TABOURET),
                                       ("Chaise / trone (`chaise.*`)", chaise_trone, "chaise", chaise_trone.SCHEMA_CHAISE)):
        q = Parametres().etendre(racine, schema)
        out += ["## %s" % titre, "", _table(q, [racine]), ""]
    from equinox.parametres import OVERRIDES_TYPOLOGIE
    out += ["## Overrides par typologie", ""]
    for t, o in OVERRIDES_TYPOLOGIE.items():
        out.append("- `%s` : %s" % (t, o or "aucun"))
    return "\n".join(out) + "\n"


def regles_md():
    out = ["# Regles materiaux -> geometrie", "",
           "Genere par `outils/generer_docs.py`. Chaque entree de catalogue porte un champ `regles` declaratif ; "
           "`equinox.regles.changer_materiau(params, categorie, cle)` les applique, recalcule en cascade les "
           "jonctions (tourillons, tenons, mortaises, inserts) et renvoie la liste des ajustements.", "",
           "Statuts d'ajustement : `AJUSTE` (parametre libre/derive modifie), `AJUSTE (valeur imposee modifiee, a "
           "confirmer)` (une valeur donnee par Fabien a du changer), `BLOQUE` (option `forcer_imposes=False`, ou au "
           "lancement d'une grammaire : la valeur imposee est gardee et le conflit signale), `ALERTE` "
           "(information sans modification).", "",
           "## Calculs du moteur", "",
           "| Calcul | Formule / regle |", "|---|---|",
           "| `section_equivalente` | d = d_frene x max((E_frene/E)^1/4, (MOR_frene/MOR)^1/3, 1) arrondi au mm sup. "
           "(rigidite en flexion E.I ~ E.d^4, resistance M/W ~ MOR.d^3) ; jamais de reduction |",
           "| `rayon_cintrage` | lamelle-colle : R >= ratio_lamelle x e_lamelle ; vapeur : R >= ratio_vapeur x "
           "section_noeud ; arrondi 10 mm ; le rayon n'est jamais diminue |",
           "| `copier` | prend la valeur de la propriete du catalogue (rembourrage, fixation, rayon de bord) |",
           "| `fixer` | impose une valeur (option `si_parmi`) |",
           "| `tourillon` | d = section_noeud / 5 -> standard 6/8/10/12/14 |",
           "| `longueur_tourillon` | L = 5 d |", "| `tenon` | e = section_noeud / 3 |",
           "| `mortaise` | p = 0,8 x section_noeud |",
           "| `longueur_insert` | 20 mm si densite >= 650 kg/m3, sinon 25 mm |",
           "| `section_metal_equivalente` | d = d_ref x (Re_ref/Re)^1/3 |",
           "| `capacite_lest` | kg/m = (cote - 2 paroi)^2 x densite x taux_remplissage -> longueur de tube requise |",
           "| `alerte` | message |", ""]
    for titre, cat in (("Bois", bois.BOIS), ("Garnissages", garnissage.GARNISSAGES), ("Metaux et lests", metaux.METAUX),
                       ("Attaches", attaches.ATTACHES)):
        out += ["## %s" % titre, ""]
        for cle, ent in cat.items():
            out.append("### `%s` - %s" % (cle, ent["nom"]))
            props = {k: v for k, v in ent.items() if k not in ("nom", "regles", "notes")}
            out.append("")
            out.append("Proprietes : " + " ; ".join("%s = %s" % (k, v) for k, v in props.items()))
            if ent.get("notes"):
                out.append("")
                out.append("Notes : " + ent["notes"])
            out.append("")
            if ent["regles"]:
                for r in ent["regles"]:
                    out.append("- `%s` <- `%s` %s : %s" % (r.get("cible") or "(alerte)", r["calcul"],
                                                          r.get("args", ""), r.get("raison", "")))
            else:
                out.append("- (aucune regle propre)")
            out.append("")
    p = Parametres.pour_typologie("banc_flore", json_utilisateur=False)
    from equinox.catalogues.garnissage import ECHELLE_ABRASION, CATEGORIES_COUT
    out += ["## Revetements : synthese", "",
            "Echelle d'abrasion Equinox 1-10 : " + " ; ".join("%s = %d-%d" % (k, a, b) for k, (a, b) in ECHELLE_ABRASION.items())
            + ". Couts au m2 par categorie (sans prix) : " + ", ".join(CATEGORIES_COUT) + ".", "",
            "| Cle | Famille | Coloris | Epaisseur (plage) | Abrasion /10 (Martindale) | Cout m2 | Rembourrage | Fixation | Bords |",
            "|---|---|---|---|---|---|---|---|---|"]
    for cle, e in garnissage.GARNISSAGES.items():
        out.append("| `%s` | %s | %s | %g (%g-%g) mm | %d (%s) | %s | %g mm | %s | %s |" % (
            cle, e["famille"], ", ".join(e["coloris"]), e["epaisseur_matiere"], e["epaisseur_plage"][0],
            e["epaisseur_plage"][1], e["abrasion"], e["abrasion_martindale"] or "n/a", e["cout_m2"],
            garnissage.rembourrage_recommande(cle), e["methode_fixation"], e["finition_bords"]))
    out += ["", "Alias conserves : " + ", ".join("`%s` -> `%s`" % kv for kv in garnissage.ALIAS.items()), ""]
    out += ["## Ajustements calcules sur le banc Flore (assise maintenue a 700 mm)", ""]
    for cle in garnissage.GARNISSAGES:
        _, aj = regles.changer_materiau(p, "garnissage", cle)
        out += ["### garnissage -> `%s`" % cle, "", "```", regles.rapport(aj), "```", ""]
    out += ["## Autres changements de materiau sur le banc Flore", ""]
    for cat, cle in (("bois", "erable_sycomore"),
                     ("bois", "chene"), ("bois", "noyer"), ("bois", "hetre"), ("inox", "inox_304"),
                     ("lest", "grenaille_acier"), ("lest", "acier_plein")):
        _, aj = regles.changer_materiau(p, cat, cle)
        out += ["### %s -> `%s`" % (cat, cle), "", "```", regles.rapport(aj), "```", ""]
    q = p.copie()
    q.set("bois.methode_cintrage", "vapeur")
    _, aj = regles.changer_materiau(q, "bois", "erable_sycomore")
    out += ["### bois -> `erable_sycomore` en cintrage vapeur", "", "```", regles.rapport(aj), "```", ""]
    return "\n".join(out) + "\n"


def main():
    with open(os.path.join(DOCS, "parametres.md"), "w", encoding="utf-8") as f:
        f.write(parametres_md())
    with open(os.path.join(DOCS, "regles_materiaux.md"), "w", encoding="utf-8") as f:
        f.write(regles_md())
    from equinox import apercu
    plan = banc_flore.concevoir()
    apercu.generer_png(plan, os.path.join(DOCS, "apercu_banc.png"), "Equinox - banc Flore (helices inox en rouge)")
    apercu.generer_helice_png(plan, os.path.join(DOCS, "apercu_helice.png"))
    for mod in (croix_saint_andre, tabouret, chaise_trone):
        apercu.generer_png(mod.concevoir(), os.path.join(DOCS, "apercu_%s.png" % mod.TYPOLOGIE))
    from equinox.fusion_outils import rapport_texte
    for mod in (banc_flore, croix_saint_andre, tabouret, chaise_trone):
        with open(os.path.join(DOCS, "rapport_%s.txt" % mod.TYPOLOGIE), "w", encoding="utf-8") as f:
            f.write(rapport_texte(mod.concevoir()))
    print("docs regenerees")


if __name__ == "__main__":
    main()
