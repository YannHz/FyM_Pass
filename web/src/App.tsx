import { PanelAdministrativo } from "./PanelAdministrativo";
import { consultar } from "./servicio";
import { CarneVirtual } from "./CarneVirtual";
import { ControlAsistencia } from "./ControlAsistencia";
import {
  ScanLine as IconoPase,
  ArrowRight as IconoContinuar,
  ShieldCheck as IconoSeguridad,
} from "lucide-react";
import { SelectorTema } from "./SelectorTema";
import { useEffect, useState, type FormEvent } from "react";

type Usuario = {
  id: number;
  nombre: string;
  usuario: string;
  rol: string;
  permiso: string;
  sede: string;
  destino: string;
};
type Resumen = { personas_por_rol: Record<string, number>; mensaje: string };

export function Aplicacion() {
  const [usuario, establecerUsuario] = useState<Usuario | null>(null);
  const [cargando, establecerCargando] = useState(true);
  const [ocupado, establecerOcupado] = useState(false);
  const [nombre, establecerNombre] = useState("");
  const [clave, establecerClave] = useState("");
  const [visible, establecerVisible] = useState(false);
  const [error, establecerError] = useState("");
  const [resumen, establecerResumen] = useState<Resumen | null>(null);

  function mostrarDestino(datos: Usuario) {
    establecerUsuario(datos);
    if (window.location.pathname !== "/mi-carne")
      window.history.replaceState(
        null,
        "",
        datos.destino + window.location.hash,
      );
  }
  useEffect(() => {
    fetch("/api/acceso/actual", {
      credentials: "same-origin",
      signal: AbortSignal.timeout(10000),
    })
      .then(async (respuesta) => {
        if (respuesta.ok) mostrarDestino(await respuesta.json());
        else if (respuesta.status === 401)
          window.history.replaceState(null, "", "/acceso");
        else
          establecerError(
            "No se pudo recuperar la sesión. Intenta iniciar sesión nuevamente.",
          );
      })
      .catch(() =>
        establecerError(
          "No se pudo conectar con el sistema. Comprueba que el servidor esté iniciado.",
        ),
      )
      .finally(() => establecerCargando(false));
  }, []);
  useEffect(() => {
    establecerResumen(null);
    if (usuario && usuario.permiso !== "personal") {
      consultar("/api/administracion/resumen")
        .then(establecerResumen)
        .catch((problema) => establecerError(problema.message));
    }
  }, [usuario]);

  async function iniciarSesion(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    establecerOcupado(true);
    establecerError("");
    try {
      const datos = await consultar("/api/acceso/iniciar", {
        method: "POST",
        body: JSON.stringify({ usuario: nombre, clave }),
      });
      establecerClave("");
      mostrarDestino(datos);
    } catch (problema) {
      establecerError(
        problema instanceof TypeError ||
          (problema instanceof Error && problema.name === "TimeoutError")
          ? "No se pudo conectar. Revisa el servidor e intenta nuevamente."
          : (problema as Error).message,
      );
    } finally {
      establecerOcupado(false);
    }
  }
  async function cerrarSesion() {
    establecerOcupado(true);
    establecerError("");
    try {
      await consultar("/api/acceso/cerrar", { method: "POST" });
      establecerUsuario(null);
      establecerResumen(null);
      establecerClave("");
      establecerNombre("");
      window.history.replaceState(null, "", "/acceso");
    } catch {
      establecerError(
        "No se pudo cerrar la sesión. Comprueba la conexión y vuelve a intentar.",
      );
    } finally {
      establecerOcupado(false);
    }
  }
  if (cargando)
    return (
      <main className="espera" role="status">
        Preparando FyM Pass…
      </main>
    );
  if (!usuario)
    return (
      <div className="acceso">
        <div className="apariencia-acceso">
          <SelectorTema />
        </div>
        <section className="presentacion">
          <a className="marca" href="/">
            FyM <strong>Pass</strong>
          </a>
          <div>
            <span className="etiqueta">FINNEY & MILLER</span>
            <h1>
              Tu día empieza
              <br />
              <span className="acento-titulo">con un Pass.</span>
            </h1>
            <p>
              Un acceso que te acompaña. Tu carné y la jornada de Finney &amp;
              Miller, en un solo lugar.
            </p>
            <div className="vista-pase" aria-hidden="true">
              <div className="cabecera-vista-pase">
                <span>FINNEY &amp; MILLER</span>
                <IconoPase size={28} />
              </div>
              <strong>
                Tu lugar.
                <br />
                Tu próximo paso.
              </strong>
              <div className="pie-vista-pase">
                <span>Acceso institucional</span>
                <span>FyM Pass</span>
              </div>
            </div>
          </div>
          <small>Sede principal · Demo funcional</small>
        </section>
        <main className="formulario-acceso">
          <form onSubmit={iniciarSesion}>
            <span className="simbolo-acceso" aria-hidden="true">
              <IconoPase size={30} />
            </span>
            <span className="etiqueta">ACCESO INSTITUCIONAL</span>
            <h2>Bienvenido de nuevo</h2>
            <p>
              Ingresa con tu cuenta. El sistema te llevará al espacio que te
              corresponde.
            </p>
            <label htmlFor="usuario">Usuario</label>
            <input
              id="usuario"
              name="username"
              autoComplete="username"
              maxLength={80}
              required
              value={nombre}
              onChange={(evento) => establecerNombre(evento.target.value)}
              disabled={ocupado}
            />
            <label htmlFor="clave">Contraseña</label>
            <div className="campo-clave">
              <input
                id="clave"
                name="password"
                type={visible ? "text" : "password"}
                autoComplete="current-password"
                required
                maxLength={256}
                value={clave}
                onChange={(evento) => establecerClave(evento.target.value)}
                disabled={ocupado}
              />
              <button
                type="button"
                className="boton-texto"
                aria-pressed={visible}
                aria-label={
                  visible ? "Ocultar contraseña" : "Mostrar contraseña"
                }
                onClick={() => establecerVisible(!visible)}
              >
                {visible ? "Ocultar" : "Mostrar"}
              </button>
            </div>
            {error && (
              <p role="alert" className="error">
                {error}
              </p>
            )}
            <button
              className="ingresar"
              disabled={ocupado || !nombre.trim() || !clave}
            >
              {ocupado ? "Ingresando…" : "Iniciar sesión"}
              <IconoContinuar size={18} aria-hidden="true" />
            </button>
            <div className="seguridad-acceso">
              <IconoSeguridad size={16} aria-hidden="true" />
              Tu cuenta, tu acceso institucional.
            </div>
            <p className="ayuda">
              ¿Necesitas una cuenta? Contacta al encargado del instituto.
            </p>
          </form>
        </main>
      </div>
    );
  const administrativo =
    usuario.permiso !== "personal" && window.location.pathname !== "/mi-carne";
  if (administrativo)
    return (
      <PanelAdministrativo
        usuario={usuario}
        alCerrar={() => void cerrarSesion()}
        cerrando={ocupado}
      />
    );
  return (
    <div className="estructura">
      <aside>
        <a className="marca" href={usuario.destino}>
          FyM <strong>Pass</strong>
        </a>
        <p>Finney & Miller</p>
        <nav aria-label="Navegación principal">
          <a href={usuario.destino} aria-current="page">
            {administrativo ? "Inicio" : "Mi acceso"}
          </a>
        </nav>
        <button
          className="secundario"
          onClick={() => {
            window.open("/mi-carne", "_blank", "noopener");
          }}
        >
          Mi carné
        </button>
        <small>{usuario.sede}</small>
      </aside>
      <main>
        <header className="cabecera">
          <div className="apariencia-personal">
            <SelectorTema />
          </div>
          <div>
            <span className="etiqueta">
              {usuario.permiso === "administrador"
                ? "ADMINISTRACIÓN"
                : usuario.permiso === "operador"
                  ? "OPERACIÓN DE ASISTENCIA"
                  : "ACCESO PERSONAL"}
            </span>
            <h1>Hola, {usuario.nombre.split(" ")[0]}.</h1>
            <p>
              {usuario.nombre} · {usuario.sede}
            </p>
          </div>
          <button
            className="secundario"
            onClick={() => void cerrarSesion()}
            disabled={ocupado}
          >
            {ocupado ? "Cerrando…" : "Cerrar sesión"}
          </button>
        </header>
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
        {administrativo ? (
          <>
            <ControlAsistencia />
            <section className="panel">
              <h2>Personas registradas</h2>
              {resumen ? (
                <>
                  <div className="conteos">
                    {[
                      ["estudiante", "Estudiantes"],
                      ["docente", "Docentes"],
                      ["administrativo", "Administrativos"],
                    ].map(([rol, titulo]) => (
                      <article key={rol}>
                        <strong>{resumen.personas_por_rol[rol] || 0}</strong>
                        <span>{titulo}</span>
                      </article>
                    ))}
                  </div>
                  <p className="nota">Cuentas ficticias de demostración.</p>
                </>
              ) : (
                <p role="status">Consultando la sede…</p>
              )}
            </section>
          </>
        ) : (
          <CarneVirtual />
        )}
      </main>
    </div>
  );
}
