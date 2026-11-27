import { useEffect, useRef, useState } from "react";
import { consultar } from "./servicio";
import { CambiarClaveInicial } from "./CambiarClaveInicial";
import { Dialogo } from "./componentesGestion";
import { CampoClave } from "./CampoClave";
import "./Seguridad.css";

type Datos = Record<string, any>;
export function CentroSeguridad({
  alVolver,
  alActualizar,
  alCerrar,
}: {
  alVolver: () => void;
  alActualizar: (datos: any) => void;
  alCerrar: () => void;
}) {
  const [estado, cambiarEstado] = useState<Datos | null>(null);
  const [actual, cambiarActual] = useState("");
  const [claveAdministrativa, cambiarClaveAdministrativa] = useState("");
  const [sesiones, cambiarSesiones] = useState<Datos[]>([]);
  const [eventos, cambiarEventos] = useState<Datos[]>([]);
  const [pagina, cambiarPagina] = useState(0);
  const [cursores, cambiarCursores] = useState<(number | null)[]>([null]);
  const [hayMas, cambiarHayMas] = useState(false);
  const [cargandoEventos, cambiarCargandoEventos] = useState(false);
  const consultaEventos = useRef(false);
  const [alertas, cambiarAlertas] = useState<Datos[]>([]);
  const [personas, cambiarPersonas] = useState<Datos[]>([]);
  const [persona, cambiarPersona] = useState("");
  const [mensaje, cambiarMensaje] = useState(""),
    [error, cambiarError] = useState("");
  const [ocupado, cambiarOcupado] = useState(false);
  const [cambiarClave, mostrarClave] = useState(false);
  const [temporal, cambiarTemporal] = useState<Datos | null>(null);
  const [confirmacion, cambiarConfirmacion] = useState<{
    accion: "restablecer" | "renovar";
    persona: string;
  } | null>(null);
  async function cargarPagina(indice: number, antes: number | null = null) {
    if (consultaEventos.current) return;
    consultaEventos.current = true;
    cambiarCargandoEventos(true);
    cambiarError("");
    try {
      const respuesta = await consultar(`/api/seguridad/auditoria${antes === null ? "" : `?antes=${antes}`}`);
      cambiarEventos(respuesta.eventos);
      cambiarHayMas(respuesta.hay_mas);
      cambiarPagina(indice);
      if (indice === 0) cambiarCursores([null]);
      else cambiarCursores(actuales => [...actuales.slice(0, indice), antes]);
    } catch (problema) { cambiarError((problema as Error).message); }
    finally { consultaEventos.current = false; cambiarCargandoEventos(false); }
  }
  async function cargar() {
    const datos = await consultar("/api/seguridad/estado");
    cambiarEstado(datos);
    cambiarSesiones(await consultar("/api/seguridad/sesiones"));
    if (datos.administrador) {
      await cargarPagina(0);
      cambiarAlertas(await consultar("/api/seguridad/alertas-qr"));
      cambiarPersonas((await consultar("/api/gestion/catalogo")).personas);
    }
  }
  useEffect(() => {
    void cargar().catch((e) => cambiarError(e.message));
  }, []);
  async function accion(ruta: string, cuerpo: Datos = { actual }) {
    if (ocupado) return;
    cambiarOcupado(true);
    cambiarError("");
    cambiarMensaje("");
    cambiarTemporal(null);
    try {
      const respuesta = await consultar(ruta, {
        method: "POST",
        body: JSON.stringify(cuerpo),
      });
      cambiarMensaje(respuesta.mensaje || "Operación completada.");
      cambiarActual("");
      cambiarClaveAdministrativa("");
      if (respuesta.clave_temporal) cambiarTemporal(respuesta);
      await cargar();
    } catch (e) {
      cambiarError((e as Error).message);
    } finally {
      cambiarOcupado(false);
    }
  }
  if (cambiarClave)
    return (
      <CambiarClaveInicial
        requiereActual
        alCambiar={(datos) => {
          mostrarClave(false);
          alActualizar(datos);
          void cargar();
        }}
        alCerrar={alCerrar}
      />
    );
  return (
    <>
      <main className="centro-seguridad">
        <header>
          <div>
            <h1>Seguridad de mi cuenta</h1>
            <p>Gestiona tus accesos, contraseñas y sesiones.</p>
          </div>
          <button className="secundario" onClick={alVolver}>
            Volver
          </button>
          <button className="boton-texto" onClick={alCerrar}>
            Cerrar sesión
          </button>
        </header>
        {error && (
          <p className="aviso error" role="alert">
            {error}
          </p>
        )}
        {mensaje && (
          <p className="aviso" role="status">
            {mensaje}
          </p>
        )}
        {estado && (
          <>
            <section className="panel">
              <h2>Contraseña y sesiones</h2>
              <p>Confirma tu contraseña actual para cerrar las sesiones de otros dispositivos.</p>
              <div className="formulario-seguridad">
                <div>
                  <label htmlFor="clave-seguridad">Contraseña actual</label>
                  <CampoClave id="clave-seguridad" nombre="clave-actual" etiqueta="contraseña actual" valor={actual} alCambiar={cambiarActual} autocompletar="current-password" deshabilitado={ocupado} />
                </div>
              </div>
              <div className="acciones-seguridad">
                <button onClick={() => mostrarClave(true)}>
                  Cambiar mi contraseña
                </button>
                <button
                  className="secundario"
                  disabled={ocupado || !actual}
                  onClick={() =>
                    void accion("/api/seguridad/sesiones/cerrar-otras")
                  }
                >
                  Cerrar otras sesiones
                </button>
              </div>
              <ul className="lista-sesiones">
                {sesiones.map((s) => (
                  <li key={s.id}>
                    <strong>{s.actual ? "Esta sesión" : "Otra sesión"}</strong>{" "}
                    · Inicio: {new Date(s.creada).toLocaleString("es-PE")} ·
                    Última actividad:{" "}
                    {new Date(s.actividad).toLocaleString("es-PE")}
                  </li>
                ))}
              </ul>
            </section>
            {estado.administrador && (
              <section className="panel">
                <h2>Protección de cuentas y carnets</h2>
                <label>
                  Persona
                  <select
                    value={persona}
                    onChange={(e) => {
                      cambiarPersona(e.target.value);
                      cambiarTemporal(null);
                    }}
                  >
                    <option value="">Selecciona una persona</option>
                    {personas.filter(p => p.activa).map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.nombre} · {p.codigo}
                      </option>
                    ))}
                  </select>
                </label>
                {persona && personas.find(p => String(p.id) === persona)?.nombre_usuario === estado.usuario &&
                  <p className="nota">Para restablecer tu propia cuenta, utiliza Cambiar mi contraseña. Puedes renovar tu carnet aquí.</p>}
                <p>
                  Confirma tu contraseña actual en esta sección. El restablecimiento
                  cierra las sesiones de la cuenta. Renovar el carnet invalida el
                  QR anterior inmediatamente.
                </p>
                <div className="formulario-seguridad">
                  <div>
                    <label htmlFor="clave-administrativa">Tu contraseña actual</label>
                    <CampoClave id="clave-administrativa" nombre="clave-administrativa" etiqueta="tu contraseña actual" valor={claveAdministrativa} alCambiar={cambiarClaveAdministrativa} autocompletar="current-password" deshabilitado={ocupado} />
                  </div>
                </div>
                {(!persona || !claveAdministrativa) &&
                  <p className="nota">Selecciona una persona y escribe tu contraseña actual para habilitar las acciones.</p>}
                <div className="acciones-seguridad">
                  <button
                    disabled={ocupado || !persona || !claveAdministrativa || personas.find(p => String(p.id) === persona)?.nombre_usuario === estado.usuario}
                    onClick={() => {
                      cambiarConfirmacion({ accion: "restablecer", persona });
                    }}
                  >
                    Restablecer acceso inicial
                  </button>
                  <button
                    className="secundario"
                    disabled={ocupado || !persona || !claveAdministrativa}
                    onClick={() => {
                      cambiarConfirmacion({ accion: "renovar", persona });
                    }}
                  >
                    Revocar y renovar carnet
                  </button>
                </div>
                {temporal && (
                  <aside className="aviso" role="status">
                    <strong>Entrega personal · se muestra una sola vez</strong>
                    <p>
                      Usuario: <code>{temporal.usuario}</code>
                    </p>
                    <p>
                      Contraseña temporal:{" "}
                      <code>{temporal.clave_temporal}</code>
                    </p>
                    <p>
                      Vence: {new Date(temporal.vence).toLocaleString("es-PE")}
                    </p>
                    <button onClick={() => cambiarTemporal(null)}>
                      Ya entregué el acceso
                    </button>
                  </aside>
                )}
              </section>
            )}
            {estado.administrador && (
              <section className="panel">
                <h2>Auditoría de seguridad</h2>
                {!!alertas.length && (
                  <aside className="aviso error" role="status">
                    <strong>Revisar intentos QR repetidos</strong>
                    <p>
                      Cinco o más rechazos similares durante los últimos 15
                      minutos. Son señales para revisión, no prueba de fraude.
                    </p>
                    <ul>
                      {alertas.map((a, i) => (
                        <li key={i}>
                          {a.intentos} intentos · {a.detalle}
                        </li>
                      ))}
                    </ul>
                  </aside>
                )}
                <button
                  className="boton-texto"
                  disabled={ocupado}
                  onClick={() =>
                    void cargar().catch((e) => cambiarError(e.message))
                  }
                >
                  Actualizar eventos y alertas
                </button>
                <p>Eventos recientes. No se guardan contraseñas ni QR.</p>
                <p role="status">Página {pagina + 1}{cargandoEventos ? " · Cargando eventos…" : ` · ${eventos.length} eventos`}</p>
                <ul className="lista-auditoria">
                  {eventos.map((e) => (
                    <li key={e.id}>
                      <strong>{e.accion.replaceAll("_", " ")}</strong>
                      <small>
                        {new Date(e.fecha).toLocaleString("es-PE")} · {e.responsable ? `Responsable: ${e.responsable}` : "Evento sin cuenta identificada"}
                      </small>
                      <p>{e.detalle}</p>
                    </li>
                  ))}
                </ul>
                {!eventos.length && !cargandoEventos && <p>No hay eventos en esta página.</p>}
                <nav className="paginacion-auditoria" aria-label="Páginas de auditoría">
                  <button type="button" className="secundario" disabled={cargandoEventos || pagina === 0}
                    onClick={() => void cargarPagina(pagina - 1, cursores[pagina - 1])}>Anterior</button>
                  <button type="button" className="secundario" disabled={cargandoEventos || !hayMas || !eventos.length}
                    onClick={() => void cargarPagina(pagina + 1, eventos.at(-1)!.id)}>Siguiente</button>
                </nav>
              </section>
            )}
          </>
        )}
      </main>
      {confirmacion && (
        <Dialogo
          titulo={
            confirmacion.accion === "restablecer"
              ? "Restablecer acceso inicial"
              : "Revocar y renovar carnet"
          }
          cerrar={() => cambiarConfirmacion(null)}
        >
          <div className="formulario-gestion">
            <p>
              {confirmacion.accion === "restablecer"
                ? `Se cerrarán las sesiones de ${personas.find(p => String(p.id) === confirmacion.persona)?.nombre || "esta persona"} y se generará un acceso temporal.`
                : `El carnet de ${personas.find(p => String(p.id) === confirmacion.persona)?.nombre || "esta persona"} quedará invalidado de inmediato y se emitirá uno nuevo.`}
            </p>
            <footer className="acciones-dialogo">
              <button
                type="button"
                className="secundario"
                autoFocus
                onClick={() => cambiarConfirmacion(null)}
              >
                Cancelar
              </button>
              <button
                type="button"
                disabled={ocupado}
                onClick={() => {
                  const ruta =
                    confirmacion.accion === "restablecer"
                      ? "restablecer"
                      : "renovar-carne";
                  const personaConfirmada = confirmacion.persona;
                  cambiarConfirmacion(null);
                  void accion(`/api/seguridad/personas/${personaConfirmada}/${ruta}`, { actual: claveAdministrativa });
                }}
              >
                {confirmacion.accion === "restablecer"
                  ? "Restablecer acceso"
                  : "Revocar y renovar"}
              </button>
            </footer>
          </div>
        </Dialogo>
      )}
    </>
  );
}
