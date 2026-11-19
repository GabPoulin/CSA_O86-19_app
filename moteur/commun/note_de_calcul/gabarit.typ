// Gabarit de la note de calcul PDF de Datum (ARCHITECTURE.md, section 8 ; issue #50, PR #55).
// Les données arrivent de Python (note_de_calcul/__init__.py) en JSON, par sys.inputs.donnees.
// Aucune logique de calcul ici : seulement la mise en page de la trace (Resultat).

#import "mitex/lib.typ": mitex, mi

#let donnees = json(bytes(sys.inputs.donnees))
#let entete = donnees.entete
#let apparence = donnees.apparence

// Couleurs : celles de la marque par défaut (marque/couleurs.md), ou celles de l'utilisateur
#let principale = rgb(apparence.principale)
#let accent = rgb(apparence.accent)
#let charbon = rgb("#333333")
#let gris = rgb("#8F8F8F")
#let gris-pale = rgb("#EEEEEE")
#let rouge = rgb("#A11D1D")

#let logo(hauteur) = if apparence.logo == none {
  image("/marque/logos/LeRepere_logo-horizontal_gris.svg", height: hauteur)
} else {
  image(bytes(apparence.logo), height: hauteur)
}

#set document(title: "Note de calcul — " + entete.projet, author: entete.ingenieur)
#set text(lang: "fr", size: 9pt, fill: charbon)
#set par(justify: false)

#let champ(nom, valeur) = [#text(fill: gris, size: 7pt)[#nom] \ #valeur]

#let en-tete = context {
  grid(
    columns: (4.2cm, 1fr),
    column-gutter: 0.4cm,
    align: (left + horizon, left + top),
    [
      #logo(1.0cm)
      #v(-0.15cm)
      #text(size: 7pt, fill: principale, weight: "bold")[Datum, par Le Repère Ingénierie]
    ],
    grid(
      columns: (1fr, 1fr, 1fr, 1fr),
      row-gutter: 0.15cm,
      column-gutter: 0.3cm,
      champ("Client", entete.client),
      champ("Projet", entete.projet),
      champ("Adresse du projet", entete.adresse),
      champ("N° de dossier", entete.dossier),
      champ("Norme et édition", entete.norme),
      champ("Date", entete.date),
      champ("Ingénieur", entete.ingenieur + " — OIQ " + entete.oiq),
      champ("Page", [#counter(page).display() de #counter(page).final().first()]),
    ),
  )
  v(0.05cm)
  line(length: 100%, stroke: 1.2pt + principale)
}

// Pied de page : zone d'initiales et de sceau en bas à droite, sur chaque page
#let pied = context grid(
  columns: (1fr, 4.2cm),
  align: (left + bottom, right + bottom),
  text(size: 7pt, fill: gris)[Datum, par Le Repère Ingénierie — note produite le #entete.date],
  rect(width: 4.2cm, height: 2.3cm, stroke: 0.6pt + gris, radius: 2pt)[
    #align(center + top)[#text(size: 6.5pt, fill: gris)[Initiales et sceau]]
  ],
)

#set page(
  paper: "us-letter",
  margin: (top: 3.0cm, bottom: 3.3cm, x: 1.5cm),
  header: en-tete,
  header-ascent: 0.35cm,
  footer: pied,
  footer-descent: 0.3cm,
)

#let tableau-donnees(lignes) = table(
  columns: (auto, 1fr, auto, auto),
  stroke: none,
  inset: (x: 3pt, y: 2pt),
  fill: (_, y) => if y == 0 { principale } else if calc.even(y) { gris-pale },
  table.header(
    ..([Symbole], [Description], [Valeur], [Source]).map(t => text(fill: white, weight: "bold", size: 7.5pt)[#t]),
  ),
  ..lignes
    .map(l => (
      mi(l.symbole),
      text(size: 7.5pt)[#l.description],
      text(size: 7.5pt)[#l.valeur],
      text(size: 7pt, fill: accent)[#l.source],
    ))
    .flatten(),
)

// Une étape : calcul à gauche, résultat justifié à droite
#let etape(e) = block(breakable: false, above: 0.1cm, below: 0.1cm, width: 100%)[
  #text(fill: accent, weight: "bold", size: 7.5pt)[#e.article] #h(0.15cm) #text(size: 7.5pt)[#e.description]
  #v(-0.2cm)
  #show math.equation.where(block: true): set align(left)
  #set text(size: 8.5pt)
  #mitex(e.calcul)
  #v(-0.25cm)
  #align(right)[#mi(e.symbole) $=$ *#e.resultat*]
  #v(-0.1cm)
  #line(length: 100%, stroke: 0.3pt + gris-pale)
]

#let verification(v) = {
  let couleur = if v.respecte { principale } else { rouge }
  align(right, block(breakable: false, fill: couleur.lighten(88%), stroke: 1pt + couleur, inset: 7pt, radius: 3pt, width: 100%)[
    #set align(right)
    #text(weight: "bold", fill: couleur)[Vérification (#v.article)] \
    #mi(v.symbole_charge) $=$ #v.charge \
    #mi(v.symbole_resistance) $=$ #v.resistance \
    Ratio : *#v.ratio* — #text(weight: "bold", fill: couleur)[#v.message]
  ])
}

#for (i, r) in donnees.resultats.enumerate() {
  if i > 0 { pagebreak() }
  block(below: 0.2cm)[
    #text(size: 11.5pt, fill: principale, weight: "bold")[#r.titre #if r.element != "" [— #r.element]]
    #h(1fr) #text(size: 8.5pt, fill: accent, weight: "bold")[#r.norme, article #r.article]
  ]

  grid(
    columns: (4.2cm, 1fr),
    column-gutter: 0.35cm,
    rect(width: 100%, height: 3.4cm, stroke: (dash: "dashed", paint: gris, thickness: 0.6pt), radius: 2pt)[
      #align(center + horizon)[#text(fill: gris, size: 7pt)[Figure schématique \ (à venir) \ #r.figure]]
    ],
    tableau-donnees(r.donnees),
  )

  v(0.15cm)
  text(size: 9.5pt, fill: principale, weight: "bold")[Calcul]
  columns(2, gutter: 0.6cm)[
    #for e in r.etapes { etape(e) }
    #if r.verification != none { v(0.15cm); verification(r.verification) }
  ]
}
