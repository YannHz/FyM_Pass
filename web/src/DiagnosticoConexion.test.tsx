// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, expect, it, vi } from 'vitest'
import { DiagnosticoConexion } from './DiagnosticoConexion'

afterEach(() => { cleanup(); vi.unstubAllGlobals() })

it('muestra API y base independientes y copia la direccion Flutter', async () => {
  vi.stubGlobal('fetch', vi.fn(async (ruta: string) => ({ ok: true, json: async () => ruta.includes('diagnostico') ? { direccion_movil: 'http://192.168.1.10:8000', mensaje: 'Misma red' } : { estado: 'disponible', motor: ruta.includes('base-datos') ? 'MariaDB' : undefined } })))
  const copiar = vi.fn(async () => {})
  Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: copiar } })
  render(<DiagnosticoConexion />)
  await waitFor(() => expect(screen.getAllByText('Disponible')).toHaveLength(2))
  expect(screen.getByText('http://192.168.1.10:8000')).toBeTruthy()
  fireEvent.click(screen.getByRole('button', { name: 'Copiar dirección' }))
  await screen.findByText('Dirección copiada.')
  expect(copiar).toHaveBeenCalledWith('http://192.168.1.10:8000')
})

it('informa que la API responde cuando solo falla la base y permite reintentar', async () => {
  let recuperada = false
  vi.stubGlobal('fetch', vi.fn(async (ruta: string) => ({ ok: !ruta.includes('base-datos') || recuperada, json: async () => ruta.includes('diagnostico') ? { direccion_movil: null, mensaje: 'Reinicia con --red auto.' } : { estado: 'disponible' } })))
  render(<DiagnosticoConexion />)
  await screen.findByText(/La API responde, pero la base no está disponible/)
  expect(screen.getByText('Reinicia con --red auto.')).toBeTruthy()
  recuperada = true
  fireEvent.click(screen.getByRole('button', { name: 'Comprobar conexión' }))
  await waitFor(() => expect(screen.getAllByText('Disponible')).toHaveLength(2))
})

it('muestra la caida total sin afirmar que MySQL fue comprobado', async () => {
  vi.stubGlobal('fetch', vi.fn(async () => { throw new Error('Sin red') }))
  render(<DiagnosticoConexion />)
  await screen.findByText('No se pudo comprobar')
  expect(screen.getByText('Sin conexión')).toBeTruthy()
})
