// @vitest-environment jsdom
import { act, cleanup, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { PuestoAsistencia } from './PuestoAsistencia'

vi.mock('./servicio', async importar => {
  const original = await importar<typeof import('./servicio')>()
  return { ...original, consultar: vi.fn() }
})
vi.mock('./LectorCamara', () => ({ LectorCamara: () => <div>Cámara de prueba</div> }))
import { consultar } from './servicio'

describe('Confirmaciones del puesto', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    window.history.replaceState(null, '', '/puesto')
    sessionStorage.setItem('fym_puesto', 'credencial de prueba')
    vi.mocked(consultar).mockImplementation(async ruta => {
      if (ruta === '/api/puesto/estado') return { nombre: 'Ingreso', qr: 'codigo de prueba', vence_en: Date.now() / 1000 + 30, camara: false, movil: true }
      if (ruta.endsWith('despues=0')) return [{ id: 1, persona: { nombre: 'Ana Demo', rol: 'Administrativo', foto: null, codigo: 'DEMO-1' }, tipo: 'entrada', hora: '2026-10-11T13:00:00Z', resultado: 'Puntual', aceptado: true, repetido: false }, { id: 2, persona: { nombre: 'Luis Demo', rol: 'Docente', foto: null, codigo: 'DEMO-2' }, tipo: 'salida', hora: '2026-10-11T22:00:00Z', resultado: 'Salida registrada', aceptado: true, repetido: false }]
      return []
    })
  })
  afterEach(() => { cleanup(); vi.useRealTimers(); vi.clearAllMocks(); sessionStorage.clear() })

  it('muestra foto o avatar, nombre, rol y resultado durante tres segundos y respeta la cola', async () => {
    await act(async () => { render(<PuestoAsistencia />) })
    expect(screen.getByRole('heading', { name: 'Ana Demo' })).toBeTruthy()
    expect(screen.getByLabelText('Sin foto de perfil')).toBeTruthy()
    expect(screen.getByText('Administrativo')).toBeTruthy()
    expect(screen.getByText('✓ Puntual')).toBeTruthy()
    await act(async () => { vi.advanceTimersByTime(2999) })
    expect(screen.getByRole('heading', { name: 'Ana Demo' })).toBeTruthy()
    expect(screen.queryByRole('heading', { name: 'Luis Demo' })).toBeNull()
    await act(async () => { vi.advanceTimersByTime(1) })
    expect(screen.queryByRole('heading', { name: 'Ana Demo' })).toBeNull()
    expect(screen.getByRole('heading', { name: 'Luis Demo' })).toBeTruthy()
    await act(async () => { vi.advanceTimersByTime(3000) })
    expect(screen.queryByRole('heading', { name: 'Luis Demo' })).toBeNull()
    expect(screen.getByText('MARCA DESDE TU TELÉFONO')).toBeTruthy()
  })
})
