# -*- coding: utf-8 -*-
"""Script Fusion 360 : typologie ``camo_fauteuil`` (grammaire ``tantra.grammaires.camo_fauteuil``).

Relancer après modification des paramètres ``tan_...`` (ou de l'état
``tan_<clé>_etat`` pour les meubles à deux états) pour régénérer le modèle.
Enveloppes de fabrication simplifiées ; ne remplace ni le visa d'un
ingénieur ni un essai de charge réel.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tantra_commun import fusion_construire  # noqa: E402

TYPOLOGIE = "camo_fauteuil"


def run(context):  # noqa: ARG001 — signature imposée par Fusion
    fusion_construire(TYPOLOGIE)
