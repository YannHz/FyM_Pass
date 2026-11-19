import { useState, type FormEvent } from "react";
import { consultar } from "./servicio";

export function CambiarClaveInicial({ alCambiar, alCerrar, requiereActual = false }: {
  requiereActual?: boolean;
  alCambiar: (datos: any) => void; alCerrar: () => void;
}) {
  const [clave, cambiarClave] = useState("");
  const [confirmacion, cambiarConfirmacion] = useState("");
  const [actual, cambiarActual] = useState("");
  const [ocupado, cambiarOcupado] = useState(false);
  const [error, cambiarError] = useState("");
  async function guardar(evento: FormEvent) {
    evento.preventDefault();
    if (ocupado) return;
    if (clave !== confirmacion) {
      cambiarError("Las contraseñas no coinciden.");
      return;
    }
    cambiarOcupado(true);
    cambiarError("");
    try {
      const datos = await consultar("/api/acceso/cambiar-clave", {
        method: "POST", body: JSON.stringify({ clave, confirmacion, actual }),
      });
      cambiarClave("");
      cambiarConfirmacion("");
      alCambiar(datos);
    } catch (problema) { cambiarError((problema as Error).message); }
    finally { cambiarOcupado(false); }
  }
  return <main className="formulario-acceso">
    <form onSubmit={guardar}>
      <h1>Establece tu contraseña</h1>
      <p>Usa entre 8 y 256 caracteres. Puedes escribir una frase con espacios. Evita tu nombre, usuario y contraseñas comunes.</p>
      {requiereActual && <>
        <label htmlFor="clave-actual">Contraseña actual</label>
        <input id="clave-actual" type="password" autoComplete="current-password" required value={actual} maxLength={256} onChange={e => cambiarActual(e.target.value)} />
      </>}
      <label htmlFor="nueva-clave">Nueva contraseña</label>
      <input id="nueva-clave" type="password" autoComplete="new-password"
        minLength={8} maxLength={256} required value={clave} disabled={ocupado}
        onChange={evento => cambiarClave(evento.target.value)} />
      <label htmlFor="confirmar-clave">Confirma tu nueva contraseña</label>
      <input id="confirmar-clave" type="password" autoComplete="new-password"
        minLength={8} maxLength={256} required value={confirmacion} disabled={ocupado}
        onChange={evento => cambiarConfirmacion(evento.target.value)} />
      {error && <p role="alert" className="error">{error}</p>}
      <p className="nota" role="status">{clave.length}/8 caracteres mínimos{confirmacion ? clave === confirmacion ? " · Las contraseñas coinciden." : " · Las contraseñas todavía no coinciden." : ""}</p>
      <div className="acciones-clave-inicial">
      <button disabled={ocupado}>{ocupado ? "Guardando…" : "Guardar y continuar"}</button>
      <button type="button" className="boton-texto" disabled={ocupado}
        onClick={alCerrar}>Cerrar sesión</button>
      </div>
    </form>
  </main>;
}
