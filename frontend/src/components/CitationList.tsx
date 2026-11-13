import { Link } from 'react-router-dom'
import type { Citation } from '../types'

const TYPE_LABELS: Record<string, string> = {
  'orientations-generales': 'Orientations générales',
  'competence-transversale': 'Compétence transversale',
  'competence-transdisciplinaire': 'Compétence transdisciplinaire',
  'competence-disciplinaire': 'Compétence disciplinaire',
  'competences-transversales': 'Compétences transversales',
  'competences-transdisciplinaires': 'Compétences transdisciplinaires',
  'competences-disciplinaires': 'Compétences disciplinaires',
  'situation-apprentissage': "Situation d'apprentissage",
  'critere-evaluation': "Critère d'évaluation",
  'contenus-formation': 'Contenus de formation',
  'contenus-notionnels': 'Contenus notionnels',
  'repertoire-tp': 'Répertoire des travaux pratiques',
  'canevas-sa': 'Canevas de SA',
  'amenagement-sa': "Aménagement des SA",
  'situation-progression': 'Suivi de progression',
  'analyse-evaluation': 'Analyse d\u2019évaluation',
  'format-epreuve': "Format d'épreuve",
  'exemples-epreuves': "Exemples d'épreuves",
  'document-transversal': 'Document transversal',
  'section': 'Section',
}

export function typeLabel(type: string): string {
  return TYPE_LABELS[type] ?? type
}

export function CitationList({ citations }: { citations: Citation[] }) {
  if (citations.length === 0) {
    return (
      <section className="citations citations-empty">
        <h3>Sources</h3>
        <p>Aucun extrait du programme n'a été mobilisé pour cette réponse.</p>
      </section>
    )
  }

  return (
    <section className="citations">
      <h3>Sources du programme</h3>
      <ul>
        {citations.map((citation) => (
          <li key={citation.extract_id}>
            <Link to={`/corpus?extract=${encodeURIComponent(citation.extract_id)}`}>
              <span className="citation-type">{typeLabel(citation.type)}</span>
              <strong>{citation.title}</strong>
              <span className="citation-ref">{citation.reference}</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}
