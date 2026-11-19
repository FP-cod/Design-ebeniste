# Table basse → cadre incliné (volet 3 — étude, grammaire non livrée)

**Statut :** typologie étudiée et chiffrée en ordre de grandeur ; **pas de grammaire ni de
script Fusion** dans cette livraison. Les cotes de départ restent dans
`parametres.CADRE_TABLE_INCLINEE` (1 100 × 700 × 420 mm, angle 70 à 82°).

## Concept

Le plateau de la table basse est fait de deux vantaux en portefeuille. Dépliés, ils forment
une planche de ~2 000 à 2 200 mm. Celle-ci se redresse autour d'un **axe traversant Ø20**
placé à une extrémité du piètement, jusqu'à ~78°. Deux **contrefiches en compas**, rangées dans
la ceinture et articulées à l'autre extrémité, viennent se verrouiller sous la planche (doigt
d'indexage + goupille captive). L'éclissage du portefeuille est verrouillé lui aussi, et des
vérins à gaz assistent le redressement.

## Pourquoi elle n'est pas livrée (résultats chiffrés)

1. **Géométrie du compas** (`tantra.grammaires._cadre.appui_compas`, testée). Avec 940 mm
   entre pivots et 78° :
   * une contrefiche de 900 mm (la plus longue qu'on range dans une table de 1 m) **n'atteint
     pas** la planche ;
   * à 940 mm, elle la rejoint à 391 mm du pivot, ce qui laisse ~1 600 mm de planche en console.
2. **Flexion de la planche en console** : avec 2 × 1 500 N en tête sur 1 600 mm et des
   montants de vantail en chêne de 2 × 45 × 120, CS 1,8. Il faut 2 × 60 × 140 pour CS 3,3, soit
   un plateau plié de ~120 mm d'épaisseur : lourd et massif pour une table basse.
3. **Stabilité** : la personne est debout **au sol**, donc les tractions sur les poignets sont
   des efforts **extérieurs**. Une personne qui se penche en arrière (W × tan 25° ≈ 510 N à
   ~2 m) donne un moment de ~1 000 N·m, contre ~130 N·m pour le poids propre (45 kg). Il faut
   une **fixation murale ou au sol obligatoire**, ou une marche-plateforme intégrée sur laquelle
   la personne se tient (ce qui rend l'effort interne).
4. **Hauteur sous plafond** : planche de 2 000 mm et axe à ~360 mm, donc un sommet à ~2 320 mm,
   limite sous un plafond de 2,50 m.

## Piste pour une passe suivante

* Ajouter une **marche-plateforme** (tablette basse retournée, comme sur la desserte), qui rend
  les efforts internes.
* Limiter la planche à ~1 900 mm et l'angle à 75°.
* Utiliser des contrefiches télescopiques à 2 positions (recouvrement ≥ 3 × section) au lieu
  d'un compas fixe.
* Ordre de grandeur de prix, à confirmer : 5 500 à 7 500 € TTC en artisanal (vantaux massifs,
  2 axes Ø20, 4 liaisons doublement verrouillées, vérins).
