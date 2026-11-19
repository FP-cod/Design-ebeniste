# -*- coding: utf-8 -*-
"""Grammaire couche 3 — aboutissant de récupération d'urine.

Module rapporté, exclusivement pour adultes consentants. Il se place à
l'arrière ou sous le meuble / près d'un aboutissant *fixe*, au voisinage
des ancrages *déjà relevés*, sans modifier Equinox / Néogothique /
Incognito / Tantra / Rangement (ces dépôts ne sont pas touchés).

Cible : typologies de meubles Equinox, Néogothique, Incognito **hors
pouf**, Tantra et Rangement, plus les aboutissants fixes (machine de
mouvement mécanique).
Le pouf vibrant Incognito n'a plus de module de collecte : il n'est
**pas** une cible (``pouf`` / ``pouf_vibrant`` lèvent une erreur).

Solutions couvertes : entonnoir déployable, gouttière sous siège,
réservoir amovible, raccord de vidange 1" NPT. Les trois modes de
vidange restent paramétrables (gravité, réservoir amovible — défaut
recommandé, raccord NPT). Contact fluide : inox 316L ou résine/polymère
non poreux (PP, PE-HD). Le Vac-U-Lock n'est pas un raccord de fluide.

Discrétion : rien de visible à l'état fermé (etat_deploiement = 0) ;
déploiement par tiroir ou panneau basculant, dans l'esprit des trappes
affleurant et du coffre Incognito (le dossier basculant de cette gamme
a été écarté : on ne le réutilise pas).

Le module s'importe hors Fusion (aucun ``import adsk`` au niveau module).
Point d'entrée Fusion : ``run(context)``.
"""

from __future__ import annotations

import math
import os
import sys
import traceback

_RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _RACINE not in sys.path:
    sys.path.insert(0, _RACINE)

from common.params_globaux import Parametres
from catalogues.materiaux import METAUX, POLYMERES, JOINTS, HABILLAGE_HORS_ZONE_HUMIDE, materiau
from common import fusion_utils as FU

# Longueur de semelle Entrave (défaut meuble), citée dans la justification de
# ancrages.neogothique.decalage_y_bout_semelle — pas formalisée en paramètre.
# y = ±(Ls/2 − decalage_y). Si Ls change, recalculer.
LS_ENTRAVE_DEFAUT_MM = 560.0

MATERIAUX_CONTACT_ADMIS = ("inox_316", "inox_316L", "inox_316l", "pp_homopolymere", "pehd")

# Pouf vibrant Incognito : plus de module de collecte, hors cible.
TYPOLOGIES_EXCLUES = frozenset({"pouf", "pouf_vibrant"})

DEFAUT_TYPOLOGIE = {
    "equinox": "banc_flore",
    "neogothique": "entrave",
    "incognito": "banquette",  # jamais le pouf
    "tantra": "tantra_chaise_double_courbe",
    "rangement": "ratelier_mural",
    "aboutissants": "sex_machine_mecanique",
}

# Typologies à couvrir (meubles + aboutissants fixes). Les grammaires non
# livrées restent dans le tableau d'arbitrages, avec TODO d'implantation.
TYPOLOGIES_CIBLES = (
    {"gamme": "equinox", "typologie": "banc_flore", "grammaire_livree": True},
    {"gamme": "equinox", "typologie": "tabouret", "grammaire_livree": True},
    {"gamme": "equinox", "typologie": "chaise_trone", "grammaire_livree": True},
    {"gamme": "equinox", "typologie": "croix_saint_andre", "grammaire_livree": True},
    {"gamme": "equinox", "typologie": "cheval_arcon", "grammaire_livree": False},
    {"gamme": "neogothique", "typologie": "entrave", "grammaire_livree": True},
    {"gamme": "incognito", "typologie": "banquette", "grammaire_livree": True},
    {"gamme": "incognito", "typologie": "canape", "grammaire_livree": False},
    {"gamme": "incognito", "typologie": "fauteuil", "grammaire_livree": False},
    {"gamme": "incognito", "typologie": "table_basse", "grammaire_livree": False},
    {"gamme": "incognito", "typologie": "banc_entree", "grammaire_livree": False},
    {"gamme": "incognito", "typologie": "bibliotheque", "grammaire_livree": False},
    {"gamme": "aboutissants", "typologie": "sex_machine_mecanique", "grammaire_livree": True},
    {"gamme": "tantra", "typologie": "tantra_chaise_double_courbe", "grammaire_livree": True},
    {"gamme": "tantra", "typologie": "tantra_fauteuil_lombaire", "grammaire_livree": True},
    {"gamme": "tantra", "typologie": "tantra_banquette_deux_niveaux", "grammaire_livree": True},
    {"gamme": "tantra", "typologie": "tantra_siege_repose_genoux", "grammaire_livree": True},
    {"gamme": "tantra", "typologie": "camo_canape", "grammaire_livree": True},
    {"gamme": "tantra", "typologie": "camo_fauteuil", "grammaire_livree": True},
    {"gamme": "tantra", "typologie": "cadre_desserte_genoux", "grammaire_livree": True},
    {"gamme": "tantra", "typologie": "cadre_table_inclinee", "grammaire_livree": False},
    {"gamme": "rangement", "typologie": "ratelier_mural", "grammaire_livree": True},
    {"gamme": "rangement", "typologie": "armoire_accessoires", "grammaire_livree": False},
    {"gamme": "rangement", "typologie": "coffre", "grammaire_livree": False},
    {"gamme": "rangement", "typologie": "support_exposition", "grammaire_livree": False},
    {"gamme": "rangement", "typologie": "armoire_verrouillable", "grammaire_livree": False},
)


def typologie_est_exclue(typologie):
    """True pour le pouf vibrant Incognito (et alias)."""
    t = (typologie or "").strip().lower().replace("-", "_").replace(" ", "_")
    if not t:
        return False
    if t in TYPOLOGIES_EXCLUES or t.startswith("pouf"):
        return True
    return False


def normaliser_typologie(gamme, typologie=None):
    """Valide la typologie, refuse le pouf, pose le défaut de gamme."""
    if typologie_est_exclue(typologie) or typologie_est_exclue(gamme):
        raise ValueError(
            "Le collecteur d'urine ne cible pas le pouf vibrant Incognito "
            "(plus de module de collecte). Typologie/gamme refusée : %s / %s. "
            "Aucune modification de /workspace/incognito."
            % (typologie, gamme)
        )
    if typologie:
        t = typologie.strip()
        if typologie_est_exclue(t):
            raise ValueError("typologie exclue : %s" % t)
        return t
    if gamme not in DEFAUT_TYPOLOGIE:
        raise ValueError("gamme inconnue : %s" % gamme)
    return DEFAUT_TYPOLOGIE[gamme]


def typologies_cibles():
    """Liste figée des typologies couvertes (hors pouf)."""
    return tuple(dict(x) for x in TYPOLOGIES_CIBLES)




def _boite(nom, x, y, z, dx, dy, dz, materiau_cle, role, note="", visible=True, demontable=False):
    return {
        "type": "boite", "nom": nom,
        "origine": (float(x), float(y), float(z)),
        "dimensions": (float(dx), float(dy), float(dz)),
        "materiau": materiau_cle, "role": role, "note": note,
        "visible": bool(visible), "demontable": bool(demontable),
    }


def _cylindre(nom, base, axe, diametre, longueur, materiau_cle, role, note="", visible=True, demontable=False):
    return {
        "type": "cylindre", "nom": nom, "base": tuple(float(c) for c in base),
        "axe": axe, "diametre": float(diametre), "longueur": float(longueur),
        "materiau": materiau_cle, "role": role, "note": note,
        "visible": bool(visible), "demontable": bool(demontable),
    }


def volume_total_ml(params=None):
    """Volume de cuve = volume utile × coefficient anti-débordement (mL)."""
    p = params if isinstance(params, Parametres) else Parametres(params or {})
    return float(p.get("collecteur_urine.volume_utile")) * float(
        p.get("collecteur_urine.coefficient_anti_debordement")
    )


def dimensions_reservoir(volume_ml, rayon_interieur_min=5.0, epaisseur_paroi=2.5):
    """Enveloppe d'un réservoir parallélépipédique couvrant ``volume_ml``.

    Intérieur utile visé 120 × 80 mm au plan, hauteur déduite. Un surcroît
    de hauteur compense (ordre de grandeur) le volume perdu aux rayons
    intérieurs. Ce n'est pas une cote de meuble.
    """
    inner_l, inner_w = 120.0, 80.0
    inner_h = (float(volume_ml) * 1000.0) / (inner_l * inner_w)
    # Compensation forfaitaire des congés (4 coins verticaux ≈ trop simple) :
    # on ajoute 2 × r / 3 en hauteur, clairement empirique.
    inner_h += 2.0 * float(rayon_interieur_min) / 3.0
    ext_l = inner_l + 2.0 * epaisseur_paroi
    ext_w = inner_w + 2.0 * epaisseur_paroi
    ext_h = inner_h + 2.0 * epaisseur_paroi
    return {
        "interieur_mm": (inner_l, inner_w, inner_h),
        "exterieur_mm": (ext_l, ext_w, ext_h),
        "epaisseur_paroi_mm": epaisseur_paroi,
        "volume_interieur_cible_ml": volume_ml,
        "volume_boite_interieure_ml": inner_l * inner_w * inner_h / 1000.0,
    }


def materiau_contact_admis(cle):
    if cle in MATERIAUX_CONTACT_ADMIS:
        return True
    # Alias catalogue
    try:
        m = materiau(cle)
    except Exception:
        return False
    if m.get("poreux"):
        return False
    return cle in POLYMERES or (cle in METAUX and cle.startswith("inox_316"))


def implantation(gamme, params=None, typologie=None):
    """Position du caisson relativement aux ancrages *déjà relevés*.

    Ne crée aucune cote de meuble. Les typologies sans surface d'assise
    cotée reçoivent un TODO d'implantation fine.
    """
    p = params if isinstance(params, Parametres) else Parametres(params or {})
    typologie = normaliser_typologie(gamme, typologie)
    notes = []
    todos = []

    if typologie == "sex_machine_mecanique" or gamme == "aboutissants":
        notes.append(
            "Aboutissant fixe — machine de mouvement mécanique : caisson indépendant "
            "au sol, sous ou en arrière de la zone de course de la tige, près de la "
            "bride d'œillet (sans modifier le meuble ni surcharger le châssis, dont "
            "la stabilité au renversement est déjà juste). L'entonnoir déployable "
            "s'aligne sous l'axe de poussée. Le port Vac-U-Lock en bout de tige "
            "reste une interface mécanique, pas un raccord de fluide."
        )
        return {
            "gamme": "aboutissants",
            "typologie": "sex_machine_mecanique",
            "origine_caisson": (0.0, 0.0, 0.0),
            "z_bord_collecte_mm": 80.0,  # hypothèse de module au sol, pas une cote meuble
            "jeu_sol_mm": 0.0,
            "ancrages_references": {
                "fixation": "bride sur œillet / anneau existant (M8 côté accessoire), sans percage",
            },
            "modification_meuble": False,
            "notes": notes,
            "todos": [],
        }

    if gamme == "equinox":
        z_traverse = p.get("ancrages.equinox.hauteur_axe_traverse")
        cote_tube = p.get("ancrages.equinox.cote_tube_traverse")
        di_anneau = p.get("ancrages.equinox.diametre_interieur_anneau")
        saillie = p.get("ancrages.equinox.saillie_oeillet")
        di_oeil = p.get("ancrages.equinox.diametre_interieur_oeillet_bas")
        encast = p.get("ancrages.equinox.profondeur_encastrement")
        # Le caisson se loge sous / derrière, sans percer. Bord supérieur de
        # l'entonnoir juste sous le tube de traverse (z typique banc Flore).
        z_dessus_tube = z_traverse + cote_tube / 2.0
        z_bord_entonnoir = z_dessus_tube - 10.0  # jeu 10 mm sous le tube, pas une cote meuble
        origine_caisson = (0.0, 0.0, 0.0)  # sol, aligné sur l'anneau arrière (mi-traverse)
        notes.append(
            "Equinox : caisson indépendant à l'arrière / sous le meuble, aligné sur l'anneau "
            "de traverse (DI %g mm, axe typique banc Flore z=%g mm, tube %g mm). "
            "Les œillets de semelle (DI %g, saillie %g, encastrement %g mm) restent libres : "
            "le caisson ne les recouvre pas, aucun perçage."
            % (di_anneau, z_traverse, cote_tube, di_oeil, saillie, encast)
        )
        if typologie == "banc_flore":
            notes.append(
                "Banc Flore : gouttière sous siège ou entonnoir déployable à l'arrière, "
                "au voisinage de l'anneau de traverse. Hauteur d'appui typique 700 mm "
                "(cote meuble, déjà citée pour la machine) : le caisson sous le banc a de la place."
            )
        elif typologie == "tabouret":
            notes.append(
                "Tabouret : emprise courte — préférer un entonnoir déployable à une longue gouttière. "
                "Anneaux de ceinture à %g mm (relevé). L'encombrement sous l'assise n'est pas coté (TODO)."
                % p.get("ancrages.equinox.tabouret_hauteur_ceinture")
            )
            todos.append(
                "Tabouret Equinox : dessous d'assise et emprise au sol du collecteur non cotés."
            )
        elif typologie == "chaise_trone":
            notes.append(
                "Chaise / trône : gouttière sous siège ou entonnoir arrière, tiroir sous l'assise. "
                "Anneaux d'accoudoirs à %g mm (relevé). Dessous d'assise non coté (TODO)."
                % p.get("ancrages.equinox.chaise_hauteur_accoudoirs")
            )
            todos.append(
                "Chaise / trône Equinox : dessous d'assise et emprise au sol du collecteur non cotés."
            )
        elif typologie == "croix_saint_andre":
            notes.append(
                "Croix de Saint-André : pas d'assise — pas de gouttière sous siège. "
                "Entonnoir déployable depuis un socle / panneau basculant bas, près des anneaux "
                "d'extrémités. La discrétion est plus difficile (meuble ouvert) : caisson bas affleurant."
            )
            todos.append(
                "Croix Equinox : implantation au sol du socle collecteur non cotée dans la grammaire d'ancrage."
            )
        elif typologie == "cheval_arcon":
            notes.append(
                "Cheval d'arçon : typologie listée dans Equinox (hauteur d'assise 760 mm, plateau "
                "700×260 mm dans parametres.py, overrides de typologie) mais **grammaire non livrée**. "
                "Logique proche du banc : gouttière sous plateau ou entonnoir arrière, près de l'anneau "
                "de traverse (même famille d'ancrages). Implantation fine en TODO."
            )
            todos.append(
                "Cheval d'arçon : pas de grammaire livrée ; ne pas inventer d'ancrages au-delà de la famille Equinox déjà relevée."
            )
        elif typologie not in ("banc_flore",):
            todos.append("Typologie Equinox « %s » : implantation fine à caler." % typologie)
        return {
            "gamme": gamme, "typologie": typologie,
            "origine_caisson": origine_caisson,
            "z_bord_collecte_mm": z_bord_entonnoir,
            "jeu_sol_mm": 8.0,  # laisse la saillie des œillets (18 mm) hors emprise du tiroir
            "ancrages_references": {
                "anneau_traverse_di_mm": di_anneau,
                "hauteur_axe_traverse_mm": z_traverse,
                "oeillet_bas_di_mm": di_oeil,
                "saillie_oeillet_mm": saillie,
            },
            "modification_meuble": False,
            "notes": notes, "todos": todos,
        }

    if gamme == "incognito":
        d_ins = p.get("ancrages.incognito.diametre_insert")
        recouv = p.get("ancrages.incognito.recouvrement")
        bord = p.get("ancrages.incognito.distance_au_bord")
        inset = p.get("ancrages.incognito.inset_x_min")
        notes.append(
            "Incognito (hors pouf) : rien de visible fermé (règle de gamme). Le collecteur "
            "se déploie par tiroir ou panneau basculant / trappe affleurante, comme les "
            "trappes de plancher et le coffre de la banquette (couvercle ≈ 95°). Le dossier "
            "basculant ou coulissant a été écarté en gamme : on ne s'y accroche pas. "
            "Le pouf vibrant n'est pas une cible (plus de module de collecte). "
            "Les inserts noyés Ø%g mm (filetage TODO), recouvrement %g mm, bord %g / "
            "inset_x ≥ %g mm, restent intacts quand ils existent (banquette) ; le module "
            "ne perce pas le meuble. /workspace/incognito n'est pas modifié."
            % (d_ins, recouv, bord, inset)
        )
        if typologie == "banquette":
            notes.append(
                "Banquette : premier meuble livré. Caisson / pieds (hauteur de pieds typologie "
                "120 mm, assise 430 mm — incognito/parametres.py) : place juste pour un réservoir "
                "plat + entonnoir ou gouttière qui se déploient hors du volume des pieds. "
                "Ne pas entrer en conflit avec le banc déployable du coffre ni avec les 4 inserts."
            )
        elif typologie in ("canape", "fauteuil", "banc_entree"):
            notes.append(
                "Typologie salon « %s » : catalogue Incognito, grammaire non livrée. "
                "Même règle de discrétion qu'une banquette ; ancrages propres non relevés (TODO). "
                "Les cotes typologiques (assise typ. 430 mm) sont dans incognito/parametres.py."
                % typologie
            )
            todos.append("Ancrages et dessous d'assise de la typologie Incognito « %s » : TODO (grammaire non livrée)." % typologie)
        elif typologie == "table_basse":
            notes.append(
                "Table basse : la typologie prévoit déjà un tiroir ou un plateau basculant "
                "pour masquer un mécanisme (incognito/parametres.py). Grammaire non livrée ; "
                "ancrages TODO. Usage plutôt comme point de collecte / vidange discret que comme siège."
            )
            todos.append("Table basse Incognito : grammaire et ancrages non livrés.")
        elif typologie == "bibliotheque":
            notes.append(
                "Bibliothèque : pas d'assise. Les montants et la plinthe peuvent masquer un "
                "réservoir ou un raccord de service. Peu adaptée à une gouttière sous siège. "
                "Grammaire non livrée ; ancrages TODO."
            )
            todos.append("Bibliothèque Incognito : grammaire et ancrages de montant / plinthe non livrés.")
        return {
            "gamme": gamme, "typologie": typologie,
            "origine_caisson": (0.0, 0.0, 0.0),
            "z_bord_collecte_mm": 60.0,  # hypothèse de module, pas une cote d'assise (non relevée)
            "jeu_sol_mm": 0.0,  # trappe affleurante
            "epaisseur_voile_affleurant_mm": recouv,
            "ancrages_references": {
                "diametre_insert_mm": d_ins,
                "filetage": p.get("ancrages.incognito.filetage"),
                "recouvrement_mm": recouv,
                "nombre_points": p.get("ancrages.incognito.nombre_points_banquette"),
            },
            "modification_meuble": False,
            "notes": notes,
            "todos": [
                "Filetage de l'insert Incognito Ø12 : TODO (non documenté).",
                "Hauteur d'assise / de trappe au sol : non relevée ici ; z_bord_collecte "
                "est une hypothèse de module à caler sur le meuble réel.",
            ],
        }

    if gamme == "neogothique":
        cote = p.get("ancrages.neogothique.plaque_cote")
        ep = p.get("ancrages.neogothique.plaque_epaisseur")
        x = p.get("ancrages.neogothique.x_pied_defaut")
        dec_y = p.get("ancrages.neogothique.decalage_y_bout_semelle")
        y = LS_ENTRAVE_DEFAUT_MM / 2.0 - dec_y
        cap = p.get("ancrages.neogothique.capacite_point")
        notes.append(
            "Néogothique (Entrave, défauts) : 4 plaques  %g×%g×%g mm aux points "
            "x=±%g, y=±%g mm (y = Ls/2 − %g, Ls défaut %g mm documenté dans la "
            "justification du paramètre, source grammaire Entrave). Le caisson se "
            "loge à l'intérieur du rectangle, sans recouvrir les plaques (jeu ≥ 10 mm), "
            "sans perçage. Filetage / DI d'anneau des plaques : TODO."
            % (cote, cote, ep, x, y, dec_y, LS_ENTRAVE_DEFAUT_MM)
        )
        return {
            "gamme": gamme, "typologie": typologie or "entrave",
            "origine_caisson": (0.0, 0.0, 0.0),
            "z_bord_collecte_mm": 50.0,  # module sous le cadre ; hauteur d'assise non cotée ici
            "jeu_sol_mm": ep + 2.0,
            "ancrages_references": {
                "plaques_xy_mm": ((x, y), (x, -y), (-x, y), (-x, -y)),
                "plaque_mm": (cote, cote, ep),
                "capacite_point_N": cap,
                "filetage": p.get("ancrages.neogothique.filetage"),
                "di_anneau": p.get("ancrages.neogothique.diametre_interieur_anneau"),
                "ls_entrave_defaut_mm": LS_ENTRAVE_DEFAUT_MM,
            },
            "modification_meuble": False,
            "emprise_max_mm": (2 * x - cote - 20.0, 2 * y - cote - 20.0),
            "notes": notes,
            "todos": [
                "Filetage et DI d'anneau des plaques Néogothique : TODO.",
                "Hauteur d'assise / de cadre au-dessus des plaques : non relevée pour le collecteur.",
            ],
        }

    if gamme == "tantra":
        filetage = p.get("ancrages.tantra.filetage")
        d_ins = p.get("ancrages.tantra.diametre_insert")
        l_ef = p.get("ancrages.tantra.longueur_encastrement")
        charge = p.get("ancrages.tantra.charge_service")
        di = p.get("ancrages.tantra.diametre_interieur_anneau")
        notes.append(
            "Tantra : caisson rapporté sous / derrière le meuble, sans perçage et sans recouvrir "
            "les inserts M12 (Ø ext. %g, encastrement %g mm, filetage %s, charge de service %g N). "
            "Aucun NPT ni port Vac-U-Lock natif ; aucun emplacement de collecteur n'est coté (TODO). "
            "DI d'anneau = %s. /workspace/tantra n'est pas modifié."
            % (d_ins, l_ef, filetage, charge, di)
        )
        if typologie in ("camo_canape", "camo_fauteuil"):
            notes.append(
                "Volet camouflable : rien de visible à l'état SALON. Le collecteur se déploie par "
                "tiroir ou panneau bas (voile affleurant), comme les caches aimantés et manchettes "
                "du meuble. Recouvrement d'insert typ. %g mm."
                % p.get("ancrages.tantra.retrait_ancre_sous_surface")
            )
            todos.append("Implantation fine sous canapé / fauteuil camouflable : dessous d'assise non coté pour le collecteur.")
        elif typologie == "cadre_desserte_genoux":
            notes.append(
                "Desserte-cadre : agenouilloir, pas une assise classique. Entonnoir déployable près "
                "de la tablette (état CADRE) plutôt qu'une longue gouttière. Hauteur barre haute typ. "
                "%g mm (MEUBLE) / %g mm (CADRE)."
                % (p.get("ancrages.tantra.cadre_desserte_hauteur_meuble"),
                   p.get("ancrages.tantra.cadre_desserte_hauteur_cadre"))
            )
        elif typologie == "cadre_table_inclinee":
            notes.append(
                "Table basse → cadre incliné : grammaire non livrée. La personne serait au sol "
                "(efforts extérieurs). Peu adapté à une gouttière sous siège. Ne pas inventer d'ancrages."
            )
            todos.append("cadre_table_inclinee : pas de grammaire ; emplacement collecteur inexistant.")
        elif typologie in (
            "tantra_chaise_double_courbe", "tantra_fauteuil_lombaire",
            "tantra_banquette_deux_niveaux", "tantra_siege_repose_genoux",
        ):
            notes.append(
                "Typologie à assise / soutien livrée (« %s ») : gouttière sous surface ou entonnoir "
                "à l'arrière, cuve amovible. Les ancrages d'insert M12 + anneau rabattable restent libres."
                % typologie
            )
            todos.append("Dessous d'assise / emprise au sol du collecteur : non cotés dans la grammaire Tantra « %s »." % typologie)
        return {
            "gamme": gamme, "typologie": typologie,
            "origine_caisson": (0.0, 0.0, 0.0),
            "z_bord_collecte_mm": 60.0,  # hypothèse de module, pas une cote d'assise Tantra
            "jeu_sol_mm": 0.0,
            "ancrages_references": {
                "filetage": filetage,
                "diametre_insert_mm": d_ins,
                "longueur_encastrement_mm": l_ef,
                "charge_service_N": charge,
                "diametre_interieur_anneau": di,
            },
            "modification_meuble": False,
            "notes": notes, "todos": todos,
        }

    if gamme == "rangement":
        notes.append(
            "Rangement : un râtelier mural n'a pas d'assise et « n'est PAS un point d'ancrage de "
            "personne ». Aucun emplacement de collecteur n'est coté (TODO). /workspace/rangement "
            "n'est pas modifié. Les ports Vac-U-Lock / douilles 1\" NPT du râtelier ne sont pas "
            "des raccords de fluide d'urine."
        )
        if typologie == "ratelier_mural":
            notes.append(
                "Râtelier mural (grammaire livrée) : pas de gouttière sous siège. Un caisson "
                "indépendant au sol à proximité n'est plus un aboutissant du râtelier. Ports typ. "
                "2 par module, entraxe %g mm, axe à %g mm du bas de panneau."
                % (p.get("ancrages.rangement.pas_ports"), p.get("ancrages.rangement.hauteur_ports"))
            )
            todos.append("Pas d'implantation collecteur sur un râtelier : typologie non porteuse.")
        else:
            notes.append(
                "Typologie « %s » : catalogue Rangement, grammaire non livrée. Aucun volume de "
                "collecte n'y est coté. Un coffre-banc (hauteur typ. 440 mm dans parametres.py) "
                "pourrait *en théorie* masquer un tiroir, mais ce n'est pas spécifié."
                % typologie
            )
            todos.append("Typologie Rangement « %s » : grammaire et emplacement collecteur non livrés." % typologie)
        return {
            "gamme": gamme, "typologie": typologie,
            "origine_caisson": (0.0, 0.0, 0.0),
            "z_bord_collecte_mm": 50.0,  # hypothèse de module indépendant, pas une cote meuble
            "jeu_sol_mm": 0.0,
            "ancrages_references": {
                "filetage_insert": p.get("ancrages.rangement.filetage_insert"),
                "point_ancrage_personne": p.get("ancrages.rangement.point_ancrage_personne"),
                "ports_npt": p.get("ancrages.rangement.ports_npt"),
            },
            "modification_meuble": False,
            "notes": notes, "todos": todos,
        }

    raise ValueError("gamme inconnue : %s" % gamme)


def comparaison_vidanges():
    """Arbitrage documenté des trois modes de vidange (la reco est dans les params)."""
    return {
        "reservoir_amovible": {
            "recommandation": "defaut",
            "avantages": (
                "Aucun raccordement au bâtiment, lavage hors meuble, joints limités au "
                "lèvre/couvercle, compatible avec la discrétion (le réservoir reste dans le caisson).",
            ),
            "inconvenients": (
                "Volume utile borné par l'encombrement du caisson ; manipulation d'un fluide ; "
                "un oubli de vidange fait déborder malgré le coefficient 1,2.",
            ),
        },
        "gravite_point_bas": {
            "recommandation": "alternative",
            "avantages": (
                "Vidange continue, volume de cuve moindre, pas de manipulation de réservoir plein.",
            ),
            "inconvenients": (
                "Exige une pente continue jusqu'à un rejet prévu (non fourni par le meuble) ; "
                "plus de tubulure à rincer ; moins discret si le rejet est apparent.",
            ),
        },
        "raccord_npt": {
            "recommandation": "option de fond",
            "avantages": (
                "Le 1\" NPT (ASME B1.20.1) est déjà au catalogue Incognito (housses / actionneur) ; "
                "raccord standard, démontable, peut aussi servir en fond de réservoir amovible.",
            ),
            "inconvenients": (
                "Ø généreux pour de l'urine (utilisable, pas nécessaire) ; absent d'Equinox, "
                "de Néogothique et de Tantra ; présent dans Rangement (douilles de ports, pas "
                "comme vidange d'urine) et Incognito (housses). Ce n'est pas un Vac-U-Lock et "
                "ne doit pas y être confondu.",
            ),
        },
        "vac_u_lock": {
            "recommandation": "non retenu comme raccord de fluide",
            "avantages": (),
            "inconvenients": (
                "Ergot / cavité conçus pour un accessoire souple, pas pour un fluide ; "
                "pas d'étanchéité liquide sourcée ; à réserver à l'interface mécanique.",
            ),
        },
    }



def arbitrages_par_typologie():
    """Tableau d'arbitrages discrétion / volume utile / facilité de vidange.

    Une ligne par typologie de meuble (Equinox, Néogothique, Incognito hors
    pouf, Tantra, Rangement) et par aboutissant fixe (machine mécanique). Les formes et vidanges
    indiquées sont des *recommandations par typologie* ; les paramètres
    restent libres (entonnoir, gouttière, réservoir amovible, gravité, NPT).
    """
    def ligne(gamme, typologie, forme, vidange, deploiement, discretion, volume, vidange_facile, arbitrage, grammaire, sources=""):
        return {
            "gamme": gamme,
            "typologie": typologie,
            "forme_conseillee": forme,
            "vidange_conseillee": vidange,
            "deploiement": deploiement,
            "discretion": discretion,
            "volume_utile": volume,
            "facilite_vidange": vidange_facile,
            "arbitrage": arbitrage,
            "grammaire_livree": grammaire,
            "sources": sources,
            "exclue": False,
        }

    rows = [
        ligne(
            "equinox", "banc_flore",
            "gouttiere_sous_siege (alternative : entonnoir déployable à l'arrière)",
            "reservoir_amovible (NPT en option de fond ; gravité si rejet prévu)",
            "tiroir arrière / sous le banc",
            "Bonne : le caisson disparaît sous le banc ; rien de visible fermé. L'anneau de traverse (DI 40, z typ. 130 mm) et les œillets de semelle restent libres.",
            "Aisé : 500 mL (cuve 600 mL) tiennent sous un banc d'appui typique 700 mm sans forcer le voile.",
            "Bonne avec réservoir amovible emporté vers un point d'eau. Gravité plus simple en usage mais exige un rejet que le meuble ne fournit pas.",
            "Le volume n'est pas le facteur limitant. On privilégie une gouttière sous siège (meilleure capture sur un banc allongé) malgré un rinçage un peu plus long qu'un entonnoir, et une cuve amovible pour ne pas dépendre du bâtiment. La gravité se justifie seulement si un rejet est prévu à l'installation.",
            True,
            "ancrages Equinox déjà relevés (anneau, œillets) ; hauteur d'appui 700 mm citée dans mouvement.hauteur (source meuble, pas recopiée comme cote d'ancrage).",
        ),
        ligne(
            "equinox", "tabouret",
            "entonnoir déployable (gouttière longue peu adaptée à l'emprise courte)",
            "reservoir_amovible",
            "tiroir compact ou panneau basculant sous l'assise",
            "Moyenne à bonne : meuble petit ; un tiroir trop profond se voit. Le voile doit rester affleurant et court.",
            "Juste : 500 mL restent possibles (cuve ~125×85×70 mm) mais l'emprise sous l'assise n'est pas cotée (TODO). Ne pas monter le volume par défaut.",
            "Correcte : cuve amovible courte, à vider souvent si l'usage enchaîne les mictions. NPT peu naturel sur un tabouret mobile.",
            "La discrétion et l'encombrement limitent plus que le volume utile. On sacrifie la gouttière (trop longue) et on garde 500 mL, tiroir court, réservoir amovible. Gravité déconseillée (tabouret déplaçable, pas de rejet lié).",
            True,
            "ancrages.equinox.tabouret_hauteur_ceinture = 160 mm ; assise typ. 440 mm dans Equinox (citée par mouvement.hauteur).",
        ),
        ligne(
            "equinox", "chaise_trone",
            "gouttiere_sous_siege ou entonnoir arrière",
            "reservoir_amovible (NPT optionnel en fond)",
            "tiroir sous l'assise",
            "Bonne : le dessous de chaise masque le caisson ; voile affleurant à l'état fermé.",
            "Aisé à moyen : 500 mL tiennent sous une assise typ. 460 mm, sous réserve du volume réel sous l'assise (non coté, TODO).",
            "Bonne avec cuve amovible. Gravité possible si la chaise est un meuble fixe près d'un rejet.",
            "Plus de place qu'un tabouret, moins qu'un banc. On reste sur 500 mL et le réservoir amovible ; la gouttière sous siège améliore la capture sans nuire à la discrétion si le tiroir est sous l'assise.",
            True,
            "ancrages.equinox.chaise_hauteur_accoudoirs = 670 mm ; assise typ. 460 mm (citée par mouvement.hauteur).",
        ),
        ligne(
            "equinox", "croix_saint_andre",
            "entonnoir déployable (pas de gouttière sous siège : pas d'assise)",
            "reservoir_amovible (gravité intéressante si la croix est scellée au sol)",
            "panneau basculant de socle / tiroir bas affleurant",
            "Plus faible : meuble ouvert, pas de caisson d'assise. Le collecteur doit tenir dans un socle bas, rien de visible une fois le panneau refermé.",
            "Aisé au sol (500 mL n'imposent pas un socle haut) — ne pas agrandir le socle pour « gagner » du volume, au détriment de la discrétion.",
            "Bonne si cuve amovible dans le socle. Gravité pertinente sur une croix fixe ; raccord NPT en sortie de socle possible.",
            "Ici la discrétion commande : entonnoir escamotable, socle bas, volume utile standard sans surdimensionner. La facilité de vidange peut aller vers la gravité seulement si le point bas existe déjà (fixation au sol).",
            True,
            "Anneaux aux extrémités (grammaire Equinox) ; pas de cote d'implantation au sol du collecteur (TODO).",
        ),
        ligne(
            "equinox", "cheval_arcon",
            "gouttiere_sous_siege (plateau) ou entonnoir arrière — à confirmer",
            "reservoir_amovible",
            "tiroir sous le plateau / à l'arrière",
            "Potentiellement bonne (meuble bas et long) une fois la grammaire livrée.",
            "Aisé en principe (assise typ. 760 mm, plateau 700×260 mm dans les overrides Equinox) : 500 mL ne posent pas de problème d'encombrement attendu.",
            "Bonne, même logique que le banc Flore.",
            "Typologie listée mais grammaire non livrée : on reprend l'arbitrage du banc (gouttière + cuve amovible) sans inventer d'ancrages au-delà de la famille déjà relevée (anneau de traverse, œillets). Implantation fine en TODO.",
            False,
            "equinox/equinox/parametres.py overrides cheval_arcon (hauteur_assise 760, plateau 700×260) ; ancrages de famille Equinox.",
        ),
        ligne(
            "neogothique", "entrave",
            "entonnoir déployable (gouttière courte si le corps est allongé sur le cadre)",
            "reservoir_amovible (gravité ou NPT pertinents : meuble déjà ancré au sol)",
            "tiroir ou panneau basculant dans un caisson bas *entre* les plaques, sans les recouvrir",
            "Moyenne : l'Entrave n'a pas la règle d'invisibilité d'Incognito, mais le caisson peut rester dans le rectangle des plaques (x=±315, y=±235 mm typ. Entrave défaut) et sous le cadre.",
            "Aisé : l'emprise interne (~570×410 mm hors plaques et jeu) accueille largement 500 / 600 mL.",
            "Très bonne : cuve amovible par défaut ; gravité et raccord 1\" NPT deviennent intéressants parce que les plaques au sol fixent déjà le meuble (le NPT sort du caisson, pas du meuble).",
            "Le volume n'est pas limitant. On reste à 500 mL. On choisit le réservoir amovible par défaut (lavage hors meuble) tout en prévoyant un fond NPT optionnel, cohérent avec une installation fixe. Ne pas recouvrir les plaques 40×40×6 (filetage / DI TODO).",
            True,
            "ancrages.neogothique (plaque, x_pied_defaut, decalage_y, Ls défaut 560 mm).",
        ),
        ligne(
            "incognito", "banquette",
            "gouttiere_sous_siege déployable *ou* entonnoir, hors du volume du banc interne",
            "reservoir_amovible (pas de NPT traversant le meuble ; option de fond de cuve seulement)",
            "tiroir ou panneau basculant / trappe affleurante (comme les trappes de plancher et le coffre ≈ 95° ; pas le dossier basculant, écarté)",
            "Excellente : règle de gamme, rien de visible fermé. Le voile reprend l'épaisseur de recouvrement (10 mm).",
            "Serré en hauteur : pieds typologie 120 mm, assise 430 mm (incognito/parametres.py). Une cuve 500 mL (~70 mm hors tout) tient entre les pieds si l'entonnoir ou la gouttière se déploient *hors* de cette hauteur (tiroir qui sort). Ne pas viser plus de 500 mL par défaut.",
            "Bonne si la cuve sort avec le tiroir (vidange et lavage hors du salon). Gravité et NPT de bâtiment malvenus dans un meuble de salon discret ; le 1\" NPT du catalogue housses/actionneur n'est pas un passage à ouvrir dans la banquette.",
            "La hauteur des pieds et le banc déployable dans le coffre limitent le volume et l'emplacement : 500 mL, cuve plate amovible, déploiement hors du coffre d'assise (arrière / trappe de plancher) pour ne pas collisionner le banc ni les 4 inserts Ø12. La discrétion prime ; on ne grossit pas la cuve.",
            True,
            "incognito/grammaires/banquette.py (coffre 95°, trappes affleurantes) ; parametres typologie (pieds 120, assise 430) ; ancrages inserts Ø12 (filetage TODO).",
        ),
        ligne(
            "incognito", "canape",
            "gouttiere_sous_siege (longueur 2/3 places) ou entonnoir",
            "reservoir_amovible",
            "tiroir sous l'assise / dans le caisson, rien de visible fermé",
            "Excellente (règle de gamme). Largeur typ. 1700 / 2200 mm (parametres.py) : le voile se fond dans le caisson.",
            "Aisé en plan (meuble long) ; hauteur d'assise typ. 430 mm, hauteur de pieds non isolée dans la typologie (TODO). 500 mL sans difficulté attendue.",
            "Bonne, cuve amovible. Même réserve que la banquette vis-à-vis d'un NPT de bâtiment.",
            "Grammaire non livrée, ancrages propres non relevés (TODO). Arbitrage provisoire : même logique que la banquette, avec plus de place en longueur donc gouttière sous siège possible. Ne pas inventer d'inserts.",
            False,
            "incognito/incognito/parametres.py typologie canape.",
        ),
        ligne(
            "incognito", "fauteuil",
            "entonnoir déployable (emprise d'une place, gouttière longue peu utile)",
            "reservoir_amovible",
            "tiroir ou panneau basculant sous l'assise",
            "Excellente (règle de gamme), sous réserve d'un tiroir court (largeur typ. 820 mm).",
            "Moyen : une place seulement ; 500 mL restent le bon ordre de grandeur, sans le monter.",
            "Bonne, cuve amovible courte.",
            "Grammaire non livrée (TODO ancrages). Même discrétion qu'une banquette, emprise plus proche du tabouret : entonnoir plutôt que longue gouttière, cuve amovible 500 mL.",
            False,
            "incognito/incognito/parametres.py typologie fauteuil (assise 430, largeur 820).",
        ),
        ligne(
            "incognito", "table_basse",
            "entonnoir déployable depuis le plateau ou le tiroir (pas une gouttière « sous siège »)",
            "reservoir_amovible (NPT de service possible dans le caisson, sans traverser un meuble d'ancrage non coté)",
            "tiroir ou plateau basculant — déjà prévu par la typologie pour masquer un mécanisme",
            "Excellente : c'est précisément le rôle du tiroir / plateau basculant décrit dans parametres.py.",
            "Aisé : plateau typ. 1200×700×hauteur 420 mm ; 500 mL tiennent largement.",
            "Très bonne : la cuve sort avec le tiroir ; point de vidange discret dans un salon.",
            "Typologie de salon sans grammaire livrée (ancrages TODO). Usage plutôt comme point de collecte / de service discret que comme siège. On garde entonnoir déployable + cuve amovible, en s'appuyant sur le tiroir déjà prévu par la typologie, sans inventer de cotes d'ancrage.",
            False,
            "incognito/incognito/parametres.py typologie table_basse (hauteur 420, 1200×700, plateau 28 mm).",
        ),
        ligne(
            "incognito", "banc_entree",
            "gouttiere_sous_siege ou entonnoir (éventuellement coffre déjà prévu par la typologie)",
            "reservoir_amovible",
            "tiroir ou panneau de coffre / basculant",
            "Excellente si le coffre / le voile reste affleurant (règle de gamme).",
            "Aisé en longueur (typ. 1200×400, assise 430 mm) pour 500 mL ; profondeur 400 mm à caler (grammaire non livrée).",
            "Bonne, cuve amovible.",
            "Proche d'un petit banc Equinox, avec la discrétion Incognito. Grammaire non livrée, ancrages TODO. Recommandation provisoire : gouttière ou entonnoir + cuve amovible 500 mL, sans dossier basculant.",
            False,
            "incognito/incognito/parametres.py typologie banc_entree.",
        ),
        ligne(
            "incognito", "bibliotheque",
            "pas de gouttière sous siège (pas d'assise) ; éventuellement entonnoir de service depuis la plinthe",
            "reservoir_amovible dans la plinthe, ou raccord_npt de service",
            "panneau basculant / plinthe affleurante",
            "Excellente (montants et plinthe masquent déjà des ancrages selon la typologie), à condition qu'aucune ferrure ne dépasse.",
            "Aisé dans une plinthe de profondeur typ. 350 mm ; 500 mL ne posent pas de problème d'encombrement.",
            "Bonne : cuve dans la plinthe, ou NPT de service si l'installation est fixe. Peu d'usage « miction directe ».",
            "Peu adaptée comme collecteur sous un siège. On la retient comme typologie de meuble Incognito hors pouf, plutôt comme point de service / de vidange discret. Grammaire et ancrages de montant non livrés (TODO).",
            False,
            "incognito/incognito/parametres.py typologie bibliotheque (2000×1000×350, montant 22 mm).",
        ),
        ligne(
            "aboutissants", "sex_machine_mecanique",
            "entonnoir déployable aligné sous l'axe de la tige (gouttière courte possible)",
            "reservoir_amovible (NPT en fond de cuve optionnel ; ne pas détourner le raccord NPT / l'ergot Vac-U-Lock de la tige)",
            "tiroir ou panneau basculant dans un caisson bas indépendant, sous ou derrière la zone de course",
            "Moyenne : la machine est déjà un module visible, plus « technique » qu'un meuble Incognito. Le collecteur ne doit rien ajouter à l'état fermé (socle / tiroir affleurant sous le châssis).",
            "Aisé : caisson au sol, 500 mL sans hausser le châssis. Ne pas fixer la cuve pleine sur le châssis (stabilité au renversement déjà juste sous 800 N à 700 mm).",
            "Bonne avec cuve amovible indépendante. Gravité possible vers un point bas de pièce. Le 1\" NPT arrière du port Vac-U-Lock n'est pas une vidange d'urine.",
            "Aboutissant fixe, pas un meuble. On sépare nettement les interfaces : ergot Vac-U-Lock + NPT de la tige d'un côté, collecteur au sol de l'autre. Discrétion = caisson bas autonome, sans surcharger la bride d'œillet. Volume 500 mL par défaut, vidange amovible.",
            True,
            "mouvement/sex_machine_mecanique.py ; interface M8 / bride déjà documentée ; port Vac-U-Lock en bout de tige.",
        ),
        ligne(
            "tantra", "tantra_chaise_double_courbe",
            "gouttiere_sous_siege ou entonnoir arrière",
            "reservoir_amovible (pas de NPT natif sur le meuble)",
            "caisson rapporté sous / derrière, sans perçage",
            "Bonne sur le volet Tantra (fonction assumée, anneaux rabattables déjà visibles). Le caisson reste bas, les 4 inserts M12 restent libres.",
            "Aisé : assise longue (typ. 1850 mm) ; 500 mL tiennent dans un caisson bas. Dessous d'assise non coté pour le collecteur (TODO).",
            "Bonne avec cuve amovible. Gravité seulement si un rejet est prévu. Pas de douille NPT dans Tantra.",
            "Typologie à soutien livrée, aucun emplacement collecteur coté. On reporte un caisson indépendant, gouttière ou entonnoir, vidange amovible, sans inventer de raccord NPT dans le meuble.",
            True,
            "ancrages.tantra (INSERT_ANCRE_M12, 4 ancrages, positions_y 760 / 1560) ; parametres TANTRA_CHAISE_DOUBLE_COURBE.",
        ),
        ligne(
            "tantra", "tantra_fauteuil_lombaire",
            "entonnoir déployable ou gouttière courte sous assise",
            "reservoir_amovible",
            "tiroir / caisson sous l'assise",
            "Bonne (fonction assumée). Deux ancrages de flasques à laisser libres.",
            "Correcte : assise typ. 340 mm au-dessus mousse — l'encombrement sous l'assise n'est pas coté (TODO). Rester à 500 mL.",
            "Cuve amovible courte. NPT peu naturel (meuble mobile, pas de rejet lié).",
            "Même logique qu'une chaise : module rapporté, sans perçage, sans NPT inventé.",
            True,
            "ancrages.tantra (2 ancrages) ; tantra_fauteuil_lombaire.py.",
        ),
        ligne(
            "tantra", "tantra_banquette_deux_niveaux",
            "gouttiere_sous_siege (niveau bas) ou entonnoir à la contremarche",
            "reservoir_amovible",
            "caisson sous le niveau bas / à l'arrière",
            "Bonne. Six ancrages de flasques restent hors du caisson.",
            "Aisé sous un niveau bas typ. 420 mm, sous réserve du dessous non coté (TODO).",
            "Cuve amovible. Gravité optionnelle si rejet prévu.",
            "Banquette profonde, capture plutôt par gouttière au niveau bas. Rien n'est modifié dans Tantra.",
            True,
            "ancrages.tantra (6 ancrages) ; tantra_banquette_deux_niveaux.py.",
        ),
        ligne(
            "tantra", "tantra_siege_repose_genoux",
            "entonnoir déployable (emprise courte, assise inclinée)",
            "reservoir_amovible",
            "caisson compact sous / entre les patins",
            "Moyenne : piètement traîneau plus ouvert qu'un coffre. Voile bas affleurant.",
            "Juste : 500 mL possibles, emprise au sol non cotée (TODO).",
            "Cuve amovible courte. NPT déconseillé (meuble déplaçable).",
            "Quatre ancrages (genoux + assise) à laisser libres. Module rapporté seulement.",
            True,
            "ancrages.tantra (4 ancrages) ; tantra_siege_repose_genoux.py.",
        ),
        ligne(
            "tantra", "camo_canape",
            "entonnoir ou gouttière à déploiement par tiroir / panneau bas affleurant",
            "reservoir_amovible",
            "tiroir bas, rien de visible à l'état SALON",
            "Exigeante : règle de discrétion du volet camouflable (aucune ferrure visible fermée). Le collecteur ne doit pas trahir le canapé au repos. Six ancrages masqués restent intacts.",
            "Serré : hauteur d'assise typ. 440 mm, dessous non coté (TODO). 500 mL par défaut, pas plus.",
            "Cuve amovible seulement (discret). Pas de NPT apparent en façade.",
            "Même discipline qu'Incognito : état fermé invisible. Implantation fine TODO. /workspace/tantra non modifié.",
            True,
            "ancrages.tantra (6 ancrages masqués, cache Ø40 × 10, retrait 10 mm) ; camo_canape.py, _salon.py.",
        ),
        ligne(
            "tantra", "camo_fauteuil",
            "entonnoir déployable (façade basculante = repose-genoux en RÉVÉLÉ)",
            "reservoir_amovible",
            "tiroir / panneau bas, invisible en SALON",
            "Exigeante, comme le canapé. Quatre ancrages (pas d'arrière). Ne pas gêner la bavette / le repose-genoux.",
            "Juste, assise typ. 440 mm, dessous non coté (TODO).",
            "Cuve amovible. Pas de NPT apparent.",
            "Collecteur rapporté, discrétion SALON, sans perçage.",
            True,
            "ancrages.tantra (4 ancrages, ancrages_arriere=False) ; camo_fauteuil.py.",
        ),
        ligne(
            "tantra", "cadre_desserte_genoux",
            "entonnoir déployable près de l'agenouilloir (état CADRE)",
            "reservoir_amovible",
            "caisson bas autonome, indépendant de la tablette pivotante",
            "Moyenne : à l'état MEUBLE le meuble est une desserte (discret) ; à l'état CADRE le collecteur doit rester bas et ne pas gêner les pieds pivotants ni les 4 ancrages (poignets / chevilles).",
            "Correcte au sol, 500 mL. Pas de « sous siège » classique.",
            "Cuve amovible. Les ancrages poignets montent avec la barre (750 → 1150 mm).",
            "Fonction agenouilloir, efforts internes sur le meuble. Module rapporté seulement, pas de NPT dans la desserte.",
            True,
            "ancrages.tantra (4 ancrages, hauteurs 750 / 1150 mm) ; cadre_desserte_genoux.py.",
        ),
        ligne(
            "tantra", "cadre_table_inclinee",
            "non recommandé (personne au sol, grammaire non livrée)",
            "reservoir_amovible si un module autonome est malgré tout installé",
            "hors typologie (pas d'implantation cotée)",
            "Faible / indéterminée : typologie étudiée seulement. Une table basse fermée pourrait masquer un module, mais rien n'est spécifié.",
            "Non coté.",
            "Sans objet tant que la grammaire n'existe pas.",
            "Ne pas inventer d'ancrage ni de volume. La note d'étude signale déjà une fixation murale/sol obligatoire ou une marche-plateforme.",
            False,
            "tantra/docs/cadre_table_inclinee.md ; CADRE_TABLE_INCLINEE (encombrement seulement).",
        ),
        ligne(
            "rangement", "ratelier_mural",
            "non porté par le râtelier (pas d'assise)",
            "sans objet sur cette typologie",
            "éventuel caisson indépendant au sol, traité à part",
            "Sans objet : typologie murale de rangement, pas un siège. Les ports NPT / Vac-U-Lock ne sont pas des vidanges d'urine.",
            "Sans objet.",
            "Sans objet.",
            "Un râtelier n'est pas une cible de collecte. On ne détourne pas une douille NPT de port. Pas de modification de /workspace/rangement.",
            True,
            "rangement/grammaires/ratelier_mural.py ; ancrages.rangement.point_ancrage_personne = False ; ports natifs distincts du collecteur.",
        ),
        ligne(
            "rangement", "armoire_accessoires",
            "non spécifié (grammaire non livrée)",
            "reservoir_amovible seulement si une typologie future le prévoit",
            "hors scripts actuels",
            "Indéterminée. Une plinthe pourrait masquer un module, rien n'est coté.",
            "Non coté.",
            "Non coté.",
            "Ne pas inventer d'implantation dans une armoire dont la grammaire n'est pas livrée.",
            False,
            "rangement/rangement/parametres.py (TYPOLOGIES, modules.hauteur_armoire 1800, profondeur 450).",
        ),
        ligne(
            "rangement", "coffre",
            "possible en théorie (coffre-banc, hauteur typ. 440 mm) — non spécifié",
            "reservoir_amovible",
            "hors scripts actuels (grammaire non livrée)",
            "Potentiellement bonne (coffre fermé), mais aucun volume de collecte n'est prévu dans les paramètres.",
            "Non coté (hauteur_coffre = 440 mm est une cote d'assise possible, pas une cote de collecteur).",
            "Non coté.",
            "Ne pas inventer un collecteur dans le coffre. Décision à prendre si une grammaire est écrite.",
            False,
            "rangement/rangement/parametres.py (modules.hauteur_coffre = 440, source tabouret Equinox).",
        ),
        ligne(
            "rangement", "support_exposition",
            "non spécifié (grammaire non livrée)",
            "sans objet tant que la typologie n'est pas grammatisée",
            "hors scripts actuels",
            "Indéterminée.",
            "Non coté.",
            "Non coté.",
            "Pas d'assise typique ; ne pas inventer d'implantation.",
            False,
            "rangement/rangement/parametres.py (TYPOLOGIES).",
        ),
        ligne(
            "rangement", "armoire_verrouillable",
            "non spécifié (grammaire non livrée)",
            "sans objet tant que la typologie n'est pas grammatisée",
            "hors scripts actuels",
            "Indéterminée (niveau de discrétion « invisible » par override).",
            "Non coté.",
            "Non coté.",
            "Ne pas inventer d'implantation. La serrure RFID et la discrétion ne suffisent pas à déduire un collecteur.",
            False,
            "rangement/rangement/parametres.py (OVERRIDES_TYPOLOGIE armoire_verrouillable).",
        ),
    ]
    # Garantir l'exclusion du pouf dans toute itération future.
    assert all(r["typologie"] not in TYPOLOGIES_EXCLUES and "pouf" not in r["typologie"] for r in rows)
    attendues = {(x["gamme"], x["typologie"]) for x in TYPOLOGIES_CIBLES}
    obtenues = {(r["gamme"], r["typologie"]) for r in rows}
    if attendues != obtenues:
        raise RuntimeError("arbitrages incomplets : %s vs %s" % (attendues, obtenues))
    return rows


def tableau_arbitrages_markdown():
    """Table Markdown (une ligne par typologie) pour le rapport docs/."""
    entete = (
        "| Gamme | Typologie | Forme conseillée | Vidange conseillée | Déploiement | "
        "Discrétion | Volume utile | Facilité de vidange | Arbitrage |"
    )
    sep = "|---|---|---|---|---|---|---|---|---|"
    lignes = [entete, sep]
    for r in arbitrages_par_typologie():
        grm = "" if r["grammaire_livree"] else " *(grammaire non livrée)*"
        lignes.append(
            "| %s | %s%s | %s | %s | %s | %s | %s | %s | %s |"
            % (r["gamme"], r["typologie"], grm, r["forme_conseillee"], r["vidange_conseillee"],
               r["deploiement"], r["discretion"], r["volume_utile"], r["facilite_vidange"],
               r["arbitrage"])
        )
    return "\n".join(lignes)


def _verifications(p, dim, impl, solides, forme, vidange, etat, pente_reelle):
    verifs = []

    def add(nom, ok, message):
        verifs.append({"nom": nom, "ok": bool(ok), "message": message})

    mat = p.get("collecteur_urine.materiau_contact")
    add("materiau_contact_non_poreux",
        materiau_contact_admis(mat),
        "Matériau au contact : %s (admis : 316L, PP, PE-HD)." % mat)

    add("cuir_sangle_hors_zone_humide",
        p.get("collecteur_urine.cuir_sangle_zone_humide") is not True,
        "Cuir / sangle interdits en zone mouillée (habillage seulement).")

    pente = p.get("collecteur_urine.pente_min")
    add("pente_ecoulement",
        pente_reelle + 1e-12 >= pente,
        "Pente réelle %.3f ≥ pente mini %g (ordre de grandeur EN 12056-2, 1:50)."
        % (pente_reelle, pente))

    rmin = p.get("collecteur_urine.rayon_interieur_min")
    add("rayon_interieur_min",
        rmin >= 5.0 - 1e-12,
        "Rayon intérieur mini %g mm (aucun angle vif, pas de recoin)." % rmin)

    v_utile = p.get("collecteur_urine.volume_utile")
    v_tot = volume_total_ml(p)
    add("volume_cuve_couvre_utile",
        dim["volume_boite_interieure_ml"] + 1e-6 >= v_tot,
        "Cuve %.1f mL ≥ volume total %.1f mL (utile %g × coef %g)."
        % (dim["volume_boite_interieure_ml"], v_tot, v_utile,
           p.get("collecteur_urine.coefficient_anti_debordement")))

    visibles = [s for s in solides if s.get("visible")]
    roles_humides = {"collecte", "reservoir", "siphon", "vidange", "joint"}
    humides_visibles = [s for s in visibles if s["role"] in roles_humides]
    if etat == 0:
        add("discretion_etat_ferme",
            len(humides_visibles) == 0,
            "État fermé : aucune pièce humide visible (%d pièce(s) apparente(s) : %s)."
            % (len(visibles), ", ".join(s["nom"] for s in visibles) or "aucune"))
    else:
        add("discretion_etat_ferme",
            True,
            "État déployé : les parties humides sont apparentes (normal).")

    add("modification_meuble",
        impl["modification_meuble"] is False,
        "Aucune modification des meubles (%s)." % impl["gamme"])

    demontables = [s for s in solides if s.get("demontable")]
    add("demontable_lavage",
        len(demontables) >= 1,
        "%d pièce(s) démontable(s) pour lavage : %s."
        % (len(demontables), ", ".join(s["nom"] for s in demontables)))

    if p.get("collecteur_urine.siphon"):
        add("siphon_garde_eau",
            (p.get("collecteur_urine.siphon_garde_eau") or 0) > 0,
            "Garde d'eau %g mm." % (p.get("collecteur_urine.siphon_garde_eau") or 0))

    add("vidange_parametree",
        vidange in ("reservoir_amovible", "gravite_point_bas", "raccord_npt"),
        "Mode de vidange : %s (défaut recommandé : réservoir amovible)." % vidange)

    # Vac-U-Lock n'est pas un raccord de fluide.
    noms = {s["nom"] for s in solides}
    add("pas_de_vac_u_lock_fluide",
        not any("vul_" in n or "vac_u_lock" in n for n in noms),
        "Aucun ergot Vac-U-Lock utilisé comme raccord de fluide.")

    return verifs


def calculer_collecteur(params=None, gamme="equinox", typologie=None):
    """Géométrie du collecteur (testable hors Fusion)."""
    p = params if isinstance(params, Parametres) else Parametres(params or {})
    typologie = normaliser_typologie(gamme, typologie)
    if typologie == "sex_machine_mecanique":
        gamme = "aboutissants"
    problemes = [x for x in p.valider() if x.niveau == "erreur"]
    if problemes:
        raise ValueError("Paramètres invalides :\n" + "\n".join(str(e) for e in problemes))

    forme = p.get("collecteur_urine.forme")
    vidange = p.get("collecteur_urine.vidange")
    deploiement = p.get("collecteur_urine.deploiement")
    etat = int(p.get("collecteur_urine.etat_deploiement") or 0)
    mat = p.get("collecteur_urine.materiau_contact")
    joint = p.get("collecteur_urine.joint")
    rmin = p.get("collecteur_urine.rayon_interieur_min")
    pente_min = p.get("collecteur_urine.pente_min")
    v_utile = p.get("collecteur_urine.volume_utile")
    v_tot = volume_total_ml(p)
    dim = dimensions_reservoir(v_tot, rmin)
    impl = implantation(gamme, p, typologie)
    ouvert = etat == 1

    ext_l, ext_w, ext_h = dim["exterieur_mm"]
    # Caisson : enveloppe du tiroir / du panneau, plus grand que le réservoir + entonnoir.
    # Largeur/longueur : hypothèses de module, bornées par l'emprise Néogothique si connue.
    cais_l, cais_w = 280.0, 180.0
    if impl.get("emprise_max_mm"):
        cais_l = min(cais_l, impl["emprise_max_mm"][0])
        cais_w = min(cais_w, impl["emprise_max_mm"][1])
    jeu = impl.get("jeu_sol_mm") or 0.0
    ep_voile = impl.get("epaisseur_voile_affleurant_mm") or 12.0
    # Hauteur de caisson : réservoir + entonnoir + voile + jeu.
    h_collecte = 55.0
    cais_h = jeu + ext_h + h_collecte + ep_voile + 8.0
    ox, oy, oz = impl["origine_caisson"]
    # Caisson centré sur l'origine d'implantation, au sol (oz typiquement 0).
    x0 = ox - cais_l / 2.0
    y0 = oy - cais_w / 2.0
    z0 = oz + jeu

    solides = []
    # Enveloppe du caisson : structure, pas au contact du fluide (peut être le même
    # matériau, ou un habillage hors zone humide — jamais de cuir côté mouillé).
    visible_caisson = True  # le caisson sous le meuble peut être masqué par le meuble lui-même
    # À l'état fermé, seule la façade / le voile affleurant est considérée visible.
    solides.append(_boite(
        "caisson", x0, y0, z0, cais_l, cais_w, cais_h - ep_voile,
        "alu_6082_t6", "caisson",
        "Caisson rapporté, non apparent à l'état fermé s'il est sous / derrière le meuble. "
        "Ne perce pas le meuble. Jeu au sol %g mm." % jeu,
        visible=False,  # toujours masqué par le voile ou le meuble
    ))

    # Voile / façade affleurante (tiroir ou panneau).
    if deploiement == "panneau_basculant":
        note_dep = (
            "Panneau basculant affleurant (ép. %g mm), dans l'esprit du coffre Incognito "
            "(ouverture typique ≈ 95°) et des trappes de plancher. Rien de visible fermé."
            % ep_voile
        )
    else:
        note_dep = (
            "Façade de tiroir affleurante (ép. %g mm). Déploiement par glissement, "
            "rien de visible à l'état fermé."
            % ep_voile
        )
    # Fermé : le voile est au nu ; ouvert : il est basculé / tiré (on le décale).
    if ouvert and deploiement == "tiroir":
        voile_x = x0 + 80.0  # course de tiroir, hypothèse de module
    else:
        voile_x = x0
    solides.append(_boite(
        "voile_affleurant", voile_x, y0, z0 + cais_h - ep_voile,
        cais_l, cais_w, ep_voile,
        "inox_316", "discretion",
        note_dep + (" État déployé." if ouvert else " État fermé : seule cette face est visible."),
        visible=True,
    ))

    # Géométrie de collecte — toujours présente (démontable), visible seulement ouverte.
    pente_reelle = pente_min
    if forme == "gouttiere":
        long_g = cais_l - 20.0
        larg_g = min(90.0, cais_w - 20.0)
        drop = pente_min * long_g
        pente_reelle = drop / long_g if long_g else pente_min
        h_g = max(25.0, drop + 18.0)
        solides.append(_boite(
            "gouttiere", x0 + 10.0, oy - larg_g / 2.0, z0 + ext_h + 8.0,
            long_g, larg_g, h_g, mat, "collecte",
            "Gouttière (banc allongé typiquement). Pente %g, longueur %g mm, "
            "dénivelé %g mm, rayons intérieurs ≥ %g mm, rebord anti-éclaboussures. "
            "Aucun recoin ; démontable pour lavage."
            % (pente_reelle, long_g, drop, rmin),
            visible=ouvert, demontable=True,
        ))
        # Rebord anti-éclaboussures (lèvre).
        solides.append(_boite(
            "lèvre_anti_eclaboussures", x0 + 10.0, oy - larg_g / 2.0,
            z0 + ext_h + 8.0 + h_g, long_g, larg_g, 6.0,
            mat, "collecte",
            "Lèvre anti-éclaboussures, même matière, rincable.",
            visible=ouvert, demontable=True,
        ))
    elif forme == "reservoir_integre":
        # La cuve EST la surface de collecte (moins de joints, lavage moins commode).
        solides.append(_boite(
            "reservoir_integre", ox - ext_l / 2.0, oy - ext_w / 2.0, z0 + 4.0,
            ext_l, ext_w, ext_h + 20.0, mat, "reservoir",
            "Réservoir intégré (forme unique). Moins de joints, lavage moins commode "
            "qu'un bac amovible. Volume intérieur cible %.0f mL, rayons ≥ %g mm, pente de fond %g."
            % (v_tot, rmin, pente_min),
            visible=ouvert, demontable=True,
        ))
        pente_reelle = pente_min
    else:
        # entonnoir (défaut)
        long_e, larg_e, h_e = min(200.0, cais_l - 20.0), min(140.0, cais_w - 20.0), h_collecte
        pente_reelle = (h_e - 8.0) / (max(long_e, larg_e) / 2.0)
        solides.append(_boite(
            "entonnoir", ox - long_e / 2.0, oy - larg_e / 2.0,
            z0 + ext_h + 8.0, long_e, larg_e, h_e, mat, "collecte",
            "Entonnoir (défaut) : concentre vers l'orifice, plus facile à rincer qu'une gouttière. "
            "Pente de paroi %.3f (mini %g), rayons intérieurs ≥ %g mm, pas de recoin, "
            "lèvre anti-éclaboussures. Démontable."
            % (pente_reelle, pente_min, rmin),
            visible=ouvert, demontable=True,
        ))
        solides.append(_boite(
            "levre_anti_eclaboussures", ox - long_e / 2.0, oy - larg_e / 2.0,
            z0 + ext_h + 8.0 + h_e, long_e, larg_e, 6.0,
            mat, "collecte",
            "Lèvre / rebord anti-éclaboussures.",
            visible=ouvert, demontable=True,
        ))

    # Réservoir (sauf forme intégrée déjà posée).
    if forme != "reservoir_integre":
        if vidange == "gravite_point_bas":
            # Cuve minimale de transit, écoulement vers un point bas.
            solides.append(_boite(
                "collecteur_transit", ox - ext_l / 2.0, oy - ext_w / 2.0, z0 + 4.0,
                ext_l, ext_w, max(20.0, ext_h * 0.4), mat, "vidange",
                "Volume de transit seulement (vidange par gravité vers un point bas, pente ≥ %g). "
                "Le rejet bâtiment n'est pas fourni par le meuble : à prévoir à l'installation."
                % pente_min,
                visible=ouvert, demontable=True,
            ))
        else:
            solides.append(_boite(
                "reservoir_amovible", ox - ext_l / 2.0, oy - ext_w / 2.0, z0 + 4.0,
                ext_l, ext_w, ext_h, mat, "reservoir",
                "Réservoir amovible, volume utile %g mL, cuve %.0f mL (coef anti-débordement %g). "
                "Démontable pour vidange et lavage. Intérieur non poreux, rayons ≥ %g mm."
                % (v_utile, v_tot, p.get("collecteur_urine.coefficient_anti_debordement"), rmin),
                visible=ouvert, demontable=True,
            ))

    if p.get("collecteur_urine.couvercle"):
        solides.append(_boite(
            "couvercle", ox - ext_l / 2.0, oy - ext_w / 2.0,
            z0 + 4.0 + (ext_h if forme != "reservoir_integre" else ext_h + 20.0),
            ext_l, ext_w, 3.0, mat, "reservoir",
            "Couvercle (limitation des odeurs et des éclaboussures). Joint %s." % joint,
            visible=ouvert, demontable=True,
        ))
        solides.append(_boite(
            "joint_couvercle", ox - ext_l / 2.0 + 3.0, oy - ext_w / 2.0 + 3.0,
            z0 + 3.0 + (ext_h if forme != "reservoir_integre" else ext_h + 20.0),
            ext_l - 6.0, ext_w - 6.0, 2.0, joint, "joint",
            "Joint plat %s (urée / ammoniac / désinfectants : voir catalogues.materiaux.JOINTS)."
            % joint,
            visible=ouvert, demontable=True,
        ))

    if p.get("collecteur_urine.siphon") and vidange != "gravite_point_bas":
        garde = p.get("collecteur_urine.siphon_garde_eau")
        solides.append(_cylindre(
            "siphon_garde_eau", (ox + ext_l / 2.0 - 18.0, oy, z0 + 4.0),
            "z", 28.0, garde + 16.0, mat, "siphon",
            "Siphon / garde d'eau %g mm (odeurs). Rincable, démontable, sans recoin anguleux."
            % garde,
            visible=ouvert, demontable=True,
        ))

    if vidange == "raccord_npt" or (vidange == "reservoir_amovible"):
        # NPT optionnel en fond : toujours dessiné en option sur le réservoir amovible,
        # obligatoire si le mode est raccord_npt. Bouchon à l'état stocké.
        d_npt = p.get("npt_1.diametre_exterieur")
        l_npt = p.get("npt_1.depassement_recommande")
        obligatoire = vidange == "raccord_npt"
        solides.append(_cylindre(
            "raccord_vidange_npt", (ox, oy, z0 + 4.0 - l_npt + 4.0),
            "z", d_npt + 8.0, l_npt, mat, "vidange",
            ("Raccord de vidange 1\" NPT femelle en fond (ASME B1.20.1, Ø ext. %g mm). "
             % d_npt)
            + ("Mode choisi : raccord_npt." if obligatoire else
               "Option sur réservoir amovible (bouchon possible) ; le défaut reste la cuve ôtée."),
            visible=ouvert, demontable=True,
        ))

    if vidange == "gravite_point_bas":
        long_tuy = cais_l / 2.0 + 40.0
        drop = pente_min * long_tuy
        solides.append(_cylindre(
            "tuyau_point_bas", (ox, oy, z0 + 10.0),
            "x", 20.0, long_tuy, mat, "vidange",
            "Conduite de gravité vers un point bas (pente ≥ %g, dénivelé %g mm sur %g mm). "
            "Le rejet n'est pas un équipement du meuble."
            % (pente_min, drop, long_tuy),
            visible=ouvert, demontable=True,
        ))

    verifs = _verifications(p, dim, impl, solides, forme, vidange, etat, pente_reelle)
    notes = list(impl["notes"])
    notes.extend([
        "Forme %s, vidange %s (recommandation par défaut : réservoir amovible, paramétrable), "
        "déploiement %s, état %s."
        % (forme, vidange, deploiement, "déployé" if ouvert else "fermé"),
        "Volume utile %g mL (ordre de grandeur sourcé : miction typique 200–300 / 350 mL, "
        "première miction 300–400 mL, capacité souvent 400–600 / ≈ 500 mL — UnityPoint, "
        "StatPearls NBK562181, Kettering). Coefficient anti-débordement %g → cuve %.0f mL."
        % (v_utile, p.get("collecteur_urine.coefficient_anti_debordement"), v_tot),
        "Hygiène : matériau %s (non poreux, rincable), joint %s, rayons ≥ %g mm, "
        "pente ≥ %g, pas de recoin, pièces démontables."
        % (mat, joint, rmin, pente_min),
        "Cuir et sangle : habillage hors zone humide seulement.",
        "Vac-U-Lock : non utilisé comme raccord de fluide. 1\" NPT : option de fond / mode dédié.",
        "Arbitrage discrétion / volume / vidange : un grand réservoir grossit le caisson et "
        "rend le voile plus visible à l'ouverture ; le tiroir court et le volume 500 mL "
        "restent dans une emprise raisonnable sous le meuble. La gravité simplifie la vidange "
        "mais exige un rejet. Voir comparaison_vidanges() et docs/.",
    ])
    notes.extend(impl.get("todos") or [])

    return {
        "params": p,
        "gamme": gamme,
        "typologie": impl.get("typologie"),
        "forme": forme,
        "vidange": vidange,
        "deploiement": deploiement,
        "etat_deploiement": etat,
        "volume_utile_ml": v_utile,
        "volume_total_ml": v_tot,
        "dimensions_reservoir": dim,
        "implantation": impl,
        "pente_reelle": pente_reelle,
        "solides": solides,
        "verifications": verifs,
        "notes": notes,
        "comparaison_vidanges": comparaison_vidanges(),
        "arbitrage": next(
            (r for r in arbitrages_par_typologie() if r["typologie"] == typologie and r["gamme"] == (
                "aboutissants" if typologie == "sex_machine_mecanique" else gamme
            )),
            None,
        ),
        "modification_meuble": False,
    }


def rapport_texte(res):
    lignes = [
        "Collecteur d'urine — Aboutissants",
        "Gamme %s, forme %s, vidange %s, déploiement %s, état %s."
        % (res["gamme"], res["forme"], res["vidange"], res["deploiement"],
           "déployé" if res["etat_deploiement"] else "fermé"),
        "Volume utile %.0f mL / cuve %.0f mL. Pente réelle %.3f."
        % (res["volume_utile_ml"], res["volume_total_ml"], res["pente_reelle"]),
        "Solides (%d) :" % len(res["solides"]),
    ]
    for s in res["solides"]:
        lignes.append(
            "  - %s [%s] visible=%s démontable=%s — %s"
            % (s["nom"], s["role"], s.get("visible"), s.get("demontable"), s.get("note") or "")
        )
    lignes.append("Vérifications :")
    for v in res["verifications"]:
        lignes.append("  [%s] %s — %s" % ("ok" if v["ok"] else "KO", v["nom"], v["message"]))
    lignes.append("Notes :")
    lignes.extend("  - %s" % n for n in res["notes"])
    return "\n".join(lignes)


def construire_fusion(design, res, nom_composant="Aboutissants_collecteur_urine"):
    import adsk.core
    import adsk.fusion
    crees, maj = res["params"].exporter_user_parameters(design)
    racine = design.rootComponent
    comp = FU.nouveau_composant(adsk.core, racine, nom_composant)
    n = 0
    for s in res["solides"]:
        if s["type"] == "boite":
            o, d = s["origine"], s["dimensions"]
            corps = FU.ajouter_boite(comp, adsk.core, adsk.fusion, s["nom"], o, d[0], d[1], d[2])
        else:
            d, L = s["diametre"], s["longueur"]
            b, ax = s["base"], s["axe"]
            if ax == "z":
                corps = FU.ajouter_boite(comp, adsk.core, adsk.fusion, s["nom"],
                                         (b[0] - d / 2, b[1] - d / 2, b[2]), d, d, L)
            elif ax == "y":
                corps = FU.ajouter_boite(comp, adsk.core, adsk.fusion, s["nom"],
                                         (b[0] - d / 2, b[1], b[2] - d / 2), d, L, d)
            else:
                corps = FU.ajouter_boite(comp, adsk.core, adsk.fusion, s["nom"],
                                         (b[0], b[1] - d / 2, b[2] - d / 2), L, d, d)
        if corps is not None:
            n += 1
    return {"composant": comp, "nb_corps": n, "user_params_crees": crees, "user_params_maj": maj}


def run(context):
    import adsk.core
    import adsk.fusion
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Aboutissants : ouvrir un design avant de lancer le collecteur d'urine.")
            return None
        res = calculer_collecteur()
        info = construire_fusion(design, res)
        ui.messageBox(
            "Collecteur d'urine : %d corps, forme %s, vidange %s, état %s."
            % (info["nb_corps"], res["forme"], res["vidange"],
               "déployé" if res["etat_deploiement"] else "fermé")
        )
        return res, info
    except Exception:
        ui.messageBox("Aboutissants — erreur :\n%s" % traceback.format_exc())
        return None


if __name__ == "__main__":
    print(rapport_texte(calculer_collecteur()))
