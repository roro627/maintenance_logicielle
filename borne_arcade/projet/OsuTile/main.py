import os
import subprocess
from menu import run_menu


def lister_exports_manquants(dossier_osu="beatmaps", dossier_maps="maps"):
    """Retourne les couples osu/python qui doivent etre exportes.

    Args:
        dossier_osu: Dossier contenant les fichiers `.osu`.
        dossier_maps: Dossier de sortie des cartes Python.

    Returns:
        Liste de tuples `(chemin_osu, chemin_py)` a exporter.
    """

    exports_manquants = []
    os.makedirs(dossier_maps, exist_ok=True)
    for filename in os.listdir(dossier_osu):
        if filename.endswith(".osu"):
            map_name = os.path.splitext(filename)[0]
            osu_path = os.path.join(dossier_osu, filename)
            py_path = os.path.join(dossier_maps, f"{map_name}.py")

            if not os.path.exists(py_path):
                exports_manquants.append((osu_path, py_path))
    return exports_manquants


def ensure_maps_exported(dossier_osu="beatmaps", dossier_maps="maps", executeur=subprocess.run):
    """Genere uniquement les cartes Python manquantes.

    Args:
        dossier_osu: Dossier contenant les fichiers `.osu`.
        dossier_maps: Dossier de sortie des cartes Python.
        executeur: Fonction d execution injectable pour les tests.

    Returns:
        Aucun.
    """

    for osu_path, py_path in lister_exports_manquants(dossier_osu, dossier_maps):
        print(f"Génération de {py_path}")
        executeur(["python3", "tools/export_map.py", osu_path, py_path], check=False)


if __name__ == "__main__":
    ensure_maps_exported()
    run_menu()
