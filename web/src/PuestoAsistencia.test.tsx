// @vitest-environment jsdom
import { act, cleanup, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { PuestoAsistencia } from './PuestoAsistencia'
import type { Confirmacion } from './servicio'

const datos = vi.hoisted(() => ({ qr: 'codigo-inicial', vence: 0, eventos: [] as Confirmacion[] }))
vi.mock('./servicio', async importar => ({
  ...await importar<typeof import('./servicio')>(),
  consultar: vi.fn(async (ruta: string) => ruta.startsWith('/api/puesto/eventos')
    ? datos.eventos.filter(evento => evento.id > Number(ruta.split('despues=')[1] || 0))
    : { nombre: 'Ingreso principal', qr: datos.qr, vence_en: datos.vence, camara: false, movil: true }),
}))
vi.mock('./SonidoAsistencia', () => ({ SonidoAsistencia: () => null }))

beforeEach(() => {
  vi.useFakeTimers()
  datos.qr = 'codigo-inicial'; datos.vence = Date.now() / 1000 + 30; datos.eventos = []
  window.history.replaceState(null, '', '/puesto')
  sessionStorage.setItem('fym_puesto', 'credencial de prueba')
})
afterEach(() => { cleanup(); vi.useRealTimers(); vi.clearAllMocks(); sessionStorage.clear(); window.history.replaceState(null, '', '/') })

it('mantiene el QR al vencer y anima solamente la llegada de un codigo diferente', async () => {
  vi.useFakeTimers()
  datos.vence = Date.now() / 1000 + 1
  render(<PuestoAsistencia />)
  await act(async () => { await Promise.resolve() })
  const inicial = screen.getByTitle('QR dinámico de asistencia').closest('svg')!
  await act(async () => { await vi.advanceTimersByTimeAsync(1200) })
  expect(screen.getByTitle('QR dinámico de asistencia').closest('svg')).toBe(inicial)
  expect(screen.getByText('Renovando el código…')).toBeTruthy()
  datos.qr = 'codigo-renovado'
  datos.vence = Date.now() / 1000 + 30
  await act(async () => { await vi.advanceTimersByTimeAsync(600) })
  const renovado = screen.getByTitle('QR dinámico de asistencia').closest('svg')!
  expect(renovado).not.toBe(inicial)
  expect(renovado.parentElement?.className).toBe('codigo-qr-renovable')
  await act(async () => { await vi.advanceTimersByTimeAsync(600) })
  expect(screen.getByTitle('QR dinámico de asistencia').closest('svg')).toBe(renovado)
})

it('muestra identidad y resultado tres segundos por persona y respeta la cola', async () => {
  datos.eventos = [
    { id: 1, persona: { nombre: 'Ana Demo', rol: 'Administrativo', foto: null, codigo: 'DEMO-1' }, tipo: 'entrada', hora: '2026-10-11T13:00:00Z', resultado: 'Puntual', aceptado: true, repetido: false },
    { id: 2, persona: { nombre: 'Luis Demo', rol: 'Docente', foto: null, codigo: 'DEMO-2' }, tipo: 'salida', hora: '2026-10-11T22:00:00Z', resultado: 'Salida registrada', aceptado: true, repetido: false },
  ]
  await act(async () => { render(<PuestoAsistencia />) })
  expect(screen.getByRole('heading', { name: 'Ana Demo' })).toBeTruthy()
  expect(screen.getByLabelText('Sin foto de perfil')).toBeTruthy()
  expect(screen.getByText('Administrativo')).toBeTruthy()
  expect(screen.getByText('✓ Puntual')).toBeTruthy()
  expect(screen.queryByRole('heading', { name: 'Luis Demo' })).toBeNull()
  await act(async () => { await vi.advanceTimersByTimeAsync(2999) })
  expect(screen.getByRole('heading', { name: 'Ana Demo' })).toBeTruthy()
  await act(async () => { await vi.advanceTimersByTimeAsync(1) })
  expect(screen.queryByRole('heading', { name: 'Ana Demo' })).toBeNull()
  expect(screen.getByRole('heading', { name: 'Luis Demo' })).toBeTruthy()
  expect(screen.getByText('Docente')).toBeTruthy()
  expect(screen.getByText('✓ Salida registrada')).toBeTruthy()
  await act(async () => { await vi.advanceTimersByTimeAsync(2999) })
  expect(screen.getByRole('heading', { name: 'Luis Demo' })).toBeTruthy()
  await act(async () => { await vi.advanceTimersByTimeAsync(1) })
  expect(screen.queryByRole('heading', { name: 'Luis Demo' })).toBeNull()
  expect(screen.getByTitle('QR dinámico de asistencia')).toBeTruthy()
})
