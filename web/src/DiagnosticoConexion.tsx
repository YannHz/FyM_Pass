import { useEffect, useRef, useState } from 'react'
import { Copy, RefreshCw, Server, Database, Smartphone } from 'lucide-react'

type Resultado = { estado?: string; motor?: string; direccion_movil?: string | null; mensaje?: string }
async function comprobar(ruta: string): Promise<Resultado | null> {
  try {
    const respuesta = await fetch(ruta, { credentials: 'same-origin', signal: AbortSignal.timeout(5000) })
    if (!respuesta.ok) return null
    return await respuesta.json()
  } catch { return null }
}

export function DiagnosticoConexion() {
  const [api, establecerApi] = useState<boolean | null>(null)
  const [base, establecerBase] = useState<Resultado | null>(null)
  const [red, establecerRed] = useState<Resultado | null>(null)
  const [ocupado, establecerOcupado] = useState(false)
  const [hora, establecerHora] = useState('')
  const [aviso, establecerAviso] = useState('')
  const montado = useRef(false), consultando = useRef(false), version = useRef(0)
  async function actualizar() {
    if (consultando.current) return
    consultando.current = true
    const actual = version.current
    establecerOcupado(true)
    const [salud, datos, conexion] = await Promise.all([
      comprobar('/api/salud'), comprobar('/api/salud/base-datos'), comprobar('/api/diagnostico/conexion'),
    ])
    if (montado.current && actual === version.current) {
      establecerApi(salud?.estado === 'disponible')
      establecerBase(datos)
      establecerRed(conexion)
      establecerHora(new Intl.DateTimeFormat('es-PE', { timeZone: 'America/Lima', hour: '2-digit', minute: '2-digit', second: '2-digit' }).format(new Date()))
      establecerOcupado(false)
    }
    if (actual === version.current) consultando.current = false
  }
  useEffect(() => {
    montado.current = true
    void actualizar()
    const intervalo = setInterval(() => void actualizar(), 30000)
    return () => { montado.current = false; version.current++; consultando.current = false; clearInterval(intervalo) }
  }, [])
  const disponible = base?.estado === 'disponible'
  return <section className="panel diagnostico-conexion" aria-label="Diagnóstico de conexión">
    <div className="cabecera"><div><h2>Conexión del sistema</h2><p>Comprueba el servidor antes de abrir la jornada.</p></div><button className="secundario" disabled={ocupado} onClick={() => void actualizar()}><RefreshCw size={16} aria-hidden="true" />{ocupado ? 'Comprobando…' : 'Comprobar conexión'}</button></div>
    <div className="estados-conexion" aria-live="polite">
      <div><Server size={20} aria-hidden="true" /><strong>API</strong><span className={`insignia ${api === null ? 'neutral' : api ? 'bien' : 'alerta'}`}>{api === null ? 'Sin comprobar' : api ? 'Disponible' : 'Sin conexión'}</span></div>
      <div><Database size={20} aria-hidden="true" /><strong>{base?.motor || 'MySQL / MariaDB'}</strong><span className={`insignia ${!hora ? 'neutral' : disponible ? 'bien' : 'alerta'}`}>{!hora ? 'Sin comprobar' : disponible ? 'Disponible' : api ? 'Sin conexión' : 'No se pudo comprobar'}</span></div>
    </div>
    {api === false && <p>Inicia la API y comprueba la dirección del servidor. Los marcados requieren conexión.</p>}
    {api && hora && !disponible && <p>La API responde, pero la base no está disponible. Revisa MySQL en XAMPP o el servicio de Linux y la configuración local.</p>}
    <div className="conexion-movil"><Smartphone size={20} aria-hidden="true" /><div><strong>Conectar Flutter</strong>{red?.direccion_movil ? <><code>{red.direccion_movil}</code><p>{red.mensaje} Comprueba /api/salud desde el teléfono; este diagnóstico no verifica su conexión ni el firewall.</p><button className="boton-texto" onClick={async () => { try { await navigator.clipboard.writeText(red.direccion_movil!); establecerAviso('Dirección copiada.') } catch { establecerAviso('No se pudo copiar; selecciona la dirección manualmente.') } }}><Copy size={16} aria-hidden="true" />Copiar dirección</button></> : <p>{red?.mensaje || 'La dirección móvil no está disponible. Comprueba API, base y sesión.'}</p>}</div></div>
    <details className="seguimiento"><summary>Recorrido para presentar la demo</summary><ol><li>Comprueba API y base; conecta Flutter a la misma red.</li><li>Abre el puesto y marca una entrada con una cuenta demo.</li><li>Consulta el resultado en Asistencia diaria y repite el escaneo para mostrar el control de duplicados.</li><li>Muestra entrada y salida de personal; el estudiante registra solamente entrada.</li><li>Pausa el puesto y verifica que rechace nuevos marcados.</li><li>Carga una contingencia con hora original y motivo, y exporta el reporte.</li></ol><p className="nota">Prepara horarios demo acordes a la presentación para mostrar puntualidad o tardanza. No cambies el reloj ni borres registros para repetir el ensayo.</p></details>
    <small>{hora ? `Última comprobación: ${hora} · Lima. Se actualiza cada 30 segundos.` : 'Preparando diagnóstico…'}</small>{aviso && <p role="status">{aviso}</p>}
  </section>
}
