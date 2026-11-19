# Accès du compte Groupe Lantier (issue #56)

**Ce fichier est lu par l'application.** Pour changer ce que voit le compte Groupe Lantier, coche ou
décoche une case : remplace `[ ]` par `[x]`, ou l'inverse. Le changement s'applique après le merge
dans `main` (GitHub : bouton crayon ✏️, puis « Propose changes » et une PR).

Le compte **admin** voit toujours tout. Ne modifie pas les identifiants entre accents graves (ex.
`flexion`) : l'application s'en sert pour reconnaître chaque fonction.

## Fonctions offertes au compte Groupe Lantier

Seulement des fonctions **intégrées au nouveau moteur** et **testées**. Claude ajoute ici chaque
nouvelle fonction intégrée, **non cochée** ; c'est toi qui décides de la cocher.

- [ ] `flexion` : Flexion (6.5.3). Limite : bloquée si d/b dépasse la limite de 6.5.3.2 (K_L selon 7.5.6.4, à venir) ; poutres composées selon 6.5.3.2.4 (lecture stricte, #48).
- [ ] `cisaillement` : Cisaillement (6.5.4.3) et cisaillement par fissuration à l'entaille (6.5.4.4).
- [ ] `compression_parallele` : Compression parallèle au fil (6.5.5). Limite : éléments composés (6.5.5.3) à venir.
- [ ] `compression_perpendiculaire` : Compression perpendiculaire au fil (6.5.6), y compris f_cp à partir de la densité G (A.6.5.6).
- [ ] `note_pdf` : Note de calcul PDF (vérifications offertes seulement). Limite : figures schématiques à venir.

## Fonctions testées convenablement

Une fonction **non cochée** ici affiche l'avertissement « En test : vérifiez les résultats avant de les
utiliser dans un dossier », dans la page et dans sa page de la note PDF, pour **tous** les comptes.
Coche-la quand elle est testée convenablement.

- [ ] `flexion`
- [ ] `cisaillement`
- [ ] `compression_parallele`
- [ ] `compression_perpendiculaire`
- [ ] `note_pdf`

## Pas encore intégrées au nouveau moteur (non offertes)

- Compression oblique par rapport au fil (6.5.7)
- Traction parallèle au fil (6.5.8)
- Flexion et charge axiale combinée (6.5.9)

Les propriétés de base (dimensions A.3, catégorie 6.2, résistances prévues 6.3, coefficients 6.4) sont
affichées à tous les comptes : elles servent à toutes les vérifications.
