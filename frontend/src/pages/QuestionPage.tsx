import { useRef, useState } from 'react'
import { api, errorMessage } from '../lib/api'
import { useMeta } from '../lib/meta'
import { Notice, Spinner } from '../components/Notice'
import { ResultPanel } from '../components/ResultPanel'
import type { GenerationResult } from '../types'

const EXAMPLES = [
  'Quelles capacités sont attendues sur la masse volumique ?',
  "Comment évaluer la compétence sur l'énergie mécanique ?",
  'Quels critères utiliser pour une situation d’apprentissage en électricité ?',
]

export function QuestionPage() {
  const { meta } = useMeta()
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState<GenerationResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const resultRef = useRef<HTMLDivElement>(null)

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    if (question.trim().length < 3) {
      setError('Saisissez une question d’au moins 3 caractères.')
      return
    }
    setError(null)
    setLoading(true)
    setResult(null)
    try {
      const response = await api.question({
        question: question.trim(),
        top_k: 5,
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
        <span className="eyebrow">Mode 01</span>
        <h1>Question au programme</h1>
        <p className="page-lede">
          Posez votre question comme vous la poseriez à un collègue. L'outil recherche
          les passages pertinents du programme, répond à partir d'eux et cite ses
          sources.
        </p>
      </header>

      {meta && !meta.llm.live && (
        <Notice tone="warn" title="Mode démonstration actif">
          Aucune clé API n'est configurée. Les réponses affichées sont des extraits
          bruts du corpus, pas des réponses générées. Renseignez{' '}
          <code>ANTHROPIC_API_KEY</code> dans <code>.env</code> pour activer la
          génération.
        </Notice>
      )}

      <form className="panel form" onSubmit={submit}>
        <label className="field">
          <span className="field-label">Votre question</span>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ex. : Quelles capacités doivent être évaluées sur la masse volumique en 3ᵉ ?"
            rows={4}
            maxLength={2000}
            disabled={loading}
          />
          <small>{question.length} / 2000 caractères</small>
        </label>

        <div className="examples">
          <span className="field-label">Exemples</span>
          <div className="chips">
            {EXAMPLES.map((example) => (
              <button
                key={example}
                type="button"
                className="chip"
                onClick={() => setQuestion(example)}
                disabled={loading}
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        {error && <Notice tone="error">{error}</Notice>}

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Recherche en cours…' : 'Interroger le programme'}
          </button>
          {loading && <Spinner label="Analyse du corpus…" />}
        </div>
      </form>

      <div ref={resultRef} className="result-anchor">
        {result && (
          <ResultPanel
            result={result}
            onReset={() => {
              setResult(null)
              setQuestion('')
            }}
          />
        )}
      </div>
    </div>
  )
}
