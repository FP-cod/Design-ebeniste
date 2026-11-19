# Aboutissants — accessoires de contention et modules rapportés

Gamme d’accessoires (bracelets, sangles, colliers, manilles, anneaux
d’ancrage) et de modules mécaniques destinés **exclusivement à des
adultes consentants**. Les scripts sont écrits pour l’API Python
d’Autodesk Fusion 360.

Les charges, coefficients et vérifications fournis ici sont des
**hypothèses de conception**. Ils ne remplacent ni une note
d’ingénieur, ni la CMU marquée d’un fabricant, ni un essai de charge
réel.

## Architecture en trois couches

Même découpage que les meubles Equinox, Néogothique, Incognito, Tantra
et Rangement (ces dépôts n’ont **pas** été modifiés).

```
aboutissants/
├── README.md
├── pytest.ini
├── docs/
│   ├── rapport_couche1_mouvement.md              # ancrages, machine, sécurité
│   ├── rapport_vac_u_lock_collecteur_cadres.md   # VUL, collecteur, cadres
│   └── rapport_compatibilite_tantra_rangement.md # audit Tantra / Rangement
├── common/                             # COUCHE 1
│   ├── params_globaux.py
│   └── fusion_utils.py                 # mm → cm (ici seulement)
├── catalogues/                         # COUCHE 2
│   ├── materiaux.py                    # métaux, bois, PP/PE-HD, joints
│   ├── visserie.py
│   ├── vac_u_lock.py
│   ├── jonctions_cadre.py              # tenon, queue d'aronde, métal
│   └── compatibilite.py                # matrices Aboutissants × gammes
├── mouvement/                          # COUCHE 3
│   └── sex_machine_mecanique.py        # + port Vac-U-Lock en bout de tige
├── interfaces/
│   └── port_vac_u_lock.py
├── hygiene/
│   └── collecteur_urine.py             # hors pouf Incognito
├── cadres/
│   └── cadre_modulaire.py              # mural, sol, poutre suspendue
└── tests/                              # pytest, hors Fusion, sans import adsk
```

Les catalogues d’accessoires (cuir, sangles, boucles, scratch, ardillon)
et les grammaires de typologie (bracelets, colliers, etc.) viendront en
complément de cette couche 2 / 3. Modules livrés : machine de mouvement
mécanique (port Vac-U-Lock en bout de tige), collecteur d'urine
(meubles et aboutissants fixes, **hors pouf vibrant Incognito**),
cadres de contention modulaires (mural, sol, poutre suspendue).

## Conventions

- **Unités internes** : mm, kg, degrés, N, MPa. Jamais de cm dans la
  logique métier. L’API Fusion travaille en **cm** : la conversion se
  fait uniquement dans `common/fusion_utils.py` (`mm_vers_cm` / `cm`).
  Les User Parameters sont écrits en expressions `"80 mm"`, `"2 deg"` ;
  Fusion convertit lui-même.
- **Nommage** : paramètres par chemin (`mouvement.course`), User
  Parameters préfixés `abo_` (`abo_mouvement_course`), comme `eq_`,
  `neo_`, `inc_`, `tan_`, `ran_`.
- **Objet `Param`** : valeur, unité, plage, rôle, justification, source
  (chemin de fichier si la cote vient d’un meuble), statut
  (`impose` / `a_valider` / `derive` / `libre` / `todo`).
- **Cotes de meubles** : uniquement si elles existent dans les scripts
  Equinox / Néogothique / Incognito / Tantra / Rangement. Sinon `valeur=None` et
  `statut=todo`, avec une justification explicite. Rien n’est inventé.
- **Imports `adsk`** : différés (uniquement dans `exporter_user_parameters`,
  `run` et `construire_fusion`). Les tests et le calcul cinématique
  s’exécutent hors Fusion.
- **Formule d’amplitude** : pour une bielle-manivelle alignée ou un
  excentrique, `course = 2 × excentricité`. Voir la grammaire.

## Interface d’ancrage normalisée (œillet M8)

Côté accessoire, le filetage retenu est **M8** (pas gros 1,25 mm),
aligné sur les inserts Equinox (`jonctions.filetage_insert`).

La machine se fixe par une **bride / chape** sur un œillet ou un anneau
**déjà présents**, sans percer ni modifier la structure visible du
meuble. Cette interface est **déduite d’Equinox**. Elle n’est pas
garantie pour Néogothique (plaques 40×40×6 sans œil coté) ni Incognito
(insert noyé Ø12, filetage non documenté, discrétion à l’état fermé).
Tantra utilise un insert **M12** (Ø ext. 16 mm, encastrement 60 mm) et
un anneau rabattable dont le DI n’est pas coté : adaptateur M12↔M8
requis, passage d’axe non garanti. Rangement a des inserts M8, mais un
râtelier **n’est pas** un point d’ancrage de personne. Détail, matrices
et TODO : `docs/rapport_couche1_mouvement.md` et
`docs/rapport_compatibilite_tantra_rangement.md`.

## Machine de mouvement mécanique

Entraînement : manivelle, pédalier ou treuil (la version électrique
viendra plus tard ; l’arbre commun Ø12 et une platine sont réservés).

- Réglage d’amplitude : trous d’excentricité 15 / 25 / 40 / 55 / 70 mm
  → courses 30 / 50 / 80 / 110 / 140 mm (`course = 2e`).
- Réglage de hauteur : goupille sur colonne, pas de 25 mm, de 350 à
  900 mm (défaut 700 mm, niveau d’un banc).
- Butées de fin de course, débrayage par goupille de manivelle.

```bash
# depuis /workspace/aboutissants, avec le .venv du workspace
/workspace/.venv/bin/python -m pytest
/workspace/.venv/bin/python -m mouvement.sex_machine_mecanique
/workspace/.venv/bin/python -m interfaces.port_vac_u_lock
/workspace/.venv/bin/python -m hygiene.collecteur_urine
/workspace/.venv/bin/python -m cadres.cadre_modulaire
```

Rapport des trois aboutissants ajoutés :
`docs/rapport_vac_u_lock_collecteur_cadres.md`.
Retour Vac-U-Lock (variantes, cales, filetages, poussée 400 N validée) :
`docs/rapport_retour_vac_u_lock.md`.

Dans Fusion : ajouter `mouvement/` comme script (ou un lanceur qui
importe `mouvement.sex_machine_mecanique` après avoir mis la racine du
projet dans `sys.path`), ouvrir un design paramétrique, exécuter
`run(context)`. Les User Parameters `abo_*` sont créés ou mis à jour.
La géométrie des cylindres est, dans cette version, approximée par leur
boîte enveloppante.

## Tests

Les tests ne chargent pas `adsk`. Ils vérifient les plages, les tolérances positives, la fidélité des cotes d'ancrage aux scripts de meubles (Equinox, Néogothique, Incognito, Tantra, Rangement), les TODO, la formule `course = 2e`, le port Vac-U-Lock, le collecteur (hors pouf), les cadres modulaires et les matrices de compatibilité (cadres × meubles, aboutissants × gammes).
