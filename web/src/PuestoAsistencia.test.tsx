// @vitest-environment jsdom
import { act, cleanup, render, screen } from '@testing-library/react'
import { afterEach, expect, it, vi } from 'vitest'
import { PuestoAsistencia } from './PuestoAsistencia'

const datos = vi.hoisted(() => ({ qr: 'codigo-inicial', vence: 0 }))
vi.mock('./servicio', () => ({ consultar: vi.fn(async (ruta: string) => ruta.startsWith('/api/puesto/eventos') ? [] : { nombre: 'Ingreso principal', qr: datos.qr, vence_en: datos.vence, camara: false, movil: true }) }))
vi.mock('./SonidoAsistencia', () => ({ SonidoAsistencia: () => null }))

afterEach(() => { cleanup(); vi.useRealTimers() })

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
