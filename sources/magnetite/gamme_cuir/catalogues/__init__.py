# -*- coding: utf-8 -*-
"""Couche 2 - Catalogues GammeCuir.

- ``cuirs`` : cuirs exterieurs, doublures, rembourrages, teintes (+ apparences Fusion) ;
- ``correspondances_meubles`` : table de correspondance teinte cuir -> materiaux
  reels des catalogues meubles (Equinox, Neogothique, Incognito ; Tantra a confirmer) ;
- ``finitions`` : finitions de tranche, fils ;
- ``quincaillerie`` : metaux, boucles, anneaux, mousquetons, cadenas, rivets, oeillets ;
- ``fermetures`` : systemes de fermeture et jonctions (couture sellier, rivets, oeillets).

Convention : toute charge de rupture ou cout non source est une ESTIMATION,
marquee ``statut_charge = "estimation_a_verifier_fournisseur"`` ; les couts
sont des categories (bas / moyen / eleve / tres_eleve), jamais des prix.
"""
