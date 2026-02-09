# Documentation developpeur TronGame

## Convention integration borne
Chaque jeu de la borne doit fournir:
- `description.txt`
- `bouton.txt`
- `highscore`
- un script de lancement dans `borne_arcade/<NomJeu>.sh`

## Runtime
- Python 3
- Pygame

## Validation technique
Executer la suite globale:
```bash
./scripts/tests/lancer_suite.sh
```

## Deploiement
La mise a jour automatique apres `git pull` est geree par `.githooks/post-merge`.
