// @vitest-environment jsdom
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, expect, it, vi } from 'vitest'
import { LectorCamara } from './LectorCamara'

const simulacion = vi.hoisted(() => ({ recibir: null as null | ((resultado: { getText: () => string }) => void), detener: vi.fn() }))
vi.mock('@zxing/browser', () => ({ BrowserQRCodeReader: class {
  async decodeFromConstraints(_opciones: unknown, _video: unknown, recibir: typeof simulacion.recibir) {
    simulacion.recibir = recibir
    return { stop: simulacion.detener }
  }
} }))
afterEach(() => { cleanup(); vi.clearAllMocks(); simulacion.recibir = null })

it('procesa el siguiente carné mantenido durante el bloqueo y evita repetirlo', async () => {
  const leer = vi.fn()
  const vista = render(<LectorCamara habilitada bloqueada={false} alLeer={leer} />)
  await act(async () => { fireEvent.click(screen.getByRole('button', { name: 'Activar cámara' })) })
  await waitFor(() => expect(simulacion.recibir).not.toBeNull())
  act(() => { simulacion.recibir?.({ getText: () => 'QR_A' }) })
  expect(leer).toHaveBeenCalledWith('QR_A')
  vista.rerender(<LectorCamara habilitada bloqueada alLeer={leer} />)
  act(() => { simulacion.recibir?.({ getText: () => 'QR_B' }) })
  expect(leer).toHaveBeenCalledTimes(1)
  vista.rerender(<LectorCamara habilitada bloqueada={false} alLeer={leer} />)
  act(() => { simulacion.recibir?.({ getText: () => 'QR_B' }) })
  expect(leer).toHaveBeenLastCalledWith('QR_B')
  act(() => { simulacion.recibir?.({ getText: () => 'QR_B' }) })
  expect(leer).toHaveBeenCalledTimes(2)
})
