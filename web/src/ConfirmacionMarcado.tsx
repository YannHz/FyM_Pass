import type { Confirmacion, Persona } from './servicio'
import { horaLocal } from './servicio'
export function AvatarPersona({ persona }: { persona: Pick<Persona, 'nombre' | 'iniciales'> | null }) {
  return <div className="foto-persona avatar" role="img" aria-label={persona ? `Iniciales de ${persona.nombre}` : 'Identificación no disponible'}>{persona?.iniciales || '?'}</div>
}
export function ConfirmacionMarcado({ evento }: { evento: Confirmacion }) {
  return <div className={`confirmacion ${evento.aceptado ? 'correcta' : 'rechazada'}`} role="status" aria-live="polite"><AvatarPersona persona={evento.persona} /><span className="etiqueta">{evento.persona?.rol || 'Identificación no disponible'}</span><h2>{evento.persona?.nombre || 'QR no reconocido'}</h2><div className="movimiento">{evento.tipo ? evento.tipo === 'entrada' ? 'Entrada' : 'Salida' : 'Marcado rechazado'} <span>{horaLocal(evento.hora)}</span></div><p className="resultado">{evento.aceptado ? '✓ ' : '✕ '}{evento.resultado}</p></div>
}
