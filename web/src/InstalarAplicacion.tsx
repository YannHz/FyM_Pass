import { useEffect, useState } from 'react'
import { Download } from 'lucide-react'

type SolicitudInstalacion = Event & {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

export function InstalarAplicacion() {
  const [solicitud, establecerSolicitud] = useState<SolicitudInstalacion | null>(null)
  const [instalada, establecerInstalada] = useState(() => window.matchMedia?.('(display-mode: standalone)').matches || Boolean((navigator as Navigator & { standalone?: boolean }).standalone))
  const [aviso, establecerAviso] = useState('')
  const [ocupada, establecerOcupada] = useState(false)
  useEffect(() => {
    function disponible(evento: Event) { evento.preventDefault(); establecerSolicitud(evento as SolicitudInstalacion) }
    function completada() { establecerInstalada(true); establecerSolicitud(null) }
    window.addEventListener('beforeinstallprompt', disponible)
    window.addEventListener('appinstalled', completada)
    return () => { window.removeEventListener('beforeinstallprompt', disponible); window.removeEventListener('appinstalled', completada) }
  }, [])
  if (instalada) return null
  async function instalar() {
    if (!solicitud || ocupada) return
    establecerOcupada(true)
    try {
      await solicitud.prompt()
      const resultado = await solicitud.userChoice
      if (resultado.outcome === 'accepted') establecerInstalada(true)
    } catch { establecerAviso('No se pudo abrir la instalación. Intenta desde el menú del navegador.') }
    finally { establecerSolicitud(null); establecerOcupada(false) }
  }
  return <details className="instalar-aplicacion">
    <summary><Download size={18} aria-hidden="true" /> Instalar FyM Pass</summary>
    <div>
      <p>Abre tu carné o el panel desde un icono en tu teléfono o computadora.</p>
      {solicitud ? <button type="button" disabled={ocupada} onClick={() => void instalar()}>{ocupada ? 'Abriendo instalación…' : 'Instalar aplicación'}</button> : <>
        <p><strong>iPhone o iPad:</strong> abre esta página en Safari, toca Compartir y elige «Añadir a pantalla de inicio».</p>
        <p><strong>Android:</strong> en el menú del navegador busca «Instalar aplicación» o «Añadir a pantalla de inicio».</p>
        <p><strong>Computadora:</strong> en Chrome o Edge busca la opción de instalar en la barra de direcciones o en el menú.</p>
      </>}
      <small>Necesitas conexión para iniciar sesión, consultar el carné y registrar asistencia. La instalación depende del navegador.</small>
      {aviso && <p role="status">{aviso}</p>}
    </div>
  </details>
}
