# Datum, par Le Repère Ingénierie

Application de calcul de charpentes. Elle commence par le bois, selon la norme **CSA O86:19, _Règles de
calcul des charpentes en bois_**.

🌐 **Application en ligne : <https://csa-o86.streamlit.app>**

📘 Norme : [version française](./pdf/CSA%20O86-F19.pdf) · [English version](./pdf/CSA%20O86-19.pdf)

> ⚠️ **Avertissement** : cet outil aide à la conception. Il ne remplace pas le jugement d'un ingénieur.
> Les résultats doivent être vérifiés par un professionnel qualifié, qui reste responsable de la conception.

---

## Où en est le projet ?

**But** : une application web (ordinateur et iPhone) pour les calculs de la norme CSA O86, puis des normes
d'acier et de béton et du CNB, avec plusieurs éditions, des figures 2D et 3D interactives et des notes de
calcul en PDF.

| Étape | État |
|---|---|
| Planification de l'architecture | ✅ terminée |
| **Phase 1** : réorganiser le moteur de calcul pour qu'il suive la norme | 🔄 à commencer |
| **Phase 2** : API (le moteur accessible par le web) | ⏳ |
| **Phase 3** : nouvelle interface web (ordinateur et mobile, figures 2D), puis notes de calcul PDF | ⏳ |
| Plus tard : 3D, projets sauvegardés, abonnements, autres normes et éditions | ⏳ |

Pendant ce temps, l'application Streamlit actuelle reste en ligne et continue de fonctionner.

---

## Ce que l'application calcule aujourd'hui

**Bois de sciage (chapitre 6)** : bois classé visuellement, MSR et MEL, bois sec ou vert, dimensions du
tableau A.3, éléments de 1 à 5 plis. Les coefficients de correction (KD, KS, KT, KH, KZ) sont appliqués
automatiquement.

| Vérification | Article | État |
|---|---|---|
| Moment de flexion, Mr | 6.5.3 | ✅ (KL selon 7.5.6.4 : avec le chapitre 7) |
| Cisaillement, Vr et Fr | 6.5.4 | ✅ |
| Compression parallèle au fil, Pr | 6.5.5 | ✅ (1 pli) |
| Compression perpendiculaire au fil, Qr et Q'r | 6.5.6 | ✅ |
| Compression oblique par rapport au fil | 6.5.7 | ⏳ |
| Traction parallèle au fil | 6.5.8 | ⏳ |
| Flexion et charge axiale combinées | 6.5.9 | ⏳ |

Chaque vérification affiche le ratio effet pondéré / résistance pondérée : 🟢 respecté (≤ 1.00) ou
🔴 dépassé.

---

## Pour suivre en détail

| Document | Contenu |
|---|---|
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Le plan : organisation du code selon la norme, éditions, interface web, feuille de route |
| [`CLAUDE.md`](./CLAUDE.md) | Les règles de travail et les décisions d'interprétation de la norme |
| [Pull requests](https://github.com/GabPoulin/CSA_O86-19_app/pulls?q=is%3Apr) | L'historique de chaque changement, avec ses justifications et ses vérifications |

---

## Lancer l'application sur son ordinateur

Prérequis : Python 3.10 ou plus récent.

```bash
git clone https://github.com/GabPoulin/CSA_O86-19_app.git
cd CSA_O86-19_app
pip install -r requirements.txt
streamlit run Accueil.py
```

Tests (les valeurs attendues sont calculées à la main à partir de la norme) :

```bash
python general_design.py   # chapitre 5
python sawn_lumber.py      # chapitre 6
```

---

## Contact

Pour toute question (for any questions) : poulin33@me.com
