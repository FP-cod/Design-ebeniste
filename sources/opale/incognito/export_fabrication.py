# -*- coding: utf-8 -*-
"""Export STL/3MF des pièces imprimables et du moule de selle (2 parties).

Aucune dépendance à Fusion : le module est testable en Python pur.
Les géométries sont des enveloppes (prismes, cylindres facettés) destinées
au prototype, pas à la série.
"""

from __future__ import annotations

import math
from pathlib import Path


def _stl_solid(nom: str, triangles: list[tuple[tuple[float, float, float], ...]]) -> str:
    lignes = [f"solid {nom}"]
    for tri in triangles:
        ax, ay, az = tri[0]
        bx, by, bz = tri[1]
        cx, cy, cz = tri[2]
        ux, uy, uz = bx - ax, by - ay, bz - az
        vx, vy, vz = cx - ax, cy - ay, cz - az
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        norme = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
        nx, ny, nz = nx / norme, ny / norme, nz / norme
        lignes.append(f"  facet normal {nx:.6f} {ny:.6f} {nz:.6f}")
        lignes.append("    outer loop")
        for x, y, z in tri:
            lignes.append(f"      vertex {x:.4f} {y:.4f} {z:.4f}")
        lignes.append("    endloop")
        lignes.append("  endfacet")
    lignes.append(f"endsolid {nom}")
    return "\n".join(lignes) + "\n"


def prisme(x, y, z, dx, dy, dz) -> list:
    """Triangles d'un pavé droit (mm)."""
    p = [
        (x, y, z), (x + dx, y, z), (x + dx, y + dy, z), (x, y + dy, z),
        (x, y, z + dz), (x + dx, y, z + dz), (x + dx, y + dy, z + dz), (x, y + dy, z + dz),
    ]
    faces = (
        (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
        (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0),
    )
    tris = []
    for a, b, c, d in faces:
        tris.append((p[a], p[b], p[c]))
        tris.append((p[a], p[c], p[d]))
    return tris


def cylindre(cx, cy, z0, rayon, hauteur, n=24) -> list:
    tris = []
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = 2 * math.pi * (i + 1) / n
        p0 = (cx + rayon * math.cos(a0), cy + rayon * math.sin(a0), z0)
        p1 = (cx + rayon * math.cos(a1), cy + rayon * math.sin(a1), z0)
        q0 = (p0[0], p0[1], z0 + hauteur)
        q1 = (p1[0], p1[1], z0 + hauteur)
        c0 = (cx, cy, z0)
        c1 = (cx, cy, z0 + hauteur)
        tris.append((c0, p1, p0))
        tris.append((c1, q0, q1))
        tris.append((p0, p1, q1))
        tris.append((p0, q1, q0))
    return tris


def ecrire_stl(chemin: Path, nom: str, triangles: list) -> Path:
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(_stl_solid(nom, triangles), encoding="ascii")
    return chemin


def exporter_pieces_prototype(dossier: str | Path) -> list[Path]:
    """Exporte les enveloppes des pièces imprimables typiques (mm)."""
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    sorties = []
    # Silentbloc TPU : cylindre Ø32 × 36
    sorties.append(ecrire_stl(dossier / "silentbloc_tpu.stl", "silentbloc_tpu", cylindre(0, 0, 0, 16, 36)))
    # Joint plat
    sorties.append(ecrire_stl(dossier / "joint_plat_tpu.stl", "joint_plat_tpu", cylindre(0, 0, 0, 20, 2)))
    # Patin
    sorties.append(ecrire_stl(dossier / "patin_amortisseur.stl", "patin_amortisseur", prisme(0, 0, 0, 40, 40, 15)))
    # Capuchon (enveloppe)
    sorties.append(ecrire_stl(dossier / "capuchon_filetage.stl", "capuchon_filetage", cylindre(0, 0, 0, 20, 12)))
    # Carter module (coque enveloppe)
    sorties.append(ecrire_stl(dossier / "carter_module.stl", "carter_module", prisme(0, 0, 0, 160, 160, 40)))
    # Adaptateur platine-lèvre (prototype, cotes incertaines)
    sorties.append(ecrire_stl(
        dossier / "adaptateur_platine_levre.stl", "adaptateur_platine_levre",
        prisme(-40, -40, 0, 80, 80, 18) + cylindre(0, 0, 18, 20, 12),
    ))
    # Panneau acoustique : enveloppe 200 × 200 × 12 (labyrinthe schématique)
    panneau = prisme(0, 0, 0, 200, 200, 12)
    # Canaux de labyrinthe simplifiés (rainures traversantes en surface)
    for i in range(5):
        panneau += prisme(15 + i * 35, 15, 8, 8, 170, 4)
    sorties.append(ecrire_stl(dossier / "panneau_acoustique_labyrinthe.stl", "panneau_acoustique_labyrinthe", panneau))
    sorties.append(ecrire_stl(dossier / "boitier_electronique.stl", "boitier_electronique", prisme(0, 0, 0, 120, 80, 45)))
    sorties.append(ecrire_stl(
        dossier / "logement_cellule.stl", "logement_cellule",
        prisme(0, 0, 0, 70, 25, 16) + prisme(58, 6, 0.4, 12, 13, 12.3),
    ))
    sorties.append(ecrire_stl(dossier / "butee_surcharge.stl", "butee_surcharge", prisme(0, 0, 0, 12, 13, 12.3)))
    return sorties


def exporter_moule_selle(dossier: str | Path, rayon_selle_mm: float = 90.0, epaisseur_peau_mm: float = 15.0) -> list[Path]:
    """Moule négatif en 2 parties, avec puits de coulée et évents (enveloppes).

    Le silicone platine (Dragon Skin 10 ou 20) se coule dans ce moule.
    La face utile doit être poncée / vernie avant usage.
    """
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    marge = 20.0
    largeur = 2 * rayon_selle_mm + 2 * marge
    # Partie inférieure : semelle + empreinte cylindrique peu profonde + puits
    bas = prisme(0, 0, 0, largeur, largeur, 25)
    # Puits de coulée (cylindre qui dépasse)
    bas += cylindre(largeur / 2.0, 8.0, 25, 8, 30)
    # Évents
    bas += cylindre(20, largeur / 2.0, 25, 3, 20)
    bas += cylindre(largeur - 20, largeur / 2.0, 25, 3, 20)
    # Partie supérieure : couvercle
    haut = prisme(0, 0, 0, largeur, largeur, 20)
    haut += cylindre(largeur / 2.0, largeur / 2.0, -epaisseur_peau_mm, rayon_selle_mm, epaisseur_peau_mm)
    p1 = ecrire_stl(dossier / "moule_selle_partie_basse.stl", "moule_selle_basse", bas)
    p2 = ecrire_stl(dossier / "moule_selle_partie_haute.stl", "moule_selle_haute", haut)
    return [p1, p2]


def exporter_tout(dossier: str | Path) -> list[Path]:
    """Pièces prototype + moule de selle."""
    dossier = Path(dossier)
    return exporter_pieces_prototype(dossier) + exporter_moule_selle(dossier)
