import { useState, type FormEvent } from "react";
import { consultar } from "./servicio";

export function CambiarClaveInicial({ alCambiar, alCerrar }: {
  alCambiar: (datos: any) => void; alCerrar: () => void;
}) {
  const [clave, cambiarClave] = useState("");
  const [confirmacion, cambiarConfirmacion] = useState("");
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
        method: "POST", body: JSON.stringify({ clave, confirmacion }),
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
      <p>Antes de continuar, reemplaza tu contraseña inicial por una personal de al menos 8 caracteres.</p>
      <label htmlFor="nueva-clave">Nueva contraseña</label>
      <input id="nueva-clave" type="password" autoComplete="new-password"
        minLength={8} maxLength={256} required value={clave} disabled={ocupado}
        onChange={evento => cambiarClave(evento.target.value)} />
      <label htmlFor="confirmar-clave">Confirma tu nueva contraseña</label>
      <input id="confirmar-clave" type="password" autoComplete="new-password"
        minLength={8} maxLength={256} required value={confirmacion} disabled={ocupado}
        onChange={evento => cambiarConfirmacion(evento.target.value)} />
      {error && <p role="alert" className="error">{error}</p>}
      <div className="acciones-clave-inicial">
      <button disabled={ocupado}>{ocupado ? "Guardando…" : "Guardar y continuar"}</button>
      <button type="button" className="boton-texto" disabled={ocupado}
        onClick={alCerrar}>Cerrar sesión</button>
      </div>
    </form>
  </main>;
}
