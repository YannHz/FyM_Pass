import { useEffect, useId, useRef, useState, type CSSProperties, type KeyboardEvent } from 'react'
import { createPortal } from 'react-dom'
import { CalendarDays, ChevronLeft, ChevronRight } from 'lucide-react'

const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
const diasSemana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
function fechaActual() { return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Lima', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date()) }
function convertir(valor: string) { return new Date(valor + 'T12:00:00Z') }
function codigo(fecha: Date) { return fecha.toISOString().slice(0, 10) }

export function SelectorFecha({ etiqueta, valor, alCambiar }: { etiqueta: string; valor: string; alCambiar: (valor: string) => void }) {
  const identificador = useId()
  const boton = useRef<HTMLButtonElement>(null)
  const panel = useRef<HTMLDivElement>(null)
  const [abierto, establecerAbierto] = useState(false)
  const [mes, establecerMes] = useState((valor || fechaActual()).slice(0, 7))
  const [enfocada, establecerEnfocada] = useState(valor || fechaActual())
  const [elegirMes, establecerElegirMes] = useState(false)
  const [posicion, establecerPosicion] = useState<CSSProperties>({})
  const [anoEscrito, establecerAnoEscrito] = useState('')
  const [ano, numeroMes] = mes.split('-').map(Number)
  const hoy = fechaActual()
  const cantidad = new Date(Date.UTC(ano, numeroMes, 0)).getUTCDate()
  const inicio = (new Date(Date.UTC(ano, numeroMes - 1, 1)).getUTCDay() + 6) % 7
  const texto = valor ? new Intl.DateTimeFormat('es-PE', {timeZone: 'UTC'}).format(convertir(valor)) : 'Seleccionar fecha'

  function abrir() {
    const limites = boton.current!.getBoundingClientRect()
    const ancho = Math.min(336, window.innerWidth - 24)
    establecerPosicion({ width: ancho, left: Math.max(12, Math.min(limites.left, window.innerWidth - ancho - 12)), top: Math.max(12, Math.min(limites.bottom + 8, window.innerHeight - 452)), maxHeight: window.innerHeight - 24 })
    establecerMes((valor || hoy).slice(0, 7))
    establecerEnfocada(valor || hoy)
    establecerElegirMes(false)
    establecerAbierto(true)
  }
  function cerrar() { establecerAbierto(false); boton.current?.focus() }
  function elegir(fecha: string) { alCambiar(fecha); cerrar() }
  function cambiarMes(diferencia: number) {
    const nuevo = new Date(Date.UTC(ano, numeroMes - 1 + diferencia, 1, 12))
    if (nuevo.getUTCFullYear() < 1900 || nuevo.getUTCFullYear() > 2100) return
    establecerMes(codigo(nuevo).slice(0, 7))
    establecerEnfocada(codigo(nuevo))
    establecerAnoEscrito(String(nuevo.getUTCFullYear()))
  }
  useEffect(() => {
    if (!abierto) return
    function fuera(evento: Event) {
      if (!panel.current?.contains(evento.target as Node) && !boton.current?.contains(evento.target as Node)) establecerAbierto(false)
    }
    function redimensionar() { establecerAbierto(false) }
    document.addEventListener('pointerdown', fuera)
    document.addEventListener('focusin', fuera)
    window.addEventListener('scroll', fuera, true)
    window.addEventListener('resize', redimensionar)
    return () => {
      document.removeEventListener('pointerdown', fuera)
      document.removeEventListener('focusin', fuera)
      window.removeEventListener('scroll', fuera, true)
      window.removeEventListener('resize', redimensionar)
    }
  }, [abierto])
  useEffect(() => {
    if (abierto && !elegirMes) panel.current?.querySelector<HTMLButtonElement>(`[data-fecha="${enfocada}"]`)?.focus({preventScroll:true})
  }, [abierto, enfocada, elegirMes])
  function navegar(evento: KeyboardEvent, fecha: string) {
    const movimientos: Record<string, number> = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -7, ArrowDown: 7 }
    if (evento.key in movimientos || evento.key === 'Home' || evento.key === 'End' || evento.key === 'PageUp' || evento.key === 'PageDown') {
      evento.preventDefault()
      const nueva = convertir(fecha)
      if (evento.key === 'PageUp' || evento.key === 'PageDown') { cambiarMes(evento.key === 'PageDown' ? 1 : -1); return }
      const columna = (nueva.getUTCDay() + 6) % 7
      nueva.setUTCDate(nueva.getUTCDate() + (evento.key === 'Home' ? -columna : evento.key === 'End' ? 6 - columna : movimientos[evento.key]))
      if (nueva.getUTCFullYear() < 1900 || nueva.getUTCFullYear() > 2100) return
      establecerMes(codigo(nueva).slice(0, 7)); establecerEnfocada(codigo(nueva))
    }
  }
  return <div className="selector-fecha">
    <span className="etiqueta-fecha" id={`${identificador}-etiqueta`}>{etiqueta}</span>
    <button ref={boton} type="button" className="selector-fecha-control" aria-label={`${etiqueta}: ${texto}`} aria-haspopup="dialog" aria-expanded={abierto} aria-controls={abierto ? identificador : undefined} onClick={() => abierto ? cerrar() : abrir()} onKeyDown={evento => { if (evento.key === 'ArrowDown') { evento.preventDefault(); abrir() } }}><span>{texto}</span><CalendarDays size={17} aria-hidden="true" /></button>
    {abierto && createPortal(<div ref={panel} id={identificador} className="calendario-fecha" role="dialog" aria-label={`Seleccionar fecha: ${etiqueta}`} style={posicion} onKeyDown={evento => { if (evento.key === 'Escape') { evento.preventDefault(); evento.stopPropagation(); cerrar() } }}>
      <header><button type="button" className="secundario mes-fecha" onClick={() => { establecerAnoEscrito(String(ano)); establecerElegirMes(!elegirMes) }} aria-expanded={elegirMes} aria-label="Elegir mes y año">{meses[numeroMes - 1]} de {ano}</button><button type="button" className="icono-boton" aria-label="Mes anterior" onClick={() => cambiarMes(-1)}><ChevronLeft size={18} aria-hidden="true" /></button><button type="button" className="icono-boton" aria-label="Mes siguiente" onClick={() => cambiarMes(1)}><ChevronRight size={18} aria-hidden="true" /></button></header>
      {elegirMes ? <><label className="ano-fecha">Año<input type="number" min="1900" max="2100" value={anoEscrito} onChange={evento => { const nuevo = evento.target.value; establecerAnoEscrito(nuevo); if (/^\d{4}$/.test(nuevo) && Number(nuevo) >= 1900 && Number(nuevo) <= 2100) establecerMes(`${nuevo}-${String(numeroMes).padStart(2,'0')}`) }} /></label><div className="meses-fecha">{meses.map((nombre, indice) => <button key={nombre} type="button" aria-pressed={indice + 1 === numeroMes} onClick={() => { const nuevo = `${ano}-${String(indice + 1).padStart(2,'0')}`; establecerMes(nuevo); establecerEnfocada(nuevo+'-01'); establecerElegirMes(false) }}>{nombre.slice(0,3)}</button>)}</div></> : <><div className="dias-fecha" aria-hidden="true">{diasSemana.map(dia => <span key={dia}>{dia}</span>)}</div><div className="rejilla-fecha" role="group" aria-label={`${meses[numeroMes - 1]} de ${ano}`}>{Array.from({length:cantidad}, (_, indice) => { const fecha = `${mes}-${String(indice + 1).padStart(2,'0')}`; return <button key={fecha} type="button" data-fecha={fecha} style={indice === 0 ? {gridColumnStart:inicio + 1} : undefined} tabIndex={fecha === enfocada ? 0 : -1} aria-label={new Intl.DateTimeFormat('es-PE',{timeZone:'UTC',dateStyle:'full'}).format(convertir(fecha))} aria-pressed={fecha === valor} aria-current={fecha === hoy ? 'date' : undefined} onKeyDown={evento => navegar(evento,fecha)} onClick={() => elegir(fecha)}>{indice + 1}</button> })}</div></>}
      <footer><button type="button" className="boton-texto" onClick={cerrar}>Cancelar</button><button type="button" className="secundario" onClick={() => elegir(hoy)}>Hoy</button></footer>
    </div>, document.body)}
  </div>
}
