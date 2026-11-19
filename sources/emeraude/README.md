# Gamme Tantra — fauteuils tantriques fixes en ébénisterie massive

Mobilier érotique pour adultes, assumé : pièces **fixes** (ni camouflables, ni modulables),
esthétique moderne à dominante classique, bois massif (chêne, frêne, noyer) et garnissage
cuir. Projet **distinct de la gamme Incognito**.

Statut : **passe 1** — architecture, couches 1 et 2 codées et testées, 4 typologies proposées
(voir `TYPOLOGIES.md`). Les scripts de grammaire (couche 3) attendent le choix des typologies.

## Arborescence

```
tantra/
├── README.md                    ← ce fichier (architecture, règles, compromis)
├── TYPOLOGIES.md                ← 4 typologies : cotes, angles, jonctions, chiffrage
├── TantraGamme/                 ← dossier d'add-in Fusion 360 (à copier dans AddIns)
│   ├── TantraGamme.manifest
│   ├── TantraGamme.py           ← point d'entrée run()/stop() ; seul fichier à importer adsk en tête
│   └── lib/
│       ├── __init__.py
│       ├── params_globaux.py    ← COUCHE 1 (pur Python)
│       ├── catalogues.py        ← COUCHE 2 (pur Python)
│       └── fusion_params.py     ← pont vers les User Parameters (import adsk paresseux)
├── tests/test_recalculs.py      ← 13 tests unitaires des recalculs (sans Fusion)
└── outils/chiffrage_indicatif.py← chiffrage des 4 typologies via la couche 2
```

Vérifications : `python -m py_compile` sur tous les modules ✔ ; `python -m unittest discover -s tests -v` ✔ (13/13) ;
manifest JSON valide ✔. Non testé dans Fusion 360 lui-même (pas de Fusion sur la machine de travail).

Installation Fusion : copier `TantraGamme/` dans
`%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\` (Windows) ou
`~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/` (macOS),
puis *Utilitaires → Scripts et compléments → TantraGamme → Exécuter*. Effet actuel :
création/mise à jour de 17 paramètres utilisateur `TG_*` dans le design actif.

## Architecture en trois couches

### (a) Couche 1 — paramètres globaux (`params_globaux.py`)
Tout ce qui est commun à la gamme, sans géométrie spécifique :

| Bloc | Contenu | Exemples (défaut) |
|---|---|---|
| `Anthropometrie` | plage P5 femme – P95 homme | poplitée 380–490 mm, profondeur fesse-poplité 440–530, hanches P95 430, centre lombaire 170–250 mm au-dessus de l'assise |
| `ChargesConception` | usage à 2, dynamique | 2 × 120 kg × coef. dynamique 2,0 → **4 709 N** ; effort latéral 15 % ; flèche ≤ L/300 |
| `ESSENCES` | chêne, frêne, noyer | ρ, prix €/m³ bas/haut, E, fc0k, fmk, fvk (assimilés EN 338 D30–D40), retrait |
| `MOUSSES` | HR35, HR45, HR55 extra-ferme, visco 50, latex 65 | densité, portance, €/m³ |
| `REVETEMENTS` | cuir pigmenté, aniline, simili PU médical, velours déperlant | €/m², coef. chute, **nettoyabilité 1–5** |
| `FINITIONS` | huile-cire, vernis PU mat, huile | €/m², nettoyabilité |
| `Tarifs` | taux horaires, coefs déchet | ébéniste 45–70 €/h, tapissier 40–60 €/h, déchet 1,5 (droit) / 2,2 (chantourné) |
| `Ergonomie` | bornes de gamme | angle assise/dossier 100–125°, bascule ≤ 15°, rayon d'arête ≥ 6 mm, cale 90 mm / 18°, boudin lombaire Ø160 |

Chaque champ porte une docstring : **unité, plage admissible, rôle**. L'instance `PARAMS`
est importée par les typologies ; `parametres_fusion()` en extrait la liste à plat pour Fusion.
Unités : mm partout dans le code ; Fusion travaille en cm en interne → `mm_vers_cm()` ou
expressions `"450 mm"`.

### (b) Couche 2 — catalogues et règles de recalcul (`catalogues.py`)
Catalogues : tourillons (Ø 6–20), largeurs de bédane, inserts M6/M8/M10 (Ø de perçage feuillus),
boulons + écrous-barillets, vis, colles (vinylique D3, PU D4, époxy, colle de peau, urée-formol).

Règles de recalcul (fonctions pures, testées) :

| Fonction | Règle |
|---|---|
| `diametre_tourillon(e)` | d ≈ e/3 → Ø standard, plafonné à e/2,5 (paroi ≥ 0,3·e) |
| `spec_tourillons(e, largeur)` | longueur 5·d, bord ≥ 2·d, entraxe ≈ 6·d (min 4·d), n ≥ 2 |
| `spec_tenon(e_trav, l_trav, e_montant)` | épaisseur e/3 → bédane ; longueur 2/3 du montant (≤ 5·t) ; double tenon si largeur > 6·t ; cheville Ø ≈ 0,8·t ; alerte si paroi < t |
| `section_pied(charge, h, essence, …)` | max(compression N/fc0d, flambement Euler avec cs = 3, 3 × tenon, minimum esthétique) arrondi à 5 mm |
| `hauteur_traverse(portée, charge, b, essence)` | max(flexion M = WL/8, flèche ≤ L/300 en service, minimum) |
| `avant_trou_vis(d, essence)` | 0,7·d en feuillu dense, 0,6·d sinon |
| `resistance_arrachement_vis(d, l, essence)` | EC5 §8.7.2 simplifié (indicatif) |
| `marge_basculement(x, xmin, xmax)` | distance du point de charge au bord du polygone d'appui (viser ≥ 100 mm) |
| `prix_bois(V, essence, cintre)` | **prix = V net × coef. déchet × prix/m³ essence** |
| `chiffrage(nomenclature, essence)` | bois + garnissage + quincaillerie/finition + heures × taux → fourchette (bas, haut) |

Coefficients bois : kmod = 0,9 (court terme, intérieur), γM = 1,3.
**Enseignement immédiat des calculs** : avec 4 709 N de charge, un pied de chêne de 300 mm
n'exige que ~12 mm (compression) / ~16 mm (flambement) : ce sont **l'assemblage et le
contreventement (raideur des nœuds face aux efforts latéraux et au balancement)** qui
dimensionnent, d'où le plancher de 40 mm et la règle « section ≥ 3 × tenon ». À l'inverse,
la **flèche** gouverne les traverses longues et les lattes (ex. ceinture 30 mm sur 1 100 mm → 60 mm mini).

### (c) Couche 3 — scripts de grammaire par typologie (à venir)
Un module par typologie (`lib/typologies/t1_vague.py`, …) : il lit `PARAMS`, applique
la grammaire de forme (profil, plans, angles), appelle la couche 2 pour chaque jonction et
section, génère esquisses/corps paramétrés dans Fusion, et produit une `Nomenclature` réelle
(volumes extraits des corps) → `chiffrage()` remplace alors les estimations manuelles.
Volontairement **non écrit** à ce stade.

## Hypothèses de prix (ordres de grandeur — à valider par devis réels)
Prix HT France 2026, **coût de revient atelier pour une pièce unique (prototype)**, hors marge,
hors TVA, hors livraison, hors outillage de série :

- Bois avivé séché qualité ébénisterie : **chêne 1 800–3 000 €/m³, frêne 1 300–2 000 €/m³,
  noyer 3 500–6 000 €/m³** ; volume brut = net × 1,5 (pièces droites) ou × 2,2 (chantournées).
- Mousses : HR35 ≈ 320 €/m³, HR45 ≈ 450, HR55 ≈ 600, visco ≈ 900, latex ≈ 1 300.
- Cuir pleine fleur pigmenté 55–90 €/m² (chute × 1,4) ; simili PU médical 25–45 €/m².
- Finition vernis PU mat ≈ 14 €/m² (produits).
- Main d'œuvre : ébéniste 45–70 €/h, tapissier 40–60 €/h.
- Un prix de vente artisan se situe typiquement à **× 1,3 à × 1,6** du coût de revient, + TVA 20 %.

La main d'œuvre représente 75 à 85 % du total : l'essence ne fait varier le prix que de
quelques centaines d'euros. Le levier coût est le **nombre d'heures** (gabarits, pièces
chantournées, garnissage complexe), pas le bois.

## Compromis majeurs

1. **Confort vs coût** — les courbes continues (chaise en S) sont les plus confortables et
   les plus chères (chantournage, gabarits, mousse à facetter, cuir à coutures multiples). Les
   plans droits avec boudins et cales rapportés (T3, T4) coûtent 30–50 % de moins.
2. **Solidité vs esthétique** — l'usage dynamique à deux impose des nœuds raides (doubles tenons
   chevillés, entretoises basses, joues en cadre-panneau). Un piétement fin « moderne » sans
   entretoise est possible mais demande des sections plus fortes aux assemblages ou des
   entretoises masquées.
3. **Massif vs pièces cintrées** — chantourner dans le massif coupe le fil (fragilité des zones
   courbes, déchet × 2,2) ; le lamellé-cintré (frêne idéal) est plus solide mais exige un moule
   (coût d'outillage amorti seulement en série).
4. **Fixe vs adaptable** — une gamme fixe ne se règle pas : on vise P5–P95 avec des compromis
   (cale fessière et boudin lombaire placés pour le gabarit médian ; les extrêmes s'adaptent par
   la posture). Option sur mesure : recalcul direct via la couche 1.
5. **Noblesse vs hygiène** — cuir aniline magnifique mais tache ; cuir pigmenté ou simili médical
   nettoyables. Vernis PU mat > huile-cire pour les surfaces bois en contact.
   Garnissages démontables (inserts M6/M8) pour nettoyage et regarnissage, sans rendre le meuble
   « modulable ».
6. **Stabilité vs encombrement** — chaise longue et double plan doivent garder ≥ 100 mm de marge
   au basculement dans le cas le plus excentré : emprise au sol et patins longs.
7. **Valeurs mécaniques** — propriétés assimilées EN 338, coefficients prudents mais **règles de
   pré-dimensionnement, pas un calcul réglementaire** : un prototype doit passer des essais type
   EN 1728 majorés (charge × 2 personnes, fatigue en balancement) avant toute diffusion.

## Note de cohabitation
Le dossier `/workspace/tantra/` contient aussi, depuis 12:45 (heure de Paris), un paquet `tantra/` +
`pyproject.toml` + `docs/` + `scripts_fusion/` écrits par un **autre agent**
(« Tantra & Bien-être » : fixes + camouflables + contention). Ils ne font pas partie de cette passe et n'ont
pas été modifiés. Les livrables de cette passe sont uniquement : `README.md`, `TYPOLOGIES.md`,
`TantraGamme/`, `tests/test_recalculs.py`, `outils/chiffrage_indicatif.py`.
