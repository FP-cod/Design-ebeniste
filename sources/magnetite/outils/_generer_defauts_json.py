# -*- coding: utf-8 -*-
"""Generateur du JSON de defauts (source de verite du schema). Relancer apres modification :
    python outils/_generer_defauts_json.py
"""
import os
import json
ABO = "aboutissants/common/params_globaux.py"
NEO_G = "neogothique/neogothique/catalogues/garnissage.py"
NEO_P = "neogothique/neogothique/parametres.py"
VAL, IMP, DER, LIB = "a_valider", "impose", "derive", "libre"
def P(v, u, role, plage=None, choix=None, statut=VAL, just="", source="", utilise_par=("menottes",)):
    d = {"valeur": v, "unite": u, "role": role}
    if plage is not None: d["plage"] = list(plage)
    if choix is not None: d["choix"] = list(choix)
    d.update({"statut": statut, "justification": just, "source": source, "utilise_par": list(utilise_par)})
    return d
def tour(membre, t, v, pl, up):
    return P(v, "mm", "Tour de %s taille %s (mesure anatomique, sans jeu)." % (membre, t), pl,
             just="Reference generique adulte reprise d'Aboutissants (a valider sur mensurations reelles).",
             source=ABO + " (anthropometrie.%s_tour_%s)" % (membre, t), utilise_par=up)
S = {}
S["gamme"] = {
  "nom": P("GammeCuir", "texte", "Nom de la gamme (prefixe des composants Fusion).", statut=IMP,
           just="Convention Equinox (gamme.nom).", utilise_par=("tous",)),
  "prefixe_fusion": P("gc_", "texte", "Prefixe des User Parameters Fusion.", statut=IMP,
           just="Convention eq_ / neo_ / inc_ / abo_ des autres gammes.", utilise_par=("tous",)),
}
tours = {}
for t, v, pl in (("S",150,(130,165)),("M",170,(155,185)),("L",190,(175,205)),("XL",210,(195,240))):
    tours["poignet_%s" % t] = tour("poignet", t, float(v), pl, ("menottes", "bracelets"))
for t, v, pl in (("S",200,(170,215)),("M",220,(205,240)),("L",245,(225,265)),("XL",270,(250,310))):
    tours["cheville_%s" % t] = tour("cheville", t, float(v), pl, ("menottes",))
for t, v, pl in (("S",330,(300,355)),("M",370,(345,395)),("L",410,(385,435)),("XL",450,(425,500))):
    tours["cou_%s" % t] = tour("cou", t, float(v), pl, ("colliers",))
S["tailles"] = tours
S["produit"] = {
  "membre": P("poignet", "texte", "Membre vise par la grammaire menottes (selectionne les tours et la largeur).",
              choix=("poignet", "cheville"), statut=LIB, just="Une seule grammaire pour poignet et cheville."),
  "taille": P("M", "texte", "Taille S/M/L/XL : le trou central de la rangee d'ardillon tombe sur le tour de cette taille.",
              choix=("S", "M", "L", "XL"), statut=LIB, just="Taille centrale par defaut."),
  "usage": P("jeu_leger", "texte", "Usage annonce : 'jeu_leger' (decoratif / contrainte symbolique) ou 'contention' "
             "(retenue reelle attachee a un meuble). Durcit les regles de securite.",
             choix=("jeu_leger", "contention"), statut=VAL,
             just="Le scratch et les fermetures faibles ne sont acceptables qu'en jeu leger."),
}
S["sangles"] = {
  "largeur_menotte_poignet": P(50.0, "mm", "Largeur de bande des menottes de poignet.", (30.0, 80.0),
      just="Meme largeur que les manilles de poignet de l'Entrave : assortiment visuel et repartition de pression.",
      source=NEO_P + " (garnissage.largeur_manille_poignet = 50)"),
  "largeur_menotte_cheville": P(60.0, "mm", "Largeur de bande des menottes de cheville.", (40.0, 90.0),
      just="Cheville plus forte et plus osseuse (malleoles) : bande plus large. Proposition a valider."),
  "largeur_collier": P(40.0, "mm", "Largeur de bande des colliers (grammaire future).", (20.0, 70.0),
      just="Compromis confort de la nuque / maintien. Neogothique utilise 60 mm pour une manille de cou fixe.",
      utilise_par=("colliers",)),
  "largeur_sangle_contention": P(38.0, "mm", "Largeur des sangles de contention (grammaire future).", (25.0, 60.0),
      just="Largeur courante de boucle de harnachement ; a confirmer selon boucles retenues.",
      utilise_par=("sangles",)),
  "largeur_passant": P(12.0, "mm", "Largeur du passant (bride qui maintient la pointe).", (8.0, 20.0),
      just="Assez large pour ne pas couper le cuir, assez etroit pour rester discret."),
  "epaisseur_passant": P(2.0, "mm", "Epaisseur du cuir du passant (refendu).", (1.5, 3.5),
      just="Un passant a 3,5 mm fait une surepaisseur disgracieuse : refendre a ~2 mm."),
  "jeu_passant": P(2.0, "mm", "Jeu ajoute a la largeur de bande pour le perimetre interieur du passant.", (0.5, 5.0),
      just="Le passant doit glisser sur deux epaisseurs de bande sans forcer."),
}
S["cuir"] = {
  "epaisseur_exterieure": P(3.5, "mm", "Epaisseur du cuir exterieur (fleur visible).", (2.0, 5.0),
      just="Classe 'moyenne' 3-3,5 mm : tenue de bande et trous d'ardillon durables, se cintre encore sur un poignet S."),
  "classes_epaisseur": P({"fine": [2.0, 2.5], "moyenne": [3.0, 3.5], "forte": [4.0, 5.0]}, "mm",
      "Classes d'epaisseur fournisseur (mini, maxi).", statut=IMP,
      just="Classes demandees par Fabien (2-2,5 / 3-3,5 / 4-5 mm).", utilise_par=("tous",)),
  "nb_couches": P(3, "", "Nombre de couches : 1 = exterieur seul, 2 = exterieur + doublure, 3 = exterieur + "
      "rembourrage + doublure.", (1, 3), just="3 couches = confort maximal pour la contention."),
  "epaisseur_doublure": P(1.2, "mm", "Epaisseur de la doublure cote peau.", (0.8, 2.0),
      just="Doublure agneau 1,2 mm comme Neogothique.", source=NEO_G + " (doublure_agneau_noir.epaisseur_mm = 1.2)"),
  "rembourrage": P(True, "bool", "Rembourrage entre exterieur et doublure (zone de contact du membre uniquement).",
      just="Confort et repartition de pression ; exige au moins 2 couches (doublure qui l'enferme)."),
  "rembourrage_materiau": P("mousse_latex", "texte", "Cle du rembourrage dans catalogues.cuirs.REMBOURRAGES.",
      choix=("mousse_latex", "feutre_laine", "neoprene"), just="Latex HD comme les manilles sellier fin Neogothique."),
  "epaisseur_rembourrage": P(4.0, "mm", "Epaisseur du rembourrage avant compression.", (0.0, 12.0),
      just="Neogothique : 3 mm (sellier fin). 4 mm propose pour une menotte de contention : confort accru.",
      source=NEO_G + " (cuir_sellier_fin_noir : rembourrage 3 mm)"),
  "retrait_rembourrage": P(2.0, "mm", "Retrait du rembourrage par rapport a la ligne de couture (de chaque cote).",
      (0.5, 6.0), just="La couture doit passer dans le cuir seul, pas dans la mousse."),
  "marge_rembourrage": P(6.0, "mm", "Marge longitudinale entre le rembourrage et les zones percees (rivets, trous).",
      (2.0, 20.0), just="Evite que les rivets ecrasent la mousse et que la mousse bourre sous l'ardillon."),
  "matiere": P("vachette_vegetale_pleine_fleur", "texte", "Cle du cuir exterieur dans catalogues.cuirs.CUIRS.",
      choix=("vachette_vegetale_pleine_fleur", "cuir_harnais_vegetal", "vachette_chrome_pleine_fleur"),
      just="Tannage vegetal : tranches lissables, se teinte, se patine comme le cuir Equinox."),
  "doublure_matiere": P("agneau_pleine_fleur", "texte", "Cle de la doublure dans catalogues.cuirs.DOUBLURES.",
      choix=("agneau_pleine_fleur", "veau_velours"), just="Agneau : doux et fin, comme Neogothique."),
}
S["tolerances"] = {
  "decoupe": P(0.3, "mm", "Tolerance de decoupe (+/-) des pieces de cuir.", (0.05, 1.5),
      just="Decoupe laser / emporte-piece ; a la main compter 0,5-1 mm. Estimation d'atelier."),
  "jeu_trou_ardillon": P(0.5, "mm", "Jeu diametral mini entre ardillon et trou.", (0.2, 2.0),
      just="Le cuir se referme apres poinconnage ; sans jeu l'ardillon force et deforme le trou."),
  "jeu_passage_boucle": P(1.0, "mm", "Jeu mini entre largeur de bande et passage interieur de boucle / anneau.",
      (0.0, 4.0), just="La tranche lissee ne doit pas frotter sur la quincaillerie."),
}
S["couture"] = {
  "pas_point": P(3.2, "mm", "Pas du point sellier (distance entre deux trous de griffe).", (2.0, 6.0),
      just="Pas sellerie fine de l'Entrave (8 points/pouce, ~3,1 points/cm). 4 mm pour du cuir de harnais.",
      source=NEO_G + " (_SELLERIE_FINE : sellier_pas = 3.2)"),
  "retrait_bord": P(3.0, "mm", "Retrait de la ligne de couture par rapport a la tranche (filet d'abattage).",
      (2.0, 8.0), just="Filet d'abattage a 3 mm comme Neogothique.", source=NEO_G + " (docstring : filet a 3 mm du bord)"),
  "fil": P("lin_cire_055", "texte", "Cle du fil dans catalogues.finitions.FILS.",
      choix=("lin_cire_055", "polyester_cire_080", "polyester_tresse_060"),
      just="Lin cire 0,55 mm comme la sellerie fine Neogothique.", source=NEO_G + " (sellier_fil = 0.55)"),
  "facteur_fil": P(4.0, "", "Longueur de fil = facteur x longueur de couture (point sellier a deux aiguilles).",
      (2.5, 6.0), just="Regle d'atelier courante (estimation non sourcee) ; a recaler sur un echantillon."),
  "marge_couture_percages": P(2.0, "mm", "Distance mini entre la ligne de couture et un percage (trou, rivet, fente).",
      (1.0, 6.0), just="Evite de fragiliser le pont de cuir entre couture et trou."),
}
S["jonctions"] = {
  "repli_boucle": P(30.0, "mm", "Longueur de cuir repliee autour de la barre de boucle (cote boucle).", (20.0, 60.0),
      just="Assez pour deux rivets ou une couture et loger le passant dans le repli."),
  "fixation_repli": P("rivets", "texte", "Fixation du repli de boucle.", choix=("rivets", "couture", "rivets_et_couture"),
      just="Rivets : demontable par un sellier et tres solide ; couture : plus fine. Voir docs/compromis.md."),
  "rivet": P("rivet_double_calotte_12", "texte", "Cle du rivet dans catalogues.quincaillerie.RIVETS.",
      choix=("rivet_double_calotte_9", "rivet_double_calotte_12", "rivet_cuivre_contre_rivet"),
      just="Double calotte : tete lisse des deux cotes (pas d'arete cote peau) ; tete 12 mm = tiges jusqu'a 14 mm pour la patte (empilement ~11,7 mm)."),
  "diametre_trou_rivet": P(3.0, "mm", "Diametre de poinconnage pour la tige de rivet.", (2.0, 5.0),
      just="Tige ~2,5-3 mm des rivets double calotte courants : a verifier sur la reference fournisseur."),
  "oeillet_diametre_interieur": P(5.0, "mm", "Diametre interieur des oeillets (grammaires futures : harnais, laçages).",
      (3.0, 12.0), just="Proposition a valider selon oeillets du fournisseur.", utilise_par=("harnais", "colliers")),
}
S["ardillon"] = {
  "nb_trous": P(5, "", "Nombre de trous d'ardillon (impair : le trou central = tour de la taille).", (3, 9),
      just="5 trous x 15 mm = +/-30 mm de reglage, couvre la plage d'une taille."),
  "entraxe_trous": P(15.0, "mm", "Entraxe des trous d'ardillon.", (10.0, 25.0),
      just="Pas plus fin qu'une ceinture (~25 mm) : un poignet a besoin d'un reglage fin."),
  "diametre_trou": P(4.5, "mm", "Diametre des trous d'ardillon.", (3.0, 7.0),
      just="Ardillon de boucle 50 mm ~3,5-4 mm + jeu : a verifier sur la boucle retenue."),
  "bout_apres_dernier_trou": P(30.0, "mm", "Longueur de pointe au-dela du dernier trou.", (15.0, 60.0),
      just="Assez long pour rester engage dans le passant au trou le plus serre."),
  "longueur_fente": P(14.0, "mm", "Longueur de la fente d'ardillon au pli de boucle.", (8.0, 25.0),
      just="Laisse pivoter l'ardillon sans couper le pli."),
}
S["extremites"] = {
  "rayon_ratio": P(0.5, "", "Rayon des extremites = ratio x largeur (0,5 = bout demi-rond).", (0.1, 0.5),
      just="Bout demi-rond : aucune pointe ni coin vif."),
  "rayon_tranche": P(0.8, "mm", "Rayon d'adoucissement des aretes de tranche (abat-carre / bisautage).", (0.3, 2.0),
      just="Supprime l'arete vive ; donne par l'abat-carre n 1-2. Estimation d'atelier."),
}
S["anneau_d"] = {
  "present": P(True, "bool", "Ajoute un anneau D sur patte rivetee.", just="Point d'attache (mousqueton, chaine)."),
  "reference": P("anneau_d_laiton_massif_6x30", "texte", "Cle de l'anneau dans catalogues.quincaillerie.ANNEAUX.",
      choix=("anneau_d_inox_soude_5x25", "anneau_d_inox_soude_6x30", "anneau_d_laiton_massif_6x30",
             "anneau_o_inox_soude_6x30"), just="Laiton pour l'assortiment cognac ; charge estimee plus faible que l'inox soude (voir docs/compromis.md) : a valider."),
  "position": P("oppose_boucle", "texte", "Position de la patte sur la bande.", choix=("oppose_boucle",),
      just="A l'oppose de la boucle : la traction ne passe pas par l'ardillon."),
  "largeur_patte": P(25.0, "mm", "Largeur de la patte qui tient l'anneau.", (12.0, 40.0),
      just="Doit passer dans l'anneau (passage interieur) avec le jeu de tolerance."),
  "longueur_patte": P(70.0, "mm", "Longueur developpee de la patte (avant repli autour de l'anneau).", (40.0, 110.0),
      just="Repliee en deux : 35 mm = fil de l'anneau + deux rivets en ligne avec leurs marges."),
  "fixation_patte": P("rivets_et_couture", "texte", "Fixation de la patte d'anneau sur la bande.",
      choix=("rivets", "rivets_et_couture"),
      just="Deux rivets seuls cisaillent sous la traction de retenue : couture sellier autour de la patte en plus."),
  "entraxe_rivets_patte": P(18.0, "mm", "Entraxe longitudinal des deux rivets de la patte.", (10.0, 35.0),
      just="Deux rivets en ligne : la patte ne pivote pas."),
}
S["securite"] = {
  "jeu_doigt": P(20.0, "mm", "Surplus de circonference interieure par rapport au tour mesure (un doigt doit passer a plat).",
      (15.0, 40.0), just="Un doigt a plat (~12-18 mm) sous la bande : surplus ~1,5-2 fois son epaisseur. "
      "Plancher 15 mm = pas d'effet garrot. Proche du jeu Aboutissants (20 mm).",
      source=ABO + " (anthropometrie.jeu_circonference_manille = 20)"),
  "deverrouillage_rapide": P(True, "bool", "Une attache a ouverture rapide (mousqueton panique) est prevue entre "
      "l'anneau et le point d'ancrage.", statut=VAL,
      just="Recommandation de securite : liberer la personne en quelques secondes sans cle."),
  "effort_service": P(500.0, "N", "Traction de service sur une menotte attachee.", (100.0, 3000.0),
      just="Traction laterale de verification de l'Entrave, reprise telle quelle (a valider).",
      source=NEO_P + " (charges.traction_manille = 500 N, a_valider)"),
  "coefficient_dynamique": P(1.5, "", "Majoration a-coups.", (1.0, 4.0),
      just="Valeur Neogothique.", source=NEO_P + " (charges.coef_dynamique = 1.5)"),
  "coefficient_securite": P(4.0, "", "Coefficient de securite sur la rupture du cuir et de la quincaillerie.",
      (2.0, 8.0), just="gamma_cuir Neogothique.", source=NEO_P + " (charges.gamma_cuir = 4)"),
  "rayon_mini_extremite": P(5.0, "mm", "Rayon mini des coins d'extremite (aucun coin vif).", (2.0, 20.0),
      just="Un coin de cuir de 3,5 mm peut griffer ; 5 mm mini. Proposition."),
}
S["finition"] = {
  "teinte": P("cognac", "texte", "Teinte du cuir (cle de catalogues.cuirs.TEINTES).",
      choix=("cognac", "noir", "tan", "havane", "brun_fonce", "bordeaux", "vert_bouteille", "bleu_nuit"),
      just="Cognac = cuir de reference Equinox.", utilise_par=("tous",)),
  "quincaillerie": P("laiton_massif_cw510l", "texte", "Metal de la quincaillerie (cle de catalogues.quincaillerie.METAUX).",
      choix=("inox_316", "inox_316_pvd_noir", "laiton_massif_cw510l", "laiton_patine", "acier_nickele"),
      just="Laiton avec cognac (regle d'assortiment) ; laiton sans plomb pour le contact peau (Equinox).",
      utilise_par=("tous",)),
  "tranche": P("teintee_lissee_cire", "texte", "Finition de tranche (cle de catalogues.finitions.TRANCHES).",
      choix=("brute", "teintee_lissee_cire", "peinte_edge_paint", "rembordee"),
      just="Tranches teintees et lustrees comme la sellerie fine Neogothique.", utilise_par=("tous",)),
  "fermeture": P("boucle_ardillon", "texte", "Systeme de fermeture (cle de catalogues.fermetures.FERMETURES).",
      choix=("boucle_ardillon", "boucle_ardillon_cadenas", "mousqueton", "scratch"),
      just="Boucle a ardillon : reglable, fiable, ouverture rapide sans cle."),
  "boucle": P("boucle_rouleau_50_laiton", "texte", "Cle de la boucle (catalogues.quincaillerie.BOUCLES).",
      choix=("boucle_rouleau_50_laiton", "boucle_rouleau_50_inox", "boucle_rouleau_60_laiton",
             "boucle_rouleau_60_inox", "boucle_verrouillable_50_inox"),
      just="Passage 50 mm = largeur de bande poignet."),
}
out = {"_aide": "Parametres globaux par defaut de la GammeCuir. Chaque feuille : valeur, unite, role, plage/choix, "
       "statut (impose / a_valider / derive / libre), justification, source (chemin si repris d'une autre gamme, "
       "vide = proposition GammeCuir a valider). Unites internes : mm, N. Ne pas editer pour un projet : "
       "surcharger dans parametres_gamme_cuir.json.", "sections": S}
CHEMIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gamme_cuir", "parametres_gamme_cuir.defauts.json")
with open(CHEMIN, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
