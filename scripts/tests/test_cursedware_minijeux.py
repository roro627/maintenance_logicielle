#!/usr/bin/env python3
"""Valide les contrats statiques des mini-jeux CursedWare sans lancer LÖVE."""

from __future__ import annotations

import re
import sys
from pathlib import Path

RACINE_PROJET = Path(__file__).resolve().parents[2]
DOSSIER_MINIJEUX = RACINE_PROJET / "borne_arcade" / "projet" / "CursedWare" / "minigames"
MOTIFS_REQUIS = {
    "module.Name": re.compile(r'module\.Name\s*=\s*"[^"]+"'),
    "module.IsActive": re.compile(r"module\.IsActive\s*=\s*(true|false)"),
    "module.new": re.compile(r"function\s+module\.new\s*\("),
    "module:GetObjective": re.compile(r"function\s+module:GetObjective\s*\("),
    "module:GetTime": re.compile(r"function\s+module:GetTime\s*\("),
    "module:getObjective": re.compile(r"function\s+module:getObjective\s*\("),
    "module:setObjective": re.compile(r"function\s+module:setObjective\s*\("),
    "module:Setup": re.compile(r"function\s+module:Setup\s*\("),
    "module:Start": re.compile(r"function\s+module:Start\s*\("),
    "module:Update": re.compile(r"function\s+module:Update\s*\("),
    "module:Stop": re.compile(r"function\s+module:Stop\s*\("),
    "module:Cleanup": re.compile(r"function\s+module:Cleanup\s*\("),
    "return module": re.compile(r"return\s+module"),
}


def lister_fichiers_minijeux() -> list[Path]:
    """Retourne la liste triee des points d entree mini-jeux.

    Returns:
        Liste des fichiers game.lua detectes.
    """

    return sorted(DOSSIER_MINIJEUX.glob("*/game.lua"))


def verifier_fichier(chemin_fichier: Path) -> None:
    """Valide la presence des symboles requis dans un mini-jeu.

    Args:
        chemin_fichier: Fichier source a verifier.

    Raises:
        ValueError: si un motif requis est absent.
    """

    contenu = chemin_fichier.read_text(encoding="utf-8")
    for nom_motif, motif in MOTIFS_REQUIS.items():
        if motif.search(contenu) is None:
            raise ValueError(
                f"{chemin_fichier.relative_to(RACINE_PROJET)} ne respecte pas le contrat mini-jeu: {nom_motif} manquant."
            )


def main() -> int:
    """Point d entree du validateur CursedWare.

    Returns:
        Code de sortie shell.
    """

    fichiers = lister_fichiers_minijeux()
    if not fichiers:
        print(
            "ERREUR: aucun mini-jeu CursedWare detecte. "
            "ACTION RECOMMANDEE: verifiez borne_arcade/projet/CursedWare/minigames/."
        )
        return 1

    try:
        for fichier in fichiers:
            verifier_fichier(fichier)
    except (OSError, ValueError) as erreur:
        print(f"ERREUR CursedWare: {erreur}")
        return 1

    print(f"OK CursedWare : {len(fichiers)} mini-jeu(x) valides")
    return 0


if __name__ == "__main__":
    sys.exit(main())
