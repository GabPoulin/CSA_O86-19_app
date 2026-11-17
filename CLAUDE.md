# CLAUDE.md : consignes pour travailler sur ce projet

Calculatrice de conception de charpentes en bois selon **CSA O86:19**, en Python et Streamlit.
L'utilisateur est ingénieur en structure de bâtiment et utilisera ce logiciel dans sa pratique.
**Une erreur de calcul peut être dangereuse.** La fiabilité passe avant tout.

## Références techniques

- **CSA O86:19 est la référence ultime.** La suivre à la lettre : articles, tableaux, équations, notes.
  La norme est dans `pdf/` (`CSA O86-F19.pdf` en français, `CSA O86-19.pdf` en anglais).
- **Code national du bâtiment du Canada 2020 (CNB 2020)** : la référence lorsque la norme y renvoie
  (charges, combinaisons, critères de tenue en service, etc.).
- Si un article est ambigu ou si une interprétation est nécessaire, **poser la question à l'utilisateur.
  Ne jamais deviner.**
- **Justifier chaque choix par la norme** : citer l'article, le texte exact (français et anglais au
  besoin) et la page du PDF, puis expliquer le raisonnement (ex. conservateur ou non conservateur).
  Toujours **lire la norme dans `pdf/` pour valider** avant de coder, au lieu de se fier à sa mémoire
  ou au code existant. Le code existant peut contenir des erreurs.
- Citer l'article de la norme dans la docstring de chaque fonction (le style actuel est à conserver).

## Conventions de calcul et d'affichage

- **Nombres affichés avec un point décimal** (ex. `45.56%`), pas de virgule.
- **Calculs de base : valeurs positives seulement** (charges, moments, efforts). Ne pas gérer les valeurs
  négatives (soulèvement, moments négatifs) pour l'instant ; elles viendront éventuellement dans des
  fonctions plus avancées.
- S'en tenir **uniquement aux formules et aux calculs de la norme**.

## Décisions sur les données (validées avec l'utilisateur)

- **Dimensions (tableau A.3)** : dimensions nominales offertes : 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14 et 16 po.
  7 et 9 po : seulement pour le gros bois vert (165 et 216 mm, seules valeurs du tableau A.3) ;
  11, 13 et 15 po n'existent pas en dimensions nominales.
  Gros bois (face étroite >= 5 po nominal) vert : dimensions du gros bois du tableau A.3.
- **Mode « dimensions brutes »** : convention de l'utilisateur (hors tableau A.3), à conserver telle quelle.
- **Traction du MSR de plus de 184 mm (tableau 6.8)** : pour les classes sans valeur dans la colonne
  « > 184 mm », bloquer la traction avec un message (à faire lors de l'ajout de l'onglet de traction).

## Architecture du code : fonctions simples d'abord

- Écrire des **fonctions simples** qui font **un seul calcul de la norme** (une équation, un coefficient,
  un tableau). Par exemple, une fonction pour KZc, une pour Cc, une pour Kc, puis une pour Pr.
- Chaque fonction simple est **testée seule** avec des valeurs calculées à la main.
- Les calculs plus complexes sont construits ensuite **en combinant ces fonctions simples**, sans
  recopier leurs formules.

## Façon de travailler

- **Faire de petits changements**, un sujet à la fois.
- **Poser les questions au fur et à mesure.** L'utilisateur répond rapidement (cellulaire ou ordinateur),
  donc il vaut mieux demander que supposer.
- Communiquer en français.

## Git et GitHub

1. **Une nouvelle branche par changement**, créée à partir de `main` à jour, avec un nom clair
   (`feature/...`, `fix/...`, `docs/...`).
2. Committer sur cette branche, la pousser sur GitHub, puis ouvrir une Pull Request vers `main`.
3. **Ne jamais merger soi-même.** Le merge dans `main` se fait seulement quand l'utilisateur confirme
   que tout fonctionne.
4. Ne jamais committer directement sur `main`.

## Tests : tester et retester

Chaque changement de calcul doit être vérifié dans **plusieurs scénarios** avant d'être présenté :

- cas typiques, cas limites (valeurs exactement au seuil, ratio = 1,00), valeurs nulles ou vides ;
- toutes les branches de la logique (chaque `if` de la norme : catégories, coefficients, conditions) ;
- les valeurs attendues sont calculées à la main à partir de la norme, pas recopiées de la sortie du code ;
- la page Streamlit est testée (pas d'exception, bon affichage) avec `streamlit.testing.v1.AppTest`
  en partant d'`Accueil.py`, puis `switch_page(...)`.

Commandes actuelles :

```bash
python general_design.py   # tests du chapitre 5
python sawn_lumber.py      # tests du chapitre 6
streamlit run Accueil.py   # lancer l'application
```

## Structure

- `general_design.py` : chapitre 5, conception générale
- `sawn_lumber.py` : chapitre 6, bois de sciage
- `pages/` : pages Streamlit ; `Accueil.py` : page d'accueil (point d'entrée)
- `csa_o86_19.db` : tableaux de la norme (SQLite, lus avec SQLAlchemy)
