// @vitest-environment jsdom
import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, expect, it, vi } from 'vitest'
import { SonidoAsistencia } from './SonidoAsistencia'
import { emitirSonido } from './sonidos'
import type { Confirmacion } from './servicio'

vi.mock('./sonidos', async importar => ({ ...await importar<typeof import('./sonidos')>(), emitirSonido: vi.fn() }))
afterEach(() => { cleanup(); vi.unstubAllGlobals(); vi.clearAllMocks() })

it('activa el audio por interacción y reproduce cada confirmación una sola vez', async () => {
  class ContextoPrueba {
    state = 'running'
    resume = vi.fn(async () => {})
    close = vi.fn(async () => {})
  }
  vi.stubGlobal('AudioContext', ContextoPrueba)
  const evento: Confirmacion = { id: 1, persona: null, tipo: 'salida', hora: '2026-10-12T22:00:00Z', resultado: 'Salida registrada', aceptado: true, repetido: false }
  const vista = render(<SonidoAsistencia evento={null} />)
  expect(emitirSonido).not.toHaveBeenCalled()
  await act(async () => { fireEvent.click(screen.getByRole('button', { name: 'Activar sonido' })) })
  expect(emitirSonido).toHaveBeenCalledTimes(1)
  vista.rerender(<SonidoAsistencia evento={evento} />)
  expect(emitirSonido).toHaveBeenLastCalledWith(expect.anything(), 'salida')
  vista.rerender(<SonidoAsistencia evento={evento} />)
  expect(emitirSonido).toHaveBeenCalledTimes(2)
  fireEvent.click(screen.getByRole('button', { name: 'Silenciar avisos' }))
  vista.rerender(<SonidoAsistencia evento={{ ...evento, id: 2, repetido: true }} />)
  expect(emitirSonido).toHaveBeenCalledTimes(2)
})
