# Assortiments par teinte de cuir

Genere par `outils/generer_docs.py` depuis `gamme_cuir/catalogues/correspondances_meubles.py`. Identifiants = cles REELLES des catalogues meubles (instantane du 18/11/2026, verifie par `tests/test_correspondances.py` contre les catalogues vivants).

Statut : **assortie** = meme coloris sur un cuir veritable meuble ; **assortie_hors_cuir** = meme coloris seulement sur un revetement non cuir (vegan, tissu) ; **proche** = nuance voisine a valider sur echantillon ; **non_assortie** = aucun meuble.

| Teinte | Statut | Equinox | Neogothique | Incognito | Tantra | Quincaillerie conseillee | Possible (contraste) |
|---|---|---|---|---|---|---|---|
| **cognac** | assortie | `cuir_classique_pleine_fleur` / cognac -> banc_flore, croix_saint_andre, tabouret, chaise_trone<br>`cuir_vegan` / cognac [non cuir] -> banc_flore, croix_saint_andre, tabouret, chaise_trone<br>`cuir_synthetique_hq` / cognac [non cuir] -> banc_flore, croix_saint_andre, tabouret, chaise_trone<br>`tissu_technique_enduit` / cognac [non cuir] -> banc_flore, croix_saint_andre, tabouret, chaise_trone | - | `cuir_cognac` / cognac -> banquette, pouf_vibrant<br>`cuir_sobre_facade` / cognac_clair *(proche, a valider)* -> banquette | a confirmer (aucun catalogue) | `laiton_massif_cw510l`, `laiton_patine` | `inox_316` |
| **tan** | proche | - | - | `cuir_sobre_facade` / cognac_clair *(proche, a valider)* -> banquette<br>`laine_bouclee` / camel [non cuir] *(proche, a valider)* -> banquette, pouf_vibrant | a confirmer (aucun catalogue) | `laiton_massif_cw510l` | `inox_316` |
| **havane** | assortie | `cuir_classique_pleine_fleur` / havane -> banc_flore, croix_saint_andre, tabouret, chaise_trone | - | `cuir_sobre_facade` / havane -> banquette | a confirmer (aucun catalogue) | `laiton_massif_cw510l`, `laiton_patine` | `inox_316` |
| **brun_fonce** | assortie | `cuir_classique_pleine_fleur` / havane *(proche, a valider)* -> banc_flore, croix_saint_andre, tabouret, chaise_trone | `cuir_harnais_noir` / brun_fonce -> entrave | - | a confirmer (aucun catalogue) | `laiton_patine`, `laiton_massif_cw510l` | `inox_316_pvd_noir` |
| **noir** | assortie | `cuir_classique_pleine_fleur` / noir -> banc_flore, croix_saint_andre, tabouret, chaise_trone<br>`cuir_vegan` / noir [non cuir] -> banc_flore, croix_saint_andre, tabouret, chaise_trone<br>`cuir_synthetique_hq` / noir [non cuir] -> banc_flore, croix_saint_andre, tabouret, chaise_trone<br>`tissu_technique_enduit` / noir [non cuir] -> banc_flore, croix_saint_andre, tabouret, chaise_trone<br>`tissu_krypton` / noir [non cuir] -> banc_flore, croix_saint_andre, tabouret, chaise_trone | `cuir_sellier_fin_noir` / noir -> entrave<br>`cuir_renforce_double_noir` / noir -> entrave<br>`cuir_harnais_noir` / noir -> entrave<br>`cuir_synthetique_pu_noir` / noir [non cuir] -> entrave<br>`cuir_pleine_fleur_noir` / noir -> entrave<br>`doublure_agneau_noir` / noir -> entrave | `cuir_noir` / noir -> banquette, pouf_vibrant<br>`cuir_sobre_facade` / noir_mat *(proche, a valider)* -> banquette | a confirmer (aucun catalogue) | `inox_316`, `inox_316_pvd_noir` | `laiton_massif_cw510l`, `laiton_patine` |
| **bordeaux** | assortie_hors_cuir | `cuir_vegan` / bordeaux [non cuir] -> banc_flore, croix_saint_andre, tabouret, chaise_trone<br>`tissu_krypton` / bordeaux [non cuir] -> banc_flore, croix_saint_andre, tabouret, chaise_trone | - | - | a confirmer (aucun catalogue) | `laiton_massif_cw510l` | `inox_316` |
| **vert_bouteille** | assortie | `cuir_classique_pleine_fleur` / vert_bouteille -> banc_flore, croix_saint_andre, tabouret, chaise_trone | - | - | a confirmer (aucun catalogue) | `laiton_massif_cw510l` | `inox_316` |
| **bleu_nuit** | assortie | `cuir_classique_pleine_fleur` / bleu_nuit -> banc_flore, croix_saint_andre, tabouret, chaise_trone<br>`tissu_krypton` / bleu_marine [non cuir] *(proche, a valider)* -> banc_flore, croix_saint_andre, tabouret, chaise_trone | - | - | a confirmer (aucun catalogue) | `inox_316` | `laiton_massif_cw510l` |

## Quincaillerie des meubles (pour accorder les metaux)

- **equinox** (equinox/equinox/catalogues/metaux.py) : `inox_316`, `inox_304`, `laiton_cw614n`, `laiton_cw510l` Anneaux et oeillets d'ancrage en inox A4 (attaches.anneau_inox_8, oeillet_inox_8).
- **neogothique** (neogothique/neogothique/catalogues/ferrures.py) : `fer_forge_mat`, `laiton_mat`, `cire_noire`, `huile_brunie`, `phosphatation_vernis_mat`, `galvanisation_peinture_mate`, `laiton_brosse_vernis_mat`, `laiton_patine_vieilli` Fer forge noir mat : s'accorde avec l'inox PVD noir ; laiton patine vieilli = contact peau prolonge a eviter (FINITIONS.laiton_patine_vieilli.contact_peau).
- **incognito** (incognito/incognito/catalogues/fixations.py) :  Quincaillerie cachee (fixations), pas d'accord visuel impose.
- **tantra** (-) :  a confirmer

## Metaux GammeCuir

| Cle | Metal | Contact peau | Cout | Reference meuble |
|---|---|---|---|---|
| `inox_316` | Inox 316L brosse | ok | moyen | equinox/equinox/catalogues/metaux.py (inox_316) |
| `inox_316_pvd_noir` | Inox 316L revetu PVD noir | ok | eleve | neogothique/neogothique/catalogues/ferrures.py (accord visuel avec fer_forge_mat / cire_noire) |
| `laiton_massif_cw510l` | Laiton massif sans plomb (CW510L), brosse vernis | ok | eleve | equinox/equinox/catalogues/metaux.py (laiton_cw510l, option contact cutane) |
| `laiton_patine` | Laiton patine vieilli | eviter_contact_prolonge | eleve | neogothique/neogothique/catalogues/ferrures.py (FINITIONS.laiton_patine_vieilli : eviter contact prolonge) |
| `acier_nickele` | Acier nickele (entree de gamme) | deconseille_allergie_nickel | bas | - |

## Gammes sans catalogue

- **tantra** : Gamme Tantra Bien-etre : seul un profil d'agent existe (fauteuils tantriques fixes, 'revetements' prevus en couche 1) ; aucun fichier de projet ni catalogue dans /workspace ou /home/box au 18/11/2026. Correspondances a confirmer quand le catalogue existera.

## Exemples d'ensembles

- Banc Flore / croix / tabouret / chaise trone Equinox en `cuir_classique_pleine_fleur` cognac -> menottes vachette vegetale **cognac**, quincaillerie **laiton massif CW510L**, fil naturel ou ton sur ton.
- Entrave Neogothique (`cuir_sellier_fin_noir`, fer forge cire noire) -> menottes **noir**, quincaillerie **inox PVD noir** (accord fer forge) ou laiton patine *hors contact peau*.
- Banquette / pouf Incognito (interieur `cuir_cognac`) -> menottes **cognac** ; rangees dans le coffre (regle 'zero cuir visible' en facade).
