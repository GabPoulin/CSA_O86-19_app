// Gabarit de la note de calcul PDF de Datum (ARCHITECTURE.md, section 8).
// Les données arrivent de Python (note_de_calcul/__init__.py) en JSON, par sys.inputs.donnees.
// Aucune logique de calcul ici : seulement la mise en page de la trace (Resultat).

#import "mitex/lib.typ": mitex, mi

#let donnees = json(bytes(sys.inputs.donnees))
#let entete = donnees.entete

// Couleurs de la marque (marque/couleurs.md)
#let vert = rgb("#233614")
#let orange = rgb("#9E5A00")
#let charbon = rgb("#333333")
#let gris = rgb("#8F8F8F")
#let gris-pale = rgb("#EEEEEE")
#let rouge = rgb("#A11D1D")

#set document(title: "Note de calcul — " + entete.projet, author: entete.ingenieur)
#set text(lang: "fr", size: 9.5pt, fill: charbon)
#set par(justify: false)

#let champ(nom, valeur) = [#text(fill: gris, size: 7.5pt)[#nom] \ #valeur]

#let en-tete = context {
  grid(
    columns: (auto, 1fr, 3.2cm),
    column-gutter: 0.4cm,
    align: (left + horizon, left + top, center + top),
    [
      #image("/marque/logos/LeRepere_logo-horizontal_gris.svg", height: 1.0cm)
      #v(-0.15cm)
      #text(size: 7.5pt, fill: vert, weight: "bold")[Datum, par Le Repère Ingénierie]
    ],
    grid(
      columns: (1fr, 1fr, 1fr),
      row-gutter: 0.18cm,
      column-gutter: 0.3cm,
      champ("Client", entete.client),
      champ("Projet", entete.projet),
      champ("N° de dossier", entete.dossier),
      champ("Adresse du projet", entete.adresse),
      champ("Norme et édition", entete.norme),
      champ("Date", entete.date),
      grid.cell(colspan: 2, champ("Ingénieur", entete.ingenieur + " — OIQ " + entete.oiq)),
      champ("Page", [#counter(page).display() de #counter(page).final().first()]),
    ),
    rect(width: 100%, height: 2.1cm, stroke: 0.6pt + gris, radius: 2pt)[
      #align(center + top)[#text(size: 7pt, fill: gris)[Initiales et sceau]]
    ],
  )
  v(0.1cm)
  line(length: 100%, stroke: 1.2pt + vert)
}

#set page(
  paper: "us-letter",
  margin: (top: 3.9cm, bottom: 1.6cm, x: 1.6cm),
  header: en-tete,
  header-ascent: 0.45cm,
  footer: context [
    #set text(size: 7pt, fill: gris)
    Datum, par Le Repère Ingénierie #h(1fr) Note de calcul produite le #entete.date
  ],
)

#show heading.where(level: 1): it => block(above: 0.5cm, below: 0.3cm)[
  #text(size: 12pt, fill: vert, weight: "bold")[#it.body]
]
#show heading.where(level: 2): it => block(above: 0.35cm, below: 0.2cm)[
  #text(size: 10pt, fill: vert, weight: "bold")[#it.body]
]

#let tableau-donnees(lignes) = table(
  columns: (auto, 1fr, auto, auto),
  stroke: none,
  inset: (x: 4pt, y: 3pt),
  fill: (_, y) => if y == 0 { vert } else if calc.even(y) { gris-pale },
  table.header(
    ..([Symbole], [Description], [Valeur], [Source]).map(t => text(fill: white, weight: "bold")[#t]),
  ),
  ..lignes.map(l => (mi(l.symbole), l.description, l.valeur, text(fill: gris)[#l.source])).flatten(),
)

#let etape(e) = block(breakable: false, above: 0.12cm, below: 0.12cm, width: 100%)[
  #grid(
    columns: (1.5cm, 1fr),
    column-gutter: 0.25cm,
    text(fill: orange, weight: "bold", size: 8.5pt)[#e.article],
    [
      #text(size: 8.5pt)[#e.description]
      #v(-0.25cm)
      #show math.equation.where(block: true): set align(left)
      #mitex(e.formule + " = " + e.substitution + " = " + e.resultat_latex)
    ],
  )
  #v(-0.12cm)
  #line(length: 100%, stroke: 0.3pt + gris-pale)
]

#let verification(v) = {
  let couleur = if v.respecte { vert } else { rouge }
  block(fill: couleur.lighten(88%), stroke: 1pt + couleur, inset: 8pt, radius: 3pt, width: 100%)[
    #text(weight: "bold", fill: couleur)[Vérification (#v.article)] \
    #mi(v.symbole_charge) $=$ #v.charge #h(0.6cm) #mi(v.symbole_resistance) $=$ #v.resistance
    #h(0.6cm) Ratio : *#v.ratio* \
    #text(weight: "bold", fill: couleur)[#v.message]
  ]
}

#for (i, r) in donnees.resultats.enumerate() {
  if i > 0 { v(0.4cm) }
  heading(level: 1)[#r.titre #if r.element != "" [— #r.element] #h(1fr) #text(size: 9pt, fill: orange)[#r.norme, article #r.article]]

  rect(width: 100%, height: 1.6cm, stroke: (dash: "dashed", paint: gris, thickness: 0.6pt), radius: 2pt)[
    #align(center + horizon)[#text(fill: gris, size: 8pt)[Figure schématique (à venir) : #r.figure]]
  ]

  heading(level: 2)[Données]
  tableau-donnees(r.donnees)

  heading(level: 2)[Calcul]
  for e in r.etapes { etape(e) }

  if r.verification != none { verification(r.verification) }
}
