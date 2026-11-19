# -*- coding: utf-8 -*-
"""Grammaire du pouf vibrant Incognito.

Pouf de salon classique (coussin amovible, tissu de façade, tourillons
et mortaises) intégrant un module de selle, pour adultes consentants.

Deux états, calculés à partir des **mêmes** paramètres de base :

* ``Etat.POUF`` (0) : coussin en place, capuchon sur le filetage, module inactif ;
* ``Etat.MODULE`` (1) : coussin retiré, selle / embout 1" NPT accessibles.

Deux niveaux de gamme (``ParametresSybian.gamme`` / ``inc_sybian_gamme``) :

* ``entree`` : moteur à balourd 24 V sous carter mousse, silentblocs caoutchouc ;
* ``haut`` : jusqu'à trois modules activables — vibration (voice coil
  VCAR0105, 105 N, 16 mm), piston (VCAR0110, 110 N, 38 mm), rotation
  (EC 45 flat + réducteur, roulement de butée). Architecture retenue :
  ``parallele_decouple`` (piston en retrait, voice coil en haut sous la
  selle). L'empilement série (voice coil en bas qui porte tout) est
  calculé pour mémoire et signalé hors capacité / hors gabarit.

Sécurité commune : 24 V DC, alim. certifiée hors meuble, rampe, arrêt
d'urgence physique câblé (indépendant de l'ESP32), présence par
cellules Wheatstone, limitation, protection thermique, carter des
pièces tournantes, selle lavable non poreuse, ventilation discrète.
Pilotage : ESP32 BLE + Wi-Fi (remplace télécommande et pédale).

Module Python pur, testable hors Fusion.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from incognito.catalogues.essences import essence_par_nom
from incognito.catalogues.housses import (
    FILETAGE_1_NPT,
    MASSE_HOUSSE_DEFAUT_KG,
    masse_embout_kg,
)
from incognito.catalogues.moteurs import (
    ROTATION_EC45,
    budget_electrique_haut,
    variante_par_gamme,
)
from incognito.catalogues.mousses import MOUSSE_COUSSIN_SALON, MOUSSE_DENSES_CARTER
from incognito.parametres import (
    CHENE,
    CUIR_COGNAC,
    DISCRETION_DEFAUT,
    GAMME_SYBIAN_ENTREE,
    GAMME_SYBIAN_HAUT,
    NIVEAU_AVERTISSEMENT,
    NIVEAU_ESSAI_REQUIS,
    NIVEAU_NON_CONFORME,
    NIVEAU_OK,
    POUF,
    Essence,
    ParametresCharge,
    ParametresDiscretion,
    ParametresGlobaux,
    ParametresSybian,
    Revetement,
    VELOURS,
    CHARGES_DEFAUT,
)
from incognito.catalogues.electronique import (
    ESP32_S3_WROOM1,
    CELLULE_50KG,
)
from incognito.presence import frequence_coupure_presence_hz
from incognito.regles import (
    ARCHITECTURE_PARALLELE,
    ARCHITECTURE_SERIE,
    CS_SILENTBLOC_MIN,
    JEU_DEBATTEMENT_MIN_MM,
    MASSE_HOUSSE_DIMENSIONNEMENT_MAX_KG,
    MASSE_HOUSSE_DIMENSIONNEMENT_MIN_KG,
    analyser_masses_empilement,
    encombrement_vertical_haut,
    recaler_module_vibrant,
    comparer_treillis_et_silentbloc,
)


class Etat(IntEnum):
    """État géométrique du pouf."""

    POUF = 0
    MODULE = 1


@dataclass(frozen=True)
class ParametresPoufVibrant:
    """Paramètres de base, communs aux deux états."""

    largeur: float = 500.0
    profondeur: float = 500.0
    hauteur: float = 430.0
    hauteur_pieds: float = 15.0
    epaisseur_paroi: float = 18.0
    epaisseur_fond: float = 18.0
    epaisseur_couronne: float = 18.0
    epaisseur_coussin: float = 90.0

    gamme: str = GAMME_SYBIAN_HAUT
    architecture: str = ARCHITECTURE_PARALLELE
    module_vibration: bool = True
    module_piston: bool = True
    module_rotation: bool = True
    masse_housse_kg: float = 0.75
    materiau_embout: str = "inox_316"

    tension_v: float = 24.0
    essence: Essence = CHENE
    revetement_exterieur: Revetement = VELOURS
    revetement_selle: Revetement = CUIR_COGNAC
    discretion: ParametresDiscretion = DISCRETION_DEFAUT
    charges: ParametresCharge = CHARGES_DEFAUT

    def __post_init__(self) -> None:
        if self.gamme not in {GAMME_SYBIAN_ENTREE, GAMME_SYBIAN_HAUT}:
            raise ValueError(f"Gamme inconnue : {self.gamme}")
        if self.architecture not in {ARCHITECTURE_PARALLELE, ARCHITECTURE_SERIE}:
            raise ValueError(f"Architecture inconnue : {self.architecture}")
        if self.masse_housse_kg < 0:
            raise ValueError("masse_housse_kg doit être ≥ 0.")
        if self.tension_v > 48.0:
            raise ValueError("Aucun 230 V dans le meuble.")
        if self.gamme == GAMME_SYBIAN_ENTREE:
            # L'entrée n'a pas les trois étages : le balourd suffit.
            pass

    @property
    def modules_actifs_haut(self) -> tuple[str, ...]:
        if self.gamme != GAMME_SYBIAN_HAUT:
            return ()
        noms = []
        if self.module_vibration:
            noms.append("vibration")
        if self.module_piston:
            noms.append("piston")
        if self.module_rotation:
            noms.append("rotation")
        return tuple(noms)


def parametres_pouf_defaut(
    globaux: ParametresGlobaux | None = None,
    **override: object,
) -> ParametresPoufVibrant:
    """Construit les paramètres depuis la typologie pouf et les globaux."""
    typo = POUF
    globaux = globaux or ParametresGlobaux()
    valeurs: dict = dict(
        largeur=typo.cote("largeur").valeur,
        profondeur=typo.cote("profondeur").valeur,
        hauteur=typo.cote("hauteur").valeur,
        gamme=globaux.sybian.gamme,
        tension_v=globaux.sybian.tension_v,
        essence=globaux.essence,
        revetement_exterieur=globaux.revetement_exterieur,
        discretion=globaux.discretion,
        charges=globaux.charges,
    )
    valeurs.update(override)
    return ParametresPoufVibrant(**valeurs)  # type: ignore[arg-type]


@dataclass(frozen=True)
class Boite:
    """Boîte alignée sur les axes, en mm."""

    x: float
    y: float
    z: float
    dx: float
    dy: float
    dz: float

    @property
    def centre(self) -> tuple[float, float, float]:
        return (self.x + self.dx / 2.0, self.y + self.dy / 2.0, self.z + self.dz / 2.0)

    def volume_m3(self) -> float:
        return max(0.0, self.dx) * max(0.0, self.dy) * max(0.0, self.dz) / 1e9

    def rentre_dans(self, contenant: "Boite", jeu: float = 0.0) -> bool:
        return (
            self.dx + jeu <= contenant.dx
            and self.dy + jeu <= contenant.dy
            and self.dz + jeu <= contenant.dz
        )


@dataclass(frozen=True)
class Piece:
    nom: str
    role: str
    boite: Boite
    materiau: str
    visible_exterieur_si_pouf: bool
    imprimable: bool = False
    commentaire: str = ""


@dataclass(frozen=True)
class Assemblage:
    nom: str
    type: str
    pieces: tuple[str, ...]
    origine: tuple[float, float, float]
    visible_etat_pouf: bool
    commentaire: str = ""


@dataclass(frozen=True)
class Verification:
    code: str
    ok: bool
    niveau: str
    message: str
    compromis: bool = False


def caisson_interieur(params: ParametresPoufVibrant) -> Boite:
    z0 = params.hauteur_pieds + params.epaisseur_fond
    dz = (
        params.hauteur
        - params.hauteur_pieds
        - params.epaisseur_fond
        - params.epaisseur_coussin
        - params.epaisseur_couronne
        - params.revetement_exterieur.epaisseur_mm
    )
    return Boite(
        params.epaisseur_paroi,
        params.epaisseur_paroi,
        z0,
        params.largeur - 2.0 * params.epaisseur_paroi,
        params.profondeur - 2.0 * params.epaisseur_paroi,
        dz,
    )



def _ajouter_pilotage_presence_acoustique(add, params: ParametresPoufVibrant, interieur: Boite, z_c: float, h_c: float) -> None:
    """Boîtier ESP32, AU, cellules, butées, panneaux aériens (non visibles)."""
    # Boîtier électronique : coin arrière gauche, en retrait des panneaux 12 mm.
    bx, by, bz = ESP32_S3_WROOM1.encombrement_boitier_mm
    ep_pan = 12.0
    x_boit = interieur.x + ep_pan + 8.0
    y_boit = interieur.y + interieur.dy - ep_pan - 8.0 - by
    z_boit = interieur.z + 4.0
    add("boitier_electronique", "electronique",
        Boite(x_boit, y_boit, z_boit, bx, by, bz),
        "petg", False, True,
        "Boîtier IP67 : ESP32-S3, ADS1220, relais de sécurité à réarmement "
        "manuel, alim. 24→5 V de la logique. Évent ePTFE, fenêtre d'antenne "
        "plastique (non masquée par du métal). L'ESP32 reste alimenté si le "
        "relais coupe les drivers.")

    # AU : sous la lèvre avant de la couronne, côté droit.
    z_levre = z_c + h_c - params.epaisseur_couronne
    add("arret_urgence", "securite",
        Boite(params.largeur - 90.0, 8.0, z_levre - 26.0, 22.0, 16.0, 22.0),
        "plastique", False, False,
        "Bouton AU Ø 22 mm, contact NF, à accrochage. Sous le chant avant "
        "droit de la couronne : accessible assis (doigts sous la lèvre, "
        "portée ~250 mm depuis l'axe), discret (invisible en façade velours). "
        "Boucle indépendante de l'ESP32 : relais de sécurité à contacts "
        "guidés, coupe le 24 V des trois drivers, réarmement manuel.")

    # Cellules Wheatstone + butées sous la couronne, autour de la selle.
    cx, cy = params.largeur / 2.0, params.profondeur / 2.0
    lc, lc_y, lc_z = CELLULE_50KG.encombrement_mm
    # Barre typique 55 × 12,7 × 12,7, posée à plat.
    portee = 80.0
    z_cell = z_levre - lc_z
    for i, (dx, dy) in enumerate(((-portee, -portee), (portee, -portee),
                                  (-portee, portee), (portee, portee)), start=1):
        x = cx + dx - lc / 2.0
        y = cy + dy - lc_y / 2.0
        add(f"cellule_charge_{i}", "capteur",
            Boite(x, y, z_cell, lc, lc_y, lc_z),
            "acier", False, False,
            "Cellule 50 kg, pont de Wheatstone (zone centrale).")
        add(f"butee_surcharge_{i}", "capteur",
            Boite(x + lc + 2.0, y, z_cell + 0.4, 12.0, lc_y, lc_z - 0.4),
            "petg", False, True,
            "Butée de surcharge : le jeu ~0,4 mm laisse fléchir la cellule "
            "en service et reprend un appui brutal avant rupture.")

    add("accelerometre_reference", "capteur",
        Boite(cx + 110.0, cy - 8.0, z_levre - 8.0, 16.0, 16.0, 8.0),
        "electronique", False, False,
        "Accéléromètre de référence sur la couronne, soustrait de la zone "
        "centrale (rejet du mode commun vibratoire).")

    # Panneaux acoustiques aériens, 12 mm, 40 %, intérieur du caisson.
    # Quatre parois + deux capots de module. Pas de fond (ventilation).
    z_p = interieur.z
    h_p = max(40.0, interieur.dz - 8.0)
    add("panneau_acoustique_av", "acoustique",
        Boite(interieur.x, interieur.y, z_p, interieur.dx, ep_pan, h_p),
        "petg", False, True,
        "Panneau labyrinthe/treillis PETG 40 %, 12 mm, bruit aérien. "
        "PLA déconseillé en service (Tg, humidité).")
    add("panneau_acoustique_ar", "acoustique",
        Boite(interieur.x, interieur.y + interieur.dy - ep_pan, z_p, interieur.dx, ep_pan, h_p),
        "petg", False, True, "Panneau arrière PETG 40 %, 12 mm.")
    add("panneau_acoustique_g", "acoustique",
        Boite(interieur.x, interieur.y + ep_pan, z_p, ep_pan, interieur.dy - 2 * ep_pan, h_p),
        "petg", False, True, "Panneau gauche PETG 40 %, 12 mm.")
    add("panneau_acoustique_d", "acoustique",
        Boite(interieur.x + interieur.dx - ep_pan, interieur.y + ep_pan, z_p,
              ep_pan, interieur.dy - 2 * ep_pan, h_p),
        "petg", False, True, "Panneau droit PETG 40 %, 12 mm.")
    add("capot_acoustique_module", "acoustique",
        Boite(cx - 80.0, cy - 80.0, z_c + 40.0, 160.0, 160.0, 12.0),
        "petg", False, True,
        "Capot treillis PETG 40 % sur le module (moteur / réducteur).")


def _pieces(etat: Etat, params: ParametresPoufVibrant) -> tuple[Piece, ...]:
    pieces: list[Piece] = []
    essence = params.essence.nom
    tissu = params.revetement_exterieur.nom
    interieur = caisson_interieur(params)
    recalage = recaler_module_vibrant(
        params.gamme if params.gamme == GAMME_SYBIAN_ENTREE else GAMME_SYBIAN_HAUT,
        masse_housse_kg=params.masse_housse_kg,
    )
    loge = recalage.logement
    pouf = etat is Etat.POUF

    def add(nom, role, boite, materiau, visible, imprimable=False, commentaire=""):
        pieces.append(Piece(nom, role, boite, materiau, visible, imprimable, commentaire))

    # Pieds / patins discrets (4 coins)
    cote_patin = 40.0
    for nom, x, y in (
        ("patin_avg", 20.0, 20.0),
        ("patin_avd", params.largeur - 20.0 - cote_patin, 20.0),
        ("patin_arg", 20.0, params.profondeur - 20.0 - cote_patin),
        ("patin_ard", params.largeur - 20.0 - cote_patin, params.profondeur - 20.0 - cote_patin),
    ):
        add(nom, "patin", Boite(x, y, 0.0, cote_patin, cote_patin, params.hauteur_pieds),
            "tpu", False, True, "Patin TPU non exposé, sous le caisson.")

    # Caisson bois
    z_c = params.hauteur_pieds
    h_c = params.hauteur - params.hauteur_pieds - params.epaisseur_coussin - params.revetement_exterieur.epaisseur_mm
    add("caisson_paroi_av", "caisson",
        Boite(0, 0, z_c, params.largeur, params.epaisseur_paroi, h_c), essence, True, False,
        "Paroi avant, ébénisterie, tourillons / mortaises.")
    add("caisson_paroi_ar", "caisson",
        Boite(0, params.profondeur - params.epaisseur_paroi, z_c, params.largeur, params.epaisseur_paroi, h_c),
        essence, True)
    add("caisson_paroi_g", "caisson",
        Boite(0, 0, z_c, params.epaisseur_paroi, params.profondeur, h_c), essence, True)
    add("caisson_paroi_d", "caisson",
        Boite(params.largeur - params.epaisseur_paroi, 0, z_c, params.epaisseur_paroi, params.profondeur, h_c),
        essence, True)
    add("caisson_fond", "caisson",
        Boite(params.epaisseur_paroi, params.epaisseur_paroi, z_c,
              interieur.dx, interieur.dy, params.epaisseur_fond),
        essence, False, False, "Fond rainé. Ouïes de ventilation discrètes, côté dessous.")
    add("couronne_assise", "caisson",
        Boite(0, 0, z_c + h_c - params.epaisseur_couronne, params.largeur, params.profondeur, params.epaisseur_couronne),
        essence, True, False,
        "Couronne structurelle : reprend le poids de l'usager, pas les silentblocs.")

    # Coussin amovible (état pouf)
    z_coussin = z_c + h_c
    if pouf:
        add("coussin_amovible", "coussin_exterieur",
            Boite(0, 0, z_coussin, params.largeur, params.profondeur,
                  params.epaisseur_coussin + params.revetement_exterieur.epaisseur_mm),
            tissu, True, False,
            "Coussin de salon amovible, masque complètement la selle et le capuchon. "
            "Dégagement intérieur pour le capuchon affleurant.")

    # Module : placement centré dans le caisson
    cx, cy = params.largeur / 2.0, params.profondeur / 2.0
    z_mod = interieur.z + 4.0
    add("cadre_module", "module",
        Boite(cx - loge.largeur_mm / 2.0, cy - loge.profondeur_mm / 2.0, z_mod,
              loge.largeur_mm, loge.profondeur_mm, max(20.0, min(loge.hauteur_mm, interieur.dz - 8.0))),
        "petg", False, True, loge.commentaire)

    # Silentblocs (aux coins du cadre)
    rec = recalage.choix_silentblocs
    sb = rec.silentbloc
    n = rec.nombre
    # 4 coins par défaut ; 6 = 2 rangées de 3 (simplifié : 4 + 2 milieux).
    positions = [
        (cx - loge.largeur_mm / 2.0 + 20, cy - loge.profondeur_mm / 2.0 + 20),
        (cx + loge.largeur_mm / 2.0 - 20 - sb.diametre_mm, cy - loge.profondeur_mm / 2.0 + 20),
        (cx - loge.largeur_mm / 2.0 + 20, cy + loge.profondeur_mm / 2.0 - 20 - sb.diametre_mm),
        (cx + loge.largeur_mm / 2.0 - 20 - sb.diametre_mm, cy + loge.profondeur_mm / 2.0 - 20 - sb.diametre_mm),
    ]
    if n >= 6:
        positions.append((cx - sb.diametre_mm / 2.0, cy - loge.profondeur_mm / 2.0 + 20))
        positions.append((cx - sb.diametre_mm / 2.0, cy + loge.profondeur_mm / 2.0 - 20 - sb.diametre_mm))
    for i, (x, y) in enumerate(positions[:n], start=1):
        add(f"silentbloc_{i}", "silentbloc",
            Boite(x, y, z_mod, sb.diametre_mm, sb.diametre_mm, sb.hauteur_libre_mm),
            sb.materiau, False, True, f"{sb.nom_affiche}, isolation du cadre.")

    # Embout 1" NPT + capuchon : au centre, au sommet de l'étage haut (sous la selle)
    dep = FILETAGE_1_NPT.depassement_recommande_mm
    od = FILETAGE_1_NPT.diametre_exterieur_mm
    z_filetage = z_c + h_c - params.epaisseur_couronne  # affleure la couronne, dépasse de `dep`
    if not pouf:
        z_filetage = z_c + h_c  # coussin retiré, embout visible au-dessus de la couronne
    add("embout_npt", "interface",
        Boite(cx - od / 2.0, cy - od / 2.0, z_filetage, od, od, dep),
        params.materiau_embout, False, False,
        "Embout 1\" NPT mâle, centré sur l'axe, méplats + butée anti-rotation. "
        "Le couple de vissage d'une housse ne doit pas cisailler le voice coil.")
    if pouf:
        add("capuchon_npt", "capuchon",
            Boite(cx - od / 2.0 - 2.0, cy - od / 2.0 - 2.0, z_filetage, od + 4.0, od + 4.0, dep),
            "petg", False, True,
            "Capuchon affleurant (insert laiton, joint torique du commerce), sous le coussin.")

    # Selle (visible seulement état MODULE)
    if not pouf:
        add("selle_peau", "selle",
            Boite(cx - 90.0, cy - 90.0, z_filetage - 15.0, 180.0, 180.0, 15.0),
            "silicone_platine", False, False,
            "Peau de selle silicone platine (Dragon Skin 10 ou 20), lavable, non poreuse. "
            "L'ouverture centrale laisse passer l'embout.")

    # Entrée : carter mousse + balourd. Haut : modules optionnels schématiques.
    if params.gamme == GAMME_SYBIAN_ENTREE:
        add("carter_balourd", "carter",
            Boite(cx - 70.0, cy - 50.0, z_mod + sb.hauteur_libre_mm + 4.0, 140.0, 100.0, 90.0),
            MOUSSE_DENSES_CARTER.nom, False, False,
            "Carter fermé, mousse dense, pièces tournantes inaccessibles.")
        add("moteur_balourd", "actionneur",
            Boite(cx - 55.0, cy - 35.0, z_mod + sb.hauteur_libre_mm + 20.0, 110.0, 70.0, 70.0),
            "acier", False, False, "Moteur 24 V à balourd sous carter.")
    else:
        z_act = z_mod + sb.hauteur_libre_mm + 4.0
        if params.module_piston:
            add("module_piston", "actionneur",
                Boite(cx - loge.largeur_mm / 2.0 + 10.0, cy - 30.0, z_act, 80.0, 60.0, 100.0),
                "aluminium", False, False,
                "Étage piston (VCAR0110), en retrait (architecture parallèle).")
        if params.module_rotation:
            add("module_rotation", "actionneur",
                Boite(cx - 40.0, cy - 40.0, z_act + (20.0 if params.module_piston else 0.0),
                      80.0, 80.0, 70.0),
                "aluminium", False, False,
                "Brushless plat + réducteur, roulement de butée séparé, limiteur de couple.")
        if params.module_vibration:
            add("module_vibration", "actionneur",
                Boite(cx - 35.0, cy - 35.0, z_filetage - 16.1 - 40.4, 70.0, 70.0, 56.5),
                "aluminium", False, False,
                "Voice coil VCAR0105, sous l'embout, masse mobile limitée à l'équipage + housse.")

    # Pilotage ESP32, AU câblé, cellules, panneaux aériens
    _ajouter_pilotage_presence_acoustique(add, params, interieur, z_c, h_c)

    add("presse_etoupe_alim", "securite",
        Boite(cx - 10.0, params.epaisseur_paroi - 2.0, z_c + 10.0, 20.0, 16.0, 16.0),
        "elastomere", False, False,
        "Entrée 24 V DC uniquement. Alimentation certifiée hors meuble.")

    return tuple(pieces)


def _assemblages(params: ParametresPoufVibrant) -> tuple[Assemblage, ...]:
    rec = recaler_module_vibrant(params.gamme, masse_housse_kg=params.masse_housse_kg)
    fix = rec.fixations
    cx, cy = params.largeur / 2.0, params.profondeur / 2.0
    items = [
        Assemblage(
            "ancrages_internes_module", "insert_noye_et_tourillon",
            ("cadre_module", "caisson_fond"),
            (cx, cy, params.hauteur_pieds + params.epaisseur_fond),
            False,
            fix.commentaire,
        ),
        Assemblage(
            "charniere_aucune", "rien",
            (),
            (0, 0, 0),
            False,
            "Pas de ferrure visible. Le coussin est simplement posé / emboîté.",
        ),
        Assemblage(
            "embout_blocage_rotation", "butée_méplats",
            ("embout_npt", "module_vibration" if params.gamme == GAMME_SYBIAN_HAUT else "carter_balourd"),
            (cx, cy, 0),
            False,
            "Méplats et butée : le vissage d'une housse ne desserre pas l'embout "
            "et ne charge pas le guidage du voice coil en torsion.",
        ),
    ]
    return tuple(items)


def _verifications(etat: Etat, params: ParametresPoufVibrant, pieces: tuple[Piece, ...]) -> tuple[Verification, ...]:
    verifs: list[Verification] = []
    interieur = caisson_interieur(params)
    rec = recaler_module_vibrant(params.gamme, masse_housse_kg=params.masse_housse_kg)
    choix = rec.choix_silentblocs
    loge = rec.logement

    rentre = Boite(0, 0, 0, loge.largeur_mm, loge.profondeur_mm, loge.hauteur_mm).rentre_dans(
        interieur, jeu=params.discretion.jeu_repli_mm
    )
    verifs.append(Verification(
        "logement_rentre_dans_caisson",
        rentre,
        NIVEAU_OK if rentre else NIVEAU_NON_CONFORME,
        f"Logement {loge.largeur_mm:.0f}×{loge.profondeur_mm:.0f}×{loge.hauteur_mm:.0f} mm "
        f"dans intérieur {interieur.dx:.0f}×{interieur.dy:.0f}×{interieur.dz:.0f} mm "
        f"(gamme {params.gamme}).",
        compromis=not rentre,
    ))

    # Isolation
    ok_iso = choix.isole_au_minimum
    verifs.append(Verification(
        "transmissibilite_isolation",
        ok_iso,
        NIVEAU_OK if choix.isole_ideal else (NIVEAU_AVERTISSEMENT if ok_iso else NIVEAU_NON_CONFORME),
        (
            f"f0 = {choix.frequence_propre_hz:.2f} Hz, f_min = {choix.frequence_exc_min_hz:.2f} Hz, "
            f"rapport = {choix.rapport_fmin_sur_f0:.2f} (cible ≥ 3, minimum √2). "
            f"T(f_min) = {choix.transmissibilite_a_fmin:.3f}, T(f_max) = {choix.transmissibilite_a_fmax:.3f}. "
            f"Plots : {choix.nombre} × {choix.silentbloc.nom_affiche}."
        ),
        compromis=not choix.isole_ideal,
    ))

    jeu_ok = choix.deflexion_statique_mm + JEU_DEBATTEMENT_MIN_MM < choix.silentbloc.hauteur_libre_mm
    verifs.append(Verification(
        "debattement_sans_contact",
        jeu_ok,
        NIVEAU_OK if jeu_ok else NIVEAU_NON_CONFORME,
        f"Déflexion statique {choix.deflexion_statique_mm:.1f} mm, jeu min {JEU_DEBATTEMENT_MIN_MM:.0f} mm, "
        f"hauteur libre plot {choix.silentbloc.hauteur_libre_mm:.0f} mm.",
        compromis=not jeu_ok,
    ))

    charge_ok = choix.charge_totale_par_plot_n * CS_SILENTBLOC_MIN <= choix.silentbloc.charge_nominale_n * CS_SILENTBLOC_MIN or (
        choix.charge_totale_par_plot_n <= choix.silentbloc.charge_nominale_n
    )
    # Clarify: OK if total load <= nominal
    charge_ok = choix.charge_totale_par_plot_n <= choix.silentbloc.charge_nominale_n
    verifs.append(Verification(
        "charge_silentblocs",
        charge_ok,
        NIVEAU_OK if charge_ok else NIVEAU_NON_CONFORME,
        f"Charge par plot {choix.charge_totale_par_plot_n:.1f} N "
        f"(statique {choix.charge_statique_par_plot_n:.1f} + dynamique "
        f"{choix.charge_dynamique_crete_estimee_n:.1f}) pour nominale "
        f"{choix.silentbloc.charge_nominale_n:.1f} N. "
        "Le poids usager doit reposer sur la couronne, pas sur les plots.",
        compromis=not charge_ok,
    ))

    # Housse
    if params.gamme == GAMME_SYBIAN_HAUT and rec.diagnostic_housse is not None:
        diag = rec.diagnostic_housse
        # Recalcul aussi aux bornes 0,5 et 1,0 kg (dimensionnement demandé)
        from incognito.regles import diagnostiquer_housse_haut, masse_embout_kg as _me
        hors_plage_dim = not (
            MASSE_HOUSSE_DIMENSIONNEMENT_MIN_KG <= params.masse_housse_kg <= MASSE_HOUSSE_DIMENSIONNEMENT_MAX_KG
        )
        verifs.append(Verification(
            "masse_housse_capacite",
            not diag.hors_capacite,
            NIVEAU_NON_CONFORME if diag.hors_capacite else (
                NIVEAU_AVERTISSEMENT if hors_plage_dim else NIVEAU_OK
            ),
            " ".join(diag.messages) + (
                f" Dimensionnement cible : {MASSE_HOUSSE_DIMENSIONNEMENT_MIN_KG:g}–"
                f"{MASSE_HOUSSE_DIMENSIONNEMENT_MAX_KG:g} kg."
            ),
            compromis=diag.hors_capacite or hors_plage_dim,
        ))
    else:
        verifs.append(Verification(
            "masse_housse_entree",
            True,
            NIVEAU_AVERTISSEMENT,
            (
                "Gamme entrée (balourd) : la housse, si elle est montée sur l'embout "
                f"1\" NPT du plateau ({params.masse_housse_kg:.2f} kg), s'ajoute à la "
                "masse suspendue et décale f0 ; elle ne « consomme » pas une course "
                "linéaire. Une housse lourde ou excentrée augmente le moment sur le "
                "carter : rester dans 0,5–1 kg, vérifier le équilibrage. La sensation "
                "n'est pas un mouvement piston de 16 mm."
            ),
            compromis=True,
        ))

    # Architecture 3 modules (haut)
    if params.gamme == GAMME_SYBIAN_HAUT:
        analyse = analyser_masses_empilement(
            params.masse_housse_kg, params.modules_actifs_haut, params.architecture
        )
        verifs.append(Verification(
            "architecture_masses",
            not analyse.hors_capacite_15hz_8mm,
            NIVEAU_NON_CONFORME if analyse.hors_capacite_15hz_8mm else NIVEAU_OK,
            analyse.recommendation + " " + " ".join(analyse.messages),
            compromis=analyse.architecture == ARCHITECTURE_SERIE or analyse.hors_capacite_15hz_8mm,
        ))
        enc = encombrement_vertical_haut(
            params.architecture, params.hauteur, params.epaisseur_coussin,
            params.hauteur_pieds, params.epaisseur_fond, params.epaisseur_couronne,
            rec.choix_silentblocs.silentbloc.hauteur_libre_mm,
            params.modules_actifs_haut or ("vibration",),
        )
        verifs.append(Verification(
            "encombrement_vertical",
            enc.rentre,
            NIVEAU_OK if enc.rentre else NIVEAU_NON_CONFORME,
            enc.commentaire,
            compromis=not enc.rentre,
        ))

    # Discrétion état pouf
    if etat is Etat.POUF:
        fautifs = [p.nom for p in pieces if p.visible_exterieur_si_pouf and p.role in
                   {"interface", "selle", "actionneur", "capuchon", "module", "silentbloc"}]
        verifs.append(Verification(
            "module_invisible_en_pouf",
            not fautifs,
            NIVEAU_OK if not fautifs else NIVEAU_NON_CONFORME,
            "À l'état pouf, le coussin masque selle, embout, capuchon et mécanisme."
            if not fautifs else f"Éléments visibles à tort : {fautifs}.",
        ))

    # Stabilité (pouf bas, large) : charge verticale dans l'empreinte.
    verifs.append(Verification(
        "stabilite",
        True,
        NIVEAU_OK,
        "Pouf bas et large (500×500) : le poids usager passe par la couronne et "
        "les parois, pas par les silentblocs. Pas de basculement typique en usage "
        "assis centré. Un effort latéral important (housse excentrée) charge le "
        "guidage, pas la bobine — à valider par essai.",
    ))

    # Ventilation / thermique (qualitatif)
    verifs.append(Verification(
        "ventilation_thermique",
        True,
        NIVEAU_AVERTISSEMENT,
        "Ouïes sous le pouf (discrétion vs débit). Protection thermique moteur "
        "imposée. Un essai d'échauffement en régime (caisson fermé, coussin en "
        "place et retiré) est obligatoire. Objectif de bruit < 50 dB(A) à 1 m : "
        "à mesurer, non garanti (un vérin à vis type P16 est déjà donné à 62 dB).",
        compromis=True,
    ))

    verifs.append(Verification(
        "securite_electrique_mecanique",
        params.tension_v <= 48.0,
        NIVEAU_OK if params.tension_v <= 48.0 else NIVEAU_NON_CONFORME,
        "24 V DC dans le meuble, alim. certifiée à l'extérieur, AU coupant tous "
        "les modules, rampe, limitation, carter des pièces tournantes, limiteur "
        "de force/couple piston et plateau, butées. Conformité machines / CEM / "
        "basse tension : essai et dossier, voir docs/pouf_vibrant.md.",
    ))

    verifs.append(Verification(
        "essai_reel_obligatoire",
        True,
        NIVEAU_ESSAI_REQUIS,
        "Tous les modèles (isolation, masses, thermique, IP67, bruit à 1 m, "
        "charge d'ancrage, fluage TPU) exigent un essai réel et, pour une mise "
        "sur le marché, un dossier de conformité (directive machines, CEM, "
        "basse tension, hygiène).",
    ))

    # Pilotage / présence / AU
    noms = {p.nom for p in pieces}
    verifs.append(Verification(
        "au_independant_esp32",
        "arret_urgence" in noms and "boitier_electronique" in noms,
        NIVEAU_OK,
        "L'arrêt d'urgence est un organe physique (contact NF + relais de "
        "sécurité à réarmement manuel) distinct du boîtier ESP32. Il coupe "
        "le 24 V des drivers des trois modules. La télécommande ne le remplace pas.",
    ))
    verifs.append(Verification(
        "presence_cellules_butees",
        all(f"cellule_charge_{i}" in noms and f"butee_surcharge_{i}" in noms for i in range(1, 5)),
        NIVEAU_OK,
        "Quatre cellules Wheatstone sous la couronne, chacune protégée par "
        "une butée de surcharge. FSR écartés.",
    ))
    boitier = next((p for p in pieces if p.nom == "boitier_electronique"), None)
    ok_boit = boitier is not None and boitier.boite.rentre_dans(interieur, jeu=0.0)
    verifs.append(Verification(
        "logement_electronique_dans_caisson",
        ok_boit,
        NIVEAU_OK if ok_boit else NIVEAU_NON_CONFORME,
        "Le boîtier ESP32 / relais rentre dans le caisson, hors du cadre module.",
    ))
    panneaux = [p for p in pieces if p.nom.startswith("panneau_acoustique") or p.nom.startswith("capot_acoustique")]
    ok_pan = all(pn.boite.rentre_dans(interieur, jeu=0.0) or pn.nom.startswith("capot") for pn in panneaux)
    # Le capot est dans le caisson également.
    ok_pan = all(
        interieur.x <= pn.boite.x and pn.boite.x + pn.boite.dx <= interieur.x + interieur.dx
        and interieur.y <= pn.boite.y and pn.boite.y + pn.boite.dy <= interieur.y + interieur.dy
        for pn in panneaux
    )
    verifs.append(Verification(
        "panneaux_acoustiques_dans_caisson",
        ok_pan and len(panneaux) >= 5,
        NIVEAU_OK if ok_pan else NIVEAU_NON_CONFORME,
        f"{len(panneaux)} panneaux / capots aériens PETG 12 mm, 40 %, dans le caisson.",
    ))
    comp = comparer_treillis_et_silentbloc()
    verifs.append(Verification(
        "treillis_pas_silentbloc",
        not comp.treillis_adapte_isolation_solidienne,
        NIVEAU_OK,
        comp.commentaire,
        compromis=False,
    ))
    fmin = choix.frequence_exc_min_hz
    fc = frequence_coupure_presence_hz(fmin)
    verifs.append(Verification(
        "filtre_presence_fc",
        fc <= fmin / 10.0 + 1e-9,
        NIVEAU_OK,
        f"Passe-bas présence : fc = {fc:.2f} Hz ≤ f_exc_min/10 = {fmin/10.0:.2f} Hz "
        f"(f_exc_min = {fmin:.1f} Hz). Voir incognito.presence.",
    ))
    for pce in pieces:
        if pce.role in {"electronique", "securite", "capteur", "acoustique"} and pce.visible_exterieur_si_pouf:
            verifs.append(Verification(
                "pilotage_invisible_en_pouf",
                False,
                NIVEAU_NON_CONFORME,
                f"La pièce {pce.nom} ne doit pas être visible à l'état pouf.",
            ))
            break
    else:
        verifs.append(Verification(
            "pilotage_invisible_en_pouf",
            True,
            NIVEAU_OK,
            "Boîtier, AU, cellules et panneaux invisibles à l'état pouf.",
        ))


    return tuple(verifs)


@dataclass(frozen=True)
class GeometriePoufVibrant:
    etat: Etat
    parametres: ParametresPoufVibrant
    pieces: tuple[Piece, ...]
    assemblages: tuple[Assemblage, ...]
    verifications: tuple[Verification, ...]

    @property
    def conforme(self) -> bool:
        return all(v.niveau != NIVEAU_NON_CONFORME for v in self.verifications)

    def piece(self, nom: str) -> Piece:
        for p in self.pieces:
            if p.nom == nom:
                return p
        raise KeyError(nom)

    def encombrement(self) -> Boite:
        xs = [p.boite.x for p in self.pieces]
        ys = [p.boite.y for p in self.pieces]
        zs = [p.boite.z for p in self.pieces]
        xm = [p.boite.x + p.boite.dx for p in self.pieces]
        ym = [p.boite.y + p.boite.dy for p in self.pieces]
        zm = [p.boite.z + p.boite.dz for p in self.pieces]
        x0, y0, z0 = min(xs), min(ys), min(zs)
        return Boite(x0, y0, z0, max(xm) - x0, max(ym) - y0, max(zm) - z0)


def calculer(etat: Etat | int, params: ParametresPoufVibrant | None = None) -> GeometriePoufVibrant:
    if not isinstance(etat, Etat):
        etat = Etat(etat)
    params = params or parametres_pouf_defaut()
    pieces = _pieces(etat, params)
    ass = _assemblages(params)
    verifs = _verifications(etat, params, pieces)
    return GeometriePoufVibrant(etat, params, pieces, ass, verifs)


def calculer_deux_etats(params: ParametresPoufVibrant | None = None) -> dict[Etat, GeometriePoufVibrant]:
    params = params or parametres_pouf_defaut()
    return {e: calculer(e, params) for e in Etat}


def vers_parametres_fusion_pouf(
    params: ParametresPoufVibrant | None = None,
) -> dict[str, tuple[float, str, str]]:
    """Paramètres utilisateur Fusion du pouf vibrant."""
    params = params or parametres_pouf_defaut()
    code_gamme = 1.0 if params.gamme == GAMME_SYBIAN_HAUT else 0.0
    return {
        "inc_sybian_gamme": (code_gamme, "", "0 entrée (balourd), 1 haut (jusqu'à 3 modules)."),
        "inc_pouf_etat": (float(Etat.POUF), "", "0 pouf (coussin en place), 1 module (selle accessible)."),
        "inc_pouf_largeur": (params.largeur, "mm", "Largeur hors-tout du pouf."),
        "inc_pouf_profondeur": (params.profondeur, "mm", "Profondeur hors-tout du pouf."),
        "inc_pouf_hauteur": (params.hauteur, "mm", "Hauteur hors-tout, dessus de coussin."),
        "inc_pouf_epaisseur_coussin": (params.epaisseur_coussin, "mm", "Épaisseur du coussin amovible."),
        "inc_module_vibration": (1.0 if params.module_vibration else 0.0, "", "Active l'étage voice coil (gamme haut)."),
        "inc_module_piston": (1.0 if params.module_piston else 0.0, "", "Active l'étage piston (gamme haut)."),
        "inc_module_rotation": (1.0 if params.module_rotation else 0.0, "", "Active l'étage rotation (gamme haut)."),
        "inc_masse_housse": (params.masse_housse_kg, "kg", "Masse de la housse (dimensionnement 0,5–1 kg)."),
        "inc_architecture_parallele": (
            1.0 if params.architecture == ARCHITECTURE_PARALLELE else 0.0, "",
            "1 = parallèle découplé (retenu), 0 = empilement série (déconseillé).",
        ),
        "inc_npt_depassement": (
            FILETAGE_1_NPT.depassement_recommande_mm, "mm",
            "Dépassement de l'embout 1\" NPT au-dessus de la selle.",
        ),
        "inc_esp32": (1.0, "", "Pilotage ESP32 BLE + Wi-Fi (remplace télécommande / pédale)."),
        "inc_au_physique": (1.0, "", "AU câblé NF + relais de sécurité, indépendant de l'ESP32."),
        "inc_presence_cellules": (1.0, "", "Présence par cellules Wheatstone (FSR écartés)."),
        "inc_panneau_acoustique_epaisseur": (12.0, "mm", "Épaisseur des panneaux aériens PETG 40 %."),
    }
