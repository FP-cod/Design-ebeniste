# -*- coding: utf-8 -*-
"""Chemins des fichiers sources des autres gammes (tracabilite des reprises).

Chemins relatifs a /workspace (machine de Fabien, releve du 18/11/2026).
Toute valeur ``repris`` de la gamme Rangement cite au moins une de ces
constantes ; les depots d'origine n'ont PAS ete modifies.
"""

EQ_PARAM = "equinox/equinox/parametres.py"
EQ_BOIS = "equinox/equinox/catalogues/bois.py"
EQ_GARN = "equinox/equinox/catalogues/garnissage.py"
EQ_ATT = "equinox/equinox/catalogues/attaches.py"
EQ_MET = "equinox/equinox/catalogues/metaux.py"

NEO_PARAM = "neogothique/neogothique/parametres.py"
NEO_BOIS = "neogothique/neogothique/catalogues/bois.py"
NEO_GARN = "neogothique/neogothique/catalogues/garnissage.py"
NEO_FER = "neogothique/neogothique/catalogues/ferrures.py"
NEO_ATT = "neogothique/neogothique/catalogues/attaches.py"

INC_PARAM = "incognito/incognito/parametres.py"
INC_FIX = "incognito/incognito/catalogues/fixations.py"
INC_HOUSSES = "incognito/incognito/catalogues/housses.py"

ABO_PARAM = "aboutissants/common/params_globaux.py"
ABO_PORT = "aboutissants/interfaces/port_vac_u_lock.py"
ABO_MAT = "aboutissants/catalogues/materiaux.py"
ABO_JC = "aboutissants/catalogues/jonctions_cadre.py"

# Tantra : DEUX implementations coexistent (en cours d'ecriture le 18/11/2026,
# dossiers crees vers 12:45-12:50, absents au debut de cette passe).
TANTRA_PARAM = "tantra/tantra/parametres.py"
TANTRA_LIB = "tantra/TantraGamme/lib/params_globaux.py"

# GammeCuir (accessoires cuir) : dossier cree vers 13:00 le 18/11/2026.
GC_CUIRS = "gamme_cuir/gamme_cuir/catalogues/cuirs.py"
GC_CORR = "gamme_cuir/gamme_cuir/catalogues/correspondances_meubles.py"

#: Instantane : gammes lues pour cette passe (date du releve).
GAMMES_LUES = ("Equinox", "Neogothique", "Incognito", "Aboutissants", "Tantra", "GammeCuir")
RELEVE = "18/11/2026 ~13:05 (Tantra, GammeCuir et Aboutissants etaient en cours de modification)"

A_VALIDER = "À VALIDER"
