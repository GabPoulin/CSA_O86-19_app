# CLAUDE.md : consignes pour travailler sur ce projet

**Datum, par Le Repère Ingénierie** : application de calcul de charpentes, en commençant par
le bois selon **CSA O86:19** (Python ; interface Streamlit, à remplacer par une interface web).
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
  besoin) et la page **de la norme** (numéro imprimé au bas de la page, pas celui du fichier PDF :
  page imprimée = page du PDF - 6 dans `CSA O86-F19.pdf`), puis expliquer le raisonnement (ex. conservateur ou non conservateur).
  Toujours **lire la norme dans `pdf/` pour valider** avant de coder, au lieu de se fier à sa mémoire
  ou au code existant. Le code existant peut contenir des erreurs.
- Citer l'article de la norme dans la docstring de chaque fonction (le style actuel est à conserver).

## Conventions de calcul et d'affichage

- **Nombres affichés avec un point décimal** (ex. `45.56%`), pas de virgule.
- **Calculs de base : valeurs positives seulement** (charges, moments, efforts). Ne pas gérer les valeurs
  négatives (soulèvement, moments négatifs) pour l'instant ; elles viendront éventuellement dans des
  fonctions plus avancées.
- S'en tenir **uniquement aux formules et aux calculs de la norme**.
- **Unités** : **tous les calculs se font en métrique**, comme les normes (mm, N, MPa). L'impérial sert
  **uniquement à l'affichage des entrées et des résultats**, avec une bascule en tout temps pour toutes
  les grandeurs (dimensions, forces, moments…). La note de calcul indique **les deux unités** pour les
  données et les résultats (ex. `b = 38 mm (1.50 po)`).
- **Toujours écrire les unités avec les chiffres** : dans le code, les commentaires, les tests, les
  messages et la documentation (ex. `# 12 620 N / 4,448 N/lb = 2837 lb`).
- **Vocabulaire** : on compare une **charge pondérée** (P_f, T_f, V_f, M_f…) à une **résistance
  pondérée**. Ne pas utiliser « effet ».
- **Formules en LaTeX** dans la trace des calculs ; chaque vérification a une **figure schématique**
  (SVG, pas à l'échelle). Format de la note de calcul : voir `ARCHITECTURE.md`, section 8.

## Décisions sur les données (validées avec l'utilisateur)

- **Dimensions (tableau A.3)** : dimensions nominales offertes : 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14 et 16 po.
  7 et 9 po : seulement pour le gros bois vert (165 et 216 mm, seules valeurs du tableau A.3) ;
  11, 13 et 15 po n'existent pas en dimensions nominales.
  Gros bois (face étroite >= 5 po nominal) vert : dimensions du gros bois du tableau A.3.
- **KZ (tableau 6.13)** (issue #45) : la **dimension réelle** (sèche, verte ou brute) choisit la ligne.
  Une grande face absente du tableau (ex. 143, 165 ou 216 mm) prend la ligne de la dimension
  **supérieure** (KZ diminue avec la dimension, donc conservateur). Une face étroite entre deux colonnes
  (65 à 88 mm, 103 à 113 mm) prend la **plus petite** valeur des deux colonnes voisines.
- **KT (tableau 6.11)** (issue #45) : bois traité et incisé de plus de 89 mm d'épaisseur (absent du
  tableau) : KT = 1,00.
- **Mode « dimensions brutes »** : convention de l'utilisateur (hors tableau A.3), à conserver telle quelle.
- **Traction du MSR de plus de 184 mm (tableau 6.8)** : pour les classes sans valeur dans la colonne
  « > 184 mm », bloquer la traction avec un message (à faire lors de l'ajout de l'onglet de traction).

## Architecture du code : suivre la norme

**Lire [`ARCHITECTURE.md`](./ARCHITECTURE.md) avant d'écrire ou de déplacer du code.** En résumé :

- Moteur Python indépendant de l'interface : `moteur/normes/<norme_edition>/` (ex. `csa_o86_19/`),
  une API (`api/`) et une interface web (`web/`) ; Streamlit reste en place jusqu'au remplacement.
- Le code suit la norme : `ch_6_bois_de_sciage/art_6_5_calcul_des_resistances/art_6_5_5_...py`.
  Un article dont des sous-articles sont codés devient un dossier. Titres complets en français
  **sans accents**. Pas de dossier pour les chapitres sans formule. Annexes à la fin.
- Fonctions et variables nommées avec **les symboles de 3.2**, majuscules et minuscules respectées
  (`f_c` prévue, `F_c()` corrigée, `K_Zc()`, `P_r()`, `Q_r_prime()`).
- Fonctions dans l'ordre d'apparition des formules ; fonctions de vérification à la fin, qui retournent
  un `Resultat` (trace utilisée pour l'affichage, la note de calcul PDF et les tests).
- Éditions : un dossier par édition ; un article inchangé importe celui de l'édition précédente.
- Tout en français. Aucune logique de calcul dans l'interface.
- Une modification de la structure doit d'abord être discutée avec l'utilisateur, puis notée dans
  `ARCHITECTURE.md`.

## Fonctions simples d'abord

- Écrire des **fonctions simples** qui font **un seul calcul de la norme** (une équation, un coefficient,
  un tableau). Par exemple, une fonction pour KZc, une pour Cc, une pour Kc, puis une pour Pr.
- Chaque fonction simple est **testée seule** avec des valeurs calculées à la main.
- Les calculs plus complexes sont construits ensuite **en combinant ces fonctions simples**, sans
  recopier leurs formules.

## Interprétations de la norme validées avec l'utilisateur

- **KZc (6.5.5.2.4)** : L = longueur de l'élément, pas la longueur effective ni la longueur entre les
  appuis latéraux (voir aussi A.6.5.5.2.4 b) : L = L1 + L2). KZc est calculé pour toutes les
  catégories, y compris la charpente légère (6.4.5.2) et le MSR/MEL (6.4.5.3).
- **KT dans KC (6.5.5.2.5)** : KT des « autres propriétés » (tableau 6.11), le même que dans Fc. Le KT
  du module d'élasticité ne sert qu'au calcul du module d'élasticité.
- **KH (6.4.4, tableau 6.12)** (issue #7) : un élément composé de 2 plis ou plus prend **toujours** la
  colonne « Poutres composées » (cas 1, cas 2, MSR compris). La colonne MSR (1,20) est une sous-colonne
  du **cas 2** ; au cas 1, le MSR prend 1,10. Traction au cas 2 (« — » au tableau) : KH = 1,00.
- **Ke** : une fonction simple reçoit Le (ou Ke) en chiffre. Une fonction séparée déduira Ke des
  conditions d'appui (annexe A, informative).

## Façon de travailler

- **Faire de petits changements**, un sujet à la fois.
- **Poser les questions au fur et à mesure.** L'utilisateur répond rapidement (cellulaire ou ordinateur),
  donc il vaut mieux demander que supposer.
- Communiquer en français.

## Git et GitHub

Dépôt : **`LeRepere-GP/datum`** (organisation Le Repère).

1. **Une nouvelle branche par changement**, créée à partir de `main` à jour, avec un nom clair
   (`feature/...`, `fix/...`, `docs/...`). Ne jamais committer directement sur `main`.
2. **Pas de PR automatique.** Créer une PR seulement quand c'est pertinent (travail prêt à être révisé,
   correctif à appliquer, décision à faire valider). Sinon, pousser la branche et en parler à l'utilisateur.
3. **Surveiller les PR créées** (abonnement à l'activité de la PR) : noter les approbations et répondre
   aux commentaires laissés dans GitHub.
4. **Ne jamais merger soi-même.** Le merge dans `main` se fait seulement quand l'utilisateur confirme
   que tout fonctionne.
5. **Assigner l'utilisateur (`GabPoulin`)** à chaque issue et PR créée, pour qu'il soit notifié.
6. **Issues** : créer des issues pour les bogues, les écarts avec la norme et les améliorations repérés,
   avec une **solution proposée**. Ne pas les régler sans accord quand elles touchent une interprétation
   de la norme.

## Être proactif

- Travailler de façon autonome dans des **branches à part**, en suivant la feuille de route
  (`ARCHITECTURE.md`, section 14), et **proposer les avancées de temps en temps** à l'utilisateur.
- **Quand une PR est mergée, continuer comme au début d'une séance planifiée** : lire les nouveaux
  commentaires des issues et des PR, vérifier les PR ouvertes, puis faire avancer la feuille de route.
- **Plusieurs PR à la fois sont permises** si ce sont de **petits avancements qui ne se chevauchent
  pas** (fichiers ou parties de fichiers différents, sans dépendance entre elles). Chaque branche part
  de `main` à jour. Si un nouveau travail dépend d'une PR ouverte ou touche les mêmes lignes, attendre
  son merge. Rappeler à l'utilisateur les PR à merger.
- Les décisions d'interprétation de la norme et les changements de structure restent **toujours
  soumis à l'utilisateur** avant d'être appliqués.
- **Compte Groupe Lantier** (`ACCES_GROUPE_LANTIER.md`, lu par l'application, issue #56) : quand une
  fonction est intégrée au nouveau moteur, l'ajouter dans les deux listes **non cochée**. Seul
  l'utilisateur coche les cases (offerte à Groupe Lantier ; testée, sans avertissement « en test »).

## Tests : tester et retester

Chaque changement de calcul doit être vérifié dans **plusieurs scénarios** avant d'être présenté :

- cas typiques, cas limites (valeurs exactement au seuil, ratio = 1,00), valeurs nulles ou vides ;
- toutes les branches de la logique (chaque `if` de la norme : catégories, coefficients, conditions) ;
- les valeurs attendues sont calculées à la main à partir de la norme, pas recopiées de la sortie du code ;
- la page Streamlit est testée (pas d'exception, bon affichage) avec `streamlit.testing.v1.AppTest`
  en partant d'`Accueil.py`, puis `switch_page(...)`. La connexion est exigée (`acces.py`) : dans les
  tests, définir `at.secrets["mots_de_passe"]` et se connecter (voir `tests/test_acces.py`).
- **Secrets** (mots de passe, jetons) : dans les secrets de Streamlit Cloud ou dans
  `.streamlit/secrets.toml` en local (ignoré par git). Jamais dans le code, une issue ou un commentaire.

Commandes :

```bash
pip install -r requirements-dev.txt   # outils de développement (pytest)
pytest                                # tous les tests (nouveau moteur et anciens modules)
streamlit run Accueil.py              # lancer l'application
```

Les tests roulent aussi automatiquement sur GitHub à chaque PR (`.github/workflows/tests.yml`), sur
Python 3.14 et 3.15.

## Environnement et versions

- **Python 3.14** : version de l'application en ligne (Streamlit Cloud) et de l'environnement de
  développement (`.devcontainer`). Les tests automatiques roulent aussi sur Python 3.15.
- **Versions exactes** dans `requirements.txt` et `requirements-dev.txt` (`==`), pour que l'app en ligne,
  les tests et l'ordinateur de l'utilisateur utilisent exactement les mêmes versions.
- **Dependabot** (`.github/dependabot.yml`) propose chaque semaine des PR de mise à jour (paquets
  Python, actions GitHub, `.devcontainer`). Pendant les séances, vérifier ces PR : tests automatiques,
  notes de version (changements qui pourraient toucher les calculs), puis les signaler à l'utilisateur.
  Ne jamais les merger soi-même.

## Structure

Migration en cours vers la structure de `ARCHITECTURE.md` (feuille de route : section 14, suivi dans
l'issue #30). Nouveau moteur : `moteur/` (tests dans `tests/`). Anciens modules, encore utilisés par
l'interface :

- `general_design.py` : chapitre 5, conception générale
- `sawn_lumber.py` : chapitre 6, bois de sciage
- `pages/` : pages Streamlit ; `Accueil.py` : page d'accueil (point d'entrée)
- `moteur/normes/csa_o86_19/base_de_donnees/csa_o86_19.db` : tableaux de la norme (SQLite), lus par
  `base_de_donnees.lire()` (lecture seule) ; les anciens modules y accèdent encore avec SQLAlchemy
