# Suivi des couts

## Objectif

Ce document maintient le suivi des couts du projet (temps, materiel, licences, exploitation)
conformement aux attentes de `consignes.md`.

## Methode d estimation

- Les valeurs sont des estimations consolidees au niveau equipe.
- Le temps est exprime en heures homme.
- Les couts financiers sont distingues en:
  - **cout direct**: depense reelle ou previsionnelle en EUR,
  - **cout valorise**: estimation economique de la charge de travail.
- Les logiciels utilises sont majoritairement open source (licence: 0 EUR).
- La mise a jour est obligatoire a chaque lot majeur.

## Hypotheses de calcul

- Taux de valorisation interne du temps: **30 EUR/h** (estimation pedagogique).
- Materiel principal deja disponible (borne, ecran, Raspberry Pi, boutons).
- Les couts materiels listent surtout du stock de securite et des consommables.
- Les couts licences restent a 0 EUR tant que les dependances restent open source.

## Tableau de suivi (couts directs + charge)

| Poste | Quantite | Cout unitaire EUR | Total EUR | Temps h | Commentaire |
|---|---:|---:|---:|---:|---|
| Pilotage, cadrage, suivi qualite | 1 lot | 0 | 0 | 8 | Organisation, priorisation, revues |
| Migration scripts installation/deploiement | 1 lot | 0 | 0 | 12 | `installer_borne.sh`, pipeline post-pull |
| Documentation technique et utilisateur | 1 lot | 0 | 0 | 12 | Pages `docs/`, MkDocs, tutoriels |
| Tests automatiques (unit, integration, systeme) | 1 lot | 0 | 0 | 16 | Shell + Java + Python + smoke-tests |
| Ajout et stabilisation du jeu NeonSumo | 1 lot | 0 | 0 | 16 | Gameplay, collisions, HUD, docs, tests |
| Validation sur borne physique | 1 session | 0 | 0 | 5 | Checklist materielle et verification terrain |
| Durcissement conformite consignes | 1 lot | 0 | 0 | 7 | lint, docstrings, messages erreurs |
| Consommables maintenance borne | 1 pack | 18 | 18 | 1 | Nettoyant contact, attaches, adaptateurs |
| Stock de securite carte microSD | 1 unite | 12 | 12 | 1 | Image systeme de secours |
| Cablage/connexions de remplacement | 1 kit | 15 | 15 | 2 | Remplacement rapide en cas de panne |
| Total |  |  | 45 | 80 | Cout direct cumule + charge projet |

## Synthese budgetaire

- **Cout financier estime (direct)**: **45 EUR**
- **Charge estimee**: **80 h**
- **Cout valorise du temps**: **80 h x 30 EUR/h = 2400 EUR**
- **Projection budget global (direct + valorise)**: **2445 EUR**

## Detail par categorie

### Temps
- Conception et pilotage: 8 h
- Developpement scripts/jeux: 35 h
- Qualite/tests: 23 h
- Documentation et transfert: 14 h

### Materiel
- Consommables et stock securite: 45 EUR
- Materiel principal: reutilisation de l existant (0 EUR additionnel)

### Licences
- Java (OpenJDK), Python, MkDocs, pytest, pylint, shellcheck, pygame, LÖVE: 0 EUR
- Condition: conserver des dependances compatibles open source/education

### Exploitation et risques
- Risque principal: panne carte SD -> mitigation par stock de secours.
- Risque principal: regression apres pull -> mitigation par pipeline auto + tests.
- Risque principal: ecart docs/code -> mitigation par generation + tests documentation.

## Validation

```bash
./scripts/tests/test_couts.sh
```

## Historique de mise a jour

- 2026-02-09: initialisation du suivi des couts.
- 2026-02-10: ajout du lot NeonSumo (developpement, tests, documentation).
- 2026-02-10: durcissement complet conformite consignes.
- 2026-02-10: stabilisation pipeline qualite et deploiement.
- 2026-02-10: enrichissement complet du modele de cout (temps, materiel, licences, exploitation).

## Liens associes

- Index docs: `index.md`
- Technique: `technique.md`
- Tests: `tests.md`
