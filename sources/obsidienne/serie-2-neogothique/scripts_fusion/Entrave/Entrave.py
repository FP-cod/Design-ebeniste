# -*- coding: utf-8 -*-
"""Script Fusion 360 : Entrave cou-poignets (gamme Neogothique).

Installation : voir README.md. Ce lanceur cherche le paquet ``neogothique``
(1) dans son propre dossier, (2) dans le chemin ecrit dans
``chemin_neogothique.txt`` a cote de ce fichier, (3) dans la variable
d'environnement NEOGOTHIQUE_CHEMIN, (4) deux dossiers au-dessus (depot clone).
"""

import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))


def _chemin_paquet():
    candidats = [ICI]
    fichier = os.path.join(ICI, "chemin_neogothique.txt")
    if os.path.exists(fichier):
        with open(fichier, "r", encoding="utf-8") as f:
            candidats.append(f.read().strip())
    candidats.append(os.environ.get("NEOGOTHIQUE_CHEMIN", ""))
    candidats.append(os.path.normpath(os.path.join(ICI, "..", "..")))
    for c in candidats:
        if c and os.path.isdir(os.path.join(c, "neogothique")):
            return os.path.abspath(c)
    raise ImportError("Paquet 'neogothique' introuvable (chemins essayes : %s)" % candidats)


def run(context):
    chemin = _chemin_paquet()
    if chemin not in sys.path:
        sys.path.insert(0, chemin)
    # Fusion garde les modules en memoire entre deux executions : on recharge
    # pour prendre en compte les modifications de parametres / catalogues.
    for nom in list(sys.modules):
        if nom == "neogothique" or nom.startswith("neogothique."):
            del sys.modules[nom]
    from neogothique.grammaires import entrave
    entrave.run(context)


def stop(context):
    pass
