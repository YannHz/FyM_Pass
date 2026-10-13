import { useEffect, useRef, useState } from 'react'
import type { Confirmacion } from './servicio'
import { clasificarSonido, emitirSonido } from './sonidos'

export function SonidoAsistencia({ evento }: { evento: Confirmacion | null }) {
  const contexto = useRef<AudioContext | null>(null)
  const ultimo = useRef<Confirmacion | null>(null)
  const [activo, establecerActivo] = useState(false)
  const [error, establecerError] = useState('')
  useEffect(() => () => { void contexto.current?.close().catch(() => {}); contexto.current = null }, [])
  useEffect(() => {
    if (evento === ultimo.current) return
    ultimo.current = evento
    if (evento && activo && contexto.current?.state === 'running') {
      emitirSonido(contexto.current, clasificarSonido(evento))
    }
  }, [evento, activo])
  async function alternar() {
    if (activo) { establecerActivo(false); return }
    try {
      contexto.current ??= new AudioContext()
      await contexto.current.resume()
      emitirSonido(contexto.current, 'entrada')
      establecerActivo(true)
      establecerError('')
    } catch { establecerError('No se pudo activar el sonido. Revisa los permisos de audio del navegador.') }
  }
  return <div>
    <button className="secundario" aria-pressed={activo} onClick={() => void alternar()}>{activo ? 'Silenciar avisos' : 'Activar sonido'}</button>
    {error && <p role="alert" className="error">{error}</p>}
  </div>
}
