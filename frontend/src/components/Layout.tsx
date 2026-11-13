import { Link, NavLink, Outlet } from 'react-router-dom'
import type { ReactNode } from 'react'
import { useMeta } from '../lib/meta'

type IconName = 'home' | 'question' | 'fiche' | 'exercices' | 'corpus'

const ICONS: Record<IconName, ReactNode> = {
  home: (
    <>
      <path d="M3 10.5 12 3l9 7.5" />
      <path d="M5.5 9.5V21h13V9.5" />
      <path d="M9.5 21v-6h5v6" />
    </>
  ),
  question: (
    <>
      <path d="M21 15a2 2 0 0 1-2 2H8l-4 4V5a2 2 0 0 1 2-2h13a2 2 0 0 1 2 2z" />
      <path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1 .9-1 1.7" />
      <path d="M12 16.5h.01" />
    </>
  ),
  fiche: (
    <>
      <path d="M6 3h8l4 4v14H6z" />
      <path d="M14 3v4h4" />
      <path d="M9 12h6M9 16h6" />
    </>
  ),
  exercices: (
    <>
      <path d="M9 6h11M9 12h11M9 18h11" />
      <path d="m4 6 1.2 1.2L7 5.5" />
      <path d="m4 12 1.2 1.2L7 11.5" />
      <path d="m4 18 1.2 1.2L7 17.5" />
    </>
  ),
  corpus: (
    <>
      <path d="M4 5a2 2 0 0 1 2-2h13v18H6a2 2 0 0 1-2-2z" />
      <path d="M8 3v18" />
      <path d="M12 8h4M12 12h4" />
    </>
  ),
}

const NAV: Array<{ to: string; label: string; short: string; icon: IconName; end?: boolean }> = [
  { to: '/', label: 'Accueil', short: 'Accueil', icon: 'home', end: true },
  { to: '/question', label: 'Question', short: 'Question', icon: 'question' },
  { to: '/fiche', label: 'Fiche de cours', short: 'Fiche', icon: 'fiche' },
  { to: '/exercices', label: 'Exercices', short: 'Exos', icon: 'exercices' },
  { to: '/corpus', label: 'Corpus', short: 'Corpus', icon: 'corpus' },
]

function Icon({ name }: { name: IconName }) {
  return (
    <svg
      className="icon"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {ICONS[name]}
    </svg>
  )
}

function ModeBadge() {
  const { meta } = useMeta()
  if (!meta) return null
  if (meta.llm.live) {
    return (
      <span className="badge badge-live" title={`Modèle : ${meta.llm.model}`}>
        IA active
      </span>
    )
  }
  return (
    <span className="badge badge-warn" title="Aucune clé API configurée">
      Mode démo
    </span>
  )
}

export function Layout() {
  const { meta } = useMeta()

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <Link to="/" className="brand">
            <span className="brand-mark">CP</span>
            <span className="brand-text">
              <strong>Cahier PCT</strong>
              <small>Programme officiel · Bénin</small>
            </span>
          </Link>

          <nav className="topnav" aria-label="Navigation principale">
            {NAV.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `topnav-link${isActive ? ' is-active' : ''}`
                }
              >
                <Icon name={item.icon} />
                <span>{item.label}</span>
              </NavLink>
            ))}
          </nav>

          <ModeBadge />
        </div>
      </header>

      <main className="page">
        <Outlet />
        <footer className="footer">
          <p>
            Cahier PCT {meta ? `v${meta.version}` : ''} — l'outil prépare, l'enseignant
            relit et décide.
          </p>
        </footer>
      </main>

      <nav className="tabbar" aria-label="Navigation mobile">
        {NAV.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              `tabbar-link${isActive ? ' is-active' : ''}`
            }
          >
            <Icon name={item.icon} />
            <span>{item.short}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
