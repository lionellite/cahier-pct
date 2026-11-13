import { useRef, useState } from 'react'
import { api, errorMessage } from '../lib/api'
import { useExtracts } from '../lib/useExtracts'
import { useMeta } from '../lib/meta'
import { CompetenceField } from '../components/CompetenceField'
import { Notice, Spinner } from '../components/Notice'
import { ResultPanel } from '../components/ResultPanel'
import type { GenerationResult } from '../types'

const DIFFICULTIES = [
  { value: 'progressive', label: 'Progressive' },
  { value: 'facile', label: 'Facile' },
  { value: 'moyen', label: 'Moyenne' },
  { value: 'difficile', label: 'Difficile' },
]

export function ExercicesPage() {
  const { meta } = useMeta()
  const extracts = useExtracts()
  const [competence, setCompetence] = useState('')
  const [count, setCount] = useState(5)
  const [withCorrection, setWithCorrection] = useState(true)
  const [difficulty, setDifficulty] = useState('progressive')
  const [context, setContext] = useState('')
  const [result, setResult] = useState<GenerationResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const resultRef = useRef<HTMLDivElement>(null)

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    if (competence.trim().length < 2) {
      setError('Précisez la compétence à évaluer.')
      return
    }
    setError(null)
    setLoading(true)
    setResult(null)
    try {
      const response = await api.exercices({
        competence: competence.trim(),
        count,
        with_correction: withCorrection,
        difficulty,
        context: context.trim() || undefined,
      })
      setResult(response)
      window.setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 50)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="stack">
      <header className="page-head">
        <span className="eyebrow">Mode 03</span>
        <h1>Exercices et évaluation</h1>
        <p className="page-lede">
          Générez un sujet conforme aux capacités officielles, avec une grille de
          correction rattachée aux critères du programme.
        </p>
      </header>

      {meta && !meta.llm.live && (
        <Notice tone="warn" title="Mode démonstration actif">
          Les énoncés et la grille de correction nécessitent la génération par le
          modèle. En mode démo, seuls les extraits mobilisables sont affichés.
        </Notice>
      )}

      <form className="panel form" onSubmit={submit}>
        <CompetenceField
          value={competence}
          onChange={setCompetence}
          extracts={extracts}
          listId="exercices-competences"
          disabled={loading}
        />

        <div className="field-row">
          <label className="field">
            <span className="field-label">Nombre d'exercices</span>
            <input
              type="number"
              min={1}
              max={10}
              value={count}
              onChange={(event) => setCount(Number(event.target.value))}
              disabled={loading}
            />
          </label>

          <label className="field">
            <span className="field-label">Difficulté</span>
            <select
              value={difficulty}
              onChange={(event) => setDifficulty(event.target.value)}
              disabled={loading}
            >
              {DIFFICULTIES.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <label className="checkbox">
          <input
            type="checkbox"
            checked={withCorrection}
            onChange={(event) => setWithCorrection(event.target.checked)}
            disabled={loading}
          />
          <span>Inclure la grille de correction et le barème</span>
        </label>

        <label className="field">
          <span className="field-label">Contexte particulier (facultatif)</span>
          <textarea
            value={context}
            onChange={(event) => setContext(event.target.value)}
            placeholder="Ex. : évaluation de fin de trimestre, classes de 60 élèves…"
            rows={3}
            maxLength={1000}
            disabled={loading}
          />
        </label>

        {error && <Notice tone="error">{error}</Notice>}

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Génération en cours…' : 'Générer les exercices'}
          </button>
          {loading && <Spinner label="Recherche des capacités…" />}
        </div>
      </form>

      <div ref={resultRef} className="result-anchor">
        {result && <ResultPanel result={result} onReset={() => setResult(null)} />}
      </div>
    </div>
  )
}
