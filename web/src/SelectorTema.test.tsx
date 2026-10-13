// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, expect, it } from 'vitest'
import { iniciarTema, SelectorTema } from './SelectorTema'

afterEach(() => { cleanup(); localStorage.clear(); delete document.documentElement.dataset.tema; delete document.documentElement.dataset.transparencia })

it('permite regresar al tema del sistema y conserva la transparencia reducida', () => {
  iniciarTema()
  render(<SelectorTema />)
  fireEvent.click(screen.getByLabelText('Preferencias de apariencia'))
  fireEvent.change(screen.getByLabelText('Apariencia'), { target: { value: 'oscuro' } })
  expect(document.documentElement.dataset.tema).toBe('oscuro')
  fireEvent.change(screen.getByLabelText('Apariencia'), { target: { value: 'automatico' } })
  expect(document.documentElement.dataset.tema).toBe('automatico')
  fireEvent.click(screen.getByLabelText('Reducir transparencia'))
  expect(document.documentElement.dataset.transparencia).toBe('reducida')
  expect(localStorage.getItem('fym_transparencia_reducida')).toBe('si')
  cleanup()
  render(<SelectorTema />)
  expect((screen.getByLabelText('Reducir transparencia') as HTMLInputElement).checked).toBe(true)
})

it('cierra las preferencias con Escape y devuelve el foco al control', () => {
  render(<SelectorTema />)
  const control = screen.getByLabelText('Preferencias de apariencia')
  fireEvent.click(control)
  expect(control.closest('details')?.open).toBe(true)
  fireEvent.keyDown(document, { key: 'Escape' })
  expect(control.closest('details')?.open).toBe(false)
  expect(document.activeElement).toBe(control)
})