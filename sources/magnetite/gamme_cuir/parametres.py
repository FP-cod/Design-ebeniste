# -*- coding: utf-8 -*-
"""Couche 1 - Parametres globaux de la GammeCuir (chargeur + validation).

Le schema complet (valeur, unite, plage/choix, statut, justification, source)
est dans ``parametres_gamme_cuir.defauts.json`` : c'est la reference
documentee (``docs/parametres.md`` en est generee). Les surcharges d'un projet
vont dans ``parametres_gamme_cuir.json`` (cle ``surcharges`` : chemins
``section.parametre``) ou sont passees au constructeur.

Unites internes : mm, N (jamais de cm ici : la conversion est reservee a
``fusion_outils``).

Usage ::

    from gamme_cuir.parametres import Parametres
    p = Parametres({"finition.teinte": "noir"})
    p.get("couture.pas_point")          # 3.2
    p.tour("poignet", "M")              # 170.0
    p.epaisseur_totale()                # exterieur + rembourrage + doublure
    problemes = p.valider()             # [] si tout est coherent
    p.exporter_user_parameters(design)  # dans Fusion uniquement
"""

import copy
import json
import os
import re

DOSSIER = os.path.dirname(os.path.abspath(__file__))
CHEMIN_DEFAUTS = os.path.join(DOSSIER, "parametres_gamme_cuir.defauts.json")
CHEMIN_JSON = os.path.join(DOSSIER, "parametres_gamme_cuir.json")

STATUTS = ("impose", "a_valider", "derive", "libre")
UNITES_NUMERIQUES = ("mm", "N", "")
_MANQUANT = object()


class Probleme(object):
    """Resultat de validation : niveau 'ERREUR' (bloquant) ou 'ALERTE'."""

    def __init__(self, niveau, chemin, message):
        self.niveau, self.chemin, self.message = niveau, chemin, message

    def __repr__(self):
        return "%s %s : %s" % (self.niveau, self.chemin, self.message)


def charger_schema(chemin=CHEMIN_DEFAUTS):
    """Lit le JSON de defauts et renvoie {section: {nom: meta}}."""
    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)["sections"]


class Parametres(object):
    """Jeu de parametres : defauts du schema + surcharges, avec validation."""

    def __init__(self, surcharges=None, json_utilisateur=True, schema=None):
        self.schema = copy.deepcopy(schema) if schema is not None else charger_schema()
        self.valeurs = {s: {k: copy.deepcopy(m["valeur"]) for k, m in d.items()} for s, d in self.schema.items()}
        if json_utilisateur and os.path.exists(CHEMIN_JSON):
            with open(CHEMIN_JSON, "r", encoding="utf-8") as f:
                self.fusionner(json.load(f).get("surcharges", {}))
        if surcharges:
            self.fusionner(surcharges)

    # -- acces --------------------------------------------------------------
    @staticmethod
    def _decouper(chemin):
        if chemin.count(".") != 1:
            raise KeyError("chemin attendu 'section.parametre' : %r" % chemin)
        return chemin.split(".")

    def get(self, chemin, defaut=_MANQUANT):
        s, k = self._decouper(chemin)
        try:
            return self.valeurs[s][k]
        except KeyError:
            if defaut is _MANQUANT:
                raise KeyError("parametre inconnu : %s" % chemin)
            return defaut

    def set(self, chemin, valeur):
        s, k = self._decouper(chemin)
        if s not in self.schema or k not in self.schema[s]:
            raise KeyError("parametre inconnu : %s (aucune creation a la volee)" % chemin)
        self.valeurs[s][k] = valeur

    def fusionner(self, surcharges):
        """Accepte {'section.param': v} ou {'section': {'param': v}}."""
        for cle, val in surcharges.items():
            if isinstance(val, dict) and cle in self.schema and "." not in cle:
                for k, v in val.items():
                    self.set("%s.%s" % (cle, k), v)
            else:
                self.set(cle, val)
        return self

    def meta(self, chemin):
        s, k = self._decouper(chemin)
        return self.schema[s][k]

    def feuilles(self):
        """Itere (chemin, meta, valeur) dans l'ordre du schema."""
        for s, d in self.schema.items():
            for k, m in d.items():
                yield "%s.%s" % (s, k), m, self.valeurs[s][k]

    def copie(self):
        p = Parametres.__new__(Parametres)
        p.schema, p.valeurs = self.schema, copy.deepcopy(self.valeurs)
        return p

    # -- grandeurs derivees -------------------------------------------------
    def tour(self, membre=None, taille=None):
        """Tour anatomique [mm] du membre et de la taille (defaut : produit.*)."""
        membre = membre or self.get("produit.membre")
        taille = taille or self.get("produit.taille")
        return float(self.get("tailles.%s_%s" % (membre, taille)))

    def plage_taille(self, membre=None, taille=None):
        membre = membre or self.get("produit.membre")
        taille = taille or self.get("produit.taille")
        return tuple(self.meta("tailles.%s_%s" % (membre, taille))["plage"])

    def largeur_bande(self, membre=None):
        membre = membre or self.get("produit.membre")
        return float(self.get("sangles.largeur_menotte_%s" % membre))

    def couches(self):
        """Liste ordonnee (de la peau vers l'exterieur) des couches (nom, epaisseur)."""
        n = int(self.get("cuir.nb_couches"))
        c = []
        if n >= 2:
            c.append(("doublure", float(self.get("cuir.epaisseur_doublure"))))
        if n >= 3 and self.get("cuir.rembourrage") and self.get("cuir.epaisseur_rembourrage") > 0:
            c.append(("rembourrage", float(self.get("cuir.epaisseur_rembourrage"))))
        c.append(("exterieur", float(self.get("cuir.epaisseur_exterieure"))))
        return c

    def epaisseur_totale(self):
        return sum(e for _, e in self.couches())

    def epaisseur_cuir_seul(self):
        """Epaisseur hors rembourrage (zones percees : trous, rivets)."""
        return sum(e for n, e in self.couches() if n != "rembourrage")

    def classe_epaisseur(self, e=None):
        e = self.get("cuir.epaisseur_exterieure") if e is None else e
        for nom, (mini, maxi) in self.get("cuir.classes_epaisseur").items():
            if mini - 1e-9 <= e <= maxi + 1e-9:
                return nom
        return None

    def points_par_cm(self):
        return 10.0 / float(self.get("couture.pas_point"))

    # -- validation ---------------------------------------------------------
    def valider(self):
        """Controle types, plages, choix, documentation et coherences croisees."""
        pb = []
        for chemin, m, v in self.feuilles():
            for champ in ("unite", "role", "statut", "justification"):
                if champ not in m or (champ != "unite" and not m[champ]):
                    pb.append(Probleme("ERREUR", chemin, "documentation incomplete : champ '%s'" % champ))
            if m.get("statut") not in STATUTS:
                pb.append(Probleme("ERREUR", chemin, "statut inconnu %r" % m.get("statut")))
            u = m.get("unite")
            if u == "bool":
                if not isinstance(v, bool):
                    pb.append(Probleme("ERREUR", chemin, "booleen attendu, recu %r" % (v,)))
            elif u == "texte":
                if not isinstance(v, str):
                    pb.append(Probleme("ERREUR", chemin, "texte attendu, recu %r" % (v,)))
                elif m.get("choix") and v not in m["choix"]:
                    pb.append(Probleme("ERREUR", chemin, "%r hors choix %s" % (v, m["choix"])))
            elif u in UNITES_NUMERIQUES and not isinstance(m["valeur"], dict):
                if isinstance(v, bool) or not isinstance(v, (int, float)):
                    pb.append(Probleme("ERREUR", chemin, "nombre attendu, recu %r" % (v,)))
                elif m.get("plage") and not (m["plage"][0] - 1e-9 <= v <= m["plage"][1] + 1e-9):
                    pb.append(Probleme("ERREUR", chemin, "%g %s hors plage %s" % (v, u, m["plage"])))
        if any(p.niveau == "ERREUR" for p in pb):
            return pb  # inutile de croiser des valeurs invalides
        g = self.get
        if g("ardillon.nb_trous") % 2 != 1:
            pb.append(Probleme("ERREUR", "ardillon.nb_trous", "nombre impair attendu (trou central = tour de taille)"))
        if g("cuir.rembourrage") and g("cuir.nb_couches") < 3:
            pb.append(Probleme("ERREUR", "cuir.rembourrage", "rembourrage demande avec %d couche(s) : il faut "
                               "exterieur + rembourrage + doublure (nb_couches = 3)" % g("cuir.nb_couches")))
        if self.classe_epaisseur() is None:
            pb.append(Probleme("ALERTE", "cuir.epaisseur_exterieure", "%g mm hors des classes fournisseur %s"
                               % (g("cuir.epaisseur_exterieure"), g("cuir.classes_epaisseur"))))
        w = self.largeur_bande()
        if g("couture.retrait_bord") * 2 + g("ardillon.diametre_trou") + 2 * g("couture.marge_couture_percages") > w:
            pb.append(Probleme("ERREUR", "couture.retrait_bord", "bande trop etroite pour couture + trous"))
        if g("anneau_d.largeur_patte") > w:
            pb.append(Probleme("ERREUR", "anneau_d.largeur_patte", "patte plus large que la bande"))
        if g("anneau_d.entraxe_rivets_patte") + g("jonctions.diametre_trou_rivet") >= g("anneau_d.longueur_patte") / 2:
            pb.append(Probleme("ERREUR", "anneau_d.entraxe_rivets_patte", "les rivets ne tiennent pas sur la patte "
                               "repliee (entraxe + trou >= longueur_patte / 2)"))
        if g("jonctions.repli_boucle") < g("ardillon.longueur_fente") / 2 + 2 * g("jonctions.diametre_trou_rivet") + 5:
            pb.append(Probleme("ERREUR", "jonctions.repli_boucle", "repli trop court pour la fente et les rivets"))
        return pb

    def erreurs(self):
        return [p for p in self.valider() if p.niveau == "ERREUR"]

    # -- export -------------------------------------------------------------
    def vers_json(self, chemin_fichier=None):
        texte = json.dumps({"surcharges": {c: v for c, _, v in self.feuilles()}}, ensure_ascii=False, indent=1)
        if chemin_fichier:
            with open(chemin_fichier, "w", encoding="utf-8") as f:
                f.write(texte)
        return texte

    @staticmethod
    def nom_fusion(chemin, prefixe="gc_"):
        return prefixe + re.sub(r"[^A-Za-z0-9_]", "_", chemin.replace(".", "_"))

    def parametres_exportables(self):
        """(nom, expression, unite, commentaire) des parametres numeriques en mm."""
        pref = self.get("gamme.prefixe_fusion")
        out = []
        for chemin, m, v in self.feuilles():
            if m.get("unite") == "mm" and isinstance(v, (int, float)) and not isinstance(v, bool):
                out.append((self.nom_fusion(chemin, pref), "%g mm" % v, "mm", m["role"][:200]))
        return out

    def exporter_user_parameters(self, design):
        """Cree ou met a jour les User Parameters du design. Renvoie (crees, mis_a_jour)."""
        import adsk.core  # import differe : uniquement dans Fusion (ou mock)
        crees, maj = [], []
        ups = design.userParameters
        for nom, expression, unite, commentaire in self.parametres_exportables():
            existant = ups.itemByName(nom)
            if existant:
                existant.expression = expression
                existant.comment = commentaire
                maj.append(nom)
            else:
                ups.add(nom, adsk.core.ValueInput.createByString(expression), unite, commentaire)
                crees.append(nom)
        return crees, maj
