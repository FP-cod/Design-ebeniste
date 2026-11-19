# -*- coding: utf-8 -*-
"""Gamme Incognito : mobilier de salon d'apparence classique,
dont la fonction (points d'ancrage, mécanismes) est entièrement cachée
dans la structure et se déploie par un geste discret.

Destiné exclusivement à des adultes consentants. Les modèles de charge
et de section fournis ici sont des hypothèses de conception : ils ne
remplacent ni le calcul d'un ingénieur, ni un essai de charge réel.

Architecture en trois couches, identique à Equinox / Néogothique :

1. ``incognito.parametres`` : vocabulaire partagé de la gamme (dimensions
   salon, essences, revêtements, discrétion, charges d'ancrage).
2. ``incognito.catalogues`` : matériaux et systèmes d'attache, avec
   règles déclaratives ; ``incognito.regles`` applique ces règles et
   liste les ajustements géométriques.
3. ``incognito.grammaires`` : un script de grammaire par typologie de meuble.

Unités internes : mm, kg, degrés, N, MPa. L'API Fusion travaille en cm :
la conversion est faite exclusivement dans ``incognito.fusion_outils``.
"""

__version__ = "0.1.0"
