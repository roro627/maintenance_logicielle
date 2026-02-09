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
