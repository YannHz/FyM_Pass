import { useEffect, useRef, useState } from 'react'
import { Search, CheckCircle2, UserRound } from 'lucide-react'
import { consultar, horaLocal } from './servicio'
import { Estado, Insignia, Tabla, useDatos, type Registro } from './componentesGestion'

function hoyLima() { return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Lima', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date()) }
function normalizar(texto: string) { return texto.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('es').trim() }

export function RegistroManual({ catalogo }: { catalogo: Registro }) {
  const [buscar, establecerBuscar] = useState('')
  const [persona, establecerPersona] = useState<Registro | null>(null)
  const [fecha, establecerFecha] = useState(hoyLima)
  const [revision, establecerRevision] = useState(0)
  const [ocupado, establecerOcupado] = useState(false)
  const [error, establecerError] = useState('')
  const [confirmacion, establecerConfirmacion] = useState<Registro | null>(null)
  const buscador = useRef<HTMLInputElement>(null)
  const enviando = useRef(false)
  const solicitud = useRef<{ persona: number; identificador: string } | null>(null)
  const diario = useDatos(`/api/gestion/diario?desde=${fecha}&hasta=${fecha}`, revision, 20000, true)
  const historial = useDatos(`/api/gestion/marcados?desde=${fecha}&hasta=${fecha}`, revision, 0, true)
  useEffect(() => {
    if (confirmacion && !ocupado) buscador.current?.focus()
  }, [confirmacion, ocupado])
  useEffect(() => {
    const actualizar = () => establecerFecha(hoyLima())
    const renovar = () => establecerRevision(valor => valor + 1)
    const intervalo = setInterval(actualizar, 1000)
    window.addEventListener('focus', actualizar)
    window.addEventListener('fym-sesion-renovada', renovar)
    return () => { clearInterval(intervalo); window.removeEventListener('focus', actualizar); window.removeEventListener('fym-sesion-renovada', renovar) }
  }, [])
  const estudiantes = (catalogo.personas as Registro[]).filter(dato => dato.activa && dato.rol_codigo === 'estudiante')
  const palabras = normalizar(buscar).split(/\s+/).filter(Boolean)
  const coincidencias = palabras.length ? estudiantes.filter(dato => palabras.every(palabra => normalizar(`${dato.nombre} ${dato.codigo}`).includes(palabra))) : []
  const filas: Registro[] = diario.datos || []
  const estadoPersona = persona ? filas.find(fila => fila.persona_id === persona.id) : null
  function grupo(dato: Registro) { return catalogo.grupos.find((grupo: Registro) => grupo.id === dato.grupo_id)?.codigo || 'Sin grupo' }
  function seleccionar(dato: Registro) {
    establecerPersona(dato); establecerError(''); establecerConfirmacion(null)
    if (solicitud.current?.persona !== dato.id) solicitud.current = null
  }
  const registrado = Boolean(estadoPersona?.entrada)
  const vencido = !registrado && ['Falta', 'Justificado'].includes(estadoPersona?.estado)
  async function registrar() {
    if (!persona || enviando.current || registrado || vencido) return
    enviando.current = true; establecerOcupado(true); establecerError('')
    solicitud.current ||= { persona: persona.id, identificador: crypto.randomUUID() }
    try {
      const respuesta = await consultar('/api/gestion/manual', { method: 'POST', body: JSON.stringify({ persona_id: persona.id, identificador_evento: solicitud.current.identificador }) })
      establecerConfirmacion(respuesta); establecerPersona(null); establecerBuscar(''); solicitud.current = null
      establecerRevision(valor => valor + 1)
    } catch (problema) {
      establecerError((problema as Error).message)
      establecerRevision(valor => valor + 1)
    } finally { enviando.current = false; establecerOcupado(false) }
  }
  return <>
    <section className="panel registro-manual" aria-labelledby="titulo-registro-manual">
      <div className="cabecera"><div><h2 id="titulo-registro-manual">Registrar asistencia</h2><p>Busca al estudiante y registra su entrada de hoy.</p></div><span className="etiqueta">{new Intl.DateTimeFormat('es-PE', {dateStyle:'long',timeZone:'America/Lima'}).format(new Date(fecha+'T12:00:00-05:00'))}</span></div>
      <label className="buscador buscador-manual"><Search size={20} aria-hidden="true"/><span className="solo-lector">Buscar estudiante por nombre, apellido o código</span><input ref={buscador} type="search" autoComplete="off" placeholder="Buscar estudiante por nombre, apellido o código" value={buscar} disabled={ocupado} onChange={evento => { establecerBuscar(evento.target.value); establecerPersona(null); establecerError(''); establecerConfirmacion(null) }} /></label>
      {confirmacion && <div className="confirmacion-manual" role="status"><CheckCircle2 size={24} aria-hidden="true"/><div><strong>{confirmacion.nombre}</strong><span>{confirmacion.repetido ? 'Entrada ya registrada' : 'Entrada registrada'} · {horaLocal(confirmacion.hora)} · {confirmacion.resultado}</span></div></div>}
      <Estado error={error || diario.error} cargando={diario.cargando && !diario.datos}/>
      {!persona && palabras.length > 0 && <div className="resultados-manual"><p className="nota" role="status">{coincidencias.length ? `${coincidencias.length} ${coincidencias.length === 1 ? 'coincidencia' : 'coincidencias'}${coincidencias.length > 8 ? ' · Mostrando las primeras 8; afina la búsqueda.' : ''}` : 'No se encontraron estudiantes activos con esos datos.'}</p><ul aria-label="Estudiantes encontrados">{coincidencias.slice(0,8).map(dato => { const estado = filas.find(fila => fila.persona_id === dato.id); return <li key={dato.id}><button type="button" className="resultado-manual" disabled={ocupado} onClick={() => seleccionar(dato)}><span className="avatar-manual" aria-hidden="true"><UserRound size={22}/></span><span><strong>{dato.nombre}</strong><small>{dato.codigo} · {grupo(dato)}</small></span><Insignia texto={estado?.entrada ? 'Entrada registrada' : estado?.estado === 'Falta' ? 'Falta' : 'Sin ingreso registrado'}/></button></li> })}</ul></div>}
      {!persona && !palabras.length && !confirmacion && <p className="nota ayuda-manual">Escribe un nombre, apellido o código para encontrar al estudiante.</p>}
      {persona && <article className="seleccion-manual" aria-label="Estudiante seleccionado"><div className="identidad-manual"><span className="avatar-manual" aria-hidden="true"><UserRound size={26}/></span><div><h3>{persona.nombre}</h3><p>{persona.codigo} · {grupo(persona)}</p></div></div><p role="status">{registrado ? `Entrada registrada hoy a las ${horaLocal(estadoPersona!.entrada)}.` : vencido ? 'El plazo de ingreso terminó. El estudiante debe acudir a administración para justificar su falta.' : 'Sin ingreso registrado hoy. La entrada se guardará con la hora actual del servidor.'}</p>{estadoPersona && <Insignia texto={estadoPersona.estado}/>}<div className="acciones"><button type="button" onClick={() => void registrar()} disabled={ocupado || registrado || vencido || !estadoPersona || Boolean(diario.error)}>{ocupado ? 'Registrando…' : 'Registrar entrada'}</button><button type="button" className="secundario" disabled={ocupado} onClick={() => { establecerPersona(null); establecerError(''); buscador.current?.focus() }}>Buscar otro estudiante</button></div></article>}
    </section>
    <section className="panel"><div className="cabecera"><div><h2>Registros manuales de hoy</h2><p>Entradas registradas por el personal autorizado.</p></div></div><Estado error={historial.error} cargando={historial.cargando && !historial.datos}/>{historial.datos && <Tabla filas={historial.datos.filter((fila: Registro) => fila.modalidad === 'manual')} columnas={[{titulo:'Estudiante',mostrar:fila=><>{fila.nombre}<small>{fila.codigo}</small></>},{titulo:'Hora',mostrar:fila=>horaLocal(fila.hora)},{titulo:'Responsable',mostrar:fila=>fila.responsable},{titulo:'Resultado',mostrar:fila=><Insignia texto={fila.resultado}/>}]}/>}</section>
  </>
}
