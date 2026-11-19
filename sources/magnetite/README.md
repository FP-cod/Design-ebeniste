# GammeCuir - accessoires en cuir (Fusion 360, API Python)

Menottes, bracelets, colliers, sangles de contention, paddles, floggers, martinets, harnais - assortis aux
gammes de meubles Equinox, Neogothique, Incognito (et Tantra, a confirmer). Destine exclusivement a des
adultes consentants ; aucun accessoire n'est concu pour la suspension.

Conventions reprises d'Equinox : trois couches, parametres `Param`-like documentes, unites mm (cm seulement
dans `fusion_outils`), User Parameters Fusion prefixes (`gc_`), scripts `scripts_fusion/<Nom>/<Nom>.py` +
`.manifest` avec `run(context)` et gestion d'erreur, tests pytest avec mock `adsk`.

## Arborescence

```
gamme_cuir/
  gamme_cuir/
    parametres_gamme_cuir.defauts.json   couche 1 : schema documente (valeur, unite, plage, statut, justification, source)
    parametres_gamme_cuir.json           surcharges projet ("surcharges": {"section.param": valeur})
    parametres.py                        chargeur + validation + grandeurs derivees + export User Parameters
    catalogues/
      cuirs.py                           cuirs pleine fleur, doublures, rembourrages, TEINTES (+ apparences Fusion)
      correspondances_meubles.py         mapping teinte -> identifiants reels des catalogues meubles (+ verification)
      finitions.py                       tranches, fils
      quincaillerie.py                   metaux, boucles, anneaux D/O, mousquetons, cadenas, rivets, oeillets
      fermetures.py                      systemes de fermeture, jonctions
    regles.py                            regles de compatibilite et de securite (ECHEC / ALERTE / INFO)
    geometrie.py                         contours, primitives, Plan (pur Python)
    fusion_outils.py                     Constructeur Fusion, apparences, rapport, executer()
    grammaires/menottes.py               couche 3 : menottes / bracelets poignet + cheville
  scripts_fusion/GammeCuirMenottes/      GammeCuirMenottes.py + .manifest
  tests/                                 pytest + mock Fusion (conftest.py)
  outils/_generer_defauts_json.py        source editable du JSON de defauts
  outils/generer_docs.py                 docs/parametres.md, assortiments.md, rapport, patron SVG
  docs/                                  parametres.md, assortiments.md, compromis.md, rapport_menottes.txt, patron SVG/PNG
```

## Utilisation

```bash
python -m pytest                       # tests (pytest requis)
python outils/_generer_defauts_json.py # apres modification du schema
python outils/generer_docs.py          # regenere les docs
```

Fusion : Utilitaires > Complements > Scripts et complements > + > `scripts_fusion/GammeCuirMenottes` > Executer.
Le script cree un composant `menottes_<membre>_<taille>_<teinte>` : `menotte_cuir` (doublure, rembourrage,
exterieur, patte, percages, esquisses de couture avec points de griffe), `patrons_pieces` (passant, patte a
plat), `menotte_quincaillerie` (boucle, ardillon, anneau, tetes de rivets) ; rapport dans
`~/gamme_cuir_rapport_<nom>.txt`.

## Grammaire menottes (resume)

- C_neutre = tour + jeu_doigt + pi x epaisseur_totale ; recouvrement = repli boucle + (n-1)/2 x entraxe +
  bout ; longueur developpee = C_neutre + recouvrement (poignet M cognac : 217,3 + 90 = 307,3 mm).
- Trou central = taille choisie ; 5 trous x 15 mm = +/-30 mm de reglage.
- Anneau D sur patte cousue-rivetee a l'oppose de la boucle ; rembourrage interrompu sous la patte et loin des percages.
- Couture sellier a 3 mm du bord, pas 3,2 mm (3,1 points/cm) ; longueur de fil = 4 x couture (estimation).

## Points a faire valider par Fabien

Voir le rapport de livraison ; resume : gamme Tantra (catalogue absent), teinte tan (aucun coloris exact),
bordeaux (seulement vegan/tissu Equinox), anneau D laiton vs inox (assortiment vs charge), charges de
quincaillerie a obtenir des fournisseurs, effort de service 500 N repris de l'Entrave, jeu doigt 20 mm,
cheville XL (7 trous), noms d'apparences Fusion a verifier sur l'installation.
