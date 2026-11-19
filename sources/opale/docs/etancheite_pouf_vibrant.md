# Étanchéité du pouf vibrant Incognito

Complète le plan d'essai déjà esquissé dans [pouf_vibrant.md](pouf_vibrant.md).
Objectif de conception : **IP67** du boîtier électronique et de chaque
étage de module (IEC 60529 : poussière étanche, immersion 1 m / 30 min).
Aucun 230 V dans le meuble. Les modèles et gorges sont des **hypothèses**
à valider par essai.

Ce document couvre l'étanchéité **des boîtiers, joints, presse-étoupes
et de la selle** (éclaboussures, transpiration, lubrifiants d'usage,
désinfection). Il ne décrit pas de collecte de fluide, ni de plan de
vidange, ni de surface dédiée à un contact fluide — fonctions hors
périmètre Incognito.

## Boîtier électronique (IP67)

- Enveloppe PETG 120 × 80 × 45 mm, joint torique **du commerce** (ISO 3601)
  dans une gorge calculée, vis hors du plan de joint ou puits étanches.
- **Dissipation des drivers** : les drivers de puissance sont dans ce
  boîtier ou dans un capot attenant. L'IP67 empêche une aération libre :
  prévoir un chemin thermique (puits, patte vers une semelle) et
  dimensionner d'après la conso. continue (~132 W max. des trois modules,
  typiquement bien moins en régime). Mesure d'échauffement obligatoire.
  Des ouïes du *caisson bois* (dessous, discrètes) ventilent le volume
  d'air autour du boîtier, pas l'intérieur IP67.
- **Évent ePTFE** (membrane type Gore Protective Vents ou équivalent) :
  égalise la pression (évite d'aspirer de l'eau par les joints au
  refroidissement) tout en restant étanche aux gouttes et à la poussière.
  Orientation vers le bas, non masqué par de la mousse saturée.
- **Antenne** (BLE / Wi-Fi) : fenêtre plastique dans le couvercle,
  **non masquée** par une tôle, un plan de masse continu ou un cache
  métallisé. Le bois du caisson atténue un peu le 2,4 GHz : une fente
  ou une zone mince sous le fond, côté fenêtre, est à valider par essai
  de portée (quelques mètres dans le salon).

## Joints toriques ISO 3601 et gorges

- Joints **du commerce**, pas de TPU FDM (porosité inter-couches,
  rugosité). Un TPU SLS post-traité n'est pas le défaut, à valider par essai.
- Gorges selon ISO 3601-2 (ou fiche fabricant). **Écrasement (squeeze)
  15–25 %** sur le diamètre de section (typiquement ~20 % en radial,
  15–20 % en face). Sous 15 %, risque de fuite ; au-delà de 25 %,
  extrusion et endommagement au montage.
- Largeur de gorge permettant le gonflement du matériau (surtout NBR
  dans certaines huiles — voir matrice). État de surface Ra ≤ 1,6 µm
  sur la portée, pas de plan de joint au fond de gorge, chanfreins
  d'entrée pour le montage, graisse silicone compatible avec le polymère
  et avec un contact cutané indirect.

## Presse-étoupes, thermorétractable, câbles

- Presse-étoupes IP67 (métriques, joint d'étanchéité + écrou), câble
  de diamètre dans la plage du gland, écrou serré au couple fabricant.
  Entrée 24 V au fond / face arrière du caisson (`presse_etoupe_alim`).
- Gaine **thermorétractable à colle** (double paroi) sur les épissures
  et les dénudages dans le caisson, en complément, pas en lieu et place
  du presse-étoupe.
- Passages **caisson → selle / platine** : boucle souple (rotation
  limitée, pas de slip-ring par défaut), passage par un gland ou un
  soufflet. Un collecteur tournant, s'il était exigé plus tard, est un
  point faible IP à qualifier à part.
- **Soufflet de selle** (élastomère VMQ ou TPU souple du commerce, ou
  TPU imprimé seulement s'il n'est pas la barrière IP67) autour de
  l'équipage mobile et de l'embout : protège le haut du module des
  éclaboussures et de la poussière, sans prétendre à l'immersion de
  la selle elle-même (la selle est un organe retiré / nettoyé).

## Protection des cellules de charge

- Logements PETG sous la couronne, drainés vers l'extérieur du *logement*
  uniquement au sens d'éviter l'eau stagnante sur la jauge (pas un
  circuit de fluide). Joint ou silicone d'étanchéité autour du câble
  de pont. Butée de surcharge hors du chemin d'eau.
- Conformal coating ou potting léger sur le côté jauge si le fabricant
  le permet (humidité → dérive de zéro, déjà surveillée en logiciel).

## Matrice de compatibilité (joints et soufflets)

Indications qualitatives, à confirmer sur fiches fabricant et essai
de gonflement (ASTM D471 ou équivalent). Légende : C = compatible,
L = limité / à valider, N = non recommandé.

| Milieu | EPDM | VMQ (silicone) | NBR | FKM (viton) |
| --- | :---: | :---: | :---: | :---: |
| Eau, nettoyage aqueux | C | C | C | C |
| Lubrifiant à base d'eau | C | C | C | C |
| Lubrifiant silicone | C | L (peut gonfler le VMQ) | C | C |
| Lubrifiant à l'huile / ester | N | L | C | C |
| Transpiration (eau, sel, acide lactique) | C | C | C | C |
| Désinfectant alcool (isopropanol, éthanol) | L | L | L | C |
| Désinfectant oxydant (eau oxygénée diluée, persulfate) | L | L | N | L |
| Désinfectant quaternaire / savon | C | C | C | C |

Défaut proposé : **VMQ** pour le soufflet et les joints proches de la
selle (température, contact indirect) ; **NBR** ou **FKM** pour le
boîtier électronique selon les graisses de montage. Éviter de
mélanger un lubrifiant silicone abondant avec un soufflet VMQ sans essai.

## Protocole d'essai et critères

1. **Contrôle d'assemblage** : cotes de gorge, écrasement 15–25 %, état
   de surface, graisse, couple des glands, fenêtre d'antenne dégagée,
   évent ePTFE orienté, aucun TPU FDM en torique d'IP67.
2. **IP6X** (poussière) si moyen disponible ; sinon inspection des
   labyrinthes et presse-étoupes, et essai fonctionnel après talc / farine
   de bois en atelier (indicatif seulement).
3. **Pulvérisation** (préalable, plus sévère que l'usage salon) :
   jet d'eau sur les joints, la selle en place avec capuchon, le
   soufflet et le boîtier, quelques minutes. Critère : pas d'eau à
   l'intérieur du boîtier ni des étages, isolement conservé.
4. **IPX7** : chaque volume (boîtier ESP32, étage vibration, piston,
   rotation) immergé **séparément**, 1,00 m, 30 min, eau 15–35 °C.
   Alim. 24 V débranchée ou hors liquide. Ouverture, inspection,
   séchage, essai fonctionnel, mesure d'isolement.
5. **Condensation** : cycle chaud / froid (par exemple 5 °C / 40 °C,
   quelques cycles) pour vérifier que l'évent évite l'aspiration d'eau
   et que la dérive de zéro des cellules reste sous le seuil logiciel
   (2,5 kg) après retare.
6. **Orifice d'embout** : capuchon + torique (état pouf). La housse
   montée n'est pas une barrière IP garantie.
7. **Critères d'acceptation** : aucune eau visible à l'intérieur ;
   isolement conservé ; drivers, fins de course et enable fonctionnels
   après séchage ; joints non extrudés, non gonflés hors tolérance ;
   portée radio encore conforme à l'essai de référence ; présence
   (tare + seuil) recalee et opérationnelle.
8. **Traçabilité** : PV (date, température, photos, n° de joints,
   couple de glands). Un échec relance gorge / joint / gland, pas un
   « TPU imprimable en plus ».

## Points de vigilance d'assemblage

- Ne pas peindre ou métalliser la fenêtre d'antenne.
- Ne pas obturer l'évent ePTFE (étiquette, mousse, revêtement).
- Respecter l'ordre : joint en gorge, greffer le capot sans cisailler
  le torique, vis en étoile au couple.
- Câbles : rayon de courbure, pas de traction sur le gland, boucle
  de service pour la platine (rotation limitée).
- Cellules : ne pas précharger la butée de surcharge au montage
  (jeu ~0,4 mm à vide / en service nominal).
- Après une désinfection agressive, rincer et vérifier l'état du
  soufflet et des joints VMQ.
