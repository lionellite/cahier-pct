import { useEffect, useState } from 'react'
import { api } from './api'
import type { ExtractSummary } from '../types'

export function useExtracts(): ExtractSummary[] {
  const [extracts, setExtracts] = useState<ExtractSummary[]>([])

  useEffect(() => {
    let alive = true
    api
      .corpus()
      .then((response) => {
        if (alive) setExtracts(response.extracts)
      })
      .catch(() => {
        // Les suggestions sont facultatives : la saisie libre reste possible.
      })
    return () => {
      alive = false
    }
  }, [])

  return extracts
}
