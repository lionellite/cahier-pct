import type { ReactNode } from 'react'

export function Notice({
  tone = 'info',
  title,
  children,
}: {
  tone?: 'info' | 'warn' | 'error'
  title?: string
  children: ReactNode
}) {
  return (
    <div className={`notice notice-${tone}`} role={tone === 'error' ? 'alert' : 'status'}>
      {title && <strong>{title}</strong>}
      <div>{children}</div>
    </div>
  )
}

export function Spinner({ label = 'Chargement…' }: { label?: string }) {
  return (
    <span className="spinner" role="status">
      <span className="spinner-dot" />
      {label}
    </span>
  )
}
