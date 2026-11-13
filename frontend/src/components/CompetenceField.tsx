import type { ExtractSummary } from '../types'
import { typeLabel } from './CitationList'

type Props = {
  value: string
  onChange: (value: string) => void
  extracts: ExtractSummary[]
  listId: string
  disabled?: boolean
}

export function CompetenceField({ value, onChange, extracts, listId, disabled }: Props) {
  return (
    <label className="field">
      <span className="field-label">Compétence, capacité ou thème</span>
      <input
        type="text"
        list={listId}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Ex. : masse volumique, énergie mécanique…"
        disabled={disabled}
        required
      />
      <datalist id={listId}>
        {extracts.map((extract) => (
          <option key={extract.id} value={extract.title}>
            {typeLabel(extract.type)}
          </option>
        ))}
      </datalist>
      <small>
        Choisissez un extrait du corpus ou saisissez une recherche libre. L'outil
        sélectionne les passages du programme les plus proches.
      </small>
    </label>
  )
}
