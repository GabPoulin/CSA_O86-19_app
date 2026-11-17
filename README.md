# Calculatrice | Bois : CSA O86:19

Application de calcul des charpentes en bois selon la norme **CSA O86:19, _Règles de calcul des charpentes
en bois_**. Elle est écrite en [Python](https://www.python.org/) avec une interface
[Streamlit](https://streamlit.io/).

📘 Norme : [version française](./pdf/CSA%20O86-F19.pdf) · [English version](./pdf/CSA%20O86-19.pdf)

> ⚠️ **Avertissement** : cet outil aide à la conception. Il ne remplace pas le jugement d'un ingénieur.
> Les résultats doivent être vérifiés par un professionnel qualifié, qui reste responsable de la conception.

---

## Fonctionnalités

### Bois de sciage (chapitre 6)

**Matériaux**
- Catégories détectées automatiquement selon les dimensions :
  - charpente légère
  - montants, solives et madriers
  - poutres et longerons
  - poteaux et bois carrés
- Bois classé mécaniquement : **MSR** et **MEL**.
- Groupes d'essences : sapin de Douglas-mélèze, pruche-sapin, épinette-pin-sapin (S-P-F) et essences
  nordiques, avec leurs classes (tableaux 6.4 à 6.9).
- Dimensions nettes selon le **tableau A.3** :
  - bois sec ou vert ;
  - gros bois vert ;
  - mode « dimensions brutes ».
- Éléments composés de 1 à 5 plis.
- Charges appliquées sur la grande face (poutres et longerons).

**Coefficients de correction (6.4)** : KD, KS, KT, KH et KZ, calculés automatiquement selon les options
choisies.

**Résistances (6.5)**

| Vérification | Article | État |
|---|---|---|
| Moment de flexion, Mr | 6.5.3 | ✅ (KL = 1 selon 6.5.3.2 ; sinon un message indique que KL est requis) |
| Cisaillement, Vr, et cisaillement par fissuration à l'entaille, Fr | 6.5.4 | ✅ |
| Compression parallèle au fil, Pr, selon les deux axes | 6.5.5.2 | ✅ (élément d'un seul pli) |
| Compression perpendiculaire au fil | 6.5.6 | 🚧 à venir |
| Compression oblique par rapport au fil | 6.5.7 | 🚧 à venir |
| Traction parallèle au fil | 6.5.8 | 🚧 à venir |
| Flexion et charge axiale combinées | 6.5.9 | 🚧 à venir |
| Éléments composés en compression | 6.5.5.3 | 🚧 à venir |
| KL selon 7.5.6.4 | 6.5.3.2.2 | 🚧 avec le chapitre 7 |

Chaque vérification affiche le **ratio charge/résistance** avec 2 décimales :
- 🟢 l'état limite est respecté lorsque l'effet pondéré ne dépasse pas la résistance (ratio ≤ 1.00, 5.1.2) ;
- 🔴 l'état limite est dépassé sinon.

### Conception générale (chapitre 5)

Le moteur de calcul (`general_design.py`) contient déjà :
- Kd ;
- la réduction de section ;
- la flèche et la déformation permanente ;
- l'accumulation d'eau ;
- la **vibration des planchers** (A.5.4.5, solives et CLT) ;
- le retrait dû à l'humidité ;
- le contreventement des fermes ;
- la **résistance au feu** (annexe B).

🚧 Ces calculs ne sont pas encore offerts dans l'interface.

---

## Installation

Prérequis : **Python 3.10 ou plus récent**.

```bash
git clone https://github.com/GabPoulin/CSA_O86-19_app.git
cd CSA_O86-19_app
pip install -r requirements.txt
```

Le projet contient aussi une configuration **Dev Container** (`.devcontainer/`). Elle permet d'ouvrir
le projet dans GitHub Codespaces ou VS Code avec tout déjà installé.

## Lancer l'application

```bash
streamlit run Accueil.py
```

L'application s'ouvre ensuite à l'adresse <http://localhost:8501>.

## Tests

Chaque module contient ses tests. Les valeurs attendues sont **calculées à la main à partir de la norme**.

```bash
python general_design.py   # chapitre 5
python sawn_lumber.py      # chapitre 6
```

---

## Structure du projet

| Fichier | Rôle |
|---|---|
| `Accueil.py` | Page d'accueil (point d'entrée de Streamlit) |
| `pages/1_Bois de sciage.py` | Interface du bois de sciage |
| `sawn_lumber.py` | Moteur de calcul du chapitre 6 (bois de sciage) |
| `general_design.py` | Moteur de calcul du chapitre 5 (conception générale) |
| `config.py` | Paramètres partagés (titre) |
| `csa_o86_19.db` | Tableaux de la norme (SQLite) : résistances prévues, dimensions, sous-planchers |
| `pdf/` | Norme CSA O86:19 (français et anglais) |
| `.streamlit/config.toml` | Thème de l'application |
| `CLAUDE.md` | Consignes de développement et décisions d'interprétation de la norme |

Le **moteur de calcul est séparé de l'interface**. Les modules `sawn_lumber.py` et `general_design.py`
n'utilisent pas Streamlit. Ils peuvent donc être testés et réutilisés seuls.

## Principes de développement

- **CSA O86:19 est la référence ultime** et est suivie à la lettre. Le **CNB 2020** sert lorsque la
  norme y renvoie.
- Chaque fonction cite l'**article de la norme** qu'elle applique.
- On écrit d'abord des **fonctions simples** (une équation, un coefficient ou un tableau à la fois),
  qui sont ensuite combinées pour les calculs plus complexes.
- Chaque calcul est **testé dans plusieurs scénarios**, y compris les cas limites.
- Chaque changement se fait dans **sa propre branche**, avec une Pull Request, et n'est mergé qu'après
  validation.
- Les interprétations de la norme et les décisions sur les données sont notées dans
  [`CLAUDE.md`](./CLAUDE.md).

---

## Contact

Pour toute question (for any questions) : poulin33@me.com
