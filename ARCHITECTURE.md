# Architecture du code

Ce document fixe la structure du code **avant** d'écrire de nouvelles fonctions. But : que le code
**suive la norme CSA O86:19**, pour qu'on puisse passer facilement de l'un à l'autre pour valider, et que
les fichiers restent petits et en ordre.

> Les décisions ci-dessous ont été validées avec l'utilisateur. Une modification de cette structure doit
> d'abord être discutée, puis notée ici.

---

## 1. Principes

1. **Le code suit la norme** : mêmes chapitres, mêmes articles, même ordre, mêmes symboles.
2. **Un fichier par article** de la norme, nommé avec son numéro et son titre complet.
3. **Les annexes sont à la fin**, dans leurs propres dossiers, comme dans la norme.
4. **Fonctions simples d'abord** (un calcul de la norme chacune), puis une fonction de vérification
   qui les combine.
5. **Le moteur de calcul ne dépend pas de l'interface.** L'interface ne contient aucune logique de calcul.
6. **Tout est en français**, sans accents dans les noms de fichiers, de dossiers et de fonctions.

---

## 2. Nommage

### Fichiers et dossiers

Un nom Python ne peut pas commencer par un chiffre. On utilise donc des préfixes courts. Les accents
sont retirés (macOS et Linux n'encodent pas toujours les lettres accentuées de la même façon).

| Élément de la norme | Préfixe | Exemple |
|---|---|---|
| Chapitre | `ch_` | `ch_6_bois_de_sciage/` |
| Article | `art_` | `art_6_5_5_resistance_a_la_compression_parallele_au_fil.py` |
| Annexe | `annexe_` | `annexe_A/` |
| Article d'annexe | `art_` | `art_A_6_5_5_1_coefficient_de_longueur_effective.py` |
| Tableau d'annexe | `tableau_` | `tableau_A_3_dimensions_minimales_apres_rabotage_du_bois_d_oeuvre.py` |

- Les numéros gardent leurs points remplacés par `_` (6.5.5 → `6_5_5`).
- Le **titre complet** de l'article est repris tel qu'il est dans la version française de la norme,
  sans accents, en minuscules, avec des `_` (« d'œuvre » → `d_oeuvre`).
- **Niveau des fichiers** : un fichier par article de 2e niveau (ex. 5.4). Quand un article est trop
  gros, comme 6.5 « Calcul des résistances », on descend d'un niveau (6.5.3, 6.5.4, …).

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

Quand un calcul n'a pas de symbole dans la norme (ex. choisir la catégorie de bois), on utilise un nom
descriptif en français sans accents (ex. `categorie_de_bois()`).

---

## 3. Arborescence

```
csa_o86_19/                                     ← moteur de calcul (aucun Streamlit)
  __init__.py
  base_de_donnees.py                            ← connexion unique à csa_o86_19.db
  element.py                                    ← structure partagée d'un élément (voir section 5)
  art_3_2_symboles.py                           ← symboles, définitions et unités de 3.2
  art_3_3_espacements_et_dimensions.py          ← 300/305, 400/406, 600/610 mm ; 1200/1220, 2400/2440 mm

  ch_5_conception_generale/
    art_5_1_calculs_aux_etats_limites.py
    art_5_3_conditions_et_coefficients_influant_sur_la_resistance.py
    art_5_4_exigences_relatives_a_la_tenue_en_service.py
    art_5_5_effort_de_contreventement_lateral_sur_les_membrures_d_ame_en_compression_des_fermes_de_toit_en_bois.py
    art_5_6_resistance_au_feu.py

  ch_6_bois_de_sciage/
    art_6_2_materiaux.py
    art_6_3_resistances_prevues_et_modules_d_elasticite.py
    art_6_4_coefficients_de_correction.py
    art_6_5_2_dimensions.py
    art_6_5_3_resistance_au_moment_de_flexion.py
    art_6_5_4_resistance_au_cisaillement.py
    art_6_5_5_resistance_a_la_compression_parallele_au_fil.py
    art_6_5_6_resistance_a_la_compression_perpendiculaire_au_fil.py
    art_6_5_7_resistance_a_la_compression_oblique_par_rapport_au_fil.py
    art_6_5_8_resistance_a_la_traction_parallele_au_fil.py
    art_6_5_9_resistance_a_la_flexion_et_a_la_charge_axiale_combinees.py
    (6.5.10 à 6.6 : plus tard)

  ch_7_bois_lamelle_colle/                      ← plus tard, même logique (KL selon 7.5.6.4)

  annexe_A/
    art_A_5_4_5_tenue_aux_vibrations_des_planchers_en_solives_en_bois.py   (+ tableaux A.1 et A.2)
    tableau_A_3_dimensions_minimales_apres_rabotage_du_bois_d_oeuvre.py
    art_A_6_5_5_1_coefficient_de_longueur_effective.py
    art_A_6_5_6_compression_perpendiculaire_au_fil.py
    art_A_8_5_3_tenue_aux_vibrations_des_planchers_faits_de_bois_lamelle_croise.py
    tableau_A_11_valeurs_de_densite.py
  annexe_B/
    art_B_... (résistance au feu ; titres à confirmer avec la norme lors du déplacement)

tests/                                          ← même arborescence, pytest
  ch_6_bois_de_sciage/
    test_art_6_5_5_resistance_a_la_compression_parallele_au_fil.py
    …
  interface/                                    ← tests de l'interface (AppTest)

interface/                                      ← interface Streamlit, un fichier par onglet
  bois_de_sciage/
    materiaux.py
    coefficients.py
    onglet_moment_de_flexion.py
    onglet_cisaillement.py
    onglet_compression_parallele_au_fil.py
    onglet_compression_perpendiculaire_au_fil.py
    …
Accueil.py                                      ← point d'entrée (inchangé)
pages/1_Bois de sciage.py                       ← assemble seulement les fichiers d'interface/
```

Les chapitres 1, 2 et 4 ne contiennent pas de formule. Ils n'ont pas de fichier de code.

---

## 4. Contenu d'un fichier `art_`

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

Règles :

1. La **docstring du fichier** donne le numéro et le titre de l'article, puis la liste de ses
   sous-articles, dans l'ordre.
2. Les fonctions sont **dans l'ordre d'apparition des formules dans la norme**, autant que possible.
3. La docstring de chaque fonction commence par **le numéro et le titre exacts** de l'article, puis donne
   **la formule**, les arguments avec leurs unités et la valeur retournée.
4. **Fonctions simples d'abord**, puis, **à la fin du fichier**, la ou les **fonctions de vérification**
   qui les combinent (ex. P_r selon les deux axes).
5. Une fonction simple ne recopie jamais la formule d'une autre : elle l'appelle.
6. Une valeur invalide lève `ValueError` avec un message clair qui cite l'article.
7. Les **tableaux** de la norme sont lus dans la base de données par une fonction du fichier de l'article
   qui contient le tableau.

---

## 5. Structure partagée : `element.py`

Une petite structure (`dataclass`) regroupe les données d'un élément qui reviennent dans plusieurs
articles, pour éviter de longues listes d'arguments. Son contenu exact sera fixé lors de la migration,
à partir de ce dont les articles ont réellement besoin (ex. `b`, `d`, nombre de plis, bois vert).

Les fonctions simples gardent leurs arguments explicites (symboles de la norme). Seules les fonctions
de vérification reçoivent l'élément.

---

## 6. Tests

- **pytest**, dans `tests/`, avec la même arborescence que `csa_o86_19/`.
- Un fichier de tests par fichier `art_`.
- Les valeurs attendues sont **calculées à la main à partir de la norme**, avec le calcul en commentaire.
- Cas typiques, cas limites (valeur exactement au seuil), valeurs invalides, toutes les branches.
- L'interface est testée avec `streamlit.testing.v1.AppTest`, en partant d'`Accueil.py`.
- pytest est ajouté dans `requirements-dev.txt` (l'app en ligne n'en a pas besoin).

Commande : `pytest`

---

## 7. Correspondance avec le code actuel

| Code actuel | Nouvel emplacement | Nouveau nom |
|---|---|---|
| `general_design.limit_states_design` | `ch_5/art_5_1` | vérification 5.1.2 |
| `general_design.load_duration` | `ch_5/art_5_3` | `K_D()` (5.3.2) |
| `general_design.cross_section` | `ch_5/art_5_3` | 5.3.8 |
| `general_design.elasticity`, `elastic_deflection`, `permanent_deformation`, `ponding`, `moisture` | `ch_5/art_5_4` | `E_S()`, 5.4.2, 5.4.3, 5.4.4, 5.4.6 |
| `general_design.Vibration` | `ch_5/art_5_4` (5.4.5) + `annexe_A` (A.5.4.5, A.8.5.3, tableaux A.1 et A.2) | |
| `general_design.lateral_brace` | `ch_5/art_5_5` | |
| `general_design.FireResistance` | `ch_5/art_5_6` + `annexe_B` | |
| `sawn_lumber.lumber_category` | `ch_6/art_6_2` | `categorie_de_bois()` |
| `sawn_lumber.specified_strengths` | `ch_6/art_6_3` | `f_b`, `f_v`, `f_c`, `f_cp`, `f_t`, `E`, `E_05` |
| `sawn_lumber.modification_factors` | `ch_6/art_6_4` | découpé : `K_D()`, `K_S()`, `K_T()`, `K_H()`, `K_Z()` |
| `sawn_lumber.sizes`, `nominal_sizes`, `is_timber` | `annexe_A/tableau_A_3` (+ `art_6_5_2`) | |
| `Resistances.bending_moment` | `ch_6/art_6_5_3` | découpé et validé : `M_r()`, K_L (6.5.3.2) |
| `Resistances.shear` | `ch_6/art_6_5_4` | découpé et validé : `V_r()`, `F_r()`, `K_N()` |
| `compression_strength`, `slenderness_ratio`, `compression_size_factor`, `slenderness_factor`, `compression_resistance`, `compression_parallel_axis` | `ch_6/art_6_5_5` | `F_c()`, `C_C()`, `K_Zc()`, `K_C()`, `P_r()`, vérification |
| `bearing_strength`, `bearing_size_factor`, `bearing_length_factor`, `average_bearing_area`, `bearing_resistance`, `bearing_resistance_near_support` | `ch_6/art_6_5_6` | `F_cp()`, `K_Zcp()`, `K_B()`, `A_b_prime()`, `Q_r()`, `Q_r_prime()` |
| `bearing_strength_from_density` | `annexe_A/art_A_6_5_6` | `f_cp()` à partir de G |
| `density_table_a11` | `annexe_A/tableau_A_11` | `G()` |
| `comp_angle` | `ch_6/art_6_5_7` | `N_r()` (à valider) |
| `Resistances.tensile_parallel` | `ch_6/art_6_5_8` | `T_r()` (à valider) |
| `combined_bending_axial` | `ch_6/art_6_5_9` | (à valider) |
| `Resistances.comp_parallel`, `Resistances.comp_perpendicular` | **retirées** | remplacées par 6.5.5 et 6.5.6 |
| `decking`, `foundations`, `truss` (vides) | **retirées** | recréées lors de leur développement |

---

## 8. Migration, en petites PR

Chaque étape est une PR séparée. **Aucun résultat ne doit changer** pendant un déplacement : les tests le
prouvent. L'app en ligne doit fonctionner après chaque PR.

1. **Ce document** et la mise à jour de `CLAUDE.md`.
2. **Squelette** : dossiers, `base_de_donnees.py`, `art_3_2_symboles.py`, pytest, `requirements-dev.txt`.
3. **Déplacer 6.5.5 et 6.5.6** (déjà en fonctions simples) et renommer avec les symboles.
4. **Tableau A.3, 6.2 et 6.3** (dimensions, catégories, résistances prévues).
5. **6.4** : découper `modification_factors` en `K_D()`, `K_S()`, `K_T()`, `K_H()`, `K_Z()`, et valider.
6. **6.5.3 et 6.5.4** : découper en fonctions simples et valider avec la norme.
7. **Interface** : un fichier par onglet dans `interface/`.
8. **Chapitre 5 et annexes A et B.**
9. Retirer `sawn_lumber.py` et `general_design.py`, devenus vides.

Les nouvelles fonctionnalités (6.5.7, 6.5.8, 6.5.9…) sont écrites directement dans la nouvelle structure.
