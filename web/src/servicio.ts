export type Persona = { nombre: string; rol: string; foto: string | null; codigo: string }
export type Confirmacion = { id: number; persona: Persona | null; tipo: string | null; hora: string; resultado: string; aceptado: boolean; repetido: boolean }
export type Carne = Persona & { sede: string; qr: string }
export async function consultar(ruta: string, opciones?: RequestInit) {
  let respuesta: Response
  try { respuesta = await fetch(ruta, { ...opciones, credentials: 'same-origin', signal: AbortSignal.timeout(10000), headers: { 'Content-Type': 'application/json', 'X-Fym-Peticion': '1', ...opciones?.headers } }) }
  catch { throw new Error('No se pudo confirmar el resultado. Revisa los registros antes de volver a intentar.') }
  const datos = await respuesta.json().catch(() => ({ detail: 'El servidor no pudo atender la solicitud.' }))
  if (!respuesta.ok) throw new Error(typeof datos.detail === 'string' ? datos.detail : 'No se pudo completar la solicitud.')
  return datos
}
export function horaLocal(valor: string) { return new Intl.DateTimeFormat('es-PE', { timeZone: 'America/Lima', hour: '2-digit', minute: '2-digit', second: '2-digit' }).format(new Date(valor)) }
