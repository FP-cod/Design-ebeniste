# -*- coding: utf-8 -*-
"""Moteur de regles materiaux -> geometrie (gamme Neogothique).

Quand une selection change (essence, cuir des manilles, metal, finition,
pivot, type de jonction), le moteur lit le champ ``regles`` de la NOUVELLE
entree du catalogue, recalcule les parametres cibles et renvoie la liste des
ajustements avec une explication lisible.

Syntaxe d'une regle (dict) ::

    {
      "id": "bois_epaisseur_platine",       # identifiant unique (rapport, tests)
      "cibles": ["*.platine.epaisseur"],     # chemins (motifs fnmatch) des parametres vises
      "operation": "echelle",                # voir OPERATIONS ci-dessous
      "propriete": "resistance_flexion_calcul_mpa",  # propriete du catalogue
      "exposant": 0.5,                       # cible *= (ancien/nouveau) ** exposant
      "arrondi": 1.0,                        # arrondi superieur au pas (mm)
      "serie": [1.5, 2, 2.5, 3],             # ou valeur normalisee superieure
      "mini": 35.0, "maxi": 80.0,            # bornes apres calcul
      "valeur": 6.5,                         # pour fixer / minimum / maximum
      "facteur": 1.2, "ajout": 5.0,          # pour depuis_defaut
      "bases": ["loquet.pene_diametre"],     # pour minimum_section_nette
      "constante": 12.0, "taux": 0.2,        #   (somme des bases + constante) / (1 - taux)
      "explication": "texte {ancien_val:g} {nouveau_val:g} {ratio:.3f} {chemin.de.parametre}"
    }

Operations :

- ``echelle``         : cible x (P_ancien / P_nouveau) ** exposant (sections
  dimensionnees par une propriete : resistance, module, retrait...). Reversible :
  A -> B -> A redonne la valeur initiale (aux arrondis pres).
- ``fixer``           : cible = valeur.
- ``fixer_propriete`` : cible = entree_nouvelle[propriete].
- ``minimum``         : cible = max(cible, valeur).
- ``maximum``         : cible = min(cible, valeur).
- ``depuis_defaut``   : cible = defaut_gamme x facteur + ajout (idempotent).
- ``minimum_section_nette`` : cible = max(cible, (somme des parametres
  ``bases`` + ``constante``) / (1 - ``taux``)) : quand un decor ajoure ou
  festonne retire la part ``taux`` de la matiere, la section brute est
  augmentee pour garder la section nette exigee (ex. barre crantee :
  6 mm de joue nette de chaque cote du trou de pene).
- ``recalcul``        : aucun parametre modifie ; signale une grandeur que la
  grammaire recalcule (masse...) avec le rapport des proprietes.
- ``signaler``        : message seul (precaution, incompatibilite).

Chaque application renvoie des ``Ajustement`` (chemin, avant, apres, unite,
explication, regle, source).
"""

import fnmatch
import math
import re

from .catalogues import CATEGORIES, SELECTIONS, entree

OPERATIONS = ("echelle", "fixer", "fixer_propriete", "minimum", "maximum", "depuis_defaut",
              "minimum_section_nette", "recalcul", "signaler")


class Ajustement(object):
    """Resultat d'une regle : parametre modifie, grandeur a recalculer ou alerte.

    :ivar statut: "ajuste" (valeur changee), "inchange" (regle evaluee, pas
        d'ecart apres arrondi), "recalcul" ou "alerte".
    """

    def __init__(self, chemin, avant, apres, unite, explication, regle, source, statut):
        self.chemin, self.avant, self.apres, self.unite = chemin, avant, apres, unite
        self.explication, self.regle, self.source, self.statut = explication, regle, source, statut

    def __repr__(self):
        return "<Ajustement %s>" % self

    def __str__(self):
        if self.statut in ("alerte", "recalcul"):
            return "%s [%s] %s" % (self.statut.upper(), self.source, self.explication)
        u = (" " + self.unite) if self.unite and self.unite not in ("texte", "bool", "entier") else ""
        return "%s %s : %s%s -> %s%s [%s] %s" % (self.statut.upper(), self.chemin, _fmt(self.avant), u,
                                               _fmt(self.apres), u, self.source, self.explication)

    def vers_dict(self):
        return dict(chemin=self.chemin, avant=self.avant, apres=self.apres, unite=self.unite,
                    explication=self.explication, regle=self.regle, source=self.source, statut=self.statut)


def _fmt(v):
    return ("%g" % v) if isinstance(v, float) else str(v)


def _arrondi_sup(v, pas):
    return math.ceil(v / pas - 1e-9) * pas


def _formater(texte, contexte, params):
    """Remplace {cle[:format]} par le contexte ou par un parametre (chemin pointe)."""
    def rempl(m):
        cle, fmt = m.group(1), m.group(2) or ""
        if cle in contexte:
            val = contexte[cle]
        else:
            val = params.get(cle, None)
            if val is None:
                return m.group(0)
        try:
            return format(val, fmt[1:]) if fmt else ("%g" % val if isinstance(val, float) else str(val))
        except (ValueError, TypeError):
            return str(val)
    return re.sub(r"\{([A-Za-z_][A-Za-z0-9_\.]*)(:[^}]*)?\}", rempl, texte)


def _cibles(params, motifs):
    chemins = params.chemins()
    res = []
    for motif in motifs or []:
        for c in chemins:
            if fnmatch.fnmatchcase(c, motif) and c not in res:
                res.append(c)
    return res


def appliquer_regle(params, regle, ancienne, nouvelle, source):
    """Applique une regle sur ``params`` (modifie en place). Renvoie la liste d'``Ajustement``."""
    op = regle.get("operation")
    if op not in OPERATIONS:
        raise ValueError("Operation inconnue %r dans la regle %s" % (op, regle.get("id")))
    rid = regle.get("id", "?")
    ctx = {}
    prop = regle.get("propriete")
    if prop and ancienne is not None and prop in ancienne and prop in nouvelle \
            and isinstance(nouvelle[prop], (int, float)):
        a, n = float(ancienne[prop]), float(nouvelle[prop])
        ctx.update(ancien_val=a, nouveau_val=n, ratio_brut=n / a if a else float("nan"))
        ctx["ratio"] = (a / n) ** regle.get("exposant", 1.0) if n else float("nan")
    elif prop and prop in nouvelle and isinstance(nouvelle[prop], (int, float)):
        ctx.update(ancien_val=float("nan"), nouveau_val=float(nouvelle[prop]), ratio=1.0, ratio_brut=1.0)

    if op in ("signaler", "recalcul"):
        expl = _formater(regle.get("explication", ""), ctx, params)
        return [Ajustement(None, None, None, "", expl, rid, source, "alerte" if op == "signaler" else "recalcul")]

    res = []
    for chemin in _cibles(params, regle.get("cibles")):
        meta = params.meta(chemin)
        unite = meta.unite if meta else ""
        avant = params.get(chemin)
        apres = avant
        if op == "echelle":
            if ancienne is None or "ratio" not in ctx:
                continue
            apres = avant * ctx["ratio"]
        elif op == "fixer":
            apres = regle["valeur"]
        elif op == "fixer_propriete":
            apres = nouvelle[prop]
        elif op == "minimum":
            apres = max(avant, regle["valeur"])
        elif op == "maximum":
            apres = min(avant, regle["valeur"])
        elif op == "depuis_defaut":
            d = params.defaut(chemin)
            apres = d * regle.get("facteur", 1.0) + regle.get("ajout", 0.0)
        elif op == "minimum_section_nette":
            taux = float(regle.get("taux", 0.0))
            if not 0.0 <= taux < 1.0:
                raise ValueError("regle %s : taux d'enlevement hors [0 ; 1[" % rid)
            mini = (sum(float(params.get(b)) for b in regle.get("bases", [])) + regle.get("constante", 0.0)) / (1.0 - taux)
            if "arrondi" in regle:
                mini = _arrondi_sup(mini, regle["arrondi"])
            ctx["mini"] = mini
            apres = max(float(avant), mini)
        if isinstance(apres, (int, float)) and not isinstance(apres, bool) and op in ("echelle", "depuis_defaut"):
            if "serie" in regle:
                serie = sorted(regle["serie"])
                apres = next((s for s in serie if s >= apres - 1e-9), serie[-1])
            elif "arrondi" in regle:
                apres = _arrondi_sup(apres, regle["arrondi"])
            if "mini" in regle:
                apres = max(apres, regle["mini"])
            if "maxi" in regle:
                apres = min(apres, regle["maxi"])
            if meta and meta.plage:
                apres = min(max(apres, meta.plage[0]), meta.plage[1])
            apres = float(apres)
        ctx_c = dict(ctx, avant=avant, apres=apres)
        expl = _formater(regle.get("explication", ""), ctx_c, params)
        change = (apres != avant) if not isinstance(apres, float) else abs(apres - float(avant)) > 1e-9
        if change:
            params.set(chemin, apres)
        res.append(Ajustement(chemin, avant, apres, unite, expl, rid, source, "ajuste" if change else "inchange"))
    return res


def changer_materiau(params, chemin_selection, nouvelle_cle, inclure_inchanges=False):
    """Change une selection de materiau / systeme et applique les regles.

    :param params: ``Parametres`` (non modifie : une copie est renvoyee).
    :param chemin_selection: ex. "bois.essence", "ferrures.metal",
        "garnissage.cuir_manilles", "entrave.manilles.pivot_cou",
        "jonctions.type_coulisseau_platine".
    :param nouvelle_cle: cle de l'entree du catalogue.
    :return: (nouveaux_parametres, liste d'Ajustement).
    """
    if chemin_selection not in SELECTIONS:
        raise KeyError("Selection inconnue %r (connues : %s)" % (chemin_selection, sorted(SELECTIONS)))
    categorie = SELECTIONS[chemin_selection]
    nouvelle = entree(categorie, nouvelle_cle)
    p = params.copie()
    ancienne_cle = p.get(chemin_selection)
    ancienne = CATEGORIES[categorie].get(ancienne_cle)
    ajust = [Ajustement(chemin_selection, ancienne_cle, nouvelle_cle, "texte",
                        "Selection %s : %s -> %s" % (categorie, ancienne_cle, nouvelle_cle),
                        "selection", nouvelle_cle, "ajuste" if ancienne_cle != nouvelle_cle else "inchange")]
    p.set(chemin_selection, nouvelle_cle)
    if ancienne_cle == nouvelle_cle:
        return p, ajust
    for regle in nouvelle.get("regles", []):
        ajust.extend(appliquer_regle(p, regle, ancienne, nouvelle, nouvelle_cle))
    # Coherences en cascade (finition compatible avec le nouveau metal / la nouvelle essence)
    ajust.extend(_cascades(p, chemin_selection, nouvelle_cle))
    if not inclure_inchanges:
        ajust = [a for a in ajust if a.statut != "inchange"]
    return p, ajust


def _cascades(p, chemin_selection, cle):
    from .catalogues import FINITIONS, BOIS, DECORS_BARRE
    res = []
    # Section nette de la barre crantee : re-evaluee si le pene a pu changer (metal...)
    if chemin_selection != "cremaillere.decor_barre":
        dec = DECORS_BARRE.get(p.get("cremaillere.decor_barre"), {})
        for r in dec.get("regles", []):
            if r.get("operation") == "minimum_section_nette":
                res.extend(a for a in appliquer_regle(p, r, None, dec, "cascade_section_nette")
                           if a.statut == "ajuste")
    if chemin_selection == "bois.essence":
        compat = BOIS[cle]["finitions_compatibles"]
        if p.get("bois.finition") not in compat:
            avant = p.get("bois.finition")
            p.set("bois.finition", compat[0])
            res.append(Ajustement("bois.finition", avant, compat[0], "texte",
                                  "Finition %r incompatible avec %s : remplacee par %r." % (avant, cle, compat[0]),
                                  "cascade_finition_bois", cle, "ajuste"))
    if chemin_selection == "ferrures.finition":
        if p.get("ferrures.metal") not in FINITIONS[cle]["metaux"]:
            res.append(Ajustement(None, None, None, "", "Finition %s incompatible avec le metal %s." %
                                  (cle, p.get("ferrures.metal")), "cascade_finition_metal", cle, "alerte"))
    return res


def rapport(ajustements):
    """Texte lisible (une ligne par ajustement)."""
    if not ajustements:
        return "Aucun ajustement."
    return "\n".join("- " + str(a) for a in ajustements)


def verifier_catalogues():
    """Controle de syntaxe de toutes les regles des catalogues (utilise par les tests).

    Renvoie la liste des erreurs (vide si tout est correct).
    """
    from .parametres import Parametres
    p = Parametres()
    erreurs = []
    for cat, dico in CATEGORIES.items():
        for cle, ent in dico.items():
            for r in ent.get("regles", []):
                rid = "%s/%s/%s" % (cat, cle, r.get("id"))
                if r.get("operation") not in OPERATIONS:
                    erreurs.append("%s : operation %r inconnue" % (rid, r.get("operation")))
                if r.get("operation") not in ("signaler", "recalcul"):
                    if not _cibles(p, r.get("cibles")):
                        erreurs.append("%s : aucune cible ne correspond a %s" % (rid, r.get("cibles")))
                if r.get("operation") == "minimum_section_nette":
                    for b in r.get("bases", []):
                        if b not in p.chemins():
                            erreurs.append("%s : base %r inconnue" % (rid, b))
                if r.get("operation") in ("echelle", "fixer_propriete", "recalcul"):
                    if r.get("propriete") not in ent:
                        erreurs.append("%s : propriete %r absente de l'entree" % (rid, r.get("propriete")))
                if "explication" not in r:
                    erreurs.append("%s : explication manquante" % rid)
    return erreurs
