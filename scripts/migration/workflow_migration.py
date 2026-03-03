#!/usr/bin/env python3
"""Expose en CLI le workflow de migration de versions de la borne."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE_PROJET = Path(__file__).resolve().parents[2]
MODULE_MAINTENANCE = RACINE_PROJET / "borne_arcade" / "projet" / "MaintenanceMode"
if str(MODULE_MAINTENANCE) not in sys.path:
    sys.path.insert(0, str(MODULE_MAINTENANCE))

import operations  # pylint: disable=import-error


CLES_CIBLES_JSON = [
    "id",
    "titre",
    "description",
    "type",
    "version_installee",
    "version_candidate",
    "migration_disponible",
    "resume_migration",
    "commande_migration_lisible",
    "supportee_sur_hote",
    "raison_indisponibilite",
    "version_paquet_installee",
]


def charger_configuration_maintenance() -> dict[str, object]:
    """Charge la configuration standard du mode maintenance.

    Args:
        Aucun.

    Returns:
        Dictionnaire de configuration fusionne.
    """

    chemin = MODULE_MAINTENANCE / "config_maintenance.json"
    return operations.charger_configuration(chemin)


def filtrer_cible_json(cible: dict[str, object]) -> dict[str, object]:
    """Retourne une representation stable d une cible pour JSON.

    Args:
        cible: Cible enrichie par le module operations.

    Returns:
        Dictionnaire filtre avec ordre logique stable.
    """

    resultat: dict[str, object] = {}
    for cle in CLES_CIBLES_JSON:
        if cle == "version_paquet_installee" and "version_paquet_installee" not in cible:
            continue
        resultat[cle] = cible.get(cle, "")
    return resultat


def afficher_cibles(cibles: list[dict[str, object]], mode: str, format_sortie: str) -> None:
    """Affiche les cibles de migration selon le mode demande.

    Args:
        cibles: Cibles calculees.
        mode: Mode d affichage (`toutes`, `installees`, `candidates`).
        format_sortie: Format cible (`tsv` ou `json`).

    Returns:
        Aucun.
    """

    if format_sortie == "json":
        print(json.dumps([filtrer_cible_json(cible) for cible in cibles], indent=2, ensure_ascii=False))
        return

    for cible in cibles:
        if mode == "installees":
            print(f"{cible.get('id')}\t{cible.get('titre')}\t{cible.get('version_installee')}")
            continue
        if mode == "candidates":
            print(
                f"{cible.get('id')}\t{cible.get('titre')}\t{cible.get('version_candidate')}\t"
                f"{'oui' if cible.get('migration_disponible') else 'non'}"
            )
            continue

        print(
            f"{cible.get('id')}\t{cible.get('titre')}\t"
            f"installee={cible.get('version_installee')}\t"
            f"candidate={cible.get('version_candidate')}\t"
            f"migration={'oui' if cible.get('migration_disponible') else 'non'}"
        )


def executer_operation_cli(
    operation_id: str,
    contexte_operation: dict[str, object] | None = None,
) -> int:
    """Execute une operation maintenance de workflow via la CLI.

    Args:
        operation_id: Identifiant de l operation.
        contexte_operation: Contexte optionnel de la cible et des artefacts.

    Returns:
        Code de retour shell.
    """

    configuration = charger_configuration_maintenance()
    succes, message, chemin_journal = operations.executer_operation(
        operation_id,
        configuration,
        print,
        contexte_operation,
    )
    print(message)
    print(f"Journal: {chemin_journal}")
    return 0 if succes else 1


def construire_parser() -> argparse.ArgumentParser:
    """Construit le parseur CLI du workflow de migration.

    Args:
        Aucun.

    Returns:
        Parseur argparse configure.
    """

    parser = argparse.ArgumentParser(description="Workflow CLI de migration de versions ArcadeCare")
    sous_commandes = parser.add_subparsers(dest="commande", required=True)

    for commande in ("lister-cibles", "versions-installees", "versions-candidates"):
        parser_liste = sous_commandes.add_parser(commande, help="Affiche les cibles de migration")
        parser_liste.add_argument(
            "--format",
            choices=("tsv", "json"),
            default="tsv",
            help="Format de sortie stable pour humain ou script",
        )

    parser_appliquer = sous_commandes.add_parser("appliquer", help="Applique la migration de la cible demandee")
    parser_appliquer.add_argument("--cible", required=True, help="Identifiant de la cible")

    parser_ia = sous_commandes.add_parser("preparer-ia", help="Lance l assistant IA de la cible")
    parser_ia.add_argument("--cible", required=True, help="Identifiant de la cible")
    parser_ia.add_argument(
        "--dossier-sortie",
        help="Dossier de sortie optionnel pour le brief, la reponse et la trace IA",
    )

    parser_pr = sous_commandes.add_parser("proposer-pr", help="Propose une PR pour la cible")
    parser_pr.add_argument("--cible", required=True, help="Identifiant de la cible")

    sous_commandes.add_parser("actualiser", help="Recharge les cibles de migration")
    parser_qualite = sous_commandes.add_parser("qualite", help="Relance la qualite complete")
    parser_qualite.add_argument("--cible", required=True, help="Identifiant de la cible")
    return parser


def main() -> int:
    """Point d entree principal du workflow CLI.

    Args:
        Aucun.

    Returns:
        Code de sortie shell.
    """

    parser = construire_parser()
    args = parser.parse_args()

    if args.commande in {"lister-cibles", "versions-installees", "versions-candidates"}:
        cibles = operations.collecter_cibles_migration(RACINE_PROJET)
        mode = {
            "lister-cibles": "toutes",
            "versions-installees": "installees",
            "versions-candidates": "candidates",
        }[args.commande]
        afficher_cibles(cibles, mode, args.format)
        return 0

    if args.commande == "actualiser":
        return executer_operation_cli("actualiser_cibles_migration")
    if args.commande == "appliquer":
        return executer_operation_cli(
            "appliquer_migration_cible",
            {"cible_migration_id": args.cible},
        )
    if args.commande == "preparer-ia":
        contexte = {"cible_migration_id": args.cible}
        if args.dossier_sortie:
            contexte["dossier_sortie"] = args.dossier_sortie
        return executer_operation_cli("preparer_placeholder_ia_migration", contexte)
    if args.commande == "qualite":
        return executer_operation_cli(
            "relancer_qualite_complete",
            {"cible_migration_id": args.cible},
        )
    if args.commande == "proposer-pr":
        return executer_operation_cli(
            "proposer_pr_migration",
            {"cible_migration_id": args.cible},
        )

    parser.error("Commande inconnue")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
