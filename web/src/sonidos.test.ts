import { describe, expect, it } from 'vitest'
import { clasificarSonido } from './sonidos'
import type { Confirmacion } from './servicio'

const evento: Confirmacion = { id: 1, persona: null, tipo: 'entrada', hora: '2026-10-12T13:00:00Z', resultado: 'Puntual', aceptado: true, repetido: false }

describe('Sonidos de resultados confirmados', () => {
  it('distingue entrada, salida, rechazo y una respuesta idempotente', () => {
    expect(clasificarSonido(evento)).toBe('entrada')
    expect(clasificarSonido({ ...evento, tipo: 'salida' })).toBe('salida')
    expect(clasificarSonido({ ...evento, aceptado: false, resultado: 'QR no válido' })).toBe('rechazado')
    expect(clasificarSonido({ ...evento, repetido: true })).toBe('repetido')
  })
  it('reconoce el marcado previo aunque la API lo devuelva como rechazo', () => {
    expect(clasificarSonido({ ...evento, aceptado: false, resultado: 'La asistencia de hoy ya está registrada' })).toBe('repetido')
    expect(clasificarSonido({ ...evento, aceptado: false, tipo: 'salida', resultado: 'La entrada y salida de hoy ya están registradas' })).toBe('repetido')
  })
})
