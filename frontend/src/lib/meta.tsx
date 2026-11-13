import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { api, errorMessage } from './api'
import type { Meta } from '../types'

type MetaState = {
  meta: Meta | null
  loading: boolean
  error: string | null
  reload: () => void
}

const MetaContext = createContext<MetaState | null>(null)

export function MetaProvider({ children }: { children: ReactNode }) {
  const [meta, setMeta] = useState<Meta | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [nonce, setNonce] = useState(0)

  useEffect(() => {
    let alive = true
    setLoading(true)
    setError(null)
    api
      .meta()
      .then((value) => {
        if (alive) setMeta(value)
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
  }, [nonce])

  const value = useMemo<MetaState>(
    () => ({
      meta,
      loading,
      error,
      reload: () => setNonce((current) => current + 1),
    }),
    [meta, loading, error],
  )

  return <MetaContext.Provider value={value}>{children}</MetaContext.Provider>
}

export function useMeta(): MetaState {
  const context = useContext(MetaContext)
  if (!context) {
    throw new Error('useMeta doit être utilisé dans un MetaProvider.')
  }
  return context
}
