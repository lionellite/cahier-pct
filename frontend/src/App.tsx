import { BrowserRouter, Link, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { MetaProvider } from './lib/meta'
import { HomePage } from './pages/HomePage'
import { QuestionPage } from './pages/QuestionPage'
import { FichePage } from './pages/FichePage'
import { ExercicesPage } from './pages/ExercicesPage'
import { CorpusPage } from './pages/CorpusPage'

function NotFoundPage() {
  return (
    <div className="panel placeholder">
      <span className="eyebrow">Erreur 404</span>
      <h1>Page introuvable</h1>
      <p>Cette page n'existe pas ou a été déplacée.</p>
      <Link to="/" className="btn btn-primary">
        Revenir à l'accueil
      </Link>
    </div>
  )
}

export default function App() {
  return (
    <MetaProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/question" element={<QuestionPage />} />
            <Route path="/fiche" element={<FichePage />} />
            <Route path="/exercices" element={<ExercicesPage />} />
            <Route path="/corpus" element={<CorpusPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </MetaProvider>
  )
}
