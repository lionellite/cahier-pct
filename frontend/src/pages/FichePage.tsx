import { useRef, useState } from 'react'
import { api, errorMessage } from '../lib/api'
import { useExtracts } from '../lib/useExtracts'
import { useMeta } from '../lib/meta'
import { CompetenceField } from '../components/CompetenceField'
import { Notice, Spinner } from '../components/Notice'
import { ResultPanel } from '../components/ResultPanel'
import type { GenerationResult } from '../types'

export function FichePage() {
  const { meta } = useMeta()
  const extracts = useExtracts()
  const [competence, setCompetence] = useState('')
  const [duration, setDuration] = useState('2 h')
  const [classSize, setClassSize] = useState('')
  const [context, setContext] = useState('')
  const [result, setResult] = useState<GenerationResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const resultRef = useRef<HTMLDivElement>(null)

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    if (competence.trim().length < 2) {
      setError('Précisez la compétence ou le thème à préparer.')
      return
    }
    setError(null)
    setLoading(true)
    setResult(null)
    try {
      const response = await api.fiche({
        competence: competence.trim(),
        duration: duration.trim() || undefined,
        class_size: classSize.trim() || undefined,
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
        <span className="eyebrow">Mode 02</span>
        <h1>Fiche de préparation</h1>
        <p className="page-lede">
          Choisissez une compétence du programme. L'outil produit une fiche alignée sur
          les compétences, capacités et critères officiels, prête à être relue et
          adaptée.
        </p>
      </header>

      {meta && !meta.llm.live && (
        <Notice tone="warn" title="Mode démonstration actif">
          La fiche complète nécessite la génération par le modèle. En mode démo,
          l'outil affiche uniquement les extraits du programme mobilisés.
        </Notice>
      )}

      <form className="panel form" onSubmit={submit}>
        <CompetenceField
          value={competence}
          onChange={setCompetence}
          extracts={extracts}
          listId="fiche-competences"
          disabled={loading}
        />

        <div className="field-row">
          <label className="field">
            <span className="field-label">Durée de la séance</span>
            <input
              type="text"
              value={duration}
              onChange={(event) => setDuration(event.target.value)}
              placeholder="Ex. : 2 h"
              disabled={loading}
            />
          </label>

          <label className="field">
            <span className="field-label">Effectif (facultatif)</span>
            <input
              type="text"
              value={classSize}
              onChange={(event) => setClassSize(event.target.value)}
              placeholder="Ex. : 60 élèves"
              disabled={loading}
            />
          </label>
        </div>

        <label className="field">
          <span className="field-label">Contexte particulier (facultatif)</span>
          <textarea
            value={context}
            onChange={(event) => setContext(event.target.value)}
            placeholder="Ex. : salle sans électricité, matériel expérimental limité…"
            rows={3}
            maxLength={1000}
            disabled={loading}
          />
        </label>

        {error && <Notice tone="error">{error}</Notice>}

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Préparation en cours…' : 'Générer la fiche'}
          </button>
          {loading && <Spinner label="Recherche des compétences…" />}
        </div>
      </form>

      <div ref={resultRef} className="result-anchor">
        {result && <ResultPanel result={result} onReset={() => setResult(null)} />}
      </div>
    </div>
  )
}
