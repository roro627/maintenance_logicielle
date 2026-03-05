# SAE : Maintenance de la Borne d'Arcade

> **Mots-clés** : Organisation • Automatisation

## 🎯 Contexte du Projet

Le département informatique possède une borne d'arcade destinée à être exposée lors des salons, forums et Journées Portes Ouvertes (JPO) afin de présenter et valoriser les réalisations des étudiants.

### Situation Actuelle

- **Perte de données** : Le dépôt Git hébergé à l'IUT a été intégralement perdu
- **Ressources disponibles** : Seule une archive contenant une documentation minimale et le code source de la borne (salle 13) est disponible sur Moodle
- **État de la documentation** : Toutes les documentations (technique, installation, ajout de jeux, utilisateur) ont été perdues avec le dépôt GitHub

### Spécifications Techniques

- **Matériel** : Raspberry Pi 3 Model B
- **Système d'exploitation** : Actuellement Rasbian 2017, nécessitant une mise à jour vers RBpy3-RBPyos
- **⚠️ Attention** : Les versions des bibliothèques et langages sont obsolètes et nécessitent une mise à jour

---

## 📋 Objectifs de la SAE

Votre mission consiste à restaurer et moderniser la borne d'arcade en vous concentrant sur les aspects suivants :

### 1. Documentation

Automatiser la génération complète de la documentation :

- **Documentation technique** : Architecture du système, composants utilisés
- **Documentation d'installation** : Procédure complète de mise en place de la borne
- **Documentation pour l'ajout d'un nouveau jeu** : Guide pas à pas pour les développeurs
- **Documentation utilisateur** : Manuel d'utilisation de la borne

**⚠️ Exigence critique** : **TOUTE** la documentation existante doit être mise à jour (absolument toute, sans exception). Il ne s'agit pas seulement de respecter des normes de documentation, mais de mettre à jour l'intégralité du contenu documentaire.

### 2. Mise à Jour et Modernisation

- **Migration système** : Passer de l'ancienne version de Raspbian à Raspberry Pi OS récent
- **Mise à jour des dépendances** : Actualiser toutes les bibliothèques et langages de programmation
- **⚠️ Point critique** : Faire très attention à la compatibilité des versions lors des mises à jour

### 3. Automatisation

- **Installation automatisée** : Script d'installation complet du logiciel sur la borne
- **Déploiement via Git** : Mise en place d'un système de déploiement automatique
  - Après un `git pull` sur la borne, toutes les mises à jour doivent être détectées
  - La mise à jour doit s'installer automatiquement sans intervention manuelle

### 4. Évolution Fonctionnelle

- **Ajout d'un nouveau jeu** : Intégrer au moins un nouveau jeu dans la borne
- **Respect du processus** : Utiliser la documentation créée pour valider sa pertinence

---

## ✅ Livrables Attendus

1. **Documentation complète** (technique, installation, ajout de jeu, utilisateur)
2. **Scripts d'automatisation** (installation, déploiement)
3. **Tests automatisés** : Développer des tests automatisés au maximum possible pour valider :
   - Le processus d'installation
   - La procédure d'ajout de jeu
   - Le système de déploiement automatique
   - La compatibilité des nouvelles versions
   - Le fonctionnement de chaque jeu
4. **Nouveau jeu** : Au moins un jeu supplémentaire fonctionnel
5. **Validation terrain** : Tests réussis sur la borne d'arcade physique
6. **Évaluation des coûts** : Fichier `cost.md` maintenu à jour tout au long du projet (en français)

---

## 🔧 Ressources et Accès

- **Code source** : Disponible dans l'archive ZIP fournie
- **Documentation existante** : Documentation minimale présente dans l'archive
- **Accès à la borne** : Sur demande pour tester vos installations et documentations
- **Recherche complémentaire** : Internet pour les documentations des bibliothèques et outils

---

## ⚠️ Points d'Attention

- **Tests automatisés** : Automatiser au maximum les tests pour garantir la reproductibilité et la fiabilité
- **Tests terrain** : Valider chaque étape sur la borne physique avant de considérer le travail terminé
- **Documentation exhaustive** : Elle doit être suffisamment claire pour qu'une personne tierce puisse reproduire l'installation. **Toute** modification du code doit être accompagnée d'une mise à jour de la documentation correspondante
- **Suivi des coûts** : Maintenir à jour le fichier `cost.md` avec une estimation des coûts (temps, matériel, licences, etc.)
- **Organisation et automatisation** : Ces deux principes doivent guider toutes vos décisions techniques

---

## 🤖 Protocole IA Linux de Vérification (sans `act`)

Ce protocole est destiné à une IA exécutée sur Linux pour valider les correctifs récents:

- correction du workflow migration quand la cible est déjà à jour (no-op non bloquant),
- robustesse du mapping boutons J1 hors joystick (Java + NeonSumo),
- robustesse de `B3` dans NeonSumo,
- détection automatique du chemin projet pour l autostart via `bootstrap_borne.sh`.

### Pré-requis

1. Exécuter depuis un compte utilisateur Linux standard (pas directement `root`).
2. Avoir `sudo` disponible.
3. Se placer à la racine du dépôt.
4. Ne pas exécuter `act` dans ce protocole.

### Étape 1 - Préparation

```bash
set -Eeuo pipefail
cd "$(git rev-parse --show-toplevel)"
```

### Étape 2 - Tests ciblés migration no-op

```bash
python3 -m pytest -q borne_arcade/projet/MaintenanceMode/tests/test_operations.py -k "deja_alignee_retourne_succes_info"
```

Résultat attendu: `1 passed`.

### Étape 3 - Tests ciblés entrées NeonSumo (dont B3)

```bash
python3 -m pytest -q borne_arcade/projet/NeonSumo/tests/test_main_menu.py -k "gerer_entree_borne_associe_les_touches_arcade_attendues or construire_aliases_boutons_j1_inclut_les_touches_numeriques or touche_juste_appuyee_accepte_les_aliases"
```

Résultat attendu:

- mapping nominal présent (`B3 -> K_h`),
- alias numérique présent (`B3 -> K_3` et `K_KP3`),
- test en succès.

### Étape 4 - Tests Java ciblés boutons J1 hors joystick

```bash
bash ./scripts/tests/test_unitaires_java.sh
bash ./scripts/tests/test_jeux_java_cibles.sh --jeu Puissance_X
```

Résultat attendu: succès des tests `TestUnitaireClavierBorneArcade` et `TestContratPuissanceX`.

### Étape 5 - Régression Lua (contrat CursedWare)

```bash
bash ./scripts/tests/test_jeux_lua_cibles.sh --jeu CursedWare
bash ./scripts/tests/test_versions_compatibilite.sh
```

Résultat attendu:

- pas d erreur de syntaxe Lua,
- version Lua détectée compatible (>= minimum configuré),
- test terminé en succès.

### Étape 6 - Vérification autostart dynamique via bootstrap

Objectif: prouver que `bootstrap_borne.sh` réécrit automatiquement `~/.config/autostart/borne.desktop` avec le chemin réel du dépôt.

```bash
CHEMIN_REEL="$(pwd)/borne_arcade/lancerBorne.sh"
AUTOSTART="${HOME}/.config/autostart/borne.desktop"

mkdir -p "$(dirname "${AUTOSTART}")"
cat > "${AUTOSTART}" <<'EOF'
[Desktop Entry]
Type=Application
Name=BorneArcade
Exec=/bin/bash -lc "/tmp/chemin_faux/lancerBorne.sh"
EOF

sudo -E bash ./bootstrap_borne.sh
grep -Fx "Exec=/bin/bash -lc \"${CHEMIN_REEL}\"" "${AUTOSTART}"
```

Résultat attendu:

- `grep` retourne 0,
- la ligne `Exec` pointe exactement vers le chemin courant du dépôt,
- aucune saisie manuelle de chemin n est nécessaire.

### Étape 7 - Vérification anti-régression globale (statique/scripts)

```bash
bash ./scripts/tests/test_anti_regressions.sh
```

Résultat attendu: `Test anti regressions: OK`.

### Étape 8 - Vérification terrain Raspberry Pi (si accès physique)

1. Redémarrer la borne: `sudo reboot`.
2. Vérifier que le menu borne se lance automatiquement.
3. Dans NeonSumo, vérifier physiquement:
   - `B3` via touche nominale (`H`) fonctionne,
   - `B3` via alias numérique (`3` ou pavé numérique `3`) fonctionne.

### Critères d acceptation finaux

1. Toutes les commandes ci-dessus retournent `0`.
2. Aucun message bloquant du type `Aucune migration candidate detectee` lors d une cible déjà alignée.
3. `~/.config/autostart/borne.desktop` contient la ligne `Exec` alignée sur le chemin réel.
4. Les entrées J1 hors joystick (dont `B3`) sont validées par tests automatiques et, si possible, par validation matérielle.
