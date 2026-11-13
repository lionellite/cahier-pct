export type ExtractSummary = {
  id: string
  title: string
  type: string
  level: string
  status: string
  pages: number[]
  reference: string
  tags: string[]
}

export type ExtractDetail = ExtractSummary & {
  content: string
  source: {
    document?: string
    edition?: string | null
    pages?: number[]
    url?: string | null
  }
  metadata: {
    tags?: string[]
    competences?: string[]
    capacites?: string[]
    criteres?: string[]
    [key: string]: unknown
  }
  version: number
}

export type CorpusStats = {
  id: string
  level: string | null
  levels?: string[]
  discipline?: string | null
  program?: {
    title?: string
    edition?: string | null
    pages?: number
    source?: string
  }
  extract_count: number
  expected_extracts: number
  completion: number | null
  characters: number
  by_type: Record<string, number>
  by_status: Record<string, number>
  validated: number
  corpora?: Array<{
    id: string
    level: string | null
    extract_count: number
    expected_extracts: number
    completion: number | null
  }>
}

export type CorpusResponse = {
  corpus: CorpusStats
  extracts: ExtractSummary[]
}

export type Meta = {
  name: string
  version: string
  llm: {
    mode: 'live' | 'mock'
    model: string
    live: boolean
  }
  corpus: CorpusStats
}

export type Citation = {
  extract_id: string
  title: string
  type: string
  reference: string
  pages: number[]
  status: string
}

export type RetrievedExtract = {
  extract_id: string
  title: string
  type: string
  score: number
  status: string
}

export type GenerationResult = {
  mode: 'question' | 'fiche' | 'exercices'
  content: string
  citations: Citation[]
  retrieved: RetrievedExtract[]
  model: string
  llm_mode: 'live' | 'mock'
  usage: {
    input_tokens?: number
    output_tokens?: number
  }
}

export type QuestionPayload = {
  question: string
  level?: string
  top_k?: number
}

export type FichePayload = {
  competence: string
  level?: string
  duration?: string
  class_size?: string
  context?: string
}

export type ExercicesPayload = {
  competence: string
  level?: string
  count?: number
  with_correction?: boolean
  difficulty?: string
  context?: string
}
