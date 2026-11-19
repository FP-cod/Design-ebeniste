# -*- coding: utf-8 -*-
"""Couche 2 — matrices de compatibilité Aboutissants × gammes de meubles.

Les dépôts Equinox, Néogothique, Incognito, Tantra et Rangement ont été
inspectés **sans modification**. Les statuts ne tranchent que ce que les
scripts documentent ; tout le reste est signalé comme limite, TODO ou
décision à soumettre.
"""

from __future__ import annotations

# Aligné sur common.params_globaux.GAMMES_ANCRAGES.
GAMMES = ("equinox", "neogothique", "incognito", "tantra", "rangement")

INTERFACES = (
    "interface_oeillet_m8",
    "port_vac_u_lock",
    "collecteur_urine",
    "npt_1",
    "sex_machine_mecanique",
)

STATUTS = ("compatible", "compatible_adaptateur", "limite", "incompatible", "a_venir")

LEGENDE = {
    "compatible": "Usage prévu, sans adapter ni modifier le meuble.",
    "compatible_adaptateur": "Usage prévu via un adaptateur rapporté, sans modifier le meuble.",
    "limite": "Possible sous conditions (support, discrétion, géométrie, typologie) ou partiellement adapté.",
    "incompatible": "Ne pas combiner (raison structurelle, de typologie ou d'emploi).",
    "a_venir": "Accessoire ou implantation non encore grammatisée ; le point d'accroche peut exister.",
}

NOMS_GAMMES = {
    "equinox": "Equinox",
    "neogothique": "Néogothique",
    "incognito": "Incognito (hors pouf)",
    "tantra": "Tantra",
    "rangement": "Rangement",
}


def cell(statut, note, decision_fabien=False):
    if statut not in STATUTS:
        raise ValueError("statut inconnu : %s" % statut)
    return {"statut": statut, "note": note, "decision_fabien": bool(decision_fabien)}


def matrice_interfaces_gammes():
    """Matrice interfaces Aboutissants (œillet M8, Vac-U-Lock, collecteur, NPT, machine) × gammes."""
    m = {
        "interface_oeillet_m8": {
            "equinox": cell(
                "compatible",
                "Interface déduite d'Equinox : inserts M8, œillets fil Ø8 / DI 12, anneau DI 40, "
                "tige M8 traversante. Accroche par bride / chape sur un œillet ou un anneau déjà présent, "
                "sans percer le meuble.",
            ),
            "neogothique": cell(
                "limite",
                "Plaques 40×40×6 seulement. Filetage et DI d'anneau : TODO. Une bride de plaque est "
                "possible sans perçage, mais le passage d'un axe M8 n'est pas garanti.",
            ),
            "incognito": cell(
                "limite",
                "Insert noyé Ø12, filetage non documenté, pas d'œillet apparent. L'interface M8 n'est "
                "pas déduite d'Incognito. Adaptateur uniquement à l'état déployé ; rien de visible fermé.",
            ),
            "tantra": cell(
                "compatible_adaptateur",
                "Insert d'ancre M12 (Ø ext. 16, encastrement 60 mm, charge de service 1500 N, CS 3) "
                "et anneau rabattable (cuvette Ø50 × 12 mm) ou anneau à épaulement vissé à l'usage. "
                "Le filetage M12 n'est pas l'interface M8 Aboutissants : il faut un adaptateur M12↔M8 "
                "ou une chape calée sur l'anneau. Le DI et le fil de l'anneau ne sont pas cotés (TODO) : "
                "le passage d'un axe de bride n'est pas garanti. Volet camouflable : accessoires visibles "
                "uniquement à l'état RÉVÉLÉ (caches aimantés, manchettes, bavette). Décision : adapter "
                "en M12 ou conserver M8 côté accessoire.",
                decision_fabien=True,
            ),
            "rangement": cell(
                "incompatible",
                "Les inserts M8 existent (crochets, consoles, ports filetés, CMU catalogue 2500 N) et "
                "sont géométriquement au pas M8, mais « un râtelier n'est PAS un point d'ancrage de "
                "personne » (charges.effort_accidentel). Ne pas y brider une retenue, une machine ou "
                "un cadre comme on le ferait sur un œillet Equinox. Les inserts restent utilisables "
                "pour les accessoires de rangement et les ports Vac-U-Lock filetés.",
            ),
        },
        "port_vac_u_lock": {
            "equinox": cell(
                "compatible_adaptateur",
                "Pas de port natif. Adaptateur rapporté : chape sur l'anneau DI 40 (préféré à l'œillet "
                "bas DI 12), sans modifier le meuble.",
            ),
            "neogothique": cell(
                "compatible_adaptateur",
                "Pas de port natif. Bride sur plaque 40×40×6, filetage et DI d'anneau TODO, sans perçage.",
            ),
            "incognito": cell(
                "compatible_adaptateur",
                "Pas de port natif sur les inserts Ø12 (le NPT Incognito est côté housses / actionneur). "
                "Douille rapportée sur l'insert au déploiement, cache affleurant fermé ; filetage TODO.",
            ),
            "tantra": cell(
                "limite",
                "Aucun port Vac-U-Lock dans les scripts. On peut concevoir un adaptateur rapporté sur "
                "l'insert M12 (sans modifier le meuble), sous réserve du DI d'anneau (TODO) et d'une "
                "décision M12↔M8. Aucun emplacement n'est réservé. Sur le volet camouflable, seulement "
                "à l'état RÉVÉLÉ. Ajout rétroactif d'un port natif : décision, les dépôts Tantra ne "
                "sont pas modifiés.",
                decision_fabien=True,
            ),
            "rangement": cell(
                "compatible",
                "Ports natifs sur le râtelier mural (grammaire livrée) : 2 ports par module, entraxe "
                "200 mm, axe à 130 mm du bas de panneau (pose typ. 900 mm). Systèmes : port_vac_u_lock_npt "
                "(défaut, ergot à arrière npt_1_male dans une douille femelle, plot 70×40 mm), "
                "port_vac_u_lock_m8 (tige M8x1.25 × 16 dans un insert M8, CMU 2500 N), "
                "port_npt_1_femelle, port_cache_affleurant (cache 10 mm). Montage arrière par défaut "
                "npt_1_male à trancher vs filete_machine Aboutissants. Les typologies coffre / armoires "
                "n'ont pas encore de grammaire de ports.",
                decision_fabien=True,
            ),
        },
        "collecteur_urine": {
            "equinox": cell(
                "compatible",
                "Caisson rapporté à l'arrière / sous le meuble, près des ancrages déjà relevés, sans perçage. "
                "Voir arbitrages par typologie (banc, tabouret, chaise, croix, cheval d'arçon).",
            ),
            "neogothique": cell(
                "compatible",
                "Caisson dans le rectangle des plaques 40×40×6, sans les recouvrir, sans perçage.",
            ),
            "incognito": cell(
                "limite",
                "Hors pouf. Rien de visible fermé. Place juste sous la banquette (pieds typ. 120 mm). "
                "Typologies salon non livrées : implantation TODO.",
            ),
            "tantra": cell(
                "limite",
                "Aucun emplacement de collecteur n'est coté (TODO). Les typologies à assise ou "
                "agenouilloir livrées (chaise double courbe, fauteuil lombaire, banquette deux niveaux, "
                "siège repose-genoux, canapé / fauteuil camouflables, desserte-cadre) peuvent recevoir "
                "un caisson rapporté sous / derrière, sans modifier le meuble et sans NPT de vidange "
                "natif. Volet camouflable : déploiement discret seulement, rien de visible en SALON. "
                "La table inclinée n'a pas de grammaire ; la personne y serait au sol (peu naturel).",
            ),
            "rangement": cell(
                "incompatible",
                "Le râtelier mural n'a pas d'assise ni d'emplacement de collecte. Un caisson indépendant "
                "au sol à proximité n'est plus un aboutissant du râtelier. Coffre / armoires : grammaires "
                "non livrées, aucun volume de collecte coté (TODO) — ne pas inventer d'implantation.",
            ),
        },
        "npt_1": {
            "equinox": cell(
                "incompatible",
                "Absent des scripts. Pas d'ajout rétroactif (décision déjà posée). Un NPT peut exister "
                "sur l'aboutissant (machine, collecteur) sans transiter par le meuble.",
            ),
            "neogothique": cell(
                "incompatible",
                "Absent des scripts. Même logique : pas d'ajout rétroactif dans le meuble.",
            ),
            "incognito": cell(
                "compatible",
                "Embout mâle 1\" NPT retenu pour housses / actionneur (pas pour les inserts d'ancrage Ø12).",
            ),
            "tantra": cell(
                "incompatible",
                "Absent des scripts (grep 18 nov. 2026). L'ajout rétroactif d'une douille NPT dans un "
                "meuble Tantra est une décision ; les dépôts ne sont pas modifiés. Un NPT peut exister "
                "sur un aboutissant rapporté (collecteur, port d'adaptateur) sans transiter par le meuble.",
                decision_fabien=True,
            ),
            "rangement": cell(
                "compatible",
                "Douilles 1\" NPT femelles natives (ports.npt = True) : profondeur L4 = 25,006 mm, "
                "Ø ext. 33,401 mm, plots rapportés 70×40 mm, paroi bois mini 12 mm, fond mini 6 mm. "
                "Le système port_npt_1_femelle laisse la douille seule ; port_vac_u_lock_npt y visse "
                "un ergot à arrière mâle (à trancher vs M8 fileté).",
                decision_fabien=True,
            ),
        },
        "sex_machine_mecanique": {
            "equinox": cell(
                "compatible_adaptateur",
                "Machine au sol, bride / chape sur l'anneau DI 40 ou un montant de cadre, sans percer "
                "le meuble. Stabilité déjà juste (800 N à 700 mm) : le châssis reste au sol.",
            ),
            "neogothique": cell(
                "compatible_adaptateur",
                "Idem, bride de plaque possible ; DI d'anneau TODO. Machine au sol, sans perçage.",
            ),
            "incognito": cell(
                "limite",
                "Seulement à l'état déployé, après adaptateur sur insert Ø12 (filetage TODO). "
                "Une machine visible enfreint la discrétion à l'état fermé. Pouf non ciblé.",
            ),
            "tantra": cell(
                "limite",
                "Aucun emplacement machine n'est coté. La machine peut reposer au sol près du meuble "
                "(châssis autonome) ; une liaison éventuelle vers un insert M12 exige un adaptateur "
                "et le DI d'anneau (TODO), filetage M12 ≠ M8. Les ancrages Tantra sont dimensionnés "
                "pour retenir une personne *installée sur le meuble* (effort interne) : une traction "
                "extérieure de 1500 N peut faire basculer le meuble à vide (la grammaire le signale). "
                "Volet camouflable : machine visible incompatible avec l'état SALON.",
                decision_fabien=True,
            ),
            "rangement": cell(
                "incompatible",
                "Un râtelier mural n'est pas un appui de machine (800 N de poussée dynamique, support "
                "mural TODO, et ce n'est pas un point d'ancrage de personne). Cohabitation possible "
                "dans la pièce, sans liaison au râtelier. Coffre / armoires : pas de grammaire, "
                "pas d'emplacement (TODO).",
            ),
        },
    }

    for interface in INTERFACES:
        if interface not in m:
            raise RuntimeError("matrice interfaces incomplète : %s" % interface)
        for g in GAMMES:
            if g not in m[interface]:
                raise RuntimeError("matrice interfaces incomplète : %s × %s" % (interface, g))
    return {
        "interfaces": m,
        "gammes": GAMMES,
        "statuts": STATUTS,
        "legende": dict(LEGENDE),
        "noms_gammes": dict(NOMS_GAMMES),
    }


def decisions_a_trancher():
    """Liste courte des décisions à soumettre (cotes manquantes ou choix d'architecture)."""
    return (
        {
            "id": "tantra_di_fil_anneau",
            "sujet": "Tantra — DI et fil de l'anneau rabattable / à épaulement",
            "question": "Quels diamètre intérieur et Ø de fil retenir ? Sans ces cotes, le passage d'un axe de bride Aboutissants n'est pas garanti.",
        },
        {
            "id": "tantra_m12_vs_m8",
            "sujet": "Tantra — filetage M12 vs interface Aboutissants M8",
            "question": "Faut-il un adaptateur M12↔M8 côté accessoire, produire des brides / anneaux M12, ou conserver deux interfaces ?",
        },
        {
            "id": "tantra_ports_npt_natifs",
            "sujet": "Tantra — ports Vac-U-Lock et douilles NPT natifs",
            "question": "Ajouter rétroactivement des ports / NPT dans les meubles Tantra (les dépôts ne seront pas modifiés ici), ou s'en tenir à des adaptateurs rapportés ?",
        },
        {
            "id": "tantra_collecteur_machine",
            "sujet": "Tantra — emplacements collecteur et machine",
            "question": "Faut-il réserver des cotes d'implantation (sous / derrière les sièges, châssis au sol) ? Aucune n'existe aujourd'hui.",
        },
        {
            "id": "tantra_cadre_table_inclinee",
            "sujet": "Tantra — table basse → cadre incliné",
            "question": "Grammaire non livrée ; la note d'étude exige une fixation murale/sol ou une marche-plateforme. Trancher la suite et les ancrages.",
        },
        {
            "id": "tantra_discretion_camo",
            "sujet": "Tantra volet camouflable — état SALON / RÉVÉLÉ",
            "question": "Confirmer que tout aboutissant visible (machine, port, cadre au sol, anneau déployé) n'est admissible qu'à l'état RÉVÉLÉ, comme la règle Incognito.",
        },
        {
            "id": "rangement_montage_arriere",
            "sujet": "Rangement — montage arrière des ports Vac-U-Lock",
            "question": "Conserver npt_1_male (défaut Rangement, douille NPT interchangeables) ou aligner sur filete_machine M8 (défaut Aboutissants, système port_vac_u_lock_m8) ?",
        },
        {
            "id": "rangement_ancrage_personne",
            "sujet": "Rangement — interdiction d'ancrage de personne",
            "question": "Confirmer qu'on ne bride jamais une retenue, une machine ou un cadre de contention sur les crochets / barres / inserts d'un râtelier, malgré le filetage M8 commun.",
        },
        {
            "id": "rangement_caissons",
            "sujet": "Rangement — coffre et armoires",
            "question": "Grammaires non livrées : faut-il y prévoir des ports, un collecteur (coffre-banc) ou une capacité d'ancrage ? Rien n'est coté aujourd'hui.",
        },
        {
            "id": "rangement_support_mur",
            "sujet": "Rangement / cadres muraux — capacité du support de bâtiment",
            "question": "pose.capacite_support_mur reste TODO (None). Relevé sur place obligatoire avant tout usage en charge.",
        },
    )


def matrice_markdown():
    """Tableau Markdown interfaces × gammes, pour le rapport."""
    m = matrice_interfaces_gammes()
    gammes = m["gammes"]
    lignes = [
        "### Aboutissants × gammes",
        "",
        "| Interface | " + " | ".join(NOMS_GAMMES[g] for g in gammes) + " |",
        "|" + "---|" * (1 + len(gammes)),
    ]
    for interface in INTERFACES:
        cells = [interface]
        for g in gammes:
            c = m["interfaces"][interface][g]
            suffix = " *(décision)*" if c["decision_fabien"] else ""
            cells.append("**%s**%s — %s" % (c["statut"], suffix, c["note"]))
        lignes.append("| " + " | ".join(cells) + " |")
    return "\n".join(lignes)
