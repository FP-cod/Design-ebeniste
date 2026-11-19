# Tantra — mobilier pour adultes consentants : tantra, camouflable, cadres transformables

Paquet Python `tantra` (logique pure, testée avec pytest) + scripts Fusion 360
(`scripts_fusion/`, point d'entrée `run(context)`). Conventions reprises de
`/workspace/incognito` (non modifié) :

* cotes en **mm** ; conversion en cm **uniquement** dans `tantra/fusion_outils.py` ;
* dataclasses figées ; paramètres utilisateur Fusion préfixés **`tan_`** ;
* une fiche `.md` par typologie dans `docs/`.

> **Avertissement.** Toutes les vérifications reposent sur des **modèles simplifiés**
> (flexion de poutre, portance EC5, arrachement par analogie avec les vis, basculement
> rigide). Chaque typologie porte les niveaux « essai requis » et « visa d'ingénieur ». Avant
> toute fabrication ou vente, il faut un **ingénieur structure** et un **essai de charge réel**
> sur prototype (3 × charge de service, ancrages à 3 × 1 500 N, fatigue).

## Lancer

```
cd /workspace/tantra
python -m pytest            # tests
python -m tantra.rapport    # régénère la partie chiffrée des fiches docs/<typologie>.md
```

Dans Fusion : *Utilitaires → Scripts et compléments*, ajouter `scripts_fusion/`, exécuter
`tantra_parametres_fusion` (tous les paramètres) puis le script d'une typologie. Le document doit
être en « Z vers le haut ». Pour un meuble à deux états, modifier `tan_<clé>_etat` (0/1) puis
relancer le script : le conteneur `tantra_<typologie>` est supprimé puis reconstruit.
**Non testé dans Fusion** (pas de Fusion sur la machine) : seule la partie « plan de
construction » est testée en Python pur.

## Architecture en trois couches

| Couche | Modules | Contenu |
|---|---|---|
| 1 — paramètres globaux | `parametres.py` | unités, essences (valeurs **caractéristiques** : ρk, E, fm,k, fv,k), revêtements, charges (1 500 N/ancrage, 1 100 N/personne, ×1,5 dynamique, CS ≥ 3), anthropométrie P5/P50/P95 sourcée, 8 typologies avec plages, export `tan_...` |
| 2 — catalogues et règles | `catalogues/` (fixations, mousses, mécanismes, coûts), `regles.py`, `chiffrage.py`, `courbes.py`, `geometrie.py` | tourillons, tenons, inserts M12, verrous, axes, prix nov. 2026 ; règles de recalcul (bloc d'ancrage, flexion, tenons, cintrage, portance, double verrouillage, pincement, manœuvre, télescope) ; courbes d'Hermite par points clés ; stabilité sur 4 arêtes |
| 3 — grammaires | `grammaires/*.py`, `registre.py`, `scripts_fusion/` | une grammaire par typologie (états complets recalculés), un script Fusion par typologie |

Repère : x = largeur (depuis la gauche), y = profondeur (avant = 0), z = hauteur (sol = 0).
Chaque pièce est un profil plan extrudé selon un axe.

### Hypothèses de calcul principales

* CS appliqué aux résistances **caractéristiques** (Incognito appliquait des contraintes
  admissibles) ; bloc d'ancrage minimal 50 × 80 × 80 mm en massif.
* Arrachement d'insert : formule EC5 des vis, f_ax,k = 0,52 d^-0,5 l^-0,1 ρk^0,8 (par analogie).
* Portance : f_h = 0,082 (1 − 0,01 d) ρk, × 0,7 en travers du fil. Broches inox A4-70 :
  0,6 × 700 MPa × aire.
* Double verrouillage :
  * ≥ 2 verrous de forme, chacun seul à CS ≥ 3 ;
  * ≥ 1 à ressort qui s'enclenche seul ;
  * tous captifs.
* Pincement : jeu ≤ 8 mm ou ≥ 25 mm (EN ISO 13854). Effort de manœuvre ≤ 150 N. Recouvrement
  télescopique ≥ 3 × section.
* Stabilité : coefficient ≥ 1,5 (≥ 1,2 pour les cas accidentels).
* Anthropométrie : Pheasant & Haslegrave, *Bodyspace*, 3ᵉ éd., 2006 (adultes britanniques de
  19 à 65 ans), à recouper avec DINED (TU Delft) ; Mandal 1981 pour les assises inclinées.

### Hypothèses de chiffrage (estimations datées de novembre 2026, HT)

* **Bois (€/m³)** : chêne 2 400, hêtre 1 500, frêne 1 700, noyer 4 300, lamellé de hêtre 1 900,
  contreplaqué bouleau 4 200.
* **Pertes** : massif × 1,8, lamellé × 1,25, contreplaqué × 1,35.
* **Main-d'œuvre** : ébéniste 58 €/h, tapissier 52 €/h ; tapisserie 1,5 h + 1,4 h/m² ; montage
  2 h + contrôle 1,5 h.
* **Autres postes** : finition 1,2 €/kg de bois ; emballage 45 € ; amortissement moule 120 € par
  pièce cintrée.
* **Prix** : coefficient commercial 1,45 ; TVA 20 % ; fourchette ± 25 %. Prototype :
  main-d'œuvre × 2,5 et moule entier.

## Typologies et chiffrages

| Typologie | Volet | Prix indicatif TTC | Fourchette | Prototype |
|---|---|---|---|---|
| tantra_chaise_double_courbe | tantra | 4930 € | 3700–6150 € | ≈ 14750 € |
| tantra_fauteuil_lombaire | tantra | 4080 € | 3050–5100 € | ≈ 13300 € |
| tantra_banquette_deux_niveaux | tantra | 7410 € | 5550–9250 € | ≈ 20300 € |
| tantra_siege_repose_genoux | tantra | 3200 € | 2400–4000 € | ≈ 7000 € |
| camo_canape | camouflable | 8260 € | 6200–10350 € | ≈ 15750 € |
| camo_fauteuil | camouflable | 6490 € | 4850–8100 € | ≈ 13150 € |
| cadre_desserte_genoux | cadre | 4430 € | 3300–5550 € | ≈ 9000 € |

| Volet | Typologie | Fiche |
|---|---|---|
| 1 Tantra & bien-être (fixe, assumé) | chaise double courbe ; fauteuil lombaire ; banquette deux niveaux ; siège à repose-genoux | `tantra_*.md` |
| 2 Camouflable (zéro élément visible) | canapé ; bergère à repose-genoux ; *fiches* : table basse, banc d'entrée, tête de lit | `camo_*.md`, `fiches_camouflables.md` |
| 3 Cadres transformables | desserte → cadre à genoux ; *étude* : table basse → cadre incliné | `cadre_*.md` |
| Marché | Liberator, Sportsheets, Tantra Chair, Kinky Beds, BondageBox… | `marche_camouflable.md` |

## Compromis clés

1. **Prix artisanal et marché** : 3,2 à 8,3 k€ TTC, soit 2,5 à 5 fois le marché de masse
   (Tantra Chair 1 449 $, sofas UE 400–900 €). Le segment français vide se situe à 1–3 k€ et
   demande une petite série (gabarits, moules amortis sur 50 pièces et plus).
2. **Ancrage et effort extérieur** : 1 500 N tiré de l'extérieur fait basculer **tout** meuble
   posé. Les ancrages retiennent une personne installée **sur** le meuble (effort interne).
   C'est pourquoi la desserte-cadre place l'usager sur le meuble et prévoit un tirant mural
   contre la traction à vide, et pourquoi la table inclinée est restée à l'étude.
3. **Confort et coût** : coques plus épaisses (moins de flasques) ou rayons plus doux (cale en
   mousse plutôt qu'en coque).
4. **Discrétion et tenue** : la traverse avant du canapé passe à 70 mm pour loger l'insert ;
   les caches et manchettes ajoutent de la quincaillerie (≈ un tiers du prix matière sur le canapé).
5. **Taille unique et anthropométrie** : le siège à repose-genoux ne couvre pas P5–P95 avec un
   seul jeu de cotes.

## Tests

`python -m pytest` : couches 1-2, règles, courbes et géométrie, toutes les grammaires dans tous
les états (conformité par défaut et cas non conformes provoqués), discrétion, double
verrouillage, pincement, plans Fusion et générateur de fiches. Le fichier
`tests/test_recalculs.py` appartient au travail « TantraGamme » voisin (voir plus bas) ; il
passe aussi.

## Coexistence avec « TantraGamme »

`README.md` (racine), `TYPOLOGIES.md`, `TantraGamme/`, `outils/` et `tests/test_recalculs.py`
ont été écrits par un autre travail (passe 1 d'un add-in « TantraGamme », paramètres `TG_*`).
Ils n'ont pas été modifiés. Ce README-ci décrit le paquet `tantra`.

## Questions ouvertes

* Recouper les valeurs anthropométriques sur DINED ; décider s'il faut deux tailles pour le
  siège à repose-genoux.
* Obtenir des devis réels (lamellé-cintré, cuir, Soss, verrous inox, vérins) pour remplacer
  les prix catalogue.
* Confirmer les normes applicables : EN 1728, EN 12520 et EN 12521, EN 14749 (anti-basculement),
  EN ISO 13854 ; le mobilier érotique n'a pas de norme dédiée.
* Table inclinée : marche-plateforme intégrée ou fixation murale obligatoire ?
* Fusion : valider les scripts dans un vrai document (orientation Z, signe des plans décalés).
