# -*- coding: utf-8 -*-
"""Configuration pytest : rend importables le paquet ``tantra`` et ``scripts_fusion``."""
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for chemin in (RACINE, os.path.join(RACINE, "scripts_fusion")):
    if chemin not in sys.path:
        sys.path.insert(0, chemin)
