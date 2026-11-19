# Architecture de Datum

**Datum, par Le Repère Ingénierie** : application web de calcul de charpentes.

Ce document fixe la structure de l'application **avant** d'écrire de nouvelles fonctions. Une modification
de cette structure doit d'abord être discutée avec l'utilisateur, puis notée ici.

---

## 1. Vision et objectifs

- **Datum, par Le Repère Ingénierie** : une **application web** de calcul de charpentes, accessible en tout temps sur **ordinateur** et sur
  **mobile (iPhone)**.
- **CSA O86** (bois) d'abord, puis **CSA S16** (acier), **CSA A23.3** (béton) et le **CNB** (charges et
  combinaisons).
- **Plusieurs éditions** de chaque norme : on travaille dans l'édition choisie, et les anciennes éditions
  restent utilisables.
- Des **images 2D** et des **modèles 3D interactifs en temps réel** (ex. assemblage boulonné). Les
  fonctions 3D les plus lourdes peuvent être réservées à l'ordinateur ; le mobile garde les calculs et la 2D.
- Des **notes de calcul en PDF**, complètes, simples et lisibles, pour l'archivage.
- Plus tard : **sauvegarde des calculs par projet**, **comptes clients** avec abonnement mensuel ou annuel,
  et une **version gratuite de démonstration**.

## 2. Principes

1. **Le code suit la norme** : mêmes chapitres, mêmes articles, même ordre, mêmes symboles.
2. **Le moteur de calcul est indépendant de l'interface.** Il est en Python, sans aucune dépendance à
   l'interface. L'interface ne contient aucune logique de calcul.
3. **Fonctions simples d'abord** (un calcul de la norme chacune), puis des fonctions de vérification
   qui les combinent.
4. **Chaque vérification produit une trace** (article, formule, valeurs, résultat). Cette trace sert à
   l'affichage du détail, à la note de calcul PDF et aux tests.
5. **Chaque édition est autonome**, mais réutilise le code des éditions précédentes quand un article ne
   change pas.
6. **Tout est en français**, sans accents dans les noms de fichiers, de dossiers et de fonctions.

---

## 3. Vue d'ensemble du dépôt

```
moteur/                     ← moteur de calcul Python (aucune dépendance à l'interface)
  commun/                   ← outils partagés par toutes les normes
    resultat.py             ← trace d'une vérification (section 8)
    registre.py             ← catalogue des calculs offerts par édition (section 9)
  normes/
    csa_o86_19/             ← bois, édition 2019 (section 5)
    csa_o86_24/             ← bois, édition suivante (plus tard)
    csa_s16_19/             ← acier (plus tard)
    csa_a23_3_19/           ← béton (plus tard)
    cnb_2020/               ← CNB : charges et combinaisons (plus tard)
api/                        ← API web (FastAPI) qui expose le moteur
web/                        ← interface web (section 10)
tests/                      ← pytest, même arborescence que moteur/ et api/
Accueil.py, pages/          ← interface Streamlit actuelle, conservée jusqu'au remplacement
ARCHITECTURE.md, CLAUDE.md, README.md
```

---

## 4. Nommage

### Fichiers et dossiers

Un nom Python ne peut pas commencer par un chiffre : on utilise des préfixes courts. Les accents sont
retirés des noms de fichiers (macOS et Linux n'encodent pas toujours les lettres accentuées de la même
façon).

| Élément de la norme | Préfixe | Exemple |
|---|---|---|
| Norme et édition | aucun | `csa_o86_19/` |
| Chapitre | `ch_` | `ch_6_bois_de_sciage/` |
| Article | `art_` | `art_6_5_5_resistance_a_la_compression_parallele_au_fil.py` |
| Annexe | `annexe_` | `annexe_A_renseignements_supplementaires_et_autres_methodes/` |
| Tableau | `tableau_` | `tableau_A_11_valeurs_de_densite.py` |

- Les points du numéro deviennent des `_` (6.5.5 → `6_5_5`).
- Le **titre complet** de l'article est repris de la version française de la norme, sans accents, en
  minuscules, avec des `_` (« d'œuvre » → `d_oeuvre`).
- **Un article dont des sous-articles sont codés devient un dossier** du même nom, qui contient un
  fichier par sous-article. Exemple : `art_6_5_calcul_des_resistances/` contient
  `art_6_5_3_resistance_au_moment_de_flexion.py`.
- **Les chapitres ou articles sans formule n'ont pas de dossier** (ex. chapitres 1, 2 et 4).
- Les dossiers sont créés **au fur et à mesure** du développement, en suivant le plan de la section 5.

### Fonctions et variables : symboles de la norme

Les fonctions et variables portent **le symbole de la norme**, tel que défini à l'article **3.2**, en
respectant **les majuscules et les minuscules**. Le `_` sépare le symbole de son indice.

| Norme | Code | Note |
|---|---|---|
| f_c | `f_c` | résistance **prévue** (minuscule) |
| F_c | `F_c()` | résistance **corrigée** (majuscule) |
| K_Zc, K_C, C_C | `K_Zc()`, `K_C()`, `C_C()` | |
| P_r, Q_r, M_r, V_r | `P_r()`, `Q_r()`, `M_r()`, `V_r()` | |
| Q'_r, A'_b | `Q_r_prime()`, `A_b_prime()` | l'apostrophe est interdite en Python |
| E_05, A_b, L_e | `E_05`, `A_b`, `L_e` | |
| ϕ | `phi` | |

Quand un calcul n'a pas de symbole dans la norme, on utilise un nom descriptif en français sans
accents (ex. `categorie_de_bois()`).

---

## 5. Plan complet de CSA O86:19

Chapitres et articles de 2e niveau de la norme. Les articles marqués « dossier » seront découpés en un
fichier par sous-article. Les chapitres 1, 2 et 4 ne contiennent pas de formule et n'ont pas de dossier.

```
moteur/normes/csa_o86_19/
  base_de_donnees/csa_o86_19.db
  element.py                                   ← structure partagée d'un élément (section 7)

  ch_3_definitions_symboles_espacements_et_dimensions/
    art_3_2_symboles.py
    art_3_3_espacements_et_dimensions.py

  ch_5_conception_generale/
    art_5_1_calculs_aux_etats_limites.py
    art_5_2_charges.py                         (lien avec le CNB)
    art_5_3_conditions_et_coefficients_influant_sur_la_resistance.py
    art_5_4_exigences_relatives_a_la_tenue_en_service/          (dossier : 5.4.1 à 5.4.6)
    art_5_5_effort_de_contreventement_lateral_sur_les_membrures_d_ame_en_compression_des_fermes_de_toit_en_bois.py
    art_5_6_resistance_au_feu.py

  ch_6_bois_de_sciage/
    art_6_2_materiaux.py
    art_6_3_resistances_prevues_et_modules_d_elasticite.py
    art_6_4_coefficients_de_correction.py
    art_6_5_calcul_des_resistances/                             (dossier : 6.5.1 à 6.5.12)
    art_6_6_etats_limites_de_tenue_en_service.py

  ch_7_bois_lamelle_colle/
    art_7_2_materiaux.py
    art_7_3_resistances_prevues_et_modules_d_elasticite.py
    art_7_4_coefficients_de_correction.py
    art_7_5_calcul_des_resistances/                             (dossier : 7.5.1 à 7.5.12, dont K_L en 7.5.6)
    art_7_6_etats_limites_de_tenue_en_service.py

  ch_8_bois_lamelle_croise/
    art_8_2_materiaux.py
    art_8_3_coefficients_de_correction.py
    art_8_4_calcul_des_resistances/                             (dossier : 8.4.1 à 8.4.8)
    art_8_5_etats_limites_de_tenue_en_service.py

  ch_9_panneaux_structuraux/
    art_9_2_materiaux.py
    art_9_3_resistances_prevues.py
    art_9_4_coefficients_de_correction.py
    art_9_5_calcul_des_resistances/                             (dossier : 9.5.1 à 9.5.8)

  ch_10_elements_de_charpente_composites/
    art_10_3_exigences_relatives_aux_joints_transmetteurs_de_contraintes.py
    art_10_4_coefficient_de_correction_pour_joints_x_j.py
    art_10_5_poutres_a_ames_en_contreplaque_et_en_panneaux_osb/  (dossier : 10.5.1 à 10.5.9)
    art_10_6_panneaux_a_revetement_travaillant.py

  ch_11_structures_resistantes_aux_charges_laterales/
    art_11_3_calcul_des_murs_de_refend_et_des_diaphragmes_a_ossature_legere/
    art_11_4_considerations_relatives_au_calcul_des_murs_de_refend_a_ossature_legere/
    art_11_5_coefficients_de_correction_de_resistance_pour_les_murs_de_refend_et_les_diaphragmes_a_ossature_legere/
    art_11_6_resistance_des_murs_de_refend_et_des_diaphragmes_a_ossature_legere.py
    art_11_7_fleche_des_murs_de_refend_et_des_diaphragmes_a_ossature_legere.py
    art_11_8_considerations_relatives_au_calcul_parasismique_des_murs_de_refend_et_des_diaphragmes_a_ossature_legere/
    art_11_9_calcul_des_murs_de_refend_et_des_diaphragmes_en_bois_lamelle_croise/

  ch_12_assemblages/
    art_12_2_exigences_generales.py
    art_12_3_anneaux_fendus_et_disques_de_cisaillement/
    art_12_4_boulons_et_goujons/
    art_12_5_goujons_forces/
    art_12_6_tire_fond/
    art_12_7_rivets_pour_bois/
    art_12_8_connecteurs_metalliques/
    art_12_9_clous_et_pointes/
    art_12_10_etriers_a_solives.py
    art_12_11_vis_a_bois/

  ch_13_ouvrages_en_pilots_de_bois/
    art_13_2_materiaux.py
    art_13_3_resistances_prevues_et_modules_d_elasticite.py
    art_13_4_coefficients_de_correction.py
    art_13_5_calcul_des_resistances/

  ch_14_ouvrages_en_poteaux/
    art_14_2_materiaux.py
    art_14_3_resistances_prevues.py
    art_14_4_coefficients_de_correction.py
    art_14_5_calcul_des_resistances/

  ch_15_produits_proprietaires_en_bois_de_charpente_calcul/
    art_15_2_solives_en_i_prefabriquees_en_bois.py
    art_15_3_bois_de_charpente_composite.py

  ch_16_produits_proprietaires_en_bois_de_charpente_materiaux_et_evaluation/
    (seulement si des calculs sont requis : il s'agit surtout d'évaluation de produits)

  annexe_A_renseignements_supplementaires_et_autres_methodes/
    art_A_5_…/  art_A_6_…/  art_A_8_…/  …       ← même arborescence que les chapitres
    tableaux/                                   ← tableaux de l'annexe (A.1, A.2, A.3, A.11, …)

  annexe_B_resistance_au_feu_des_elements_en_bois_de_grande_section_transversale/
```

Les **annexes sont à la fin**, comme dans la norme. L'annexe A reprend l'arborescence des chapitres,
puisque ses articles portent les mêmes numéros (A.6.5.5.1 complète 6.5.5).

---

## 6. Contenu d'un fichier `art_`

```python
"""
CSA O86:19 – 6.5.5 Résistance à la compression parallèle au fil.

    6.5.5.2.2 Élancement, C_C
    6.5.5.2.4 Résistance pondérée à la compression sous charge axiale (F_c, K_Zc, P_r)
    6.5.5.2.5 Coefficient d'élancement, K_C
"""

def C_C(L_e: float, d: float) -> float:
    """
    6.5.5.2.2 Élancement, C_C.

    C_C = L_e / d <= 50

    Args:
        L_e (float): Longueur effective associée à la dimension, mm.
        d (float): Dimension dans la direction du flambage, mm.

    Returns:
        float: C_C.
    """
```

1. La **docstring du fichier** donne le numéro et le titre de l'article, puis la liste de ses
   sous-articles, dans l'ordre.
2. Les fonctions sont **dans l'ordre d'apparition des formules dans la norme**, autant que possible.
3. La docstring de chaque fonction commence par **le numéro et le titre exacts**, puis donne **la formule**,
   les arguments avec leurs unités et la valeur retournée.
4. **Fonctions simples d'abord** (elles retournent un nombre), puis, **à la fin du fichier**, les
   **fonctions de vérification**, qui les combinent et retournent un `Resultat` (section 8).
5. Une fonction ne recopie jamais la formule d'une autre : elle l'appelle.
6. Une valeur invalide lève `ValueError` avec un message clair qui cite l'article.
7. Les **tableaux** sont lus dans la base de données de l'édition par une fonction du fichier de
   l'article (ou de l'annexe) qui contient le tableau.

---

## 7. Structure partagée : `element.py`

Une petite structure (`dataclass`) regroupe les données d'un élément qui reviennent dans plusieurs
articles (ex. `b`, `d`, nombre de plis, bois vert). Son contenu exact sera fixé pendant la migration,
selon ce dont les articles ont réellement besoin. Les fonctions simples gardent des arguments explicites
(symboles de la norme). Seules les fonctions de vérification reçoivent l'élément.

---

## 8. Trace des calculs et notes de calcul PDF

### La trace : `Resultat`

Chaque fonction de vérification retourne un `Resultat` (`moteur/commun/resultat.py`) :

- les **entrées** (avec symboles et unités) ;
- une liste d'**étapes**. Chaque étape contient : l'article, une description, la **formule en LaTeX**
  (symboles), la **formule avec les valeurs remplacées** (en LaTeX), le **résultat** et son unité ;
- la **vérification** finale : charge pondérée, résistance pondérée, ratio, respecté ou dépassé ;
- la **figure** de l'élément (voir plus bas) ;
- l'**édition de la norme** utilisée.

Cette trace est la **source unique** pour :

1. le détail affiché dans l'interface (« Voir plus ») ;
2. la **note de calcul PDF** ;
3. les tests.

### La note de calcul PDF (format validé avec l'utilisateur)

**En-tête, sur chaque page** :

| Champ | |
|---|---|
| Datum, par Le Repère Ingénierie (logo) | |
| Nom du client | |
| Nom du projet | |
| Adresse du projet | |
| Numéro de dossier (ou de projet) | |
| Date | |
| Norme et édition (ex. CSA O86:19) | |
| Nom de l'ingénieur et numéro de membre OIQ | |
| **Zone pour les initiales et le sceau** | sur chaque page |
| Numéro de page | |

**Contenu de chaque vérification** :

1. le titre (ex. « Compression parallèle au fil — Poteau P-1 ») ;
2. une **figure schématique** de l'élément (pas à l'échelle) ;
3. un tableau des **données** (section, dimensions, résistances prévues, coefficients, charges) ;
4. **toutes les étapes de calcul**, chacune avec : l'article, la description, **la formule**, **la formule
   avec les valeurs**, puis **le résultat** ;
5. la vérification finale (ratio en %, respecté ou dépassé).

Les **formules sont écrites en LaTeX** dans la trace. Elles sont affichées avec KaTeX dans l'interface,
et rendues proprement dans le PDF. La façon de produire le PDF (gabarit HTML ou moteur LaTeX) sera
choisie à la phase 3.

### Figures schématiques

Chaque vérification a une **figure schématique**, pas à l'échelle, qui montre l'élément et la charge.
Exemple : pour la compression parallèle au fil, une colonne de bois comprimée dans le sens du fil, avec
la charge P_f, la longueur L et la section b × d.

- Les figures sont des **SVG**, dessinées à partir des données de l'élément (dimensions, charge…).
- La même figure sert dans l'interface et dans la note de calcul PDF.

### Unités : métriques et impériales

- **Tous les calculs se font en unités métriques**, comme dans les normes (mm, N, MPa, kN, kN·m).
  Aucune conversion à l'intérieur du moteur ni des formules.
- Les unités impériales servent **uniquement à l'affichage pour l'utilisateur** : les **entrées** et les
  **résultats**. La conversion se fait à l'entrée (impérial → métrique) et à l'affichage
  (métrique → impérial), jamais ailleurs.
- **Bascule métrique / impérial en tout temps** pour toutes les grandeurs : dimensions (mm / po),
  longueurs (mm ou m / pi), forces (kN / lb), moments (kN·m / lb·po), contraintes (MPa / psi), etc.
- La **note de calcul indique les deux unités** pour les données et les résultats, par exemple
  `b = 38 mm (1.50 po)` et `P_r = 12.62 kN (2837 lb)`. Les étapes intermédiaires restent en métrique,
  comme dans la norme.

## 9. Éditions de la norme

- **Chaque édition est un dossier autonome** (`csa_o86_19/`, `csa_o86_24/`…), avec sa propre base de
  données.
- **Article inchangé** : le fichier de la nouvelle édition importe les fonctions de l'édition précédente,
  sans copier le code.
- **Article modifié** (marqué Δ dans la norme) : il a sa propre version dans la nouvelle édition.
- **Chapitre ou article nouveau** : il n'existe que dans la nouvelle édition.
- **Chapitre ou article retiré** : il est simplement absent de la nouvelle édition.
- **Registre** (`moteur/commun/registre.py`) : chaque édition déclare la liste des calculs qu'elle offre
  (identifiant, article, titre, entrées). L'interface n'affiche que les calculs de l'édition choisie.
- **Tests par édition** : chaque édition a ses propres tests. Les anciennes éditions restent testées.
- Un **projet sauvegardé** garde l'édition utilisée, ainsi que les **entrées** (pas les résultats) : les
  résultats sont recalculés avec la même édition.

---

## 10. Interface web

**Technologie (proposée)** : API **FastAPI** (Python) qui expose le moteur, et interface web en
**TypeScript** avec **React**.

| Besoin | Outil |
|---|---|
| Pages et formulaires, ordinateur et mobile (responsive) | React + Tailwind CSS |
| Installation sur l'écran d'accueil de l'iPhone | application web progressive (PWA) |
| Formules | KaTeX |
| Figures 2D en temps réel | SVG |
| Modèles 3D interactifs en temps réel | three.js (React Three Fiber), sur ordinateur d'abord |

- La géométrie (2D ou 3D) est dessinée **instantanément dans le navigateur** à chaque changement. Les
  calculs sont faits par l'API.
- Le **moteur reste sur le serveur**, ce qui protège le code et permet de contrôler l'accès selon
  l'abonnement.
- L'**interface Streamlit actuelle reste en ligne** jusqu'à ce que la nouvelle interface offre au moins
  les mêmes fonctions.

---

## 11. Hébergement, comptes et abonnements

**Maintenant (gratuit)** :

- interface web : hébergement statique gratuit (ex. Cloudflare Pages ou Vercel) ;
- API : offre gratuite qui se met en veille (ex. Google Cloud Run ou Render). Le premier calcul après
  une pause peut prendre quelques secondes.

**Comptes d'essai (Streamlit, issue #56)** : deux comptes protégés par mot de passe, en attendant les
vrais comptes :

- `acces.py` : connexion (mots de passe dans les secrets de Streamlit Cloud, section `[mots_de_passe]`,
  jamais dans le code), comptes `admin` (tout) et `lantier` (Groupe Lantier : seulement les fonctions
  choisies par l'utilisateur), et état « en test » de chaque fonction (avertissement affiché tant que
  la fonction n'est pas testée convenablement) ;
- `retours.py` : formulaire « Commentaire » qui crée une issue dans un dépôt GitHub privé (secrets
  `[retours]` : `jeton` et `depot`).

**Plus tard** :

- **comptes et sauvegarde des projets** : base de données et authentification (ex. Supabase) ;
- **abonnements mensuels ou annuels** : paiement en ligne (ex. Stripe) ;
- **version gratuite de démonstration** : le registre indique, pour chaque calcul, s'il est offert en
  démonstration ou réservé aux abonnés. **Par défaut, un calcul est réservé aux abonnés** (validé avec
  l'utilisateur) ; les calculs offerts en démonstration sont marqués un par un ;
- un hébergement payant de quelques dollars par mois évite la mise en veille de l'API.

---

## 12. Tests

- **pytest**, dans `tests/`, avec la même arborescence que `moteur/` et `api/`.
- Un fichier de tests par fichier `art_`, et par édition.
- Valeurs attendues **calculées à la main à partir de la norme**, avec le calcul en commentaire.
- Cas typiques, cas limites (valeur exactement au seuil), valeurs invalides, toutes les branches.
- L'interface Streamlit est testée avec `streamlit.testing.v1.AppTest` tant qu'elle existe ; la nouvelle
  interface aura ses propres tests.

---

## 13. Correspondance avec le code actuel

| Code actuel | Nouvel emplacement (dans `moteur/normes/csa_o86_19/`) | Nouveau nom |
|---|---|---|
| `general_design.limit_states_design` | `ch_5/art_5_1` (règle de 5.1.2) + `Verification` dans `commun/resultat.py` | `verifier_etat_limite_ultime()` |
| `general_design.load_duration` | `ch_5/art_5_3` | `K_D()` (5.3.2) |
| `general_design.cross_section` | `ch_5/art_5_3` | 5.3.8 |
| `general_design.elasticity`, `elastic_deflection`, `permanent_deformation`, `ponding`, `moisture` | `ch_5/art_5_4_…/` | `E_S()`, 5.4.2, 5.4.3, 5.4.4, 5.4.6 |
| `general_design.Vibration` | `ch_5/art_5_4_…/art_5_4_5_vibration.py` + `annexe_A` (A.5.4.5, A.8.5.3, tableaux A.1 et A.2) | |
| `general_design.lateral_brace` | `ch_5/art_5_5` | |
| `general_design.FireResistance` | `ch_5/art_5_6` + `annexe_B` | |
| `sawn_lumber.lumber_category` | `ch_6/art_6_2` | `categorie_de_bois()` |
| `sawn_lumber.specified_strengths` | `ch_6/art_6_3` | `resistances_prevues()` → `ResistancesPrevues` (`f_b`, `f_v`, `f_c`, `f_cp`, `f_t`, `E`, `E_05`), `classes()` |
| `sawn_lumber.modification_factors` | `ch_6/art_6_4` | découpé : `K_S()`, `K_T()`, `cas_de_systeme()`, `K_H()`, `K_Z()` (tableaux 6.10 à 6.13) ; `K_D()` viendra avec 5.3.2 (étape 6) |
| `sawn_lumber.sizes`, `nominal_sizes`, `is_timber` | `annexe_A/tableaux/tableau_A_3` | `dimension_nette()`, `dimensions_nominales()`, `est_gros_bois()` |
| `Resistances.bending_moment` | `art_6_5/art_6_5_3` | découpé et validé : `F_b()`, `S()`, `rapport_hauteur_largeur_maximal()`, `K_L()`, `M_r()`, `verifier_flexion()` |
| `Resistances.shear` | `art_6_5/art_6_5_4` | découpé et validé : `F_v()`, `V_r()`, `F_f()`, `F_r()`, `alpha()`, `eta()`, `K_N()`, `verifier_cisaillement()`, `verifier_cisaillement_par_fissuration()` |
| `compression_strength`, `slenderness_ratio`, `compression_size_factor`, `slenderness_factor`, `compression_resistance`, `compression_parallel_axis` | `art_6_5/art_6_5_5` | `F_c()`, `C_C()`, `K_Zc()`, `K_C()`, `P_r()`, vérification |
| `bearing_strength`, `bearing_size_factor`, `bearing_length_factor`, `average_bearing_area`, `bearing_resistance`, `bearing_resistance_near_support` | `art_6_5/art_6_5_6` | `F_cp()`, `K_Zcp()`, `K_B()`, `A_b_prime()`, `Q_r()`, `Q_r_prime()` |
| `bearing_strength_from_density` | `annexe_A/art_A_6_…/art_A_6_5_6` | `f_cp()` à partir de G |
| `density_table_a11` | `annexe_A/tableaux/tableau_A_11` | `G()` |
| `comp_angle` | `art_6_5/art_6_5_7` | `N_r()` (à valider) |
| `Resistances.tensile_parallel` | `art_6_5/art_6_5_8` | `T_r()` (à valider) |
| `combined_bending_axial` | `art_6_5/art_6_5_9` | (à valider) |
| `Resistances.comp_parallel`, `Resistances.comp_perpendicular` | **retirées** | remplacées par 6.5.5 et 6.5.6 |
| `decking`, `foundations`, `truss` (vides) | **retirées** | recréées lors de leur développement |

---

## 14. Feuille de route

Chaque étape est une ou plusieurs petites PR. **Aucun résultat ne doit changer** pendant un déplacement :
les tests le prouvent. L'application en ligne doit fonctionner après chaque PR.

**Phase 1 : moteur dans la nouvelle structure**
1. Squelette : `moteur/`, `commun/` (`resultat.py`, `registre.py`, `unites.py`), 5.1.2, pytest,
   `requirements-dev.txt`, `art_3_2_symboles.py`.
2. Déplacer 6.5.5 et 6.5.6 (déjà en fonctions simples), avec les symboles et la trace.
3. Tableau A.3, 6.2 et 6.3.
4. 6.4 : découper `modification_factors` et valider.
5. 6.5.3 et 6.5.4 : découper en fonctions simples et valider avec la norme.
6. Chapitre 5 et annexes A et B.
7. Retirer `sawn_lumber.py` et `general_design.py`, devenus vides. Streamlit utilise alors le nouveau moteur.

**Phase 2 : API**
8. FastAPI : catalogue des calculs par édition, et un appel par vérification. Tests.

**Phase 3 : nouvelle interface web**
9. Interface web pour le bois de sciage, avec au moins les fonctions de Streamlit, sur ordinateur et
   mobile, avec figures 2D. Mise en ligne gratuite.
10. Note de calcul PDF.
11. Retrait de Streamlit.

**Plus tard** : sélecteur d'édition, nouveaux chapitres et nouvelles normes, 3D interactive, projets
sauvegardés, comptes et abonnements, version de démonstration.

Les nouvelles fonctionnalités de calcul (6.5.7, 6.5.8, 6.5.9…) sont écrites directement dans la nouvelle
structure.
