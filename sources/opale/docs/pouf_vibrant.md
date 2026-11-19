# Pouf vibrant Incognito

Pouf de salon classique intégrant un module de selle, exclusivement
pour adultes consentants. À l'état *pouf*, un coussin amovible standard
masque complètement la selle : aucune ferrure, aucun cuir technique, aucun
filetage n'est visible.

Grammaire : `incognito/grammaires/pouf_vibrant.py`. Script Fusion :
`scripts_fusion/incognito_pouf_vibrant.py`. Export STL / moule :
`incognito/export_fabrication.py`.

Les modèles de charge, d'isolation et de budget électrique sont des
**hypothèses de conception**. Ils ne remplacent ni un essai réel, ni un
dossier de conformité (directive machines, CEM, basse tension).

---

## Deux états, un jeu de paramètres

| État | `inc_pouf_etat` | Description |
| --- | ---: | --- |
| `POUF` | 0 | Coussin en place, capuchon sur le filetage, module inactif |
| `MODULE` | 1 | Coussin retiré, selle et embout 1" NPT accessibles |

## Deux niveaux de gamme

Paramètre `ParametresSybian.gamme` = `'haut'` \| `'entree'`. Dans Fusion :
`inc_sybian_gamme` = **1** (haut) ou **0** (entrée). Le changement de gamme
recalcule le logement moteur, les silentblocs (raideur, f0, transmissibilité)
et les fixations internes (nombre, diamètre, entraxe).

| | **Haut** | **Entrée** |
| --- | --- | --- |
| Actionneur principal | Voice coil SUPT `VCAR0105-0164-00A` : **105 N crête**, 35,4 N continu à 25 °C, **course 16,1 mm** (16,4 mm sur une autre page catalogue — écart documenté), 20,1 V, 150 g mobiles, stator Ø 60,4 mm, L 40,4 mm. Sources : [supt-motor.com](http://www.supt-motor.com/products/yzxyqd.html), [supt-motion.com](http://supt-motion.com/en/productshow_21_76.html). | Moteur 24 V à **balourd** sous carter en mousse dense (hypothèse de conception : 0,045 kg × 12 mm, 1 500–4 500 tr/min limités). |
| Autres modules | Piston + rotation, activables séparément (voir plus bas) | Non |
| Silentblocs | Silicone très souple (défaut), f0 ≈ 6 Hz | Caoutchouc, f0 typique ≈ 14 Hz |
| Isolation visée | f0 ≤ f_min_isolée / 3, f_min_isolée = **18 Hz** | f_min = 25 Hz (1 500 tr/min), rapport typique ~1,8 (√2 ok, < 3) |
| Driver | Courant constant, rampe, limitation, AU | Variateur 24 V, rampe, limitation, AU |
| Guidage | Ressorts / flexures sur l'équipage mobile | Carter fermé, pas de course linéaire |
| Prix vendu indicatif (Fabien) | **800–1 000 €** (voice coil seul, brief d'origine) | **300–400 €** |
| Coût matière (ESTIMATION) | 250–450 € (1 module) ; 3 modules : voir budget ci-dessous | 80–150 € |
| Sensation | Course axiale nette, amplitude et fréquence pilotables, option piston / rotation | Vibration d'ensemble, plus simple, plus bruyant, moins « piston » |
| Bruit / complexité | Plus silencieux (pas d'engrenage sur les voice coils) ; assemblage nettement plus exigeant | Plus simple à monter ; le balourd et le carter rayonnent davantage |

La tension catalogue du VCAR0105 (20,1 V) n'est pas 24 V : un driver à
courant constant alimenté en 24 V DC est compatible **si** le courant reste
dans le calibre de la bobine (fiche à demander).

---

## Trois modules (gamme haut)

Objectif : vibration + poussée type piston + rotation sous la selle.
Plaque chauffante **écartée**.

### Modules et activation

| Module | Paramètre Fusion | Matériel retenu | Grandeurs |
| --- | --- | --- | --- |
| Vibration | `inc_module_vibration` | VCAR0105-0164-00A | 105 N crête, 16,1 mm, 8–40 Hz physiques, **18–40 Hz** en zone isolée |
| Piston | `inc_module_piston` | VCAR0110-0380-00A (même famille, [fiche](http://www.supt-motor.com/products/yzxyqd.html)) | 110 N crête, 37,4 N continu, **course 38 mm**, 23,2 V, 150 g, Ø 60,4 × 60,4 mm, 1–8 Hz |
| Rotation | `inc_module_rotation` | maxon EC 45 flat 70 W 24 V, réf. **411812** ([boutique](https://www.maxongroup.com/maxon/view/product/motor/ecmotor/ecflat/ecflat45/411812), 226,94 € HT, nov. 2026) + réducteur ~26:1 (estimation 280 €) | 128 mNm moteur → **≈ 2,3 N·m** en sortie, **≈ 187 tr/min**, 141 g. Charge axiale moteur **3,8 N** seulement |

Alternative piston non retenue : Actuonix P16 (12 V, 50–200 mm, jusqu'à 300 N,
46 mm/s, **62 dB** constructeur, 80–90 USD, [fiche](https://www.actuonix.com/assets/images/datasheets/ActuonixP16Datasheet.pdf)). Trop bruyant pour l'objectif 50 dB(A), 12 V, trop long.

**Roulement de butée séparé** (type 51106 ou supérieur) sous le plateau :
la charge axiale admissible du EC 45 (3,8 N) ne doit jamais voir le poids
d'un usager. **Limiteur de couple** (coupure driver et/ou embrayage) et
**butées** sur piston et plateau : risque de pincement / blessure.

### Architecture retenue : parallèle découplé

Si le voice coil est **en bas** et doit accélérer piston + plateau + selle +
housse (empilement série) :

- masse mobile typique ≈ 2,5 kg avec housse 0,75 kg ;
- force requise à 15 Hz / 8 mm ≈ **179 N > 105 N** — hors capacité ;
- hauteur d'empilement ≈ 331 mm > intérieur d'un pouf 430 mm (≈ 289 mm).

**Retenu** : piston **en retrait**, relié par un palonnier au chariot ;
rotation au centre ; **voice coil tout en haut** sous la selle, ne portant
que l'équipage + la housse ; filetage au sommet.

- masse mobile vibration ≈ 1,27 kg (housse 0,75 kg) → ≈ 90 N à 15 Hz / 8 mm, sous les 105 N crête ;
- housse **1,0 kg** : ≈ 108 N → **avertissement / hors capacité** au point typique (réduire amplitude ou fréquence) ;
- hauteur modules ≈ 213 mm, ça **rentre** dans 289 mm (pouf 430 mm).

Câbles vers le plateau tournant : **rotation limitée** (±120° à ±150°) et
boucle souple, par défaut (pas de collecteur). Un slip-ring 24 V + signaux
n'est envisagé que si une rotation continue est exigée (usure, IP, CEM).

### Encombrement, masse, coût, conso (3 modules, ESTIMATIONS novembre 2026)

| Poste | Ordre de grandeur | Source / nature |
| --- | --- | --- |
| Encombrement (parallèle) | ~213 mm de haut, dans 500×500 | Calcul grammaire, pouf 430 mm, coussin 90 mm |
| Masse modules (sans bois) | ~4–6 kg cadre + actionneurs | Hypothèse |
| VCAR 0105 + VCAR 0110 | à demander (souvent 150–400 USD / pièce) | ESTIMATION, pas de tarif public figé |
| EC 45 flat 70 W | 226,94 € HT | maxon, nov. 2026 |
| Réducteur + butée + drivers | ~600–900 € | ESTIMATION |
| BOM 3 modules + bois + selle | **900–1 500 €** | ESTIMATION matière |
| Prix vendu 3 modules | à fixer (le 800–1 000 € de Fabien correspondait au haut 1 module) | — |
| Conso. continue / crête (3 modules) | **5,5 A / 19 A** à 24 V, soit 132 W / 450 W | ESTIMATION `budget_electrique_haut` |
| Alim. 24 V certifiée, hors meuble | ≥ **25 A / 585 W** (marge 30 % sur la crête) | Dimensionnement indicatif, à mesurer |

Objectif de bruit : **< 50 dB(A) à 1 m** (pression acoustique, champ
approximativement libre, module en fonctionnement typique, pouf posé au
sol). C'est un **objectif de conception**, pas une garantie. Les voice coils
aident ; le réducteur de rotation est le risque principal. Mesure à faire
selon un protocole type NF EN ISO 3744 ou, a minima, sonomètre classe 2 à
1,00 m, 4 points autour du meuble, pondération A.

---

## Interface selle (filetage)

### Ce que les marques font réellement

L'embout retenu par conception est un **1" NPT mâle conique**, ASME B1.20.1
(11,5 TPI, Ø ext. 33,40 mm, engagement à la main L1 = 10,16 mm, longueur
utile L2 = 17,34 mm, dépassement recommandé au-dessus de la selle : **25 mm**).

**Aucune des housses officielles listées n'utilise ce filetage** d'après les
sources publiques consultées. Le 1" NPT est un choix d'interface (standard
de tuyauterie, parfois utilisé en DIY), pas le filetage d'origine.

| Produit | Interface réelle | 1" NPT natif ? | Certitude | Sources |
| --- | --- | --- | --- | --- |
| Sybian (platine officielle) | Lèvre avant sous le *contact piece*, centrage, tirage arrière ; tige plastique ou ressort dans un puits | Non | établi | [Manuel 2014](https://sybian.com/wp-content/uploads/2014/04/SybianManualRevise2014-1.pdf) |
| Smooth Flat Top, Orb, G-Wave | Housses officielles Sybian, même platine | Non | établi | [sybian.com/attachments](https://sybian.com/attachments/), [Joan Price 2016](https://joanprice.com/2016/02/sybian-update-new-silicone-attachments.html) |
| Motorbunny Original | Housse tendue sur le *receiver* ; ressort ou tige. « Compatible Sybian » = cette platine, pas un NPT. Le Buck est en Vac-U-Lock, autre système. | Non | établi | Guide de démarrage 2021 ; [motorbunny.com](https://motorbunny.com/collections/all/products/attachment) |
| The Cowgirl / Unicorn | Dock magnétique + tiges/ressorts propriétaires, **non interchangeable** | Non | établi | [ridethecowgirl.com](https://ridethecowgirl.com/products/additional-springs-and-plastic-stems-set-4), [thewhiteunicorn.com](https://www.thewhiteunicorn.com/collections/sex-machines) |
| Tremor | Silicone annoncé compatible Sybian et Motorbunny (même logique platine) | Non | établi | [thetremor.com/collections/attachments](https://thetremor.com/collections/attachments) |

### Adaptateurs

- **NPT → NPS droit** (même pas, sans conicité) : cotes établies (ASME B1.20.1). Joint torique sur registre, pas d'étanchéité par coincement.
- **NPT → platine à lèvres Sybian / Motorbunny / Tremor** : principe clair, **cotes de platine incertaines** (pas de plan public). Prototype imprimable à caler par relevé physique.
- **NPT → dock Cowgirl** : cotes inconnues, pas d'adaptateur livré.
- **NPT → Vac-U-Lock** : option probable, hors brief platine, cotes à caler sur une pièce commerciale.

### Embout, matériau, capuchon, couple

- Position : **axe du pouf**, au **sommet de l'étage le plus haut** (voice coil en architecture parallèle). Dépassement 25 mm au-dessus de la surface de selle pour visser une housse (engagement ≥ L1, idéalement proche de L2).
- Matériau de l'embout : **inox 316** (sueur, lubrifiant à l'eau). Le laiton résiste mieux au grippage mais se tache et peut gêner un contact cutané. **Recommandation** : embout 316, **capuchon PETG + insert laiton** (évite le grippage inox-inox), joint torique **du commerce**. Masse ajoutée d'un embout tubulaire 316 ≈ 0,07 kg (`masse_embout_kg`), comptée dans la masse mobile.
- Pièce rapportée, vissée / collée / goupillée sur l'équipage, **butée** et **méplats** : le couple de vissage d'une housse ne doit ni dévisser l'embout, ni tordre le guidage, ni charger la bobine. Les efforts latéraux (housse ou usager décentrés) passent dans le **guidage**, pas dans la bobine.
- Capuchon affleurant sous le coussin, état pouf, avec joint torique (étanchéité de l'orifice).

### Masse de housse

- Dimensionnement demandé : **0,5–1 kg**. Défaut de grammaire : **0,75 kg**.
- Seule masse publique trouvée : Smooth Flat Top, **0,200 kg** sur [thekinksters.co.uk](https://thekinksters.co.uk/product/1385/smooth-flat-top-beige-sybian-attachment.html) (rubrique Weight, éventuellement poids d'expédition).
- Paramètre `masse_housse` / `inc_masse_housse`. Avertissement automatique si hors capacité (ex. **1,0 kg** à 15 Hz / 8 mm ≈ 108 N > 105 N en gamme haut).
- **Gamme entrée** : la housse s'ajoute à la masse suspendue (décale f0) et peut créer un moment si elle est excentrée ; elle ne « consomme » pas une course de 16 mm.

---

## Impression 3D

### Tableau pièce → procédé / matériau

| Pièce | Procédé | Matériau | Exposée ? | Raison |
| --- | --- | --- | --- | --- |
| Silentblocs, treillis | FDM TPU 85A–95A ou SLS flexible | TPU | Non | Isolation ; raideur/fluage/température **à caractériser par essai** |
| Joint plat / patin / accouplement | FDM TPU | TPU | Non | Amortissement, pas d'IP67 |
| Joint torique IP67 | **Commerce** (ISO 3601) | NBR ou VMQ | Non | Un torique TPU FDM n'est généralement **pas** étanche IP67 (porosité inter-couches, rugosité). SLS + post-traitement : à valider par essai, pas le défaut |
| Carter, flasques, guides de module | FDM PETG (ou ABS enceinte) | PETG/ABS | Non | Structure *de module* uniquement — pas l'ébénisterie |
| Embout 1" NPT porteur | Usinage | Inox 316 | Non | Précision et couple de vissage |
| Adaptateur platine-lèvre (proto) | FDM PETG | PETG | Non | Cotes encore incertaines |
| Capuchon | FDM PETG + insert laiton + torique commerce | — | Non | Discrétion + anti-grippage |
| Moule de selle, 2 parties | FDM PETG fin ou SLA | PETG / résine | Non | Évents et puits de coulée |
| Peau de selle | Coulée | **Dragon Skin 10 ou 20** (silicone platine) | Oui | Jamais de TPU FDM au contact de la peau |
| Caisson, couronne | Ébénisterie | Feuillu de gamme, tourillons / mortaises | Oui | Vocabulaire salon |

Paramètres FDM indicatifs : TPU buse 0,4 mm, couche 0,16 mm, 3 parois, 30 % (treillis à figer après essai), 230 / 50 °C, lent ; PETG couche 0,20 mm, 4 parois, 40 %, 245 / 80 °C. Moule : couche 0,12 mm, face utile poncée / vernie.

Le script Fusion exporte les STL dans `exports_impression/pouf_vibrant/` (pièces + `moule_selle_partie_basse.stl` / `_haute.stl`). On peut aussi appeler `incognito.export_fabrication.exporter_tout(dossier)` hors Fusion.

### Bruit aérien et isolation solidienne

Deux phénomènes distincts :

- **Isolation solidienne** (8–60 Hz, f0 ≈ 6 Hz, raideur ~1,5 N/mm) : les silentblocs **restent en élastomère** (silicone du commerce ou TPU). Un treillis rigide PETG/PLA à 40 % de remplissage, même enveloppe Ø 32 × 36 mm, a une raideur estimée ~7 150 N/mm en borne flexion (~4 800× le plot silicone) : f0 ≈ 414 Hz, T(18 Hz) ≈ 1,00 — aucune isolation (règle `comparer_treillis_et_silentbloc`, testée).
- **Bruit aérien** (moteur, réducteur, typiquement 100 Hz–plusieurs kHz) : **panneaux** labyrinthe / treillis **PETG** 12 mm, remplissage 40 %, topologie labyrinthe, nid d'abeille ou Schwarz-P, à tapisser l'intérieur du caisson et les capots de modules. Le **PLA** n'est acceptable qu'en proto : Tg ≈ 55–65 °C (proche d'un capot de driver) et sensibilité à l'humidité. Export STL : `panneau_acoustique_labyrinthe.stl`.

TPU imprimé : uniquement là où l'élasticité est requise (joints plats, patins, amortisseurs, option de plot). Selle et contact peau : silicone platine Dragon Skin coulé ; le TPU peut servir au moule.

#### Sources acoustiques (telles que fournies par Fabien)

1. Faci, Mezache et al., « TPU-based labyrinth metamaterials for architectural applications: integrated optimization of mechanical properties and acoustic performance through additive manufacturing », *The International Journal of Advanced Manufacturing Technology*, en ligne le 5 mars 2026 (print avril 2026, issues 9–10, p. 4933–4955), doi:10.1007/s00170-026-17663-z. Article **trouvé**. Fabien en tire 20,6 dBA (métamatériau TPU labyrinthique, 40 % de remplissage) contre 16,9 dBA (TPU massif) : une seule étude, comparaison métamatériau optimisé vs brut. Le PDF est derrière paywall ; ces deux valeurs n'apparaissent pas dans le résumé ouvert et n'ont **pas été relues** dans le texte intégral — chiffres tels que fournis par Fabien, attribués à cet article.
2. Öztürk S., « Acoustical performance of additively manufactured metamaterials: sound absorption and transmission loss », *Engineering Research Express* 7 0455a1, publié le **27 novembre 2025**, doi:10.1088/2631-8695/ae1791. Article **trouvé et relu** (résumé et discussion). FDM PLA vs TPU, topologies solid / honeycomb / Schwarz-P, bande **100–6100 Hz** (confirmée). En comparaison FEM, le PLA donne une absorption et une perte par transmission plus élevées que le TPU sur la plus grande partie de la bande ; les mesures TPU suivent le même ordre des topologies, avec des amplitudes un peu plus faibles. Conclusion, confirmée par l'article : **c'est surtout la géométrie qui fait la performance acoustique**.

Le détail figé dans le catalogue est `NOTE_ACOUSTIQUE_TREILLIS`.

#### Impact coût des panneaux (ESTIMATION novembre 2026)

Environ 3,1 kg de PETG à 40 % : **+61 à +108 €** (filament 18–30 €/kg + inserts). Soit 5–9 % du milieu de fourchette matière 900–1 500 € (1 200 €) : **marginal**, même ordre de grandeur (environ 960–1 610 € si on l'ajoute au bout à bout). L'électronique de pilotage et la chaîne AU (ESP32, ADS1220, cellules, relais de sécurité, etc.) est un poste à part, plus significatif (~178–419 €, même date) — voir `budget_complet_ajouts()`.

---

## Plan d'essai d'étanchéité (IP67 / joints toriques)

Objectif : vérifier l'indice **IP67** (poussière étanche, immersion 1 m / 30 min, IEC 60529) de chaque étage du module, **sans 230 V dans le meuble** (seulement 24 V, alim. débranchée ou alimentée hors liquide selon le mode).

1. **Conception des gorges** selon ISO 3601-2, joints toriques **du commerce** (pas de TPU FDM). Un joint plat TPU peut s'ajouter en appui, pas en barrière unique.
2. **Contrôle visuel et dimensionnel** des gorges, état de surface, graisse silicone compatible.
3. **IP6X** : essai poussière si moyen disponible ; à défaut, inspection des labyrinthes et presse-étoupe.
4. **IPX7** : chaque étage (vibration, piston, rotation, boîtier drivers) immergé séparément, 1,00 m, 30 min, puis ouverture, contrôle d'absence d'eau, mesure d'isolement, essai fonctionnel après séchage.
5. **Orifice d'embout** : capuchon + torique en place (état pouf) ; puis housse montée (si elle prétend étancher — ce n'est pas garanti).
6. **Câbles** : presse-étoupe testé avec le cordon 24 V ; slip-ring éventuel = essai dédié (souvent le point faible).
7. **Critères** : pas d'eau à l'intérieur, isolement conservé, fonctionnement des fins de course / drivers, pas de gonflement des joints.
8. **Traçabilité** : procès-verbal (date, température de l'eau, photos, n° de joints). Un échec relance un changement de gorge ou de joint, pas un « TPU imprimable en plus ».

Le dossier complet (gorges 15–25 %, ePTFE, antenne, matrice EPDM/VMQ/NBR/FKM, pulvérisation / immersion / condensation, assemblage) est dans [etancheite_pouf_vibrant.md](etancheite_pouf_vibrant.md).

---

## Sécurité et conformité

Imposé et câblé :

- **24 V DC** uniquement dans le meuble ; alimentation certifiée **à l'extérieur** ;
- **arrêt d'urgence physique câblé, indépendant de l'ESP32** : contact NF, relais de sécurité, réarmement manuel, coupe le 24 V des drivers des **trois** modules. Placement : sous le chant avant droit de la couronne (accessible assis, discret en façade). Détail : [pilotage_esp32.md](pilotage_esp32.md) ;
- **présence par cellules Wheatstone** (FSR écartés), enable matériel des drivers, filtre fc ≤ f_exc_min/10, temporisation de levée 250 ms ;
- **pilotage ESP32-S3 BLE + Wi-Fi** (remplace télécommande et pédale), appairage BLE sécurisé, Wi-Fi authentifié, watchdog de connexion ;
- rampe de démarrage, limitation de vitesse / courant, protection thermique, ventilation discrète (ouïes sous le pouf) ;
- carter fermant toutes les pièces tournantes ;
- limiteur de force (piston) et de couple (plateau), butées mécaniques ;
- selle et revêtement lavables, non poreux (silicone platine).

Mise sur le marché UE : dossier **directive machines** (2006/42/CE, ou le règlement successeur applicable), **CEM**, **basse tension** (l'alim. externe), éventuellement RED si télécommande radio, et règles jouet / hygiène des matériaux au contact. Ce package **ne constitue pas** ce dossier.

---

## Compromis principaux

1. **Discrétion vs ventilation et bruit** : des ouïes trop ouvertes trahissent le meuble ; trop fermées, l'échauffement grimpe.
2. **Filetage 1" NPT vs housses officielles** : compatibilité native **non établie** ; il faut des adaptateurs, dont certains ont des cotes encore incertaines.
3. **Masse de housse vs 105 N** : 0,5–0,75 kg passe au point typique 15 Hz / 8 mm ; 1 kg est juste au-dessus — compromis amplitude / fréquence.
4. **Trois modules vs prix et gabarit** : l'architecture parallèle rentre dans 430 mm ; le série, non. Le budget 3 modules dépasse le 800–1 000 € du haut « un module ».
5. **Rumble 8 Hz vs isolation** : la zone bien isolée commence vers **18 Hz** (f0 ≈ 6 Hz). En dessous, le meuble peut vibrer et trahir l'usage.
6. **TPU imprimé vs IP67 et peau** : utile en amortisseurs cachés ; interdit en torique d'étanchéité et en contact cutané.
7. **Rotation continue vs limitée** : le slip-ring complique l'IP et la CEM ; la rotation limitée est plus sûre.
8. **Bruit aérien vs isolation solidienne** : les panneaux PETG n'isolent pas le meuble à 8–60 Hz ; les silentblocs élastomère n'absorbent pas le spectre du réducteur. Les deux sont nécessaires, pour des rôles différents.
9. **Filtre de présence vs temporisation de levée** : un seul passe-bas à fc = f_exc_min/10 ne peut pas transitoire en 200–300 ms et atténuer 40 dB à f_exc ; d'où soustraction de zone + chemin rapide + temporisation 250 ms.

---

## Paramètres Fusion utiles

`inc_sybian_gamme`, `inc_pouf_etat`, `inc_pouf_largeur/profondeur/hauteur`, `inc_module_vibration`, `inc_module_piston`, `inc_module_rotation`, `inc_masse_housse`, `inc_architecture_parallele`, `inc_npt_depassement`, `inc_sybian_tension`, `inc_esp32`, `inc_au_physique`, `inc_presence_cellules`, `inc_panneau_acoustique_epaisseur`. Relancer le script après modification.

---

## Questions ouvertes

- Confirmer le relevé de platine Sybian / Motorbunny pour figer l'adaptateur à lèvres.
- Fiche courant / résistance du VCAR0105 et du VCAR0110, et tarif réel.
- Réducteur exact (référence maxon ou autre) et niveau de bruit mesuré à 1 m.
- Faut-il réellement livrer les 3 modules dans le prix 800–1 000 € (alors insuffisant) ou un haut « vibration seule » à ce tarif, et un haut « 3 axes » à un tarif distinct ?
- Rotation continue (slip-ring) ou limitée ?
- Pouf restant à 430 mm (recommandé avec l'architecture parallèle) ou déclinaison plus haute ?
