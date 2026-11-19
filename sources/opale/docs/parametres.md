# Paramètres globaux — gamme Incognito (couche 1)

Ce document décrit le vocabulaire partagé de la gamme, implémenté dans
`incognito/parametres.py`. Toutes les longueurs sont en **millimètres**,
les forces en **newtons**, les contraintes et modules en **MPa**, les
masses volumiques en **kg/m³**.

Les dataclasses sont **figées**. On instancie une variante plutôt que de
muter un défaut.

> **Avertissement.** Les valeurs mécaniques, les charges et les
> vérifications de section sont des *hypothèses de conception*. Elles
> ne constituent ni un justificatif Eurocode 5, ni une certification.
> Tout ancrage destiné à retenir une personne exige le visa d'un
> ingénieur et un **essai de charge réel**.

La gamme s'adresse exclusivement à des **adultes consentants**. À
l'état fermé, aucune ferrure, aucun anneau, aucun cuir n'est visible
(règle de discrétion).

---

## Dimensions salon par typologie

Hypothèses d'usage européen courant (assise de salon ~420–450 mm,
tables basses ~400–450 mm). Ce ne sont pas des valeurs normalisées NF.

### Hauteurs de référence

| Grandeur | Défaut | Plage | Unité | Commentaire |
| --- | ---: | --- | --- | --- |
| Hauteur d'assise (canapé, fauteuil, banquette, banc d'entrée, pouf) | 430 | 420–450 | mm | Dessus de coussin |
| Hauteur de table basse | 420 | 400–450 | mm | Dessus de plateau |

### Canapé

| Cote | Défaut | Plage | Commentaire |
| --- | ---: | --- | --- |
| `hauteur_assise` | 430 | 420–450 | Alignée sur la gamme |
| `profondeur_hors_tout` | 980 | 900–1100 | Y compris dossier |
| `profondeur_assise` | 560 | 520–620 | Utile, hors dossier |
| `hauteur_dossier` | 900 | 820–1000 | Depuis le sol |
| `largeur_deux_places` | 1700 | 1550–1900 | Hors-tout |
| `largeur_trois_places` | 2200 | 2000–2400 | Hors-tout |
| `hauteur_accoudoir` | 630 | 580–680 | Depuis le sol |

### Fauteuil

| Cote | Défaut | Plage | Commentaire |
| --- | ---: | --- | --- |
| `hauteur_assise` | 430 | 420–450 | |
| `largeur_hors_tout` | 820 | 750–920 | Y compris accoudoirs |
| `profondeur_hors_tout` | 900 | 820–1000 | |
| `profondeur_assise` | 560 | 520–620 | |
| `hauteur_dossier` | 900 | 820–1000 | |

### Table basse

| Cote | Défaut | Plage | Commentaire |
| --- | ---: | --- | --- |
| `hauteur` | 420 | 400–450 | |
| `longueur` | 1200 | 1000–1400 | |
| `largeur` | 700 | 550–850 | |
| `epaisseur_plateau` | 28 | 22–40 | Massif ou plaqué |

### Banc d'entrée

Distinct de la *banquette* de salon (premier meuble de la gamme).

| Cote | Défaut | Plage | Commentaire |
| --- | ---: | --- | --- |
| `hauteur_assise` | 430 | 420–450 | |
| `longueur` | 1200 | 1000–1400 | |
| `profondeur` | 400 | 350–480 | Plus étroit qu'une banquette |
| `hauteur_dossier` | 800 | 0–900 | 0 si sans dossier |

### Pouf

| Cote | Défaut | Plage | Commentaire |
| --- | ---: | --- | --- |
| `hauteur` | 430 | 420–450 | Alignée sur l'assise |
| `largeur` | 500 | 400–650 | Ou diamètre |
| `profondeur` | 500 | 400–650 | |

### Bibliothèque

| Cote | Défaut | Plage | Commentaire |
| --- | ---: | --- | --- |
| `hauteur` | 2000 | 1800–2300 | Y compris corniche |
| `largeur` | 1000 | 800–1400 | Un corps |
| `profondeur` | 350 | 300–420 | |
| `epaisseur_montant` | 22 | 18–32 | |
| `entraxe_tablettes` | 320 | 250–400 | |

### Banquette (premier meuble)

Les cotes du banc fonctionnel (appui 700 × 1150 mm) sont des
**hypothèses documentées** : le squelette Equinox fourni ne contenait
pas les cotes du banc Feuille / Flore.

| Cote | Défaut | Plage | Commentaire |
| --- | ---: | --- | --- |
| `hauteur_assise` | 430 | 420–450 | État fermé |
| `longueur` | 1300 | 1200–1600 | Doit loger 1150 mm + parois |
| `profondeur_hors_tout` | 680 | 600–780 | Trop faible : stabilité en cause |
| `profondeur_assise` | 540 | 500–620 | |
| `hauteur_dossier` | 880 | 800–980 | |
| `hauteur_pieds` | 120 | 90–160 | Tournés / fuseaux |
| `hauteur_appui_banc` | 700 | 650–750 | Dessus du cuir, état déployé |
| `longueur_appui_banc` | 1150 | 1100–1250 | Hypothèse |
| `largeur_appui_banc` | 320 | 280–380 | Largeur du coussin d'appui |

---

## Essences classiques

Valeurs approximatives à **12 % d'humidité**, bois de fil.

**Sources.** USDA Forest Products Laboratory, *Wood Handbook*
(FPL-GTR-282) pour les moyennes de masse volumique, de module
d'élasticité et de MOR ; classes NF EN 338 (feuillus D30 / D40) pour
l'ordre de grandeur de `fm,k` ; fiches CIRAD / FCBA pour les feuillus
européens.

**Hypothèses.** `fm,k` est un ordre de grandeur de 5e centile, nettement
inférieur au MOR moyen de la littérature. La contrainte admissible
retenue vaut environ `fm,k / 2,8` à `/ 3,5` et sert uniquement aux
vérifications simplifiées du package. Elle n'inclut pas `k_mod`, `γ_M`,
l'humidité de service, les nœuds ni le fil dévié.

| Identifiant | Affichage | Nom latin | ρ (kg/m³) | E (MPa) | fm,k (MPa) | σ_adm flexion (MPa) | τ_adm (MPa) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `chene` | Chêne | *Quercus robur / petraea* | 710 | 12 500 | 40 | 14 | 2,0 |
| `noyer` | Noyer | *Juglans regia* | 650 | 11 600 | 36 | 12 | 1,8 |
| `hetre` | Hêtre | *Fagus sylvatica* | 720 | 14 000 | 40 | 14 | 2,0 |
| `frene` | Frêne | *Fraxinus excelsior* | 690 | 13 000 | 40 | 14 | 2,0 |
| `merisier` | Merisier | *Prunus avium* | 610 | 10 300 | 30 | 10 | 1,6 |

Essence par défaut de la gamme : **chêne** (tenue mécanique et
apparence classique).

---

## Revêtements discrets

Règle de gamme : **zéro cuir visible** à l'état fermé. Le cuir
(cognac ou noir) est réservé à l'intérieur caché (banc déployé).

| Identifiant | Affichage | Famille | Épaisseur (mm) | Usage | Couleurs typiques |
| --- | --- | --- | ---: | --- | --- |
| `velours` | Velours | tissu | 2,0 | extérieur visible | gris souris, vert sauge, crème, marine, taupe |
| `lin` | Lin | tissu | 1,5 | extérieur visible | naturel, ivoire, gris clair, terre |
| `laine_bouclee` | Laine bouclée | tissu | 3,5 | extérieur visible | ivoire, grège, charbon, camel |
| `tissu_chine` | Tissu chiné | tissu | 2,0 | extérieur visible | gris, beige, bleu-gris |
| `cuir_cognac` | Cuir cognac | cuir | 2,0 | intérieur caché | cognac |
| `cuir_noir` | Cuir noir | cuir | 2,0 | intérieur caché | noir |
| `cuir_sobre_facade` | Cuir sobre de façade | cuir | 2,0 | *dérogation* | cognac clair, havane, noir mat |

La dérogation « club en cuir uni » peut passer visuellement pour un
meuble de salon, mais elle enfreint la règle de gamme. Elle n'est **pas
retenue par défaut** et est signalée par la validation.

Défauts : façade **velours**, banc **cuir cognac**.

---

## Paramètres de discrétion

| Paramètre | Défaut | Unité | Rôle |
| --- | ---: | --- | --- |
| `retrait_min_ancre_sous_surface_mm` | 10 | mm | Bois ou cache minimal entre l'ancre et toute surface visible à l'état fermé |
| `jeu_mecanique_mm` | 2 | mm | Jeu des charnières, joues, trappes |
| `jeu_repli_mm` | 4 | mm | Marge pour que le banc replié rentre (tissu, tolérances, hygrométrie) |
| `epaisseur_recouvrement_bois_mm` | 10 | mm | Cache bois affleurant typique |
| `epaisseur_recouvrement_tissu_mm` | 2 | mm | Tissu de façade hors mousse |
| `epaisseur_min_paroi_visible_mm` | 18 | mm | Minimum d'une paroi vue de l'extérieur |
| `mortaise_charniere_recul_bord_mm` | 8 | mm | Recul d'une mortaise Soss par rapport au chant visible |

**Compromis.** Augmenter un retrait améliore la discrétion mais réduit
la section de bois utile autour d'une ancre (voir ci-dessous).

---

## Paramètres de charge des ancrages

| Paramètre | Défaut | Unité | Commentaire |
| --- | ---: | --- | --- |
| `charge_service_ancrage_n` | 1500 | N | Par point d'ancrage (hypothèse : adulte, traction) |
| `charge_service_appui_n` | 1500 | N | Verticale sur l'appui du banc (un adulte + marge) |
| `coefficient_securite` | 3 | — | **Minimum recommandé : 3** |
| `charge_rupture_visee_ancrage_n` | 4500 | N | Calculée : service × CS (cible, non certifiée) |

Un coefficient inférieur à 3 est **non conforme** dans la validation.
Un mouvement brusque, une chute ou un effet de levier peut dépasser la
charge de service. Ces nombres ne couvrent pas un usage dynamique
sévère.

---

## Validation d'une ancre encastrée

La fonction `valider_ancrage(essence, geometrie, charges, discretion)`
applique un **modèle volontairement simplifié** :

- section nette sous l'hypothèse σ = F × CS / σ_adm ;
- paroi de cisaillement : F × CS = τ_adm × L_encastrement × t × n_plans ;
- le cache de discrétion n'est *pas* compté dans la section résistante
  s'il n'est pas structurel ;
- distance au bord minimale retenue : max(25 mm, 2 × Ø), contre le fendage.

Un signalement `essai_requis` est **toujours** émis.

Géométrie d'ancre par défaut (déjà dimensionnée pour passer le modèle
simplifié en chêne, 1500 N, CS 3, retrait 10 mm) :

| Cote | Défaut | mm |
| --- | ---: | --- |
| Diamètre d'insert | 12 | |
| Longueur d'encastrement | 80 | |
| Épaisseur du bloc | 54 | |
| Largeur du bloc | 70 | |
| Longueur du bloc | 80 | |
| Recouvrement (cache) | 10 | |
| Distance au bord | 30 | |

### Compromis discrétion / solidité signalés

1. **Rail trop mince.** Un panneau d'appui élégant de 22–28 mm ne peut
   pas noyer une ancre 1500 N / CS 3 tout en conservant 10 mm de
   retrait : il resterait trop peu de bois. Recaler un *bloc d'ancrage
   local* plus volumineux, masqué sous le cuir du banc (c'est la règle
   de `incognito.regles.recaler_bloc_ancrage`). Épaissir tout le rail
   ferait sortir le pack du caisson ou alourdrait l'apparence fermée.
2. **Retrait vs paroi.** Réduire le cache pour gagner de la section
   trahit l'ancre (témoin, son, perçage). On épaissit le bloc caché,
   on ne réduit pas le retrait visible.
3. **Distance au bord.** Rapprocher l'ancre du chant facilite parfois
   l'attache d'un bracelet, mais favorise le fendage.
4. **Cuir de façade.** Esthétique « club » possible, règle de gamme
   enfreinte.

### Ce qui exige un ingénieur ou un essai réel

- justificatif Eurocode 5 (ou équivalent) avec `k_mod`, `γ_M`, classes
  de service, défauts du bois, orientation du fil ;
- dimensionnement des assemblages (tourillons, mortaises, collage)
  sous charge dynamique ;
- **essai de charge réel** sur prototype : chaque ancrage et l'appui,
  statique puis avec à-coups, au moins jusqu'à la charge de rupture
  visée ;
- tenue dans le temps (humidité, fluage, vieillissement de la colle).

---

## Export Fusion 360

`vers_parametres_fusion()` retourne un dictionnaire

```text
nom → (valeur, unité, commentaire)
```

Les noms sont ASCII, préfixés par `inc_`. Les longueurs restent en mm
(unité utilisateur Fusion). La conversion vers les **cm internes** de
l'API est exclusivement dans `incognito.fusion_outils` et les scripts
`scripts_fusion/`.

Le script `scripts_fusion/incognito_parametres_fusion.py` crée ou met à
jour ces paramètres (`UserParameters`) : un paramètre déjà présent voit
son expression et son commentaire rafraîchis.

---

## Questions ouvertes (couche 1)

Voir aussi `docs/banquette.md`. En particulier : essence préférée,
charge cible par ancrage, revêtement de façade et couleur, cuir du
banc (cognac ou noir).


## Paramètres du module de selle (pouf)

| Paramètre Fusion | Défaut | Commentaire |
| --- | --- | --- |
| `inc_sybian_gamme` | 1 | 0 = entrée (balourd), 1 = haut (voice coil, jusqu'à 3 modules) |
| `inc_sybian_tension` | 24 V | Aucun 230 V dans le meuble |

Détail : [pouf_vibrant.md](pouf_vibrant.md).
