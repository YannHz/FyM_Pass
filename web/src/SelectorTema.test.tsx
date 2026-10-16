// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, expect, it, vi } from 'vitest'
import { iniciarTema, SelectorTema } from './SelectorTema'

afterEach(() => {
  cleanup(); localStorage.clear(); vi.unstubAllGlobals()
  delete document.documentElement.dataset.tema
  delete document.documentElement.dataset.transparencia
})

it('alterna con un clic y conserva la eleccion al volver a abrir', () => {
  localStorage.setItem('fym_tema', 'claro')
  iniciarTema()
  render(<SelectorTema />)
  fireEvent.click(screen.getByRole('button', { name: 'Cambiar a modo oscuro' }))
  expect(document.documentElement.dataset.tema).toBe('oscuro')
  expect(localStorage.getItem('fym_tema')).toBe('oscuro')
  cleanup()
  render(<SelectorTema />)
  fireEvent.click(screen.getByRole('button', { name: 'Cambiar a modo claro' }))
  expect(document.documentElement.dataset.tema).toBe('claro')
  expect(screen.queryByRole('combobox')).toBeNull()
  expect(screen.queryByText('Reducir transparencia')).toBeNull()
})

it('alterna desde la apariencia efectiva del sistema y descarta la transparencia anterior', () => {
  vi.stubGlobal('matchMedia', vi.fn(() => ({ matches: true, addEventListener: vi.fn(), removeEventListener: vi.fn() })))
  localStorage.setItem('fym_transparencia_reducida', 'si')
  document.documentElement.dataset.transparencia = 'reducida'
  iniciarTema()
  render(<SelectorTema />)
  fireEvent.click(screen.getByRole('button', { name: 'Cambiar a modo claro' }))
  expect(document.documentElement.dataset.tema).toBe('claro')
  expect(document.documentElement.dataset.transparencia).toBeUndefined()
})

it('sincroniza el control con los cambios de otra ventana', () => {
  localStorage.setItem('fym_tema', 'claro')
  render(<SelectorTema />)
  localStorage.setItem('fym_tema', 'oscuro')
  fireEvent(window, new StorageEvent('storage', { key: 'fym_tema' }))
  expect(screen.getByRole('button', { name: 'Cambiar a modo claro' })).toBeTruthy()
  expect(document.documentElement.dataset.tema).toBe('oscuro')
})

it('permite cambiar de tema aunque el navegador bloquee el almacenamiento', () => {
  localStorage.setItem('fym_tema', 'claro')
  const almacenamiento = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => { throw new Error('No disponible') })
  render(<SelectorTema />)
  fireEvent.click(screen.getByRole('button', { name: 'Cambiar a modo oscuro' }))
  expect(document.documentElement.dataset.tema).toBe('oscuro')
  expect(screen.getByRole('button', { name: 'Cambiar a modo claro' })).toBeTruthy()
  almacenamiento.mockRestore()
})
