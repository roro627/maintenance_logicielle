# ArcadeCare

ArcadeCare est un projet de maintenance et de modernisation d une borne arcade
multi-jeux (Java, Python, Lua) sur Raspberry Pi.

## Objectif principal

Automatiser au maximum les futures mises a jour de la borne vers des versions
plus recentes de:

- Raspberry Pi OS
- Python
- Java
- Lua

L'objectif final est d'éviter les migrations manuelles risquees et de rendre
la maintenance reproductible, testable et validable en continu.

## Vision produit cible

Le jeu de maintenance doit devenir le point de pilotage central des migrations:

1. Afficher les versions actuellement installees (OS, Python, Java, Lua).
2. Lister uniquement les versions plus recentes disponibles.
3. Proposer une migration de version depuis l interface.
4. Executer la migration via une commande.
5. Utiliser une IA pour adapter le code des jeux / de la borne aux changements de version, mettre a jour les tests et documentation.
6. Ouvrir une Pull Request pour revue humaine.

## Workflow de migration

La chaine cible est maintenant exposee par `scripts/migration/workflow_migration.py`
et par le jeu `MaintenanceMode`:

1. Detection des versions installees.
2. Detection des versions candidates (plus recentes uniquement).
3. Selection d une cible de migration.
4. Application de la migration par commande.
5. Via assistance IA :
   1. Regeneration ou adaptation du code impacte.
   2. Mise a jour automatique:
      - tests,
      - documentation,
      - scripts de build/deploiement si necessaire.
6. Execution complete des controles qualite / workflow. Si concluant, continuer, sinon renvoyer à l'étape 5.
7. Proposition de PR.
8. Relecture/validation humaine.
9. Merge sur `main` apres accord explicite.

## Etat actuel du projet

- Base technique existante pour borne arcade Raspberry Pi.
- Jeu `MaintenanceMode` deja integre pour les operations d exploitation.
- Workflow migration versions maintenant structure en CLI stable (`tsv`/`json`) et session persistante.
- Installation/deploiement automatise via scripts shell.
- Verification qualite par tests et workflows GitHub Actions.
- Documentation centralisee dans `docs/`.

## Structure du depot

- `borne_arcade/`: menu principal, jeux et scripts de lancement.
- `config/`: configuration globale (versions minimales, variables borne).
- `scripts/`: installation, deploiement, tests, documentation.
- `docs/`: source documentaire complete du projet.
- `.github/workflows/`: pipelines CI/CD.
- `MG2D/`: miroir local de la librairie MG2D (non modifiable localement).

## Documentation

- Index principal: `docs/index.md`
- Installation: `docs/installation.md`
- Architecture: `docs/architecture.md`
- Technique: `docs/technique.md`
- Tests: `docs/tests.md`
- Deploiement: `docs/deploiement.md`
- Guide utilisateur: `docs/utilisateur.md`
- Rendu global: `docs/rendu.md`

Site statique (apres generation): `site/index.html`

## Commandes rapides

### Installation / bootstrap

```bash
chmod +x ./bootstrap_borne.sh
sudo ./bootstrap_borne.sh
```

Le bootstrap installe aussi `codex` automatiquement pour le workflow IA de migration.

### Validation locale standard

```bash
./scripts/tests/lancer_suite.sh
./scripts/docs/generer_documentation.sh
```

### Verification CI/CD locale obligatoire

```bash
~/.local/bin/act -W .github/workflows/qualite.yml -j verification --container-architecture linux/amd64 -P ubuntu-latest=catthehacker/ubuntu:act-latest
~/.local/bin/act -W .github/workflows/verification_reelle.yml -j verification_reelle_debian11 --container-architecture linux/amd64 -P ubuntu-latest=catthehacker/ubuntu:act-latest
```

## Gouvernance des changements

- Toute evolution doit maintenir la compatibilite borne (materiel, affichage,
  mapping boutons).
- Toute correction doit etre couverte par tests anti-regression.
- Toute modification technique doit mettre a jour la documentation `docs/`.
- Toute adaptation generee par IA doit passer par PR puis validation humaine
  avant merge sur `main`.
- Toute modification doit respecter les normes de code du projet formulé dans `AGENTS.md`.

## Feuille de route prioritaire ArcadeCare

1. Formaliser le workflow exact de migration de versions.
2. Etendre `MaintenanceMode` pour afficher versions installees/disponibles.
3. Implementer la commande de bascule de version pilotable depuis la borne.
4. Maintenir le pipeline IA `Codex CLI + Ollama + Context7` d adaptation code + tests + docs.
5. Automatiser la creation de PR de migration pre-validee.
