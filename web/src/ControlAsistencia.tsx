import { useEffect, useState } from 'react'
import { consultar, horaLocal, type Persona } from './servicio'
type Punto = { nombre: string; activo: boolean; camara_puesto_habilitada: boolean; escaneo_movil_habilitado: boolean }
type Marcado = { id: number; persona: Persona; tipo: string; hora: string; resultado: string; modalidad: string }
export function ControlAsistencia() {
  const [punto, establecerPunto] = useState<Punto | null>(null)
  const [marcados, establecerMarcados] = useState<Marcado[]>([])
  const [error, establecerError] = useState(''), [ocupado, establecerOcupado] = useState(false)
  const [camara, establecerCamara] = useState(true), [movil, establecerMovil] = useState(true)
  async function actualizar() { const [datos, registros] = await Promise.all([consultar('/api/asistencia/punto'), consultar('/api/asistencia/marcados')]); establecerPunto(datos); establecerMarcados(registros) }
  useEffect(() => {
    let cancelado = false
    consultar('/api/asistencia/punto').then(datos => { if (!cancelado) { establecerPunto(datos); establecerCamara(datos.camara_puesto_habilitada); establecerMovil(datos.escaneo_movil_habilitado) } }).catch(problema => establecerError(problema.message))
    void actualizar().catch(problema => establecerError(problema.message))
    const intervalo = setInterval(() => void actualizar().catch(problema => establecerError(problema.message)), 4000)
    return () => { cancelado = true; clearInterval(intervalo) }
  }, [])
  async function abrir() {
    const ventana = window.open('about:blank', 'fym-puesto', 'popup,width=1280,height=900')
    if (!ventana) { establecerError('Permite las ventanas emergentes para abrir el puesto.'); return }
    establecerOcupado(true); establecerError('')
    try { const datos = await consultar('/api/asistencia/abrir', { method: 'POST', body: JSON.stringify({ camara_puesto_habilitada: camara, escaneo_movil_habilitado: movil }) }); ventana.location.replace(`/puesto#acceso=${encodeURIComponent(datos.token_puesto)}`); ventana.opener = null; await actualizar() }
    catch (problema) { ventana.close(); establecerError((problema as Error).message) }
    finally { establecerOcupado(false) }
  }
  async function pausar() { establecerOcupado(true); establecerError(''); try { await consultar('/api/asistencia/pausar', { method: 'POST' }); await actualizar() } catch (problema) { establecerError((problema as Error).message) } finally { establecerOcupado(false) } }
  return <><section className="panel"><div className="cabecera"><div><h2>Puesto de asistencia</h2><p>{punto?.nombre || 'Ingreso principal'} · {punto?.activo ? 'Abierto' : 'Cerrado'}</p></div><span className="etiqueta">SEDE PRINCIPAL</span></div><fieldset disabled={ocupado}><legend>Modalidades al abrir el puesto</legend><label className="opcion"><input type="checkbox" checked={movil} onChange={evento => establecerMovil(evento.target.checked)} /> QR dinámico para escaneo desde el teléfono</label><label className="opcion"><input type="checkbox" checked={camara} onChange={evento => establecerCamara(evento.target.checked)} /> Cámara web para leer el carné virtual</label></fieldset><div className="acciones"><button onClick={() => void abrir()} disabled={ocupado || (!camara && !movil)}>{ocupado ? 'Preparando…' : punto?.activo ? 'Reabrir puesto con estas opciones' : 'Iniciar asistencia'}</button><button className="secundario" disabled={ocupado || !punto?.activo} onClick={() => void pausar()}>Pausar puesto</button></div>{error && <p role="alert" className="error">{error}</p>}<p className="nota">La pantalla de marcado se abre en una ventana independiente. Permite el acceso a la cámara allí si activas esa modalidad.</p></section><section className="panel"><h2>Últimos marcados</h2><p className="nota">Horarios ficticios de demo: entrada 08:00, salida 17:00; tolerancia de 10 minutos. No representan los horarios reales del instituto.</p>{marcados.length ? <div className="tabla-contenedor"><table><thead><tr><th>Persona</th><th>Rol</th><th>Movimiento</th><th>Fecha y hora</th><th>Resultado</th></tr></thead><tbody>{marcados.map(marcado => <tr key={marcado.id}><td>{marcado.persona.nombre}</td><td>{marcado.persona.rol}</td><td>{marcado.tipo === 'entrada' ? 'Entrada' : 'Salida'}</td><td>{new Intl.DateTimeFormat('es-PE', { timeZone: 'America/Lima', day: '2-digit', month: '2-digit' }).format(new Date(marcado.hora))} · {horaLocal(marcado.hora)}</td><td>{marcado.resultado}</td></tr>)}</tbody></table></div> : <p>Todavía no hay marcados. Abre el puesto y presenta un carné para probar el recorrido.</p>}</section></>
}
