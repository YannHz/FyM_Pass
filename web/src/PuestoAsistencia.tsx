import { useEffect, useRef, useState } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import { consultar, type Confirmacion } from './servicio'
import { ConfirmacionMarcado } from './ConfirmacionMarcado'
import { lazy, Suspense } from 'react'
const LectorCamara = lazy(() => import('./LectorCamara').then(modulo => ({ default: modulo.LectorCamara })))
import { SonidoAsistencia } from './SonidoAsistencia'

type Estado = { nombre: string; qr: string; vence_en: number; camara: boolean; movil: boolean }

export function PuestoAsistencia() {
  const [token] = useState(() => {
    const nuevo = new URLSearchParams(window.location.hash.slice(1)).get('acceso')
    if (nuevo) { sessionStorage.setItem('fym_puesto', nuevo); window.history.replaceState(null, '', '/puesto') }
    return nuevo || sessionStorage.getItem('fym_puesto') || ''
  })
  const [estado, establecerEstado] = useState<Estado | null>(null)
  const [error, establecerError] = useState('')
  const [evento, establecerEvento] = useState<Confirmacion | null>(null)
  const [segundos, establecerSegundos] = useState(0)
  const cursor = useRef(0), cola = useRef<Confirmacion[]>([]), ocupado = useRef(false), enviando = useRef(false)
  useEffect(() => {
    let cancelado = false, temporizador: ReturnType<typeof setTimeout>
    const mostrar = () => {
      if (!ocupado.current && cola.current.length) {
        ocupado.current = true; establecerEvento(cola.current.shift()!)
        temporizador = setTimeout(() => { if (!cancelado) { establecerEvento(null); ocupado.current = false; mostrar() } }, 3000)
      }
    }
    let consultaEnCurso = false
    const actualizar = async () => {
      if (consultaEnCurso) return
      consultaEnCurso = true
      try {
        const [datos, eventos] = await Promise.all([consultar('/api/puesto/estado', { headers: { 'X-Fym-Puesto': token } }), consultar(`/api/puesto/eventos?despues=${cursor.current}`, { headers: { 'X-Fym-Puesto': token } })])
        if (cancelado) return
        establecerEstado(datos); establecerError('')
        for (const nuevo of eventos as Confirmacion[]) { if (nuevo.id > cursor.current) { cola.current.push(nuevo); cursor.current = nuevo.id } }
        mostrar()
      } catch (problema) { if (!cancelado) { establecerError((problema as Error).message); establecerEstado(null); cola.current = [] } }
      finally { consultaEnCurso = false }
    }
    void actualizar(); const intervalo = setInterval(() => void actualizar(), 600)
    return () => { cancelado = true; clearInterval(intervalo); clearTimeout(temporizador); ocupado.current = false }
  }, [token])
  useEffect(() => { const intervalo = setInterval(() => establecerSegundos(Math.max(0, Math.ceil((estado?.vence_en || 0) - Date.now() / 1000))), 200); return () => clearInterval(intervalo) }, [estado?.vence_en])
  async function leerCarne(contenido: string) {
    if (enviando.current || ocupado.current) return
    enviando.current = true
    try {
      const datos: Confirmacion = await consultar('/api/puesto/leer', { method: 'POST', headers: { 'X-Fym-Puesto': token }, body: JSON.stringify({ contenido, identificador_evento: crypto.randomUUID() }) })
      if (datos.repetido) cola.current.push({ ...datos, resultado: 'La asistencia ya fue marcada' })
    }
    catch (problema) { establecerError((problema as Error).message) }
    finally { enviando.current = false }
  }
  return <div className="puesto"><header className="encabezado-puesto"><a className="marca" href="/puesto">FyM <strong>Pass</strong></a><span>{estado?.nombre || 'Puesto de asistencia'}</span><SonidoAsistencia evento={evento} /></header>{error && <p role="alert" className="error">{error}</p>}<main className={`zona-puesto ${estado?.camara && estado.movil ? 'doble' : ''}`}>
    {estado?.movil && <section className="codigo-puesto"><span className="etiqueta">MARCA DESDE TU TELÉFONO</span><h1>Escanea y registra<br />tu asistencia.</h1><div className="qr-puesto"><div className="codigo-qr-renovable" key={estado.qr}><QRCodeSVG value={estado.qr} size={320} level="M" marginSize={4} title="QR dinámico de asistencia" /></div></div><p>Abre tu cuenta en FyM Pass y escanea este código.</p><small className="vigencia-qr">{segundos > 0 ? `El código se renueva en ${segundos} s` : 'Renovando el código…'}</small></section>}
    {estado?.camara && <section className="camara-puesto"><span className="etiqueta">PRESENTA TU CARNÉ VIRTUAL</span><h2>Acerca tu QR a la cámara.</h2><Suspense fallback={<p role="status">Cargando cámara…</p>}><LectorCamara habilitada={Boolean(estado)} bloqueada={Boolean(evento)} alLeer={valor => void leerCarne(valor)} orientacion="user" /></Suspense></section>}
    {!estado && <section className="puesto-cerrado"><h1>El puesto está cerrado.</h1><p>El encargado puede abrirlo o reanudarlo desde su panel.</p></section>}
  </main>{evento && <div className="confirmacion-puesto"><ConfirmacionMarcado evento={evento} /></div>}</div>
}
