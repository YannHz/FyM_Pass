import { useEffect, useRef, useState } from 'react'
import { SlidersHorizontal as IconoApariencia } from 'lucide-react'

type Tema = 'claro' | 'oscuro' | 'automatico'
const clave = 'fym_tema'
const claveTransparencia = 'fym_transparencia_reducida'
function leerTema(): Tema {
  try { const valor = localStorage.getItem(clave); return valor === 'claro' || valor === 'oscuro' ? valor : 'automatico' }
  catch { return 'automatico' }
}
function leerTransparencia() {
  try { return localStorage.getItem(claveTransparencia) === 'si' } catch { return false }
}
function aplicarPreferencias() {
  document.documentElement.dataset.tema = leerTema()
  document.documentElement.dataset.transparencia = leerTransparencia() ? 'reducida' : 'normal'
}
export function iniciarTema() {
  aplicarPreferencias()
  window.addEventListener('storage', evento => {
    if ([clave, claveTransparencia, null].includes(evento.key)) aplicarPreferencias()
  })
}
export function SelectorTema() {
  const preferencias = useRef<HTMLDetailsElement>(null)
  const [tema, establecerTema] = useState<Tema>(leerTema)
  const [transparenciaReducida, establecerTransparenciaReducida] = useState(leerTransparencia)
  useEffect(() => {
    const sincronizar = () => { establecerTema(leerTema()); establecerTransparenciaReducida(leerTransparencia()) }
    window.addEventListener('storage', sincronizar)
    return () => window.removeEventListener('storage', sincronizar)
  }, [])
  useEffect(() => {
    const cerrarFuera = (evento: PointerEvent) => { if (evento.target instanceof Node && !preferencias.current?.contains(evento.target) && preferencias.current) preferencias.current.open = false }
    const cerrarConTeclado = (evento: KeyboardEvent) => { if (evento.key === 'Escape' && preferencias.current?.open) { preferencias.current.open = false; preferencias.current.querySelector('summary')?.focus() } }
    document.addEventListener('pointerdown', cerrarFuera)
    document.addEventListener('keydown', cerrarConTeclado)
    return () => { document.removeEventListener('pointerdown', cerrarFuera); document.removeEventListener('keydown', cerrarConTeclado) }
  }, [])
  return <details ref={preferencias} className="preferencias-visuales"><summary className="icono-boton" aria-label="Preferencias de apariencia" title="Preferencias de apariencia"><IconoApariencia size={20} aria-hidden="true" /></summary><div className="opciones-apariencia"><strong>A tu manera</strong><label>Apariencia<select value={tema} onChange={evento => {
    const elegido = evento.target.value as Tema
    establecerTema(elegido); document.documentElement.dataset.tema = elegido
    try { localStorage.setItem(clave, elegido) } catch {}
  }}><option value="automatico">Según el sistema</option><option value="claro">Clara</option><option value="oscuro">Oscura</option></select></label><label className="opcion"><input type="checkbox" checked={transparenciaReducida} onChange={evento => {
    const reducida = evento.target.checked
    establecerTransparenciaReducida(reducida); document.documentElement.dataset.transparencia = reducida ? 'reducida' : 'normal'
    try { localStorage.setItem(claveTransparencia, reducida ? 'si' : 'no') } catch {}
  }} />Reducir transparencia</label><small>El movimiento se adapta a las preferencias de tu dispositivo.</small></div></details>
}