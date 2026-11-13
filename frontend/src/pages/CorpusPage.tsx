import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api, errorMessage } from '../lib/api'
import { typeLabel } from '../components/CitationList'
import { Markdown } from '../components/Markdown'
import { Notice, Spinner } from '../components/Notice'
import type { CorpusResponse, ExtractDetail, ExtractSummary } from '../types'

const STATUS_LABELS: Record<string, string> = {
  demo: 'Démonstration',
  draft: 'Brouillon',
  validated: 'Validé',
  deprecated: 'Obsolète',
}

function StatusPill({ status }: { status: string }) {
  return (
    <span className={`status status-${status}`}>
      {STATUS_LABELS[status] ?? status}
    </span>
  )
}

export function CorpusPage() {
  const [params, setParams] = useSearchParams()
  const selectedId = params.get('extract')

  const [data, setData] = useState<CorpusResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [query, setQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('')

  const [detail, setDetail] = useState<ExtractDetail | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    setLoading(true)
    api
      .corpus()
      .then((response) => {
        if (alive) setData(response)
      })
      .catch((err) => {
        if (alive) setError(errorMessage(err))
      })
      .finally(() => {
        if (alive) setLoading(false)
      })
    return () => {
      alive = false
    }
  }, [])

  useEffect(() => {
    if (!selectedId) {
      setDetail(null)
      setDetailError(null)
      return
    }
    let alive = true
    setDetailLoading(true)
    setDetailError(null)
    api
      .extract(selectedId)
      .then((response) => {
        if (alive) setDetail(response.extract)
      })
      .catch((err) => {
        if (alive) setDetailError(errorMessage(err))
      })
      .finally(() => {
        if (alive) setDetailLoading(false)
      })
    return () => {
      alive = false
    }
  }, [selectedId])

  const filtered = useMemo(() => {
    if (!data) return []
    const needle = query.trim().toLowerCase()
    return data.extracts.filter((extract) => {
      if (typeFilter && extract.type !== typeFilter) return false
      if (!needle) return true
      return [extract.title, extract.reference, extract.tags.join(' ')]
        .join(' ')
        .toLowerCase()
        .includes(needle)
    })
  }, [data, query, typeFilter])

  const types = useMemo(
    () => (data ? Object.keys(data.corpus.by_type).sort() : []),
    [data],
  )

  function select(extract: ExtractSummary) {
    setParams({ extract: extract.id })
  }

  function closeDetail() {
    setParams({})
  }

  const progress =
    data?.corpus.completion != null ? Math.round(data.corpus.completion * 100) : 0

  return (
    <div className="stack">
      <header className="page-head">
        <span className="eyebrow">Base de connaissances</span>
        <h1>Corpus du programme</h1>
        <p className="page-lede">
          Chaque extrait est daté, référencé et porte un statut de validation. C'est la
          matière première de toutes les réponses de Cahier PCT.
        </p>
      </header>

      {data && (
        <section className="panel corpus-summary">
          <div className="corpus-summary-head">
            <div>
              <h2>{data.corpus.corpora?.length ? 'Programmes PCT par niveau' : data.corpus.program?.title ?? 'Programme PCT'}</h2>
              <p className="muted small">
                {data.corpus.program?.edition
                  ? `Édition ${data.corpus.program.edition} · `
                  : ''}
                {data.corpus.extract_count} extraits ·{' '}
                {data.corpus.characters.toLocaleString('fr-FR')} caractères
              </p>
            </div>
            <span className="badge badge-neutral">
              {data.corpus.validated} validé
              {data.corpus.validated > 1 ? 's' : ''}
            </span>
          </div>
          <div className="progress" aria-label={`Couverture : ${progress} %`}>
            <span style={{ width: `${Math.min(100, Math.max(0, progress))}%` }} />
          </div>
          <p className="muted small">
            Couverture : {data.corpus.extract_count} / {data.corpus.expected_extracts}{' '}
            extraits attendus ({progress} %).
          </p>
        </section>
      )}

      {loading && (
        <div className="panel">
          <Spinner label="Chargement du corpus…" />
        </div>
      )}
      {error && <Notice tone="error">{error}</Notice>}

      <div className="corpus-layout">
        <section className="corpus-column">
          <div className="toolbar">
            <label className="field field-inline">
              <span className="sr-only">Rechercher dans le corpus</span>
              <input
                type="search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Rechercher un titre, un thème…"
              />
            </label>
            <label className="field field-inline">
              <span className="sr-only">Filtrer par type</span>
              <select
                value={typeFilter}
                onChange={(event) => setTypeFilter(event.target.value)}
              >
                <option value="">Tous les types</option>
                {types.map((type) => (
                  <option key={type} value={type}>
                    {typeLabel(type)}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {data && (
            <p className="muted small">
              {filtered.length} extrait{filtered.length > 1 ? 's' : ''} affiché
              {filtered.length > 1 ? 's' : ''}
            </p>
          )}

          <ul className="corpus-list">
            {filtered.map((extract) => (
              <li key={extract.id}>
                <button
                  type="button"
                  className={`corpus-item${selectedId === extract.id ? ' is-selected' : ''}`}
                  onClick={() => select(extract)}
                >
                  <span className="corpus-item-top">
                    <span className="citation-type">{typeLabel(extract.type)}</span>
                    <StatusPill status={extract.status} />
                  </span>
                  <strong>{extract.title}</strong>
                  <span className="muted small">{extract.reference}</span>
                </button>
              </li>
            ))}
          </ul>

          {data && filtered.length === 0 && (
            <p className="muted">Aucun extrait ne correspond à ce filtre.</p>
          )}
        </section>

        <aside className="corpus-detail">
          {!selectedId && (
            <div className="panel placeholder">
              <p>
                Sélectionnez un extrait pour lire son contenu, ses métadonnées et son
                statut de validation.
              </p>
            </div>
          )}

          {selectedId && detailLoading && (
            <div className="panel">
              <Spinner label="Chargement de l'extrait…" />
            </div>
          )}

          {selectedId && detailError && <Notice tone="error">{detailError}</Notice>}

          {detail && !detailLoading && (
            <article className="panel extract-detail">
              <div className="extract-detail-head">
                <div>
                  <span className="citation-type">{typeLabel(detail.type)}</span>
                  <h2>{detail.title}</h2>
                  <p className="muted small">
                    {detail.reference} · version {detail.version}
                  </p>
                </div>
                <button
                  type="button"
                  className="btn btn-ghost btn-small"
                  onClick={closeDetail}
                >
                  Fermer
                </button>
              </div>

              <div className="extract-meta">
                <StatusPill status={detail.status} />
                <span className="muted small">ID : {detail.id}</span>
              </div>

              <Markdown>{detail.content}</Markdown>

              {detail.metadata.competences &&
                detail.metadata.competences.length > 0 && (
                  <div className="meta-group">
                    <h3>Compétences</h3>
                    <ul>
                      {detail.metadata.competences.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}

              {detail.metadata.capacites && detail.metadata.capacites.length > 0 && (
                <div className="meta-group">
                  <h3>Capacités</h3>
                  <ul>
                    {detail.metadata.capacites.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}

              {detail.metadata.criteres && detail.metadata.criteres.length > 0 && (
                <div className="meta-group">
                  <h3>Critères d'évaluation</h3>
                  <ul>
                    {detail.metadata.criteres.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}

              {detail.tags.length > 0 && (
                <div className="chips">
                  {detail.tags.map((tag) => (
                    <span key={tag} className="chip chip-static">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </article>
          )}
        </aside>
      </div>
    </div>
  )
}
