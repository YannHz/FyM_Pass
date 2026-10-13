// @vitest-environment jsdom
import { afterEach, expect, it, vi } from 'vitest'
import { cambiarConTransicion } from './transiciones'

afterEach(() => { vi.unstubAllGlobals(); Reflect.deleteProperty(document, 'startViewTransition') })

it('navega inmediatamente cuando el navegador no admite transiciones', () => {
  const cambio = vi.fn()
  cambiarConTransicion(cambio)
  expect(cambio).toHaveBeenCalledOnce()
})

it('respeta reducir movimiento aunque el navegador admita transiciones', () => {
  vi.stubGlobal('matchMedia', vi.fn(() => ({ matches: true })))
  const iniciar = vi.fn()
  Object.defineProperty(document, 'startViewTransition', { configurable: true, value: iniciar })
  const cambio = vi.fn()
  cambiarConTransicion(cambio)
  expect(cambio).toHaveBeenCalledOnce()
  expect(iniciar).not.toHaveBeenCalled()
})
it('aplica la transición nativa y cancela la anterior al navegar rápidamente', async () => {
  vi.stubGlobal('matchMedia', vi.fn(() => ({ matches: false })))
  const transiciones: { ready: Promise<void>; finished: Promise<void>; skipTransition: ReturnType<typeof vi.fn> }[] = []
  const iniciar = vi.fn((actualizar: () => void) => {
    actualizar()
    const transicion = { ready: Promise.resolve(), finished: Promise.resolve(), skipTransition: vi.fn() }
    transiciones.push(transicion)
    return transicion
  })
  Object.defineProperty(document, 'startViewTransition', { configurable: true, value: iniciar })
  const primero = vi.fn(), segundo = vi.fn()
  cambiarConTransicion(primero)
  cambiarConTransicion(segundo)
  expect(primero).toHaveBeenCalledOnce()
  expect(segundo).toHaveBeenCalledOnce()
  expect(iniciar).toHaveBeenCalledTimes(2)
  expect(transiciones[0].skipTransition).toHaveBeenCalledOnce()
  await Promise.all(transiciones.map(transicion => transicion.finished))
})