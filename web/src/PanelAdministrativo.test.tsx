// @vitest-environment jsdom
import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { PanelAdministrativo } from './PanelAdministrativo'
import { consultar } from './servicio'

vi.mock('./servicio', async importar => ({ ...await importar<typeof import('./servicio')>(), consultar: vi.fn() }))
beforeEach(() => {
  vi.stubGlobal('scrollTo', vi.fn())
  vi.stubGlobal('matchMedia', vi.fn((consulta: string) => ({
    matches: false,
    media: consulta,
    onchange: null,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    addListener: vi.fn(),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })))
})
afterEach(() => { cleanup(); vi.clearAllMocks(); vi.unstubAllGlobals(); window.history.replaceState(null, '', '/') })

it('descarta las filas de preplanilla mientras carga justificaciones', async () => {
  window.history.replaceState(null, '', '/administracion#preplanilla')
  let resolver: (datos: unknown) => void = () => {}
  vi.mocked(consultar).mockImplementation(async ruta => {
    if (ruta.includes('catalogo')) return { personas: [], roles: [], grupos: [], carreras: [], horarios: [] }
    if (ruta.includes('preplanilla')) return [{ persona_id: 1, nombre: 'Docente prueba', horas_programadas: 8, horas_permanencia: 7, minutos_tardanza: 0, faltas: 0, sin_salida: 0, estimacion: 70, descuento_referencial: 0 }]
    if (ruta.includes('justificaciones')) return new Promise(respuesta => { resolver = respuesta })
    return []
  })
  await act(async () => { render(<PanelAdministrativo usuario={{ nombre: 'Admin prueba', usuario: 'admin', permiso: 'administrador', sede: 'Principal' }} alCerrar={() => {}} cerrando={false} />) })
  expect(screen.getByText('Docente prueba')).toBeTruthy()
  fireEvent.click(screen.getByRole('button', { name: /^Justificaciones$/ }))
  expect(screen.queryByText('Docente prueba')).toBeNull()
  expect(screen.getByRole('heading', { name: 'Bandeja de solicitudes' })).toBeTruthy()
  await act(async () => { resolver([]) })
  expect(screen.getByText('Todavía no hay registros.')).toBeTruthy()
})

it('mantiene los cuatro destinos móviles y respeta los permisos del operador', async () => {
  vi.mocked(consultar).mockImplementation(async ruta => {
    if (ruta.includes('catalogo')) return { personas: [], roles: [], grupos: [], carreras: [], horarios: [] }
    if (ruta.includes('resumen')) return { presentes: 0, tardanzas: 0, faltas: 0, pendientes: 0, semana: [], diario: [] }
    return []
  })
  await act(async () => { render(<PanelAdministrativo usuario={{ nombre: 'Operador prueba', usuario: 'operador', permiso: 'operador', sede: 'Principal' }} alCerrar={() => {}} cerrando={false} />) })
  const navegacion = within(screen.getByRole('navigation', { name: 'Navegación móvil' }))
  expect(navegacion.getAllByRole('button').map(boton => boton.textContent)).toEqual(['Resumen', 'Jornada', 'Gestión', 'Instituto'])
  await act(async () => { fireEvent.click(navegacion.getByRole('button', { name: 'Instituto' })) })
  const instituto = within(screen.getByRole('region', { name: 'Módulos de Instituto' }))
  expect(instituto.queryByRole('button', { name: /Tolerancias y reglas/ })).toBeNull()
  await act(async () => { fireEvent.click(instituto.getByRole('button', { name: /Personas y carnés/ })) })
  expect(screen.getByRole('heading', { name: 'Directorio institucional' })).toBeTruthy()
  expect(navegacion.getByRole('button', { name: 'Instituto' }).getAttribute('aria-current')).toBe('page')
  expect(window.location.hash).toBe('#personas')
  expect(window.scrollTo).toHaveBeenCalledWith(0, 0)
  await act(async () => { fireEvent.click(navegacion.getByRole('button', { name: 'Gestión' })) })
  expect(within(screen.getByRole('region', { name: 'Módulos de Gestión' })).queryByRole('button', { name: /Preplanilla docente/ })).toBeNull()
  await act(async () => { fireEvent.click(navegacion.getByRole('button', { name: 'Resumen' })) })
  expect(screen.getByRole('heading', { name: 'La jornada de hoy' })).toBeTruthy()
})