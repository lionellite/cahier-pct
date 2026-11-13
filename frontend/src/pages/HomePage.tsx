import { Link } from 'react-router-dom'
import { useMeta } from '../lib/meta'

const MODES = [
  {
    to: '/question',
    number: '01',
    title: 'Poser une question',
    text: "Interrogez le programme en langage naturel. Chaque réponse cite la compétence, la capacité ou la section qui la justifie.",
    cta: 'Ouvrir le mode question',
  },
  {
    to: '/fiche',
    number: '02',
    title: 'Préparer une fiche',
    text: "Obtenez une fiche de préparation complète : objectifs, déroulement, matériel et évaluation, alignés sur le programme officiel.",
    cta: 'Créer une fiche',
  },
  {
    to: '/exercices',
    number: '03',
    title: 'Générer des exercices',
    text: "Produisez un sujet et sa grille de correction à partir d'une compétence du programme, avec les critères officiels.",
    cta: 'Créer une évaluation',
  },
]

export function HomePage() {
  const { meta, loading, error } = useMeta()
  const corpus = meta?.corpus
  const progress = corpus?.completion != null ? Math.round(corpus.completion * 100) : 0

  return (
    <div className="stack">
      <section className="hero">
        <span className="eyebrow">Assistant pédagogique · PCT Bénin</span>
        <h1>
          Préparer ses cours de PCT,
          <br />
          sans quitter le programme officiel.
        </h1>
        <p className="hero-lede">
          Cahier PCT répond aux questions des enseignants, prépare des fiches et génère
          des exercices <strong>uniquement à partir du programme certifié</strong>. Chaque
          réponse est traçable : l'enseignant peut vérifier la source en un clic.
        </p>
        <div className="hero-actions">
          <Link to="/question" className="btn btn-primary">
            Poser une question
          </Link>
          <Link to="/corpus" className="btn btn-secondary">
            Explorer le corpus
          </Link>
        </div>
      </section>

      <section className="mode-grid" aria-label="Les trois modes">
        {MODES.map((mode) => (
          <Link key={mode.to} to={mode.to} className="mode-card">
            <span className="mode-number">{mode.number}</span>
            <h2>{mode.title}</h2>
            <p>{mode.text}</p>
            <span className="mode-cta">{mode.cta} →</span>
          </Link>
        ))}
      </section>

      <section className="panel corpus-card">
        <div className="corpus-card-head">
          <div>
            <span className="eyebrow">Base de connaissances</span>
            <h2>Programmes officiels PCT</h2>
          </div>
          {corpus && (
            <span className="badge badge-neutral">
              {corpus.extract_count} / {corpus.expected_extracts} extraits
            </span>
          )}
        </div>

        {loading && <p className="muted">Chargement de l'état du corpus…</p>}
        {error && (
          <p className="muted">
            État du corpus indisponible : {error}. Vérifiez que l'API Flask est lancée.
          </p>
        )}

        {corpus && (
          <>
            <div className="progress" aria-label={`Couverture du corpus : ${progress} %`}>
              <span style={{ width: `${Math.min(100, Math.max(0, progress))}%` }} />
            </div>
            <p className="muted small">
              {corpus.validated} extrait{corpus.validated > 1 ? 's' : ''} validé
              {corpus.validated > 1 ? 's' : ''} · {corpus.characters.toLocaleString('fr-FR')}{' '}
              caractères indexés
              {corpus.corpora && corpus.corpora.length > 1
                ? ` · ${corpus.corpora.length} corpus : ${corpus.corpora
                    .map((c) => c.id)
                    .join(', ')}`
                : ''}
              . Les extraits sont en cours de validation pédagogique.
            </p>
          </>
        )}
      </section>

      <section className="principles">
        <article>
          <h3>Fidélité</h3>
          <p>
            Aucune réponse hors programme non signalée. Si l'information n'y est pas,
            l'outil le dit.
          </p>
        </article>
        <article>
          <h3>Traçabilité</h3>
          <p>
            Chaque affirmation renvoie à un extrait daté, avec sa page et son statut de
            validation.
          </p>
        </article>
        <article>
          <h3>Sobriété</h3>
          <p>
            Une application web mobile légère, utilisable là où l'enseignant prépare
            réellement ses cours.
          </p>
        </article>
      </section>
    </div>
  )
}
