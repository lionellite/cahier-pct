import { useState } from 'react'
import type { GenerationResult } from '../types'
import { CitationList } from './CitationList'
import { Markdown } from './Markdown'

const TITLES: Record<GenerationResult['mode'], string> = {
  question: 'Réponse',
  fiche: 'Fiche de préparation',
  exercices: 'Évaluation et exercices',
}

type Props = {
  result: GenerationResult
  onReset?: () => void
}

export function ResultPanel({ result, onReset }: Props) {
  const [copied, setCopied] = useState(false)

  async function copy() {
    try {
      await navigator.clipboard.writeText(result.content)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 2000)
    } catch {
      setCopied(false)
    }
  }

  return (
    <article className="result" aria-live="polite">
      <header className="result-head">
        <div>
          <span className="eyebrow">Résultat</span>
          <h2>{TITLES[result.mode]}</h2>
        </div>
        <div className="result-actions">
          {result.llm_mode === 'mock' && (
            <span className="badge badge-warn">Mode démo</span>
          )}
          <button type="button" className="btn btn-ghost" onClick={copy}>
            {copied ? 'Copié' : 'Copier'}
          </button>
          {onReset && (
            <button type="button" className="btn btn-ghost" onClick={onReset}>
              Recommencer
            </button>
          )}
        </div>
      </header>

      <Markdown>{result.content}</Markdown>
      <CitationList citations={result.citations} />

      <p className="result-foot">
        Modèle : {result.model} · {result.citations.length} extrait
        {result.citations.length > 1 ? 's' : ''} mobilisé
        {result.citations.length > 1 ? 's' : ''}
      </p>
    </article>
  )
}
