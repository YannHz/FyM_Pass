import { AgregarAlumnos } from './AgregarAlumnos'
import { useRef, useState, type FormEvent } from 'react'
import { Plus, GraduationCap, ContactRound, Users } from 'lucide-react'
import { Dialogo, Insignia, Vacio, type Registro } from './componentesGestion'
import { SelectorFiltro } from './SelectorFiltro'
import { ConfiguradorIngreso } from './ConfiguradorIngreso'
import { ConfirmarHorario } from './ConfirmarHorario'
import { resumenHorario, type Tramo } from './EditorHorario'
import { consultar } from './servicio'

export type ContextoCarreras = { carreraId: number | null; vista: 'carreras' | 'horarios' }
type Propiedades = { catalogo: Registro; administrador: boolean; nuevaCarrera: (valor?: Registro) => void;
  nuevoHorario: (valor?: Registro) => void; nuevaPersona: (persona?: Registro, grupo?: Registro) => void;
  guardado: (mensaje: string) => void; contexto: ContextoCarreras; cambiarContexto: (valor: ContextoCarreras) => void }

function FormularioGrupo({ carrera, grupo, horario, cerrar, guardado }: { carrera: Registro; grupo?: Registro; horario?: Registro; cerrar: () => void; guardado: (mensaje: string) => void }) {
  const [ciclo, establecerCiclo] = useState(grupo?.ciclo || 'I')
  const [turno, establecerTurno] = useState(grupo?.turno || 'Mañana')
  const [tramos, establecerTramos] = useState<Tramo[]>(() => horario?.tramos.map((tramo: Tramo) => ({ ...tramo, hora_salida: null })) || [0, 1, 2, 3, 4].map(dia => ({ dia_semana: dia, hora_entrada: '08:00', hora_salida: null })))
  const [activo, establecerActivo] = useState(grupo?.activo ?? true)
  const [ocupado, establecerOcupado] = useState(false), [error, establecerError] = useState('')
  const envio = useRef(false)
  async function guardar(evento: FormEvent) {
    evento.preventDefault()
    if (envio.current || !tramos.length) return
    envio.current = true; establecerOcupado(true); establecerError('')
    try {
      const codigo = grupo?.codigo || `${carrera.codigo}-${ciclo.trim().toUpperCase()}-${turno.slice(0, 1)}`.slice(0, 30)
      const respuesta = await consultar('/api/gestion/grupos', { method: 'POST', body: JSON.stringify({ id: grupo?.id, carrera_id: carrera.id, ciclo, turno, codigo, activo,
        ingreso: { nombre: `${carrera.codigo} · Ciclo ${ciclo} · ${turno}`.slice(0, 100), tramos } }) })
      guardado(respuesta.mensaje + ' Agrega alumnos y confirma su horario.'); cerrar()
    } catch (problema) { establecerError((problema as Error).message) }
    finally { envio.current = false; establecerOcupado(false) }
  }
  return <Dialogo titulo={grupo ? 'Configurar ciclo y turno' : 'Añadir ciclo y turno'} cerrar={cerrar} bloqueado={ocupado} clase="dialogo-grupo"><form onSubmit={guardar} className="formulario-grupo"><p className="contexto-carrera"><GraduationCap size={20} aria-hidden="true"/>{carrera.nombre}</p><fieldset disabled={ocupado}><div className="datos-grupo"><label>Semestre / ciclo<input required maxLength={30} value={ciclo} onChange={evento => establecerCiclo(evento.target.value)}/></label><div><span>Turno</span><SelectorFiltro etiqueta="Turno" enFormulario valor={turno} alCambiar={establecerTurno} opciones={['Mañana', 'Tarde', 'Noche'].map(valor => ({ valor, texto: valor }))}/></div></div><fieldset><legend>Días y horas de ingreso</legend><ConfiguradorIngreso tramos={tramos} cambiar={establecerTramos}/></fieldset>{grupo && <label className="opcion"><input type="checkbox" checked={activo} onChange={evento => establecerActivo(evento.target.checked)}/>Grupo activo</label>}</fieldset><p className="nota">Este horario se aplicará a los alumnos cuando confirmes su asignación. Los registros anteriores se conservan.</p>{error && <p role="alert" className="aviso error">{error}</p>}<footer className="acciones-dialogo"><button type="button" className="secundario" disabled={ocupado} onClick={cerrar}>Cancelar</button><button disabled={ocupado || !tramos.length || !ciclo.trim()}>{ocupado ? 'Guardando…' : 'Guardar configuración'}</button></footer></form></Dialogo>
}

export function CarrerasHorarios({ catalogo, administrador, nuevaCarrera, nuevoHorario, nuevaPersona, guardado, contexto, cambiarContexto }: Propiedades) {
  const [grupoAlumnos, establecerGrupoAlumnos] = useState<Registro | null>(null)
  const [grupoEditar, establecerGrupoEditar] = useState<Registro | null | undefined>(undefined)
  const [confirmacion, establecerConfirmacion] = useState<{ grupo?: Registro; horario: Registro; personas: Registro[] } | null>(null)
  const carrera = catalogo.carreras.find((valor: Registro) => valor.id === contexto.carreraId) || catalogo.carreras[0]
  const grupos = catalogo.grupos.filter((valor: Registro) => valor.carrera_id === carrera?.id)
  const personal = catalogo.personas.filter((valor: Registro) => valor.activa && ['docente', 'administrativo'].includes(valor.rol_codigo))
  const laborales = catalogo.horarios.filter((valor: Registro) => valor.activo && valor.tramos.length && valor.tramos.every((tramo: Tramo) => tramo.hora_salida))
  return <div className="modulo-carreras"><div className="opciones-ingreso" role="group" aria-label="Tipo de horario"><button type="button" className="secundario" aria-pressed={contexto.vista === 'carreras'} onClick={() => cambiarContexto({ ...contexto, vista: 'carreras' })}><GraduationCap size={18} aria-hidden="true"/>Estudiantes</button><button type="button" className="secundario" aria-pressed={contexto.vista === 'horarios'} onClick={() => cambiarContexto({ ...contexto, vista: 'horarios' })}><ContactRound size={18} aria-hidden="true"/>Docentes y administrativos</button></div>
  {contexto.vista === 'carreras' ? <><p className="nota">1. Crea la carrera · 2. Configura ciclo y turno · 3. Agrega alumnos · 4. Confirma el horario</p><div className="organizacion-carreras"><section className="panel listado-carreras"><div className="cabecera"><h2>Carreras</h2>{administrador && <button type="button" className="icono-boton" aria-label="Añadir carrera" onClick={() => nuevaCarrera()}><Plus size={18}/></button>}</div><div className="opciones-carrera">{catalogo.carreras.map((valor: Registro) => <button type="button" key={valor.id} className="opcion-carrera" aria-pressed={valor.id === carrera?.id} onClick={() => cambiarContexto({ ...contexto, carreraId: valor.id })}><span className="codigo-carrera">{valor.codigo}</span><strong>{valor.nombre}</strong><small>{valor.activa ? 'Activa' : 'Inactiva'}</small></button>)}</div>{!carrera && <Vacio titulo="Crea la primera carrera"/>}</section>
  {carrera && <section className="panel"><div className="cabecera"><div><h2>{carrera.nombre}</h2><p>Ciclos y turnos</p></div>{administrador && <div className="acciones"><button type="button" className="boton-texto" onClick={() => nuevaCarrera(carrera)}>Editar carrera</button><button type="button" onClick={() => establecerGrupoEditar(null)}><Plus size={16}/>Añadir ciclo y turno</button></div>}</div><div className="grupos-simplificados">{grupos.map((grupo: Registro) => {
    const horario = catalogo.horarios.find((valor: Registro) => valor.id === grupo.horario_id)
    const alumnos = catalogo.personas.filter((valor: Registro) => valor.grupo_id === grupo.id && valor.rol_codigo === 'estudiante')
    const pendientes = alumnos.filter((valor: Registro) => valor.activa && !valor.asignaciones?.some((asignacion: Registro) => asignacion.horario_id === grupo.horario_id))
    return <article className="grupo-simplificado" key={grupo.id}><div className="cabecera"><div><h3>Ciclo {grupo.ciclo} · {grupo.turno}</h3><p>{horario ? resumenHorario(horario.tramos) : 'Configura el horario de ingreso'}</p></div><Insignia texto={grupo.activo ? 'Activo' : 'Desactivado'}/></div><p className="nota">{alumnos.length} alumnos · {pendientes.length} por confirmar</p><details><summary>Ver alumnos</summary><ul className="personas-confirmacion">{alumnos.map((alumno: Registro) => <li key={alumno.id}>{alumno.nombre}<small>{alumno.codigo}</small></li>)}</ul>{!alumnos.length && <p className="nota">Agrega los alumnos de este ciclo y turno.</p>}</details>{administrador && <div className="acciones"><button type="button" className="boton-texto" onClick={() => establecerGrupoEditar(grupo)}>Configurar horario</button><button type="button" className="secundario" disabled={!grupo.activo || !carrera.activa} onClick={() => establecerGrupoAlumnos(grupo)}><Users size={16}/>Agregar alumnos</button><button type="button" disabled={!grupo.activo || !horario?.activo || !alumnos.some((valor: Registro) => valor.activa)} onClick={() => establecerConfirmacion({ grupo, horario, personas: alumnos.filter((valor: Registro) => valor.activa) })}>Confirmar horario</button></div>}</article>
  })}</div>{!grupos.length && <Vacio titulo="Configura el primer ciclo y turno" detalle="Establece los días y la hora de entrada antes de agregar alumnos."/>}</section>}</div></> : <section className="panel"><div className="cabecera"><div><h2>Horarios laborales</h2><p>Entrada y salida por día, independientes de las carreras.</p></div>{administrador && <button type="button" onClick={() => nuevoHorario()}><Plus size={16}/>Crear horario laboral</button>}</div><div className="biblioteca-horarios">{laborales.map((horario: Registro) => <article className="tarjeta-horario" key={horario.id}><h3>{horario.nombre}</h3><p>{resumenHorario(horario.tramos)}</p>{administrador && <div className="acciones"><button type="button" disabled={!personal.length} onClick={() => establecerConfirmacion({ horario, personas: personal })}>Asignar personal</button><button type="button" className="boton-texto" onClick={() => nuevoHorario(horario)}>Crear copia</button></div>}</article>)}</div>{!laborales.length && <Vacio titulo="Crea un horario laboral" detalle="Después podrás elegir los docentes o administrativos y confirmar desde qué fecha lo usarán."/>}<p className="nota">Para cambiar un horario, crea una copia y confirma la nueva asignación. Se conserva el historial anterior.</p></section>}
  {grupoEditar !== undefined && carrera && <FormularioGrupo carrera={carrera} grupo={grupoEditar || undefined} horario={catalogo.horarios.find((valor: Registro) => valor.id === grupoEditar?.horario_id)} cerrar={() => establecerGrupoEditar(undefined)} guardado={guardado}/>}
  {grupoAlumnos && <AgregarAlumnos grupo={grupoAlumnos} catalogo={catalogo} cerrar={() => establecerGrupoAlumnos(null)} registrar={() => { const grupo = grupoAlumnos; establecerGrupoAlumnos(null); nuevaPersona(undefined, grupo) }} guardado={guardado}/>}
  {confirmacion && <ConfirmarHorario {...confirmacion} cerrar={() => establecerConfirmacion(null)} guardado={guardado}/>}
  </div>
}
