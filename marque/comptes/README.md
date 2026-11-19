# Image de marque de chaque compte (application et note de calcul)

Un dossier par compte, nommé avec l'identifiant du compte (`acces.py`) : `lantier/` pour Groupe Lantier.
Quand ce compte est connecté, la note de calcul PDF prend ce logo et ces couleurs par défaut.
Il peut encore les changer pour la séance, dans « Apparence de la note ».

| Fichier | Contenu |
|---|---|
| `logo.svg` (ou `logo.png`, `logo.jpg`) | Logo de l'en-tête. **SVG de préférence**, sinon PNG haute résolution (au moins 1000 px de large, fond transparent). Format horizontal, idéalement : il est affiché à 1.0 cm de haut. |
| `logo_renverse.svg` | Logo pour fond foncé : barre latérale de l'application. |
| `symbole.svg` | Symbole seul : icône de l'onglet du navigateur et barre latérale repliée. |
| `logo_vertical*.svg` | Autres versions du logo, gardées pour plus tard. |
| `polices.toml` | Familles de polices : `titres` (en majuscules) et `texte`. Ex. `titres = "Rift"`, `texte = "DIN 2014"`. |
| `polices/` | Fichiers de polices (`.otf`, `.ttf`). **Jamais dans git** (`.gitignore`) : ce sont des polices sous licence et le dépôt est public. Une police absente est remplacée par la police par défaut. |
| `couleurs.toml` | Deux couleurs hexadécimales : `principale` (titres, lignes, en-têtes de tableau ; fond de la barre latérale) et `accent` (articles, sources ; boutons principaux et accents de l'interface). Facultatif : `fond`, couleur de fond de l'interface. Exemple ci-dessous. |

```toml
principale = "#233614"
accent = "#9E5A00"
```

Un fichier absent garde la valeur par défaut (Le Repère). Une couleur mal écrite (autre que `#RRGGBB`)
produit une erreur.

**Pour déposer les fichiers** : sur GitHub, ouvre `marque/comptes/lantier/`, puis « Add file » >
« Upload files ». Choisis « Create a new branch » et propose les changements (PR). Le logo s'applique
après le merge dans `main`.
