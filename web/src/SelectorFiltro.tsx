import { useEffect, useId, useRef, useState, type KeyboardEvent, type CSSProperties } from 'react'
import { createPortal } from 'react-dom'
import { Check, ChevronDown } from 'lucide-react'

type Opcion = { valor: string; texto: string }

export function SelectorFiltro({ etiqueta, valor, opciones, alCambiar }: { etiqueta: string; valor: string; opciones: Opcion[]; alCambiar: (valor: string) => void }) {
  const identificador = useId()
  const boton = useRef<HTMLButtonElement>(null)
  const lista = useRef<HTMLUListElement>(null)
  const busqueda = useRef({ texto: '', hora: 0 })
  const [abierto, establecerAbierto] = useState(false)
  const [activo, establecerActivo] = useState(0)
  const [posicion, establecerPosicion] = useState<CSSProperties>({})
  const seleccion = Math.max(0, opciones.findIndex(opcion => opcion.valor === valor))

  function abrir(indice = seleccion) {
    const limites = boton.current!.getBoundingClientRect()
    const altura = Math.min(320, opciones.length * 44 + 16)
    const arriba = window.innerHeight - limites.bottom < altura + 16 && limites.top > window.innerHeight - limites.bottom
    establecerPosicion({ left: Math.max(8, Math.min(limites.left, window.innerWidth - limites.width - 8)), width: limites.width, maxHeight: Math.max(44, Math.min(320, (arriba ? limites.top : window.innerHeight - limites.bottom) - 16)), ...(arriba ? { bottom: window.innerHeight - limites.top + 8 } : { top: limites.bottom + 8 }) })
    establecerActivo(indice)
    establecerAbierto(true)
  }
  function elegir(indice: number) {
    alCambiar(opciones[indice].valor)
    establecerAbierto(false)
    boton.current?.focus()
  }
  useEffect(() => {
    if (!abierto) return
    function cerrarFuera(evento: Event) {
      if (!boton.current?.contains(evento.target as Node) && !lista.current?.contains(evento.target as Node)) establecerAbierto(false)
    }
    function cerrar() { establecerAbierto(false) }
    document.addEventListener('pointerdown', cerrarFuera)
    document.addEventListener('focusin', cerrarFuera)
    window.addEventListener('resize', cerrar)
    window.addEventListener('scroll', cerrarFuera, true)
    return () => {
      document.removeEventListener('pointerdown', cerrarFuera)
      document.removeEventListener('focusin', cerrarFuera)
      window.removeEventListener('resize', cerrar)
      window.removeEventListener('scroll', cerrarFuera, true)
    }
  }, [abierto])
  useEffect(() => { if (abierto) lista.current?.children[activo]?.scrollIntoView({ block: 'nearest' }) }, [activo, abierto])

  function manejarTecla(evento: KeyboardEvent<HTMLButtonElement>) {
    const tecla = evento.key
    if (tecla === 'Tab' || tecla === 'Escape') { establecerAbierto(false); return }
    if (['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(tecla)) {
      evento.preventDefault()
      const indice = tecla === 'Home' ? 0 : tecla === 'End' ? opciones.length - 1 : Math.max(0, Math.min(opciones.length - 1, activo + (tecla === 'ArrowDown' ? 1 : -1)))
      if (!abierto) abrir(tecla === 'Home' || tecla === 'End' ? indice : seleccion)
      else establecerActivo(indice)
    } else if (tecla === 'Enter' || tecla === ' ') {
      evento.preventDefault()
      if (abierto) elegir(activo)
      else abrir()
    } else if (tecla.length === 1 && !evento.ctrlKey && !evento.metaKey && !evento.altKey) {
      evento.preventDefault()
      const ahora = Date.now()
      busqueda.current = { texto: (ahora - busqueda.current.hora < 700 ? busqueda.current.texto : '') + tecla.toLocaleLowerCase('es'), hora: ahora }
      const indice = opciones.findIndex(opcion => opcion.texto.toLocaleLowerCase('es').startsWith(busqueda.current.texto))
      if (indice >= 0) { if (abierto) establecerActivo(indice); else abrir(indice) }
    }
  }
  return <div className="selector-filtro">
    <button ref={boton} type="button" className="selector-filtro-control" role="combobox" aria-label={`${etiqueta}: ${opciones[seleccion]?.texto}`} aria-expanded={abierto} aria-haspopup="listbox" aria-controls={abierto ? identificador : undefined} aria-activedescendant={abierto ? `${identificador}-${activo}` : undefined} onKeyDown={manejarTecla} onClick={() => abierto ? establecerAbierto(false) : abrir()}>
      <span>{opciones[seleccion]?.texto}</span><ChevronDown size={16} aria-hidden="true" />
    </button>
    {abierto && createPortal(<ul ref={lista} id={identificador} role="listbox" aria-label={etiqueta} className="selector-filtro-lista" style={posicion} onPointerDown={evento => { if (evento.pointerType === 'mouse') evento.preventDefault() }}>
      {opciones.map((opcion, indice) => <li key={opcion.valor} id={`${identificador}-${indice}`} role="option" aria-selected={opcion.valor === valor} data-activo={activo === indice} onPointerMove={() => establecerActivo(indice)} onClick={() => elegir(indice)}><span>{opcion.texto}</span>{opcion.valor === valor && <Check size={16} aria-hidden="true" />}</li>)}
    </ul>, document.body)}
  </div>
}
