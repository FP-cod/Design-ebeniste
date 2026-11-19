# -*- coding: utf-8 -*-
"""Grammaire couche 3 — port Vac-U-Lock réutilisable.

Le port est un ergot (plug) mâle destiné à recevoir n'importe quel accessoire
compatible Vac-U-Lock du marché (cavité en base). Il s'ajoute aux fixations
existantes (filetage 1\" NPT, points d'ancrage) sans les remplacer et sans
modifier les meubles Equinox / Néogothique / Incognito.

Géométrie : enveloppe de révolution calée sur les cotes *sourcées*
(longueur 3 in, tête 1,25 in, tige 0,75 in). Le profil intermédiaire
(« balle » à deux épaulements, flancs paraboliques) n'est pas chiffré
dans les sources : il n'est pas inventé ici. Un prototype doit être
calé sur une pièce commerciale.

Verrouillage complémentaire par défaut : collier de serrage (désactivable),
seul mode compatible avec des accessoires du marché non percés.

Point d'entrée Fusion : ``run(context)``. Fonction appelable :
``calculer_port`` / ``adapter_sur_tige`` / ``adaptateur_ancrage``.
"""

from __future__ import annotations

import math
import os
import sys
import traceback

_RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _RACINE not in sys.path:
    sys.path.insert(0, _RACINE)

from common.params_globaux import Parametres, effort_vide_theorique_tete, jeu_radial_variantes
from catalogues.vac_u_lock import (
    rapport_arrachement, compatible_ergot, compatible_cale,
    filetage_cote_machine as fiche_filetage,
)
from common import fusion_utils as FU

# Épaisseur d'épaulement : HYPOTHÈSE d'atelier (collerette_epaisseur = TODO brevet).
EP_EPAULEMENT_ATELIER_MM = 8.0


def _boite(nom, x, y, z, dx, dy, dz, materiau, role, note=""):
    return {
        "type": "boite", "nom": nom,
        "origine": (float(x), float(y), float(z)),
        "dimensions": (float(dx), float(dy), float(dz)),
        "materiau": materiau, "role": role, "note": note,
    }


def _cylindre(nom, base, axe, diametre, longueur, materiau, role, note=""):
    return {
        "type": "cylindre", "nom": nom, "base": tuple(float(c) for c in base),
        "axe": axe, "diametre": float(diametre), "longueur": float(longueur),
        "materiau": materiau, "role": role, "note": note,
    }


def profil_enveloppe(params=None):
    """Liste (z_mm, rayon_mm) de l'enveloppe sourcée, origine à la pointe.

    Trois stations seulement, toutes issues de cotes publiées :
    pointe (r=0), tête max, tige max en fin de longueur. Le ventre médian
    n'est pas interpolé comme cote de définition (TODO).
    """
    p = params if isinstance(params, Parametres) else Parametres(params or {})
    L = p.get("vac_u_lock.plug_longueur")
    r_tete = p.get("vac_u_lock.plug_diametre_tete_max") / 2.0
    r_tige = p.get("vac_u_lock.plug_diametre_tige_max") / 2.0
    # Petite zone de nez arrondi : non cotée — on pose un chanfrein d'enveloppe
    # de 4 mm, clairement hors sources (fabrication, pas une cote brevet).
    return {
        "stations": (
            (0.0, 0.0),
            (4.0, r_tete),          # atteinte du Ø tête (longueur du nez NON sourcée)
            (L * 0.5, r_tete),      # maintien du Ø tête jusqu'à mi-longueur : HYPOTHÈSE d'enveloppe
            (L, r_tige),
        ),
        "longueur": L,
        "rayon_tete": r_tete,
        "rayon_tige": r_tige,
        "avertissement": (
            "Enveloppe simplifiée. Le nez de 4 mm et le maintien du Ø tête jusqu'à "
            "mi-longueur ne sont pas dans le brevet (flancs paraboliques, deux "
            "épaulements). Forme étoilée, angle de cône et Ø intermédiaire : TODO, "
            "non cotés — pas inventés. Les deux variantes de tête restent paramétrées ; "
            "un jeu de cales rattrape le jeu. Calibrage sur pièce réelle recommandé."
        ),
    }



def longueur_arriere_hors_ergot(params=None):
    """Longueur derrière la base de l'ergot : épaulement + filetage machine et/ou NPT."""
    p = params if isinstance(params, Parametres) else Parametres(params or {})
    L = EP_EPAULEMENT_ATELIER_MM
    montage = p.get("vac_u_lock.montage_arriere")
    if montage in ("filete_machine", "filete_et_npt"):
        L += p.get("vac_u_lock.filetage_cote_machine_longueur")
    if montage in ("npt_1_femelle", "npt_1_male", "filete_et_npt"):
        L += p.get("npt_1.depassement_recommande")
    return L


def calculer_port(params=None, origine=(0.0, 0.0, 0.0), axe="x",
                  avec_cache=False, prefixe="vul_"):
    """Géométrie du port (ergot + raccord arrière + verrouillage optionnel + cache).

    ``origine`` est le centre de la pointe de l'ergot. L'axe pointe vers
    l'accessoire (l'arrière NPT / collier est du côté négatif).
    """
    p = params if isinstance(params, Parametres) else Parametres(params or {})
    probl = [x for x in p.valider() if x.niveau == "erreur"]
    if probl:
        raise ValueError("Paramètres invalides :\n" + "\n".join(str(e) for e in probl))

    prof = profil_enveloppe(p)
    L = prof["longueur"]
    d_tete = 2.0 * prof["rayon_tete"]
    d_tige = 2.0 * prof["rayon_tige"]
    ox, oy, oz = origine
    mat = "inox_316"
    if not compatible_ergot(mat):
        raise ValueError("matériau d'ergot non admis")

    typ = p.get("vac_u_lock.verrouillage_type")
    actif = bool(p.get("vac_u_lock.verrouillage_actif")) and typ != "aucun"
    montage = p.get("vac_u_lock.montage_arriere")
    etat = int(p.get("vac_u_lock.etat_deploiement") or 0)
    cache_ep = p.get("vac_u_lock.cache_epaisseur")

    def along(s):
        """Point à s mm de la pointe le long de l'axe (s>0 vers l'accessoire? wait)

        Origine = pointe. L'ergot s'étend vers l'arrière (vers la machine),
        l'accessoire s'enfile depuis la pointe. Donc le corps de l'ergot
        occupe s = 0 (pointe) à s = +L (vers l'arrière? ou avant?)

        Convention machine : tige vers +X, accessoire au-delà de la tige
        donc la pointe est au plus loin en +X, l'arrière vers -X depuis la pointe.
        Si origine = pointe, l'ergot va vers -axe.
        """
        if axe == "x":
            return (ox - s, oy, oz)
        if axe == "y":
            return (ox, oy - s, oz)
        return (ox, oy, oz - s)

    solides = []
    # Enveloppe : un cylindre de Ø tête sur L (boîte/cylindre enveloppant).
    # Plus un cylindre de Ø tige pour la partie arrière, même longueur :
    # on expose deux corps « tete » et « tige » pour la lecture, la tige
    # étant l'enveloppe min.
    base_tete = along(0.0)
    # Cylindre : base = début, longueur le long de -axe, donc base at tip
    # and extending toward rear: our _cylindre uses positive length along +axe
    # from base. To extend toward -axe, put base at the rear end.
    arriere = along(L)
    solides.append(_cylindre(
        prefixe + "ergot_enveloppe_tete", arriere, axe, d_tete, L, mat, "ergot",
        "Enveloppe Ø tête %g mm (variante %s), L %g mm. %s"
        % (d_tete, p.get("vac_u_lock.variante_tete"), L, prof["avertissement"]),
    ))
    solides.append(_cylindre(
        prefixe + "ergot_enveloppe_tige", arriere, axe, d_tige, L, mat, "ergot",
        "Enveloppe Ø tige %g mm (0,75 in, brevet). Le profil réel à deux épaulements reste à caler."
        % d_tige,
    ))

    # Épaulement / collerette de butée (épaisseur NON sourcée : 8 mm, hypothèse
    # d'atelier clairement marquée, pas une cote brevet).
    ep_col = EP_EPAULEMENT_ATELIER_MM
    d_col = max(d_tete + 16.0, 50.0)
    base_col = along(L + ep_col)
    solides.append(_cylindre(
        prefixe + "epaulement", base_col, axe, d_col, ep_col, mat, "ergot",
        "Épaulement d'appui de la base de l'accessoire. Épaisseur 8 mm : HYPOTHÈSE d'atelier "
        "(collerette_epaisseur = TODO dans le brevet).",
    ))

    # Filetage côté machine (défaut M8x1.25) et/ou NPT optionnel.
    l_fil = p.get("vac_u_lock.filetage_cote_machine_longueur")
    cle_fil = p.get("vac_u_lock.filetage_cote_machine")
    fiche = fiche_filetage(cle_fil)
    filete = montage in ("filete_machine", "filete_et_npt")
    npt = montage in ("npt_1_femelle", "npt_1_male", "filete_et_npt")
    if filete:
        solides.append(_cylindre(
            prefixe + "filetage_cote_machine", along(L + ep_col + l_fil), axe,
            fiche["diametre_mm"], l_fil, mat, "filetage",
            "Tige filetée côté machine %s (Ø %g mm, pas %g mm, %s). "
            "Relevé vaculocks.com ; défaut M8x1.25 cohérent Equinox. "
            "L'ergot se visse sur la machine (marché), il ne se clipse pas."
            % (cle_fil, fiche["diametre_mm"], fiche.get("pas_mm") or 0.0, fiche["norme"]),
        ))
    l_npt = p.get("npt_1.depassement_recommande")
    d_npt = p.get("npt_1.diametre_exterieur") + 8.0
    if npt:
        decal = (l_fil if filete else 0.0) + l_npt
        solides.append(_cylindre(
            prefixe + "raccord_npt", along(L + ep_col + decal), axe, d_npt, l_npt, mat, "npt",
            "Raccord 1 pouce NPT (%s), Ø ext. nominal filet %g mm, L2=%g mm (ASME B1.20.1). "
            "Interface distincte du Vac-U-Lock et du filetage côté machine."
            % (montage, p.get("npt_1.diametre_exterieur"), p.get("npt_1.longueur_utile_L2")),
        ))

    # Cales d'ajustement (jeu radial entre variantes de tête).
    cales_info = None
    if p.get("vac_u_lock.cales_actives"):
        mat_c = p.get("vac_u_lock.cales_materiau")
        if not compatible_cale(mat_c):
            raise ValueError("matériau de cale non admis : %s" % mat_c)
        ep_c = float(p.get("vac_u_lock.cales_epaisseur_en_place") or 0.0)
        jeu = jeu_radial_variantes(p)
        if ep_c > 0:
            # Manchon autour de la tête (longueur d'enveloppe de tête ~ L/2).
            solides.append(_cylindre(
                prefixe + "cales_ajustement", along(0.0), axe,
                d_tete + 2.0 * ep_c, max(L * 0.5, 8.0), mat_c, "cale",
                "Cales d'ajustement, épaisseur radiale %g mm (jeu typique entre variantes "
                "31,75 / 27,94 mm : %g mm). Jeu d'épaisseurs %s mm, matériau %s "
                "(316L ou polymère non poreux). Elles rattrapent le jeu d'un ergot plus petit "
                "dans une cavité plus grande ; elles ne réduisent pas un ergot trop gros."
                % (ep_c, jeu, p.get("vac_u_lock.cales_epaisseurs"), mat_c),
            ))
        cales_info = {
            "materiau": mat_c,
            "epaisseurs_jeu_mm": list(p.get("vac_u_lock.cales_epaisseurs") or []),
            "epaisseur_en_place_mm": ep_c,
            "jeu_radial_variantes_mm": jeu,
        }

    verrou = None
    if actif and typ == "collier_serrage":
        # Collier en deux demi-coquilles devant l'épaulement, vis M4.
        e_col = 10.0
        base_c = along(L + 0.5)  # juste devant l'épaulement, côté accessoire
        # Pour la géométrie testable : un anneau enveloppant (boîte/cylindre).
        solides.append(_cylindre(
            prefixe + "collier_serrage", along(L + e_col), axe, d_col + 8.0, e_col,
            mat, "verrouillage",
            "Collier de serrage, %s vis %s, appuie la base de l'accessoire contre l'épaulement "
            "sans percer le gode. Désactivable (verrouillage_actif / type aucun)."
            % (p.get("vac_u_lock.collier_nombre_vis"), p.get("vac_u_lock.collier_vis")),
        ))
        verrou = "collier_serrage"
    elif actif and typ == "goupille_transversale":
        solides.append(_cylindre(
            prefixe + "goupille_transversale", along(L * 0.6),
            "y" if axe == "x" else "x", 4.0, d_tete + 16.0, mat, "verrouillage",
            "Goupille transversale : incompatibilité marché (perçage du gode) — option seulement.",
        ))
        verrou = "goupille_transversale"
    elif actif and typ == "bague_baionnette":
        solides.append(_cylindre(
            prefixe + "bague_baionnette", along(L + 12.0), axe, d_col + 6.0, 12.0,
            mat, "verrouillage",
            "Bague à baïonnette sur le port (pas sur le gode du marché).",
        ))
        verrou = "bague_baionnette"

    if avec_cache and etat == 0:
        # Cache / bouchon affleurant qui coiffe l'ergot à l'état fermé.
        solides.append(_cylindre(
            prefixe + "cache_affleurant", along(-2.0), axe, d_col + 4.0,
            L + ep_col + cache_ep, "inox_316", "cache",
            "Cache / bouchon, épaisseur de voile %g mm, invisible à l'état fermé "
            "(convention état_deploiement=0, comme Incognito)."
            % cache_ep,
        ))

    arr = rapport_arrachement(
        d_tete,
        p.get("securite.charge_service_poussee_machine"),
        p.get("securite.coefficient_dynamique"),
        typ if actif else "aucun",
        p.get("vac_u_lock.collier_vis"),
        p.get("vac_u_lock.collier_nombre_vis"),
        p.get("securite.coefficient_ancrage"),
    )

    variante = p.get("vac_u_lock.variante_tete")
    notes = [
        "Interface additivée : Vac-U-Lock (ergot, variante tête %s, Ø %g mm) + arrière %s "
        "(filetage %s) ; ancrages meuble inchangés."
        % (variante, d_tete, montage, cle_fil if filete else "—"),
        "Deux diamètres de tête restent des variantes (brevet 31,75 mm, boutique 27,94 mm) ; "
        "on ne tranche pas. Cales d'ajustement pour le jeu radial typique %.3f mm."
        % (jeu_radial_variantes(p) or 0.0),
        prof["avertissement"],
        "Vide théorique max ≈ %.0f N ; effort de calcul ≈ %.0f N (poussée nominale validée 400 N "
        "× k_dyn 2) ; collier CMU ≈ %.0f N."
        % (arr["vide_theorique_max_N"], arr["effort_calcul_N"], arr["cmu_collier_vis_N"]),
        "Cycles certifiés : TODO (aucune donnée publique). Inspection visuelle à prévoir.",
        "Cavité des accessoires : même forme, légèrement plus petite (interférence = TODO).",
        "Forme étoilée, angle de cône et diamètre intermédiaire : TODO, non cotés par les sources.",
    ]
    return {
        "params": p,
        "profil": prof,
        "origine": origine,
        "axe": axe,
        "longueur_ergot": L,
        "solides": solides,
        "verrouillage": verrou,
        "arrachement": arr,
        "notes": notes,
        "avec_cache": avec_cache and etat == 0,
        "variante_tete": variante,
        "diametre_tete": d_tete,
        "filetage_cote_machine": cle_fil if filete else None,
        "cales": cales_info,
        "todos_geometrie": [
            c for c, _ in p.todos() if c.startswith("vac_u_lock.")
        ],
    }


def adapter_sur_tige(params, origine_pointe, axe="x", prefixe="vul_"):
    """Port en bout de tige (machine) : pas de cache, verrouillage selon paramètres."""
    return calculer_port(params, origine=origine_pointe, axe=axe, avec_cache=False, prefixe=prefixe)


def adaptateur_ancrage(gamme, params=None, prefixe=None):
    """Port discret rapporté sur un ancrage *existant*, sans modifier le meuble.

    ``gamme`` : 'equinox' | 'neogothique' | 'incognito' | 'tantra' | 'rangement'.
    Le module se bride / s'adapte ; les cotes d'ancrage manquantes restent TODO.
    """
    p = params if isinstance(params, Parametres) else Parametres(params or {})
    prefixe = prefixe or ("vul_%s_" % gamme)
    solides = []
    notes = []
    jonctions = []
    etat = int(p.get("vac_u_lock.etat_deploiement") or 0)

    if gamme == "equinox":
        # Bride sur l'anneau DI 40 (préféré) — même principe que la machine.
        di = p.get("ancrages.equinox.diametre_interieur_anneau")
        fil = p.get("ancrages.equinox.diametre_fil_oeillet")
        z = p.get("ancrages.equinox.hauteur_axe_traverse")
        axe_b = p.get("mouvement.bride_diametre_axe_anneau")
        solides.append(_boite(
            prefixe + "chape_anneau", -12.0, -20.0, z - 20.0, 24.0, 40.0, 40.0,
            "inox_316", "adaptateur",
            "Chape sur anneau Equinox existant (DI %g, fil Ø%g), sans percage du meuble. "
            "Hauteur d'axe traverse typique %g mm (banc Flore)."
            % (di, fil, z),
        ))
        solides.append(_cylindre(
            prefixe + "axe_chape", (0.0, -25.0, z), "y", axe_b, 50.0,
            "inox_316", "adaptateur", "Axe Ø%g dans l'anneau DI %g." % (axe_b, di),
        ))
        jonctions.append({
            "type": "chape_axe", "cible": "anneau_equinox",
            "modification_meuble": False,
            "di_mm": di, "filetage_serrage": "M8",
        })
        notes.append("Equinox : accroche préférée = anneau DI 40, pas l'œillet bas DI 12.")
        # Port au-dessus de la chape, pointe vers +Z (usage typique) ou +X.
        origine = (40.0, 0.0, z)
        port = calculer_port(p, origine=origine, axe="x", avec_cache=True, prefixe=prefixe)
        solides.extend(port["solides"])
        notes.extend(port["notes"])
        return {**port, "solides": solides, "jonctions": jonctions, "notes": notes, "gamme": gamme}

    if gamme == "incognito":
        d_ins = p.get("ancrages.incognito.diametre_insert")
        filetage = p.get("ancrages.incognito.filetage")  # None, TODO
        recouv = p.get("ancrages.incognito.recouvrement")
        notes.append(
            "Incognito : insert noyé Ø%g mm, filetage %s (TODO). L'adaptateur se visse ou se clippe "
            "dans l'orifice existant au déploiement, cache affleurant de %g mm à l'état fermé. "
            "Aucune pièce visible fermée (règle de gamme)."
            % (d_ins, filetage, recouv)
        )
        # Cavalier / douille Ø12, sans modifier l'insert.
        solides.append(_cylindre(
            prefixe + "douille_insert", (0.0, 0.0, 0.0), "z", d_ins, 20.0,
            "inox_316", "adaptateur",
            "Douille d'adaptation sur insert Ø12. Filetage de l'insert inconnu : "
            "la douille devra être calée (axe lisse + frein, ou filetage une fois relevé). "
            "Ne perce pas le meuble.",
        ))
        jonctions.append({
            "type": "douille_insert", "cible": "insert_incognito_o12",
            "modification_meuble": False,
            "diametre_insert_mm": d_ins, "filetage": filetage,
        })
        port = calculer_port(p, origine=(0.0, 0.0, 30.0), axe="z", avec_cache=True, prefixe=prefixe)
        solides.extend(port["solides"])
        return {**port, "solides": solides, "jonctions": jonctions, "notes": notes + port["notes"], "gamme": gamme}

    if gamme == "neogothique":
        cote = p.get("ancrages.neogothique.plaque_cote")
        ep = p.get("ancrages.neogothique.plaque_epaisseur")
        cap = p.get("ancrages.neogothique.capacite_point")
        filetage = p.get("ancrages.neogothique.filetage")
        di = p.get("ancrages.neogothique.diametre_interieur_anneau")
        notes.append(
            "Néogothique : plaque 40×40×6 seulement dans la grammaire. Filetage=%s, DI anneau=%s (TODO). "
            "L'adaptateur est une bride de plaque (serre les 40 mm), sans percage. "
            "Passage d'un axe d'œil non garanti tant que le DI n'est pas coté."
            % (filetage, di)
        )
        solides.append(_boite(
            prefixe + "bride_plaque", -cote / 2.0 - 4.0, -cote / 2.0 - 4.0, 0.0,
            cote + 8.0, cote + 8.0, ep + 8.0,
            "inox_316", "adaptateur",
            "Bride enserrant la plaque d'ancrage %g×%g×%g mm, capacité catalogue %g N. "
            "Pas de modification de la plaque."
            % (cote, cote, ep, cap),
        ))
        jonctions.append({
            "type": "bride_plaque", "cible": "plaque_ancrage_sol_neogothique",
            "modification_meuble": False,
            "plaque_mm": (cote, cote, ep), "filetage": filetage, "di_anneau": di,
        })
        port = calculer_port(p, origine=(0.0, 0.0, ep + 20.0), axe="z", avec_cache=True, prefixe=prefixe)
        solides.extend(port["solides"])
        return {**port, "solides": solides, "jonctions": jonctions, "notes": notes + port["notes"], "gamme": gamme}

    if gamme == "tantra":
        d_ins = p.get("ancrages.tantra.diametre_insert")
        filetage = p.get("ancrages.tantra.filetage")
        l_ef = p.get("ancrages.tantra.longueur_encastrement")
        di = p.get("ancrages.tantra.diametre_interieur_anneau")
        recouv = p.get("ancrages.tantra.retrait_ancre_sous_surface")
        notes.append(
            "Tantra : insert M12 (Ø ext. %g mm, encastrement %g mm, filetage %s). "
            "L'adaptateur se visse dans l'insert existant ou se bride sur l'anneau rabattable / "
            "à épaulement, sans perçage. DI d'anneau = %s (TODO) : passage d'axe non garanti. "
            "Filetage M12 ≠ interface M8 Aboutissants : bague / réducteur à spécifier. "
            "Volet camouflable : cache affleurant (%g mm) à l'état SALON ; port visible en RÉVÉLÉ seulement."
            % (d_ins, l_ef, filetage, di, recouv)
        )
        solides.append(_cylindre(
            prefixe + "douille_insert_m12", (0.0, 0.0, 0.0), "z", d_ins, 20.0,
            "inox_316", "adaptateur",
            "Douille d'adaptation sur insert Ø16 / filetage M12. Ne perce pas le meuble. "
            "Réduction M12→M8 ou chape d'anneau à caler une fois le DI relevé.",
        ))
        jonctions.append({
            "type": "douille_insert", "cible": "insert_tantra_m12",
            "modification_meuble": False,
            "diametre_insert_mm": d_ins, "filetage": filetage,
            "diametre_interieur_anneau": di, "longueur_encastrement_mm": l_ef,
        })
        port = calculer_port(p, origine=(0.0, 0.0, 30.0), axe="z", avec_cache=True, prefixe=prefixe)
        solides.extend(port["solides"])
        return {**port, "solides": solides, "jonctions": jonctions, "notes": notes + port["notes"], "gamme": gamme}

    if gamme == "rangement":
        # Le râtelier a des ports natifs : l'adaptateur rappelle cette voie, sans modifier le meuble.
        filetage = p.get("ancrages.rangement.filetage_insert")
        pas = p.get("ancrages.rangement.pas_ports")
        h_ports = p.get("ancrages.rangement.hauteur_ports")
        plot_l = p.get("ancrages.rangement.plot_largeur")
        plot_p = p.get("ancrages.rangement.plot_profondeur")
        n_ports = p.get("ancrages.rangement.ports_par_module")
        montage = p.get("ancrages.rangement.montage_arriere_defaut")
        systeme = p.get("ancrages.rangement.systeme_port_defaut")
        notes.append(
            "Rangement : ports Vac-U-Lock / douilles 1\" NPT *natifs* sur le râtelier mural "
            "(%s ports/module, entraxe %g mm, axe à %g mm du bas de panneau, plot %g×%g mm, "
            "système %s, montage arrière %s). On n'ajoute pas un port sur un crochet ou une barre : "
            "ce ne sont pas des ancrages de personne. /workspace/rangement n'est pas modifié. "
            "Typologies coffre / armoires : grammaire de ports non livrée."
            % (n_ports, pas, h_ports, plot_l, plot_p, systeme, montage)
        )
        # Repère d'un port typique (premier module, premier port), ergot selon défaut NPT mâle.
        origine = (0.0, plot_p, 0.0)
        jonctions.append({
            "type": "port_natif", "cible": "port_rangement_ratelier",
            "modification_meuble": False,
            "filetage_insert": filetage,
            "systeme": systeme,
            "montage_arriere": montage,
            "plot_mm": (plot_l, plot_p, plot_l),
        })
        port = calculer_port(p, origine=origine, axe="y", avec_cache=False, prefixe=prefixe)
        solides.extend(port["solides"])
        return {**port, "solides": solides, "jonctions": jonctions, "notes": notes + port["notes"], "gamme": gamme}

    raise ValueError("gamme inconnue : %s" % gamme)


def rapport_texte(res):
    lignes = ["Port Vac-U-Lock — Aboutissants",
              "L=%g mm, Ø tête=%g mm, Ø tige=%g mm, verrouillage=%s"
              % (res["longueur_ergot"], 2 * res["profil"]["rayon_tete"],
                 2 * res["profil"]["rayon_tige"], res["verrouillage"])]
    a = res["arrachement"]
    lignes.append("Arrachement : vide max %.0f N, Fcalc %.0f N, CMU collier %.0f N, cycles=%s"
                  % (a["vide_theorique_max_N"], a["effort_calcul_N"], a["cmu_collier_vis_N"],
                     a["cycles_certifies"]))
    lignes.append("Solides (%d) :" % len(res["solides"]))
    for s in res["solides"]:
        lignes.append("  - %s [%s] %s" % (s["nom"], s["role"], s.get("note") or ""))
    if res.get("jonctions"):
        lignes.append("Jonctions :")
        for j in res["jonctions"]:
            lignes.append("  - %s" % j)
    lignes.append("Notes :")
    lignes.extend("  - %s" % n for n in res["notes"])
    return "\n".join(lignes)


def construire_fusion(design, res, nom_composant="Aboutissants_port_vac_u_lock"):
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
            ui.messageBox("Aboutissants : ouvrir un design avant de lancer le port Vac-U-Lock.")
            return None
        res = calculer_port()
        info = construire_fusion(design, res)
        ui.messageBox("Port Vac-U-Lock : %d corps, verrouillage %s."
                      % (info["nb_corps"], res["verrouillage"]))
        return res, info
    except Exception:
        ui.messageBox("Aboutissants — erreur :\n%s" % traceback.format_exc())
        return None


if __name__ == "__main__":
    print(rapport_texte(calculer_port()))
