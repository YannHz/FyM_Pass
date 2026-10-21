import { useId, useRef, useState } from 'react'
import { Search, UserPlus, X, GraduationCap, Check, Info } from 'lucide-react'
import { Dialogo, Vacio, type Registro } from './componentesGestion'
import { consultar } from './servicio'
import { AvatarPersona } from './ConfirmacionMarcado'
import './AgregarAlumnos.css'

export function AgregarAlumnos({ grupo, catalogo, cerrar, registrar, guardado }: {
  grupo: Registro; catalogo: Registro; cerrar: () => void; registrar: () => void; guardado: (mensaje: string) => void
}) {
  const identificador = useId()
  const [busqueda, establecerBusqueda] = useState('')
  const [seleccion, establecerSeleccion] = useState<number[]>([])
  const [ocupado, establecerOcupado] = useState(false), [error, establecerError] = useState('')
  const enviando = useRef(false)
  const alumnos = catalogo.personas.filter((persona: Registro) => persona.activa && persona.rol_codigo === 'estudiante' && persona.grupo_id !== grupo.id)
  const normalizar = (valor: string) => valor.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('es')
  const visibles = alumnos.filter((persona: Registro) => normalizar(`${persona.nombre} ${persona.codigo}`).includes(normalizar(busqueda)))
  const todosVisibles = visibles.length > 0 && visibles.every((persona: Registro) => seleccion.includes(persona.id))
  const carrera = catalogo.carreras.find((valor: Registro) => valor.id === grupo.carrera_id)
  function grupoActual(persona: Registro) {
    const actual = catalogo.grupos.find((valor: Registro) => valor.id === persona.grupo_id)
    const carreraActual = catalogo.carreras.find((valor: Registro) => valor.id === actual?.carrera_id)
    return actual ? `${carreraActual?.codigo || ''} · Ciclo ${actual.ciclo} · ${actual.turno}` : 'Sin grupo asignado'
  }
  async function guardar() {
    if (enviando.current || !seleccion.length) return
    enviando.current = true; establecerOcupado(true); establecerError('')
    try {
      const respuesta = await consultar(`/api/gestion/grupos/${grupo.id}/alumnos`, { method: 'POST', body: JSON.stringify({
        alumnos: alumnos.filter((persona: Registro) => seleccion.includes(persona.id)).map((persona: Registro) => ({ persona_id: persona.id, grupo_esperado: persona.grupo_id || null })),
      }) })
      guardado(respuesta.mensaje); cerrar()
    } catch (problema) { establecerError((problema as Error).message) }
    finally { enviando.current = false; establecerOcupado(false) }
  }
  function seleccionarVisibles() {
    establecerSeleccion(actual => todosVisibles
      ? actual.filter(id => !visibles.some((persona: Registro) => persona.id === id))
      : [...new Set([...actual, ...visibles.map((persona: Registro) => persona.id)])])
  }
  return <Dialogo titulo="Agregar alumnos" cerrar={cerrar} bloqueado={ocupado} clase="dialogo-agregar-alumnos">
    <div className="seleccion-alumnos" aria-busy={ocupado}>
      <section className="destino-alumnos" aria-label="Grupo de destino">
        <span className="simbolo-destino" aria-hidden="true"><GraduationCap size={24}/></span>
        <div><span className="rotulo-destino">Grupo de destino</span><h3>{carrera?.nombre}</h3><p>Ciclo {grupo.ciclo}<span aria-hidden="true"> · </span>{grupo.turno}</p></div>
      </section>
      <fieldset disabled={ocupado} className="controles-seleccion-alumnos">
        <legend className="solo-lectura-alumnos">Alumnos registrados</legend>
        <div className="herramientas-seleccion-alumnos">
          <div className="campo-busqueda-alumnos">
            <label className="solo-lectura-alumnos" htmlFor={identificador}>Buscar alumnos registrados</label>
            <Search size={19} aria-hidden="true"/>
            <input id={identificador} type="search" autoComplete="off" value={busqueda} placeholder="Buscar por nombre o ID" onChange={evento => establecerBusqueda(evento.target.value)}/>
            {busqueda && <button className="limpiar-busqueda-alumnos" type="button" aria-label="Limpiar búsqueda" onClick={() => establecerBusqueda('')}><X size={17}/></button>}
          </div>
          <button type="button" className="secundario registrar-nuevo-alumno" onClick={registrar}><UserPlus size={18} aria-hidden="true"/>Registrar nuevo alumno</button>
        </div>
        <div className="resumen-lista-alumnos"><span role="status">{visibles.length} {busqueda ? (visibles.length === 1 ? 'resultado' : 'resultados') : 'alumnos disponibles'}</span>{visibles.length > 0 && <button type="button" className="boton-texto" onClick={seleccionarVisibles}>{todosVisibles ? 'Quitar selección visible' : busqueda ? 'Seleccionar resultados' : 'Seleccionar todos'}</button>}</div>
        <div className="listado-seleccion-alumnos" role="group" aria-label="Alumnos disponibles">
          {visibles.map((persona: Registro) => {
            const elegido = seleccion.includes(persona.id)
            return <label key={persona.id} className="fila-seleccion-alumno" data-seleccionado={elegido}>
              <span className="casilla-alumno"><input type="checkbox" checked={elegido} onChange={() => establecerSeleccion(actual => actual.includes(persona.id) ? actual.filter(id => id !== persona.id) : [...actual, persona.id])}/><Check size={15} aria-hidden="true"/></span>
              <span className="avatar-seleccion-alumno" aria-hidden="true"><AvatarPersona persona={{ nombre: persona.nombre, iniciales: persona.iniciales }}/></span>
              <span className="datos-seleccion-alumno"><strong>{persona.nombre}</strong><span className="codigo-seleccion-alumno">{persona.codigo}</span><span className="origen-seleccion-alumno">Grupo actual: {grupoActual(persona)}</span></span>
            </label>
          })}
          {!visibles.length && <Vacio titulo={busqueda ? 'No encontramos coincidencias' : 'No hay alumnos por agregar'} detalle={busqueda ? 'Prueba con otro nombre o ID. También puedes registrar un nuevo alumno.' : 'Los alumnos que ya están en este grupo no aparecen aquí.'}/>}
        </div>
      </fieldset>
      <p className="aclaracion-seleccion-alumnos"><Info size={17} aria-hidden="true"/><span>Pasarán al grupo elegido. Su horario se conserva hasta confirmar el nuevo.</span></p>
      {error && <p role="alert" className="aviso error error-seleccion-alumnos">{error}</p>}
      <footer className="pie-seleccion-alumnos"><span className="total-seleccion-alumnos" role="status" aria-live="polite">{seleccion.length ? <><strong>{seleccion.length}</strong> {seleccion.length === 1 ? 'alumno seleccionado' : 'alumnos seleccionados'}</> : 'Selecciona los alumnos que deseas agregar'}</span><div><button className="secundario" type="button" disabled={ocupado} onClick={cerrar}>Cancelar</button><button type="button" disabled={ocupado || !seleccion.length} onClick={() => void guardar()}>{ocupado ? 'Agregando…' : 'Agregar alumnos'}</button></div></footer>
    </div>
  </Dialogo>
}
