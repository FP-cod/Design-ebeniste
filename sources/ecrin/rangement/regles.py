# -*- coding: utf-8 -*-
"""Regles de la gamme Rangement : grandeurs derivees et contraintes de coherence.

Deux familles de fonctions :

1. ``recalculer_derives(p)`` : recalcule les parametres ``derive`` (epaisseur
   du cuir, longueur d'insert, epaulement d'ergot, tourillons, tenons) et
   renvoie la liste des ``Ajustement`` avec leur explication.
2. ``verifier_*`` : verifications physiques et de coherence. Chacune renvoie
   des ``Verification`` (niveau 'ok' | 'alerte' | 'echec' | 'todo') :

   - crochets : flexion de la tige, arrachement de l'insert, effort accidentel ;
   - barres de suspension : flexion, fleche (portee / 300), effort accidentel ;
   - etageres : flexion, fleche, porte-a-faux (ratio du systeme + fleche) ;
   - ports : profondeur et largeur mini du plot pour la douille 1" NPT,
     pas des ports, degagement des accessoires ;
   - tiroirs : longueur de glissiere compatible avec la profondeur ;
   - portes et serrures : epaisseurs mini / maxi (lecture RFID) ;
   - discretion (regles Incognito), tanins (Neogothique), stabilite des
     armoires, support mural (TODO tant que non releve).

``verifier_coherence(p)`` enchaine toutes les verifications qui ne dependent
que des parametres ; les grammaires ajoutent celles qui dependent de la
geometrie.

Hypotheses : formules de RDM elementaires (poutre sur deux appuis, console),
ordres de grandeur de conception - ne remplacent ni une note de calcul ni un
essai de charge.
"""

import math

from .catalogues import bois as _bois, garnissage as _garn, quincaillerie as _quin
from .catalogues import systemes as _sys, jonctions as _jonc
from .geometrie import Verification

G = 9.81  # m/s2

#: Recul des consoles de barre par rapport au bord du module (ratelier) [mm].
MARGE_CONSOLE = 20.0


def portee_barre(p, marge_console=MARGE_CONSOLE):
    """Portee libre d'une barre entre ses deux consoles (epaisseur = panneau mural)."""
    return p.get("modules.module_largeur") - 2.0 * (marge_console + p.get("panneaux.epaisseur_panneau_mural"))


# ---------------------------------------------------------------------------
# Ajustements (grandeurs derivees)
# ---------------------------------------------------------------------------
class Ajustement(object):
    def __init__(self, chemin, avant, apres, raison):
        self.chemin, self.avant, self.apres, self.raison = chemin, avant, apres, raison

    def __repr__(self):
        return "AJUSTE %s : %s -> %s (%s)" % (self.chemin, self.avant, self.apres, self.raison)

    __str__ = __repr__


def _ajuster(p, chemin, valeur, raison, res):
    avant = p.get(chemin)
    if avant != valeur:
        p.set(chemin, valeur)
        res.append(Ajustement(chemin, avant, valeur, raison))


def recalculer_derives(p):
    """Recalcule les parametres derives sur ``p`` (en place). Renvoie les ajustements."""
    res = []
    g = p.get
    fam = g("cuir.famille")
    if fam in _garn.GARNISSAGES:
        _ajuster(p, "cuir.epaisseur", _garn.GARNISSAGES[fam]["epaisseur"], "epaisseur de la famille %s" % fam, res)
    ess = g("bois.essence")
    if ess in _bois.ESSENCES:
        dens = _bois.ESSENCES[ess]["densite"]
        _ajuster(p, "quincaillerie.longueur_insert", 20.0 if dens >= 650.0 else 25.0,
                 "insert M8 : 20 mm si densite >= 650 kg/m3 (%s : %g) sinon 25 - Equinox" % (ess, dens), res)
    _ajuster(p, "ports.epaulement_diametre", max(g("ports.plug_diametre_tete") + 16.0, 50.0),
             "max(tete + 16, 50) - Aboutissants calculer_port", res)
    t = _jonc.cotes_tourillon(g("panneaux.epaisseur_caisson"))
    _ajuster(p, "jonctions.diametre_tourillon", t["diametre"], "d <= 0,5 x %g mm" % g("panneaux.epaisseur_caisson"), res)
    _ajuster(p, "jonctions.longueur_tourillon", t["longueur"], "L = 5 d", res)
    _ajuster(p, "jonctions.alesage_chant", t["alesage_chant"], "alesage chant = 2,5 d", res)
    e = g("panneaux.epaisseur_panneau_mural")
    tm = _jonc.cotes_tenon(e, e)
    _ajuster(p, "jonctions.epaisseur_tenon", tm["epaisseur_tenon"], "tiers de %g mm" % e, res)
    _ajuster(p, "jonctions.profondeur_mortaise", round(tm["profondeur_mortaise"], 2), "0,8 x %g mm" % e, res)
    return res


# ---------------------------------------------------------------------------
# Outils de RDM
# ---------------------------------------------------------------------------
def module_flexion_rond(d, paroi=None):
    """W [mm3] d'un rond plein ou d'un tube."""
    if paroi:
        di = d - 2.0 * paroi
        return math.pi * (d ** 4 - di ** 4) / (32.0 * d)
    return math.pi * d ** 3 / 32.0


def inertie_rond(d, paroi=None):
    di = (d - 2.0 * paroi) if paroi else 0.0
    return math.pi * (d ** 4 - di ** 4) / 64.0


def _niveau(valeur, limite):
    return "ok" if valeur <= limite + 1e-9 else "echec"


def _materiau(p, cle_metal):
    """(limite admissible [MPa], E [MPa], limite de 'deformation' [MPa], nom, notes)."""
    if cle_metal in (None, "bois"):
        ess = p.get("bois.essence")
        sig, methode = _bois.sigma_adm(ess)
        ent = _bois.ESSENCES[ess]
        mor = ent["resistance_flexion"] or 3.0 * sig
        note = "" if methode == "incognito" else " (sigma_adm repli prudent : essence sans valeur sourcee)"
        return sig, ent["module_elasticite"], mor, "bois %s" % ess, note
    m = _quin.METAUX[cle_metal]
    return (m["limite_elastique"] / p.get("securite.securite_metal"), m["module_elasticite"],
            m["limite_elastique"], cle_metal, "")


# ---------------------------------------------------------------------------
# Crochets
# ---------------------------------------------------------------------------
def verifier_crochet(p, cle=None, nom="crochet"):
    cle = cle or p.get("systemes.crochet")
    geo = _sys.SYSTEMES[cle]["geometrie"]
    d, a = geo["diametre_tige"], geo["saillie"]
    lim, _, re_, mat, note = _materiau(p, geo["metal"])
    f = p.get("charges.charge_crochet") * G * p.get("securite.coefficient_dynamique")
    sigma = f * a / module_flexion_rond(d)
    res = [Verification(nom + "_flexion", _niveau(sigma, lim), sigma, lim, "MPa",
                        "tige O%g %s, saillie %g : %.0f N (charge x k_dyn) -> %.1f MPa <= %.1f MPa%s"
                        % (d, mat, a, f, sigma, lim, note))]
    if geo.get("platine_diametre"):
        cap = _quin.VISSERIE["insert_filete_m8"]["capacite_service"]
        traction = f * a / (geo["platine_diametre"] / 2.0) + f
        res.append(Verification(nom + "_insert", _niveau(traction, cap), traction, cap, "N",
                                "insert M8 : traction par levier de platine %.0f N <= %.0f N (Equinox)" % (traction, cap)))
    fa = p.get("charges.effort_accidentel")
    sa = fa * a / module_flexion_rond(d)
    res.append(Verification(nom + "_accidentel", "ok" if sa <= re_ else "alerte", sa, re_, "MPa",
                            "traction accidentelle %.0f N -> %.0f MPa (limite %s %.0f MPa) : un crochet n'est pas un "
                            "point d'ancrage" % (fa, sa, "elastique" if geo["metal"] else "MOR", re_)))
    return res


# ---------------------------------------------------------------------------
# Barres de suspension
# ---------------------------------------------------------------------------
def verifier_barre(p, portee, cle=None, nom="barre"):
    cle = cle or p.get("systemes.barre")
    geo = _sys.SYSTEMES[cle]["geometrie"]
    d, paroi = geo["diametre"], geo["paroi"]
    lim, e_mod, re_, mat, note = _materiau(p, geo["materiau"])
    w, i = module_flexion_rond(d, paroi), inertie_rond(d, paroi)
    q = p.get("charges.charge_lineaire_barre") * G / 1000.0          # N/mm
    k = p.get("securite.coefficient_dynamique")
    sigma = k * q * portee ** 2 / 8.0 / w
    fleche = 5.0 * q * portee ** 4 / (384.0 * e_mod * i)
    f_lim = portee / p.get("securite.fleche_admissible")
    fa = p.get("charges.effort_accidentel")
    sa = fa * portee / 4.0 / w
    return [
        Verification(nom + "_flexion", _niveau(sigma, lim), sigma, lim, "MPa",
                     "%s O%g%s portee %.0f mm, %g kg/m x k_dyn : %.1f MPa <= %.1f MPa%s"
                     % (mat, d, (" x %g" % paroi) if paroi else "", portee, p.get("charges.charge_lineaire_barre"),
                        sigma, lim, note)),
        Verification(nom + "_fleche", _niveau(fleche, f_lim), fleche, f_lim, "mm",
                     "fleche de service %.2f mm <= portee/%g = %.2f mm" % (fleche, p.get("securite.fleche_admissible"), f_lim)),
        Verification(nom + "_accidentel", "ok" if sa <= re_ else "alerte", sa, re_, "MPa",
                     "%.0f N a mi-portee -> %.0f MPa (limite %.0f MPa)" % (fa, sa, re_)),
    ]


# ---------------------------------------------------------------------------
# Etageres
# ---------------------------------------------------------------------------
def verifier_etagere(p, portee, profondeur, epaisseur=None, porte_a_faux=0.0, cle=None, nom="etagere"):
    """Etagere massive sur deux appuis + porte-a-faux eventuel a chaque bout."""
    cle = cle or p.get("systemes.etagere")
    h = epaisseur or p.get("panneaux.epaisseur_etagere")
    lim, e_mod, _, mat, note = _materiau(p, "bois")
    q = p.get("charges.charge_etagere") * (profondeur / 1000.0) * G / 1000.0     # N/mm
    w, i = profondeur * h ** 2 / 6.0, profondeur * h ** 3 / 12.0
    k = p.get("securite.coefficient_dynamique")
    sigma = k * q * portee ** 2 / 8.0 / w
    fleche = 5.0 * q * portee ** 4 / (384.0 * e_mod * i)
    fadm = p.get("securite.fleche_admissible")
    res = [Verification(nom + "_flexion", _niveau(sigma, lim), sigma, lim, "MPa",
                        "%s ep. %g, portee %.0f, prof. %.0f : %.2f MPa <= %.1f MPa%s"
                        % (mat, h, portee, profondeur, sigma, lim, note)),
           Verification(nom + "_fleche", _niveau(fleche, portee / fadm), fleche, portee / fadm, "mm",
                        "fleche %.2f mm <= portee/%g (fluage du bois non compte)" % (fleche, fadm))]
    if porte_a_faux > 0:
        ratio_max = _sys.SYSTEMES[cle]["contraintes"].get("porte_a_faux_max_ratio", 0.25)
        ratio = porte_a_faux / float(portee)
        res.append(Verification(nom + "_porte_a_faux_ratio", _niveau(ratio, ratio_max), ratio, ratio_max, "",
                                "porte-a-faux %.0f mm = %.2f x portee (max %.2f pour %s, regle d'atelier À VALIDER)"
                                % (porte_a_faux, ratio, ratio_max, cle)))
        f_c = q * porte_a_faux ** 4 / (8.0 * e_mod * i)
        lim_c = 2.0 * porte_a_faux / fadm
        res.append(Verification(nom + "_porte_a_faux_fleche", _niveau(f_c, lim_c), f_c, lim_c, "mm",
                                "fleche en bout de console %.2f mm <= 2a/%g = %.2f mm" % (f_c, fadm, lim_c)))
    return res


# ---------------------------------------------------------------------------
# Ports Aboutissants (Vac-U-Lock / 1" NPT)
# ---------------------------------------------------------------------------
def diametre_douille_npt(p):
    return p.get("ports.npt_diametre_exterieur") + 2.0 * p.get("ports.npt_paroi_douille")


def profondeur_min_npt(p, cle_port=None):
    """Profondeur de bois mini pour loger une douille 1\" NPT femelle :
    L4 (filet complet) + fond mini (+ cache affleurant si le port en a un)."""
    cle_port = cle_port or p.get("systemes.port")
    prof = p.get("ports.npt_longueur_totale") + p.get("ports.fond_mini_douille")
    if _sys.SYSTEMES[cle_port]["geometrie"].get("cache"):
        prof += p.get("discretion.epaisseur_cache")
    return prof


def largeur_min_plot(p):
    return diametre_douille_npt(p) + 2.0 * p.get("ports.paroi_bois_mini")


def verifier_port_npt(p, profondeur_bois, largeur_bois, nom="port"):
    req_p, req_l = profondeur_min_npt(p), largeur_min_plot(p)
    res = [Verification(nom + "_profondeur_npt", "ok" if profondeur_bois >= req_p - 1e-9 else "echec",
                        profondeur_bois, req_p, "mm",
                        "profondeur %.1f >= L4 %.3f + fond %g%s = %.1f mm"
                        % (profondeur_bois, p.get("ports.npt_longueur_totale"), p.get("ports.fond_mini_douille"),
                           " + cache" if req_p > p.get("ports.npt_longueur_totale") + p.get("ports.fond_mini_douille")
                           else "", req_p)),
           Verification(nom + "_largeur_plot", "ok" if largeur_bois >= req_l - 1e-9 else "echec", largeur_bois, req_l,
                        "mm", "largeur %.1f >= douille O%.1f + 2 x %g = %.1f mm"
                        % (largeur_bois, diametre_douille_npt(p), p.get("ports.paroi_bois_mini"), req_l))]
    if p.get("ports.vac_u_lock"):
        de = p.get("ports.epaulement_diametre")
        res.append(Verification(nom + "_appui_epaulement", "ok" if largeur_bois >= de else "alerte", largeur_bois, de, "mm",
                                "face d'appui %.0f mm pour l'epaulement O%.0f de l'ergot" % (largeur_bois, de)))
    return res


def verifier_port_filete(p, epaisseur_bois, nom="port"):
    """Ergot a tige filetee (defaut Aboutissants) dans un insert M8 Equinox."""
    from .catalogues import quincaillerie as _q
    fil, l_fil = p.get("ports.filetage_ergot"), p.get("ports.filetage_ergot_longueur")
    l_ins = p.get("quincaillerie.longueur_insert")
    cap = _q.VISSERIE["insert_filete_m8"]["capacite_service"]
    effort = p.get("charges.effort_accidentel")
    return [
        Verification(nom + "_filetage_insert", "ok" if fil.startswith("M8") else "echec", fil, "M8", "",
                     "filetage de l'ergot %s compatible insert M8 (Equinox)" % fil),
        Verification(nom + "_longueur_filetage", "ok" if l_fil <= l_ins + 1e-9 else "echec", l_fil, l_ins, "mm",
                     "tige %g mm <= insert %g mm" % (l_fil, l_ins)),
        Verification(nom + "_insert_dans_panneau", "ok" if l_ins <= epaisseur_bois + 1e-9 else "echec", l_ins,
                     epaisseur_bois, "mm", "insert %g mm dans %g mm de bois (traversant admis, face murale)"
                     % (l_ins, epaisseur_bois)),
        Verification(nom + "_arrachement_insert", _niveau(effort, cap), effort, cap, "N",
                     "effort accidentel %g N <= capacite insert %g N" % (effort, cap)),
    ]


def verifier_montage_port(p, nom="port_montage"):
    """Le systeme de port choisi et ports.montage_arriere doivent concorder."""
    from .catalogues import systemes as _s
    geo = _s.SYSTEMES.get(p.get("systemes.port"), {}).get("geometrie", {})
    attendu = geo.get("montage_arriere")
    if attendu is None:
        return []
    m = p.get("ports.montage_arriere")
    return [Verification(nom, "ok" if m == attendu else "alerte", m, attendu, "",
                         "ports.montage_arriere = %s ; le systeme %s attend %s" % (m, p.get("systemes.port"), attendu))]


def verifier_pas_ports(p, pas=None, largeur_plot=None, nom="ports"):
    pas = pas if pas is not None else p.get("ports.pas_ports")
    res = []
    lp = p.get("ports.plug_longueur")
    res.append(Verification(nom + "_pas_vs_ergot", "ok" if pas >= lp else "alerte", pas, lp, "mm",
                            "pas %g >= longueur d'ergot %g (regle Aboutissants _valider_cadre)" % (pas, lp)))
    dg = p.get("ports.degagement_accessoire")
    res.append(Verification(nom + "_degagement", "ok" if pas >= dg else "alerte", pas, dg, "mm",
                            "pas %g >= degagement accessoire %g" % (pas, dg)))
    if largeur_plot is not None:
        mini = largeur_plot + p.get("discretion.jeu_mecanique")
        res.append(Verification(nom + "_chevauchement", _niveau(mini, pas), pas, mini, "mm",
                                "plots de %g mm au pas de %g : pas de chevauchement" % (largeur_plot, pas)))
    return res


# ---------------------------------------------------------------------------
# Support mural (tasseau biseaute)
# ---------------------------------------------------------------------------
def verifier_support_mural(p, masse_kg, levier, bras_vertical, nom="support_mural"):
    """Poids de calcul et arrachement du tasseau haut (moment autour de la cale basse)."""
    w = masse_kg * G * p.get("securite.coefficient_dynamique")
    t = w * levier / max(bras_vertical, 1.0)
    cap = p.get("pose.capacite_support_mur")
    detail = ("masse %.1f kg x g x k_dyn = %.0f N (cisaillement) ; arrachement tasseau %.0f N (levier %.0f / bras %.0f)"
              % (masse_kg, w, t, levier, bras_vertical))
    if cap is None:
        return [Verification(nom, "todo", max(w, t), None, "N",
                             detail + " ; capacite du mur INCONNUE : releve obligatoire avant pose (Aboutissants)")]
    return [Verification(nom, _niveau(max(w, t), cap), max(w, t), cap, "N", detail + " <= %.0f N" % cap)]


# ---------------------------------------------------------------------------
# Caissons : tiroirs, portes, serrures, stabilite
# ---------------------------------------------------------------------------
def longueur_glissiere(p, cle=None):
    """Plus grande glissiere du catalogue compatible avec la profondeur d'armoire."""
    cle = cle or p.get("systemes.tiroir")
    ent = _sys.SYSTEMES[cle]
    dispo = p.get("modules.profondeur_armoire") - p.get("panneaux.epaisseur_fond") - \
        p.get("panneaux.epaisseur_porte") - ent["contraintes"].get("profondeur_min_marge", 0.0)
    ok = [lg for lg in ent["geometrie"].get("longueurs", []) if lg <= dispo]
    return (max(ok) if ok else None), dispo


def verifier_tiroir(p):
    cle = p.get("systemes.tiroir")
    lg, dispo = longueur_glissiere(p, cle)
    if not _sys.SYSTEMES[cle]["geometrie"].get("longueurs"):
        return [Verification("tiroir_glissiere", "ok", dispo, None, "mm", "%s : longueur libre (%.0f mm)" % (cle, dispo))]
    return [Verification("tiroir_glissiere", "ok" if lg else "echec", lg or 0.0, dispo, "mm",
                         "%s : glissiere %s mm dans %.0f mm disponibles (fiche fabricant pour la charge %g kg)"
                         % (cle, lg, dispo, p.get("charges.charge_tiroir")))]


def verifier_porte_serrure(p):
    res = []
    ep = p.get("panneaux.epaisseur_porte")
    porte, serr = _sys.SYSTEMES[p.get("systemes.porte")], _sys.SYSTEMES[p.get("systemes.serrure")]
    mini = porte["contraintes"].get("epaisseur_min", 0.0)
    res.append(Verification("porte_epaisseur", "ok" if ep >= mini else "echec", ep, mini, "mm",
                            "%s : porte %g >= %g mm" % (p.get("systemes.porte"), ep, mini)))
    smin = serr["contraintes"].get("epaisseur_min", 0.0)
    res.append(Verification("serrure_epaisseur", "ok" if ep >= smin else "echec", ep, smin, "mm",
                            "%s : porte %g >= %g mm" % (p.get("systemes.serrure"), ep, smin)))
    lect = serr["contraintes"].get("epaisseur_max_lecture")
    if lect is not None:
        reste = ep - p.get("panneaux.lamage_lecteur")
        res.append(Verification("serrure_lecture", "ok" if reste <= lect else "echec", reste, lect, "mm",
                                "lecture a travers %g mm de bois (porte %g - lamage %g ; max %g, fiche fabricant)"
                                % (reste, ep, p.get("panneaux.lamage_lecteur"), lect)))
        rmin = p.get("discretion.retrait_min_ancre")
        res.append(Verification("serrure_lamage_discretion", "ok" if reste >= rmin else "alerte", reste, rmin, "mm",
                                "bois restant %g mm >= retrait de discretion %g mm (Incognito)" % (reste, rmin)))
    if serr["contraintes"].get("secours_obligatoire"):
        res.append(Verification("serrure_secours", "alerte", None, None, "",
                                "serrure electronique : prevoir une ouverture de secours (piles)"))
    return res


def verifier_stabilite_armoire(p):
    h = p.get("modules.hauteur_armoire")
    prof = p.get("modules.profondeur_armoire")
    elance = h / prof
    if p.get("pose.anti_basculement"):
        return [Verification("armoire_anti_basculement", "ok", elance, None, "",
                             "elancement h/p = %.1f ; fixation anti-basculement prevue" % elance)]
    niveau = "echec" if h > 1600.0 else ("alerte" if elance > 3.0 else "ok")
    return [Verification("armoire_anti_basculement", niveau, elance, 3.0, "",
                         "armoire %g mm sans fixation murale (elancement %.1f)" % (h, elance))]


# ---------------------------------------------------------------------------
# Coherences transverses
# ---------------------------------------------------------------------------
def verifier_discretion_materiaux(p):
    res = []
    niveau = p.get("discretion.niveau")
    if niveau == "invisible":
        if p.get("discretion.cuir_visible_ferme"):
            res.append(Verification("discretion_cuir", "echec", None, None, "",
                                    "niveau 'invisible' : aucun cuir visible meuble ferme (regle Incognito)"))
        for fam in ("porte", "serrure", "tiroir"):
            cle = p.get("systemes." + fam)
            if _sys.SYSTEMES[cle]["compromis"]["discretion"] <= 2:
                res.append(Verification("discretion_" + fam, "alerte", None, None, "",
                                        "%s peu discret (note %d/5) pour le niveau 'invisible'"
                                        % (cle, _sys.SYSTEMES[cle]["compromis"]["discretion"])))
    if p.get("cuir.famille") in _garn.INTERIEUR_CACHE_SEULEMENT and p.get("discretion.cuir_visible_ferme"):
        res.append(Verification("cuir_interieur_seulement", "echec", None, None, "",
                                "%s est reserve a l'interieur cache (Incognito)" % p.get("cuir.famille")))
    ess = p.get("bois.essence")
    metaux = {p.get("quincaillerie.metal")}
    for fam in ("crochet", "barre"):
        geo = _sys.SYSTEMES[p.get("systemes." + fam)]["geometrie"]
        metaux.add(geo.get("metal") or geo.get("materiau"))
    if ess in ("chene", "chene_fume") and "fer_forge_mat" in metaux:
        res.append(Verification("tanins_fer", "alerte", None, None, "",
                                "chene + fer : taches noires (tanins) - cirer/vernir les ferrures (Neogothique)"))
    _, methode = _bois.sigma_adm(ess)
    if methode != "incognito":
        res.append(Verification("essence_sigma", "alerte", None, None, "",
                                "%s : pas de contrainte admissible sourcee, repli sur la plus faible du catalogue" % ess))
    if p.get("ports.npt") and _sys.SYSTEMES[p.get("systemes.port")]["geometrie"].get("douille"):
        prof = profondeur_min_npt(p)
        e = p.get("panneaux.epaisseur_panneau_mural")
        if e < prof:
            res.append(Verification("npt_dans_panneau", "alerte", e, prof, "mm",
                                    "panneau %g mm < %.1f mm : douilles NPT dans des plots rapportes obligatoires" % (e, prof)))
    return res


def verifier_coherence(p, typologie=None):
    """Toutes les verifications qui ne dependent que des parametres."""
    typologie = typologie or p.typologie
    res = verifier_crochet(p) + verifier_barre(p, portee_barre(p))
    res += verifier_discretion_materiaux(p) + verifier_pas_ports(p) + verifier_montage_port(p)
    if typologie != "ratelier_mural":
        larg = p.get("modules.module_largeur") - 2 * p.get("panneaux.epaisseur_caisson")
        prof = p.get("modules.profondeur_armoire") - p.get("panneaux.epaisseur_fond") - p.get("panneaux.epaisseur_porte")
        res += verifier_etagere(p, larg, prof) + verifier_tiroir(p) + verifier_porte_serrure(p)
        if typologie in ("armoire_accessoires", "armoire_verrouillable"):
            res += verifier_stabilite_armoire(p)
    return res
