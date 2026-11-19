# -*- coding: utf-8 -*-
"""Package ``tantra`` — gamme Tantra & Bien-être (mobilier pour adultes consentants).

Trois volets, chacun en trois couches (même architecture qu'Incognito) :

1. ``tantra.parametres`` — vocabulaire partagé : dimensions, anthropométrie,
   essences, revêtements, charges (couche 1) ;
2. ``tantra.catalogues`` et ``tantra.regles`` — matériaux, fixations,
   mécanismes, coûts et règles de recalcul (couche 2) ;
3. ``tantra.grammaires`` — une grammaire par typologie (couche 3) :

   * volet 1, fauteuils tantriques fixes : ``tantra_chaise_double_courbe``,
     ``tantra_fauteuil_lombaire``, ``tantra_banquette_deux_niveaux``,
     ``tantra_siege_repose_genoux`` ;
   * volet 2, camouflable : ``camo_canape``, ``camo_fauteuil`` ;
   * volet 3, cadres transformables : ``cadre_desserte_genoux``,
     ``cadre_table_inclinee``.

Unités internes : mm, N, MPa, kg, degrés. L'API Fusion travaille en cm :
la conversion est faite exclusivement dans ``tantra.fusion_outils``.

Tous les calculs sont des modèles simplifiés : ils ne remplacent ni le
visa d'un ingénieur, ni un essai de charge réel.
"""

__version__ = "0.1.0"
