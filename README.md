<div align="center">

# 🕹️ ArcadeCare

**Maintenance intelligente et modernisation d'une borne arcade multi-jeux sur Raspberry Pi**

[![Qualité](https://github.com/roro627/maintenance_logicielle/actions/workflows/qualite.yml/badge.svg)](https://github.com/roro627/maintenance_logicielle/actions/workflows/qualite.yml)
[![Vérification Debian 11](https://github.com/roro627/maintenance_logicielle/actions/workflows/verification_reelle.yml/badge.svg)](https://github.com/roro627/maintenance_logicielle/actions/workflows/verification_reelle.yml)
[![Plateforme](https://img.shields.io/badge/plateforme-Raspberry%20Pi%203B-c51a4a?logo=raspberrypi&logoColor=white)](https://www.raspberrypi.com/)
[![Java](https://img.shields.io/badge/Java-MG2D-orange?logo=openjdk&logoColor=white)](MG2D/)
[![Python](https://img.shields.io/badge/Python-pygame-3776ab?logo=python&logoColor=white)](borne_arcade/projet/)
[![Lua](https://img.shields.io/badge/Lua-LÖVE2D-000080?logo=lua&logoColor=white)](borne_arcade/projet/)

</div>

---

> **ArcadeCare** automatise les migrations de versions (OS, Java, Python, Lua) d'une borne arcade multi-jeux,
> rend la maintenance reproductible et valide chaque changement en continu via CI/CD et assistance IA.

---

## 📋 Table des matières

- [🕹️ ArcadeCare](#️-arcadecare)
  - [📋 Table des matières](#-table-des-matières)
  - [🎯 Objectif](#-objectif)
  - [✨ Vision produit](#-vision-produit)
  - [🔄 Workflow de migration](#-workflow-de-migration)
  - [📊 État actuel](#-état-actuel)
  - [🗂️ Structure du dépôt](#️-structure-du-dépôt)
  - [🚀 Démarrage rapide](#-démarrage-rapide)
    - [Installation / bootstrap](#installation--bootstrap)
    - [Validation locale](#validation-locale)
    - [Vérification CI/CD locale obligatoire](#vérification-cicd-locale-obligatoire)
  - [🕹️ Mode maintenance](#️-mode-maintenance)
  - [📚 Documentation](#-documentation)
  - [🛡️ Gouvernance](#️-gouvernance)

---

## 🎯 Objectif

Éviter les migrations manuelles risquées en automatisant la mise à jour de la borne vers des versions plus récentes de :

| Composant | Rôle |
| ----------- | ------ |
| 🐧 **Raspberry Pi OS** | Système d'exploitation cible |
| ☕ **Java** | Moteur principal des jeux (MG2D) |
| 🐍 **Python** | Jeux secondaires (pygame) |
| 🌙 **Lua** | Jeux secondaires (LÖVE2D) |

La maintenance doit devenir **reproductible, testable et validable en continu**.

---

## ✨ Vision produit

Le jeu `MaintenanceMode` intégré à la borne est le point de pilotage central :

| # | Fonctionnalité |
| --- | ---------------- |
| 1 | Afficher les versions installées (OS, Python, Java, Lua) |
| 2 | Lister les versions plus récentes disponibles |
| 3 | Proposer une migration depuis l'interface de la borne |
| 4 | Exécuter la migration via une commande |
| 5 | Adapter le code via IA, mettre à jour les tests et la documentation |
| 6 | Ouvrir une Pull Request pour revue humaine |

---

## 🔄 Workflow de migration

Exposé par [`scripts/migration/workflow_migration.py`](scripts/migration/workflow_migration.py) et le jeu `MaintenanceMode` :

```graphviz
┌─────────────────────────────────────────────────────────────────┐
│  1. Détection des versions installées                           │
│  2. Détection des versions candidates (plus récentes)           │
│  3. Sélection d'une cible de migration                          │
│  4. Application de la migration par commande                    │
│  5. Assistance IA                                               │
│     ├─ Régénération / adaptation du code impacté               │
│     └─ Mise à jour : tests · documentation · scripts de build   │
│  6. Exécution des contrôles qualité  ──► KO ? retour étape 5   │
│  7. Proposition de PR                                           │
│  8. Relecture / validation humaine                              │
│  9. Merge sur `main` après accord explicite                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 État actuel

- ✅ Base technique existante pour borne arcade Raspberry Pi
- ✅ Jeu `MaintenanceMode` intégré pour les opérations d'exploitation
- ✅ Workflow de migration structuré en CLI stable (`tsv` / `json`) avec session persistante
- ✅ Installation et déploiement automatisés via scripts shell
- ✅ Vérification qualité par tests et workflows GitHub Actions
- ✅ Documentation centralisée dans `docs/`

---

## 🗂️ Structure du dépôt

```graphviz
arcade-care/
├── borne_arcade/        # Menu principal, jeux et scripts de lancement
├── config/              # Configuration globale (versions minimales, variables borne)
├── scripts/             # Installation, déploiement, tests, documentation
├── docs/                # Source documentaire complète
├── .github/workflows/   # Pipelines CI/CD
└── MG2D/                # Miroir local de la librairie MG2D (non modifiable)
```

---

## 🚀 Démarrage rapide

### Installation / bootstrap

```bash
sudo bash ./bootstrap_borne.sh
```

> Le bootstrap installe également `codex` automatiquement pour le workflow IA de migration.

### Validation locale

```bash
bash ./scripts/tests/lancer_suite.sh
bash ./scripts/docs/generer_documentation.sh
```

### Vérification CI/CD locale obligatoire

```bash
~/.local/bin/act -W .github/workflows/qualite.yml \
  -j verification \
  --container-architecture linux/amd64 \
  -P ubuntu-latest=catthehacker/ubuntu:act-latest

~/.local/bin/act -W .github/workflows/verification_reelle.yml \
  -j verification_reelle_debian11 \
  --container-architecture linux/amd64 \
  -P ubuntu-latest=catthehacker/ubuntu:act-latest
```

---

## 🕹️ Mode maintenance

Accès depuis la borne via séquence clavier :

| Étape | Touche | Bouton arcade |
|-------|--------|---------------|
| 1     | `R`    | `J1X`         |
| 2     | `T`    | `J1Y`         |
| 3     | `Y`    | `J1Z`         |
| 4     | `H`    | `J1C`         |
| Lancer| `G`    | `J1B`         |

---

## 📚 Documentation

| Document | Description |
| ---------- | ------------- |
| [docs/index.md](docs/index.md) | Index principal |
| [docs/installation.md](docs/installation.md) | Guide d'installation |
| [docs/architecture.md](docs/architecture.md) | Architecture du projet |
| [docs/technique.md](docs/technique.md) | Documentation technique |
| [docs/tests.md](docs/tests.md) | Stratégie de tests |
| [docs/deploiement.md](docs/deploiement.md) | Déploiement |
| [docs/utilisateur.md](docs/utilisateur.md) | Guide utilisateur |
| [docs/rendu.md](docs/rendu.md) | Rendu global |

> Site statique généré disponible dans `site/index.html`

---

## 🛡️ Gouvernance

- 🔒 Toute évolution maintient la compatibilité matérielle (affichage, mapping boutons)
- 🧪 Toute correction est couverte par des tests anti-régression
- 📝 Toute modification technique met à jour `docs/`
- 🤖 Toute adaptation générée par IA passe par PR puis validation humaine avant merge sur `main`
- 📏 Toute modification respecte les normes de code définies dans [`AGENTS.md`](AGENTS.md)

---

<div align="center">
<em>La borne reste allumée. Le code aussi.</em>
</div>
