import type { Confirmacion, Persona } from './servicio'
import { horaLocal } from './servicio'
export function FotoPersona({ persona }: { persona: Persona | null }) {
  return persona?.foto ? <img className="foto-persona" src={persona.foto} alt={`Perfil de ${persona.nombre}`} /> : <div className="foto-persona avatar" aria-label="Sin foto de perfil">{persona ? persona.nombre.split(' ').slice(0, 2).map(parte => parte[0]).join('') : '?'}</div>
}
export function ConfirmacionMarcado({ evento }: { evento: Confirmacion }) {
  return <div className={`confirmacion ${evento.aceptado ? 'correcta' : 'rechazada'}`} role="status" aria-live="polite"><FotoPersona persona={evento.persona} /><span className="etiqueta">{evento.persona?.rol || 'Identificación no disponible'}</span><h2>{evento.persona?.nombre || 'QR no reconocido'}</h2><div className="movimiento">{evento.tipo ? evento.tipo === 'entrada' ? 'Entrada' : 'Salida' : 'Marcado rechazado'} <span>{horaLocal(evento.hora)}</span></div><p className="resultado">{evento.aceptado ? '✓ ' : '✕ '}{evento.resultado}</p></div>
}
