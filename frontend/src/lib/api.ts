import type {
  CorpusResponse,
  ExercicesPayload,
  ExtractDetail,
  FichePayload,
  GenerationResult,
  Meta,
  QuestionPayload,
} from '../types'

const BASE = (import.meta.env.VITE_API_BASE ?? '/api').replace(/\/$/, '')

export class ApiRequestError extends Error {
  readonly status: number
  readonly code: string
  readonly details?: unknown

  constructor(status: number, message: string, code = 'api_error', details?: unknown) {
    super(message)
    this.name = 'ApiRequestError'
    this.status = status
    this.code = code
    this.details = details
  }
}

type ErrorBody = {
  error?: {
    code?: string
    message?: string
    details?: unknown
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${BASE}${path}`, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...(init?.headers ?? {}),
      },
    })
  } catch {
    throw new ApiRequestError(
      0,
      "Impossible de joindre le serveur. Vérifiez que l'API Flask est démarrée.",
      'network_error',
    )
  }

  const contentType = response.headers.get('content-type') ?? ''
  const body: unknown = contentType.includes('application/json')
    ? await response.json()
    : null

  if (!response.ok) {
    const error = (body as ErrorBody | null)?.error
    throw new ApiRequestError(
      response.status,
      error?.message ?? `Erreur ${response.status}.`,
      error?.code ?? 'api_error',
      error?.details,
    )
  }

  return body as T
}

export const api = {
  meta: () => request<Meta>('/meta'),
  corpus: () => request<CorpusResponse>('/corpus'),
  extract: (id: string) =>
    request<{ extract: ExtractDetail }>(`/corpus/${encodeURIComponent(id)}`),
  question: (payload: QuestionPayload) =>
    request<GenerationResult>('/question', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  fiche: (payload: FichePayload) =>
    request<GenerationResult>('/fiche', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  exercices: (payload: ExercicesPayload) =>
    request<GenerationResult>('/exercices', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
}

export function errorMessage(error: unknown): string {
  if (error instanceof ApiRequestError) return error.message
  if (error instanceof Error) return error.message
  return 'Une erreur inattendue est survenue.'
}
