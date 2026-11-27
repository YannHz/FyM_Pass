import { useState } from "react";
import {
  Search,
  Plus,
  Presentation,
  BriefcaseBusiness,
  ContactRound,
  Pencil,
  CreditCard,
  UserX,
  UserRoundCheck,
} from "lucide-react";
import { AvatarPersona } from "./ConfirmacionMarcado";
import { Dialogo, Insignia, Tabla, Vacio, type Registro } from "./componentesGestion";
import { SelectorFiltro } from "./SelectorFiltro";
import { consultar } from "./servicio";
import "./PersonasCarnets.css";
const normalizar = (texto: string) =>
  texto
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
const roles = [
  { codigo: "docente", nombre: "Docentes", icono: Presentation },
  {
    codigo: "administrativo",
    nombre: "Administrativos",
    icono: BriefcaseBusiness,
  },
];
export function PersonasCarnets({
  catalogo,
  administrador,
  registrar,
  editar,
  abrir,
  guardado,
  usuarioActual,
}: {
  catalogo: Registro;
  administrador: boolean;
  registrar: () => void;
  editar: (persona: Registro) => void;
  abrir: (persona: Registro, vista: string) => void;
  guardado: (mensaje: string) => void;
  usuarioActual: string;
}) {
  const [buscar, cambiarBuscar] = useState(""),
    [rol, cambiarRol] = useState(""),
    [estado, cambiarEstado] = useState(""),
    [cuenta, cambiarCuenta] = useState("");
  const [personaPendiente, cambiarPersonaPendiente] = useState<Registro | null>(null);
  const [ocupado, cambiarOcupado] = useState(false);
  const [error, cambiarError] = useState("");
  async function confirmarEstadoPersona() {
    if (!personaPendiente || ocupado) return;
    cambiarOcupado(true); cambiarError("");
    try {
      const accion = personaPendiente.activa ? "baja" : "reactivar";
      const respuesta = await consultar(`/api/gestion/personas/${personaPendiente.id}/${accion}`, { method: "POST" });
      cambiarPersonaPendiente(null);
      guardado(respuesta.mensaje);
    } catch (problema) { cambiarError((problema as Error).message); }
    finally { cambiarOcupado(false); }
  }
  const personas: Registro[] = catalogo.personas;
  const filtradas = personas
    .filter(
      (persona) =>
        (!buscar ||
          normalizar(
            `${persona.nombre} ${persona.codigo} ${persona.documento || ""} ${persona.nombre_usuario || ""}`,
          ).includes(normalizar(buscar))) &&
        (!rol || persona.rol_codigo === rol) &&
        (!estado || Boolean(persona.activa) === (estado === "activos")) &&
        (!cuenta || Boolean(persona.nombre_usuario) === (cuenta === "con")),
    )
    .sort((a, b) => a.nombre.localeCompare(b.nombre, "es"));
  function seleccionarRol(valor: string) {
    cambiarRol(valor);
  }
  function limpiar() {
    cambiarBuscar("");
    cambiarRol("");
    cambiarEstado("");
    cambiarCuenta("");
  }
  return (
    <div className="personas-carnets">
      <div className="resumen-directorio" aria-label="Personas por rol">
        <button
          className="tarjeta-rol"
          aria-pressed={!rol}
          onClick={() => seleccionarRol("")}
        >
          <ContactRound size={22} aria-hidden="true" />
          <span>
            Todas las personas<strong>{personas.length}</strong>
          </span>
        </button>
        {roles.map((dato) => (
          <button
            key={dato.codigo}
            className="tarjeta-rol"
            aria-pressed={rol === dato.codigo}
            onClick={() =>
              seleccionarRol(rol === dato.codigo ? "" : dato.codigo)
            }
          >
            <dato.icono size={22} aria-hidden="true" />
            <span>
              {dato.nombre}
              <strong>
                {
                  personas.filter(
                    (persona) => persona.rol_codigo === dato.codigo,
                  ).length
                }
              </strong>
            </span>
          </button>
        ))}
      </div>
      <section className="panel">
        <div className="cabecera">
          <div>
            <h2>Directorio institucional</h2>
            <p>
              Consulta los datos, la asignación y el carnet de cada persona.
            </p>
          </div>
          {administrador && (
            <button onClick={registrar}>
              <Plus size={17} />
              Registrar persona
            </button>
          )}
        </div>
        <div className="filtros filtros-personas">
          <label className="buscador">
            <Search size={18} />
            <input
              aria-label="Buscar persona en el directorio"
              placeholder="Nombre, ID, documento o usuario"
              value={buscar}
              onChange={(evento) => cambiarBuscar(evento.target.value)}
            />
          </label>
          <SelectorFiltro
            etiqueta="Estado de la persona"
            valor={estado}
            alCambiar={cambiarEstado}
            opciones={[
              { valor: "", texto: "Todos los estados" },
              { valor: "activos", texto: "Activos" },
              { valor: "inactivos", texto: "Desactivados" },
            ]}
          />
          <SelectorFiltro
            etiqueta="Cuenta de acceso"
            valor={cuenta}
            alCambiar={cambiarCuenta}
            opciones={[
              { valor: "", texto: "Todas las cuentas" },
              { valor: "con", texto: "Con cuenta" },
              { valor: "sin", texto: "Sin cuenta" },
            ]}
          />
        </div>
        <div className="resultados-directorio">
          <span>
            {filtradas.length} de {personas.length} personas
          </span>
          {(buscar || rol || estado || cuenta) && (
            <button className="boton-texto" onClick={limpiar}>
              Limpiar filtros
            </button>
          )}
        </div>
        {filtradas.length ? (
          <Tabla
            titulo="Personas del instituto"
            filas={filtradas}
            columnas={[
              {
                titulo: "Persona",
                mostrar: (persona) => (
                  <div className="identidad-directorio">
                    <AvatarPersona
                      persona={persona as { nombre: string; iniciales: string }}
                    />
                    <button
                      className="enlace"
                      onClick={() => abrir(persona, "calendario")}
                    >
                      {persona.nombre}
                      <small>{persona.codigo}</small>
                    </button>
                  </div>
                ),
              },
              {
                titulo: "Rol",
                mostrar: (persona) => {
                  const Icono =
                    roles.find((dato) => dato.codigo === persona.rol_codigo)
                      ?.icono || ContactRound;
                  return (
                    <span className="rol-directorio">
                      <Icono size={17} aria-hidden="true" />
                      {persona.rol}
                    </span>
                  );
                },
              },
              {
                titulo: "Asignación",
                mostrar: (persona) => {
                  const horario = catalogo.horarios.find(
                    (dato: Registro) => dato.id === persona.horario_id,
                  );
                  return horario ? (
                    horario.nombre
                  ) : (
                    <span className="nota">Sin horario asignado</span>
                  );
                },
              },
              {
                titulo: "Cuenta",
                mostrar: (persona) =>
                  persona.nombre_usuario ? (
                    <>
                      {persona.nombre_usuario}
                      <small>
                        {persona.permiso === "administrador"
                          ? "Administrador"
                          : persona.permiso === "operador"
                            ? "Operador de asistencia"
                            : "Acceso personal"}
                      </small>
                    </>
                  ) : (
                    <span className="nota">Sin cuenta de acceso</span>
                  ),
              },
              {
                titulo: "Estado",
                mostrar: (persona) => (
                  <div className="estado-directorio"><Insignia texto={persona.activa ? "Activo" : "Desactivado"} />
                    {!persona.activa && persona.baja_en && <small>Baja: {new Intl.DateTimeFormat("es-PE", { timeZone: "America/Lima", dateStyle: "short", timeStyle: "short" }).format(new Date(persona.baja_en))}<br />Por {persona.baja_por}</small>}
                  </div>
                ),
              },
              {
                titulo: "Acciones",
                mostrar: (persona) => (
                  <div className="acciones-fila">
                    <button
                      className="boton-texto"
                      onClick={() => abrir(persona, "carne")}
                      aria-label={`Ver carnet de ${persona.nombre}`}
                    >
                      <CreditCard size={16} />
                      Carnet
                    </button>
                    {administrador && (
                      <><button
                        className="boton-texto"
                        onClick={() => editar(persona)}
                        aria-label={`Editar a ${persona.nombre}`}
                      >
                        <Pencil size={15} />
                        Editar
                      </button>
                      {persona.nombre_usuario !== usuarioActual && <button className="boton-texto accion-baja-persona" onClick={() => { cambiarError(""); cambiarPersonaPendiente(persona); }}>
                        {persona.activa ? <UserX size={16} aria-hidden="true" /> : <UserRoundCheck size={16} aria-hidden="true" />}
                        {persona.activa ? "Dar de baja" : "Reactivar"}
                      </button>}</>
                    )}
                  </div>
                ),
              },
            ]}
          />
        ) : (
          <Vacio
            titulo="No hay personas con estos filtros."
            detalle="Prueba otro nombre, ID o estado, o limpia los filtros para volver al directorio."
          />
        )}
        <p className="nota">
          Pulsa el nombre para abrir el expediente. Los cambios de horario se
          confirman en Horarios laborales.
        </p>
      </section>
      {personaPendiente && <Dialogo titulo={personaPendiente.activa ? "Dar de baja a una persona" : "Reactivar a una persona"} cerrar={() => cambiarPersonaPendiente(null)} bloqueado={ocupado}>
        <div className="formulario-gestion">
          <p><strong>{personaPendiente.nombre}</strong> · {personaPendiente.codigo}</p>
          <p>{personaPendiente.activa ? "Se cerrarán sus sesiones y se desactivará su acceso de inmediato. Perderá el horario asignado desde mañana. Sus asistencias y justificaciones anteriores permanecerán en los reportes. Se registrarán la fecha y el administrador responsable." : "La cuenta volverá a estar activa. El horario retirado no se recupera automáticamente; asígnale uno desde Horarios laborales si corresponde."}</p>
          {error && <p role="alert" className="aviso error">{error}</p>}
          <footer className="acciones-dialogo">
            <button type="button" className="secundario" autoFocus disabled={ocupado} onClick={() => cambiarPersonaPendiente(null)}>Cancelar</button>
            <button type="button" disabled={ocupado} onClick={() => void confirmarEstadoPersona()}>{ocupado ? "Guardando…" : personaPendiente.activa ? "Confirmar baja" : "Reactivar persona"}</button>
          </footer>
        </div>
      </Dialogo>}
    </div>
  );
}
