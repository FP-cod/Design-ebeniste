# -*- coding: utf-8 -*-
"""Table de correspondance teintes GammeCuir <-> materiaux des catalogues meubles.

Choix d'architecture : la GammeCuir N'IMPORTE PAS les paquets meubles a
l'execution (le script Fusion doit rester autonome et les gammes evoluent
separement). On garde ici un INSTANTANE explicite des identifiants reels
(releve le 18/11/2026 dans /workspace) et ``verifier_contre_catalogues()``
confronte cet instantane aux catalogues vivants quand ils sont presents
(execute par les tests : toute derive d'identifiant ou de coloris casse un
test au lieu de casser l'assortiment en silence).

Types de correspondance :

- ``exact``  : meme coloris (meme identifiant de coloris) dans le catalogue meuble ;
- ``proche`` : nuance voisine (identifiant different) - A VALIDER sur echantillon ;
- ``a_confirmer`` : gamme sans catalogue sur la machine (Tantra).

Statut d'une teinte : ``assortie`` (>= 1 exact sur un cuir veritable),
``assortie_hors_cuir`` (exact seulement sur un revetement non cuir / vegan /
synthetique), ``proche`` (seulement des nuances voisines), ``non_assortie``.
"""

import importlib
import os
import sys

from .cuirs import TEINTES

RACINE_WORKSPACE_DEFAUT = os.environ.get("GAMME_CUIR_WORKSPACE", "/workspace")

#: Instantane des materiaux meubles (identifiants et coloris REELS).
#: cle = (gamme, identifiant)
MATERIAUX_MEUBLES = {
    # --- Equinox : equinox/equinox/catalogues/garnissage.py (GARNISSAGES) ---
    ("equinox", "cuir_classique_pleine_fleur"): {
        "fichier": "equinox/equinox/catalogues/garnissage.py", "cuir_veritable": True,
        "coloris": ["noir", "cognac", "havane", "vert_bouteille", "bleu_nuit"],
        "typologies": ["banc_flore", "croix_saint_andre", "tabouret", "chaise_trone"],
        "notes": "Revetement de reference Equinox, coloris defaut cognac (garnissage.couleur = cognac, impose)."},
    ("equinox", "cuir_vegan"): {
        "fichier": "equinox/equinox/catalogues/garnissage.py", "cuir_veritable": False,
        "coloris": ["noir", "blanc", "cognac", "vert_olive", "bordeaux"],
        "typologies": ["banc_flore", "croix_saint_andre", "tabouret", "chaise_trone"], "notes": "Sans cuir veritable."},
    ("equinox", "cuir_synthetique_hq"): {
        "fichier": "equinox/equinox/catalogues/garnissage.py", "cuir_veritable": False,
        "coloris": ["noir", "cognac", "gris"],
        "typologies": ["banc_flore", "croix_saint_andre", "tabouret", "chaise_trone"], "notes": "PU haute densite."},
    ("equinox", "tissu_technique_enduit"): {
        "fichier": "equinox/equinox/catalogues/garnissage.py", "cuir_veritable": False,
        "coloris": ["noir", "cognac"],
        "typologies": ["banc_flore", "croix_saint_andre", "tabouret", "chaise_trone"], "notes": "Enduit PU type medical."},
    ("equinox", "tissu_krypton"): {
        "fichier": "equinox/equinox/catalogues/garnissage.py", "cuir_veritable": False,
        "coloris": ["noir", "gris_anthracite", "bordeaux", "bleu_marine"],
        "typologies": ["banc_flore", "croix_saint_andre", "tabouret", "chaise_trone"], "notes": "Tissu (velours cotele)."},
    # --- Neogothique : neogothique/neogothique/catalogues/garnissage.py (GARNISSAGE) ---
    ("neogothique", "cuir_sellier_fin_noir"): {
        "fichier": "neogothique/neogothique/catalogues/garnissage.py", "cuir_veritable": True,
        "coloris": ["noir"], "typologies": ["entrave"],
        "notes": "Manilles par defaut de l'Entrave (garnissage.cuir_manilles), point sellier double 3,2 mm."},
    ("neogothique", "cuir_renforce_double_noir"): {
        "fichier": "neogothique/neogothique/catalogues/garnissage.py", "cuir_veritable": True,
        "coloris": ["noir"], "typologies": ["entrave"], "notes": "Manilles harnais + doublure + ame."},
    ("neogothique", "cuir_harnais_noir"): {
        "fichier": "neogothique/neogothique/catalogues/garnissage.py", "cuir_veritable": True,
        "coloris": ["noir", "brun_fonce"], "typologies": ["entrave"], "notes": "Harnais vegetal simple epaisseur."},
    ("neogothique", "cuir_synthetique_pu_noir"): {
        "fichier": "neogothique/neogothique/catalogues/garnissage.py", "cuir_veritable": False,
        "coloris": ["noir"], "typologies": ["entrave"], "notes": "PU sur ame sangle."},
    ("neogothique", "cuir_pleine_fleur_noir"): {
        "fichier": "neogothique/neogothique/catalogues/garnissage.py", "cuir_veritable": True,
        "coloris": ["noir"], "typologies": ["entrave"], "notes": "Coussinets / garnitures."},
    ("neogothique", "doublure_agneau_noir"): {
        "fichier": "neogothique/neogothique/catalogues/garnissage.py", "cuir_veritable": True,
        "coloris": ["noir"], "typologies": ["entrave"], "notes": "Doublure."},
    # --- Incognito : incognito/incognito/catalogues/revetements.py (REVETEMENTS) ---
    ("incognito", "cuir_cognac"): {
        "fichier": "incognito/incognito/catalogues/revetements.py", "cuir_veritable": True,
        "coloris": ["cognac"], "typologies": ["banquette", "pouf_vibrant"],
        "notes": "Interieur cache uniquement (banc deploye, selle du pouf) ; defaut des deux typologies."},
    ("incognito", "cuir_noir"): {
        "fichier": "incognito/incognito/catalogues/revetements.py", "cuir_veritable": True,
        "coloris": ["noir"], "typologies": ["banquette", "pouf_vibrant"], "notes": "Interieur cache uniquement."},
    ("incognito", "cuir_sobre_facade"): {
        "fichier": "incognito/incognito/catalogues/revetements.py", "cuir_veritable": True,
        "coloris": ["cognac_clair", "havane", "noir_mat"], "typologies": ["banquette"],
        "notes": "Derogation documentee, NON retenue par defaut (regle 'zero cuir visible')."},
    ("incognito", "laine_bouclee"): {
        "fichier": "incognito/incognito/catalogues/revetements.py", "cuir_veritable": False,
        "coloris": ["ivoire", "grege", "charbon", "camel"], "typologies": ["banquette", "pouf_vibrant"],
        "notes": "Tissu de facade."},
}

#: Gammes connues sans catalogue materiau sur la machine.
GAMMES_SANS_CATALOGUE = {
    "tantra": "Gamme Tantra Bien-etre : seul un profil d'agent existe (fauteuils tantriques fixes, 'revetements' "
              "prevus en couche 1) ; aucun fichier de projet ni catalogue dans /workspace ou /home/box au "
              "18/11/2026. Correspondances a confirmer quand le catalogue existera.",
}

GAMMES = ("equinox", "neogothique", "incognito", "tantra")


def _c(gamme, materiau, coloris, type_="exact", note=""):
    return {"gamme": gamme, "materiau": materiau, "coloris": coloris, "type": type_, "note": note}


#: Correspondances teinte cuir -> materiaux meubles.
CORRESPONDANCES = {
    "cognac": [
        _c("equinox", "cuir_classique_pleine_fleur", "cognac", note="teinte de reference Equinox (banc a fesser cognac)"),
        _c("equinox", "cuir_vegan", "cognac"), _c("equinox", "cuir_synthetique_hq", "cognac"),
        _c("equinox", "tissu_technique_enduit", "cognac"),
        _c("incognito", "cuir_cognac", "cognac", note="cuir de l'interieur cache (banquette, pouf)"),
        _c("incognito", "cuir_sobre_facade", "cognac_clair", "proche", "nuance plus claire, derogation non retenue"),
    ],
    "tan": [
        _c("incognito", "cuir_sobre_facade", "cognac_clair", "proche", "tan ~ cognac clair : a valider sur echantillon"),
        _c("incognito", "laine_bouclee", "camel", "proche", "accord tissu de facade camel / cuir tan, a valider"),
    ],
    "havane": [
        _c("equinox", "cuir_classique_pleine_fleur", "havane"),
        _c("incognito", "cuir_sobre_facade", "havane", note="derogation non retenue par defaut"),
    ],
    "brun_fonce": [
        _c("neogothique", "cuir_harnais_noir", "brun_fonce", note="seule teinte non noire de l'Entrave"),
        _c("equinox", "cuir_classique_pleine_fleur", "havane", "proche", "havane plus chaud que brun fonce"),
    ],
    "noir": [
        _c("equinox", "cuir_classique_pleine_fleur", "noir"), _c("equinox", "cuir_vegan", "noir"),
        _c("equinox", "cuir_synthetique_hq", "noir"), _c("equinox", "tissu_technique_enduit", "noir"),
        _c("equinox", "tissu_krypton", "noir"),
        _c("neogothique", "cuir_sellier_fin_noir", "noir", note="manilles par defaut de l'Entrave"),
        _c("neogothique", "cuir_renforce_double_noir", "noir"), _c("neogothique", "cuir_harnais_noir", "noir"),
        _c("neogothique", "cuir_synthetique_pu_noir", "noir"), _c("neogothique", "cuir_pleine_fleur_noir", "noir"),
        _c("neogothique", "doublure_agneau_noir", "noir"),
        _c("incognito", "cuir_noir", "noir"),
        _c("incognito", "cuir_sobre_facade", "noir_mat", "proche", "noir mat : choisir une finition mate"),
    ],
    "bordeaux": [
        _c("equinox", "cuir_vegan", "bordeaux", note="cuir vegan : matiere differente, teinte identique"),
        _c("equinox", "tissu_krypton", "bordeaux", note="tissu : accord de teinte seulement"),
    ],
    "vert_bouteille": [_c("equinox", "cuir_classique_pleine_fleur", "vert_bouteille")],
    "bleu_nuit": [
        _c("equinox", "cuir_classique_pleine_fleur", "bleu_nuit"),
        _c("equinox", "tissu_krypton", "bleu_marine", "proche", "bleu marine plus clair que bleu nuit"),
    ],
}
for _t in CORRESPONDANCES:
    CORRESPONDANCES[_t].append(_c("tantra", None, None, "a_confirmer", "aucun catalogue Tantra sur la machine"))

#: Quincaillerie des meubles a laquelle s'assortir (identifiants reels).
QUINCAILLERIE_MEUBLES = {
    "equinox": {"inox": ["inox_316", "inox_304"], "laiton": ["laiton_cw614n", "laiton_cw510l"],
                "fichier": "equinox/equinox/catalogues/metaux.py",
                "notes": "Anneaux et oeillets d'ancrage en inox A4 (attaches.anneau_inox_8, oeillet_inox_8)."},
    "neogothique": {"fer": ["fer_forge_mat"], "laiton": ["laiton_mat"],
                    "finitions": ["cire_noire", "huile_brunie", "phosphatation_vernis_mat",
                                  "galvanisation_peinture_mate", "laiton_brosse_vernis_mat", "laiton_patine_vieilli"],
                    "fichier": "neogothique/neogothique/catalogues/ferrures.py",
                    "notes": "Fer forge noir mat : s'accorde avec l'inox PVD noir ; laiton patine vieilli = "
                             "contact peau prolonge a eviter (FINITIONS.laiton_patine_vieilli.contact_peau)."},
    "incognito": {"fichier": "incognito/incognito/catalogues/fixations.py",
                  "notes": "Quincaillerie cachee (fixations), pas d'accord visuel impose."},
    "tantra": {"notes": "a confirmer"},
}


def statut_teinte(teinte, correspondances=None):
    """Statut d'assortiment d'une teinte (voir docstring du module)."""
    corr = (correspondances or CORRESPONDANCES).get(teinte, [])
    reels = [c for c in corr if c["type"] != "a_confirmer"]
    exacts = [c for c in reels if c["type"] == "exact"]
    if any(MATERIAUX_MEUBLES[(c["gamme"], c["materiau"])]["cuir_veritable"] for c in exacts):
        return "assortie"
    if exacts:
        return "assortie_hors_cuir"
    if reels:
        return "proche"
    return "non_assortie"


def meubles_assortis(teinte, gamme=None, types=("exact", "proche")):
    """Liste des (gamme, materiau, coloris, type, typologies) assortis a une teinte."""
    out = []
    for c in CORRESPONDANCES.get(teinte, []):
        if c["type"] not in types or (gamme and c["gamme"] != gamme) or c["materiau"] is None:
            continue
        m = MATERIAUX_MEUBLES[(c["gamme"], c["materiau"])]
        out.append(dict(c, typologies=list(m["typologies"]), cuir_veritable=m["cuir_veritable"]))
    return out


def verifier_coherence_interne():
    """Controles sans acces aux autres gammes. Renvoie la liste des anomalies (vide = OK)."""
    anomalies = []
    for t in TEINTES:
        if t not in CORRESPONDANCES:
            anomalies.append("teinte %s sans entree de correspondance (la marquer non_assortie explicitement)" % t)
    for t, corr in CORRESPONDANCES.items():
        if t not in TEINTES:
            anomalies.append("correspondance pour une teinte inconnue : %s" % t)
        for c in corr:
            if c["type"] == "a_confirmer":
                if c["gamme"] not in GAMMES_SANS_CATALOGUE:
                    anomalies.append("%s : 'a_confirmer' reserve aux gammes sans catalogue (%s)" % (t, c["gamme"]))
                continue
            cle = (c["gamme"], c["materiau"])
            if cle not in MATERIAUX_MEUBLES:
                anomalies.append("%s -> %s : materiau absent de l'instantane" % (t, cle))
            elif c["coloris"] not in MATERIAUX_MEUBLES[cle]["coloris"]:
                anomalies.append("%s -> %s : coloris %s absent (%s)" % (t, cle, c["coloris"],
                                                                        MATERIAUX_MEUBLES[cle]["coloris"]))
            if c["type"] == "exact" and c["coloris"] != t:
                anomalies.append("%s -> %s : 'exact' exige le meme identifiant de coloris (%s)" % (t, cle, c["coloris"]))
    return anomalies


# -- verification contre les catalogues vivants ------------------------------
def _importer(racine, dossier, module):
    chemin = os.path.join(racine, dossier)
    if not os.path.isdir(chemin):
        return None
    ajoute = chemin not in sys.path
    if ajoute:
        sys.path.insert(0, chemin)
    try:
        return importlib.import_module(module)
    finally:
        if ajoute:
            sys.path.remove(chemin)


def coloris_vivants(racine=RACINE_WORKSPACE_DEFAUT):
    """Lit les catalogues meubles reels -> {(gamme, id): [coloris]} (gammes absentes ignorees)."""
    out = {}
    mod = _importer(racine, "equinox", "equinox.catalogues.garnissage")
    if mod is not None:
        for k in mod.GARNISSAGES:
            out[("equinox", k)] = list(mod.GARNISSAGES[k]["coloris"])
    mod = _importer(racine, "neogothique", "neogothique.catalogues.garnissage")
    if mod is not None:
        for k, v in mod.GARNISSAGE.items():
            out[("neogothique", k)] = list(v["coloris"])
    mod = _importer(racine, "incognito", "incognito.catalogues.revetements")
    if mod is not None:
        for k, v in mod.REVETEMENTS.items():
            out[("incognito", k)] = list(v.couleurs_typiques)
    return out


def verifier_contre_catalogues(racine=RACINE_WORKSPACE_DEFAUT):
    """Compare l'instantane aux catalogues vivants. Renvoie (anomalies, gammes_verifiees)."""
    vivants = coloris_vivants(racine)
    gammes = sorted({g for g, _ in vivants})
    anomalies = []
    for (g, k), m in MATERIAUX_MEUBLES.items():
        if g not in gammes:
            continue
        if (g, k) not in vivants:
            anomalies.append("%s.%s n'existe plus dans le catalogue %s" % (g, k, m["fichier"]))
        elif sorted(vivants[(g, k)]) != sorted(m["coloris"]):
            anomalies.append("%s.%s : coloris vivants %s != instantane %s" % (g, k, vivants[(g, k)], m["coloris"]))
    return anomalies, gammes
