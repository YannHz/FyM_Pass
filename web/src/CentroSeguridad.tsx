import { useEffect, useState, type FormEvent } from "react";
import { QRCodeSVG } from "qrcode.react";
import { consultar } from "./servicio";
import { CambiarClaveInicial } from "./CambiarClaveInicial";
import "./Seguridad.css";

type Datos = Record<string, any>;
export function CentroSeguridad({ obligatorio = false, alVolver, alActualizar, alCerrar }: {
  obligatorio?: boolean; alVolver: () => void; alActualizar: (datos: any) => void; alCerrar: () => void;
}) {
  const [estado, cambiarEstado] = useState<Datos | null>(null);
  const [actual, cambiarActual] = useState(""), [codigo, cambiarCodigo] = useState("");
  const [preparacion, cambiarPreparacion] = useState<Datos | null>(null);
  const [codigos, cambiarCodigos] = useState<string[]>([]);
  const [sesiones, cambiarSesiones] = useState<Datos[]>([]);
  const [eventos, cambiarEventos] = useState<Datos[]>([]);
  const [alertas, cambiarAlertas] = useState<Datos[]>([]);
  const [personas, cambiarPersonas] = useState<Datos[]>([]);
  const [persona, cambiarPersona] = useState("");
  const [mensaje, cambiarMensaje] = useState(""), [error, cambiarError] = useState("");
  const [ocupado, cambiarOcupado] = useState(false);
  const [cambiarClave, mostrarClave] = useState(false);
  const [temporal, cambiarTemporal] = useState<Datos | null>(null);
  async function cargar() {
    if (obligatorio) { cambiarEstado({ mfa_activo: false }); return; }
    const datos = await consultar("/api/seguridad/estado");
    cambiarEstado(datos);
    cambiarSesiones(await consultar("/api/seguridad/sesiones"));
    if (datos.administrador) {
      cambiarEventos(await consultar("/api/seguridad/auditoria"));
      cambiarAlertas(await consultar("/api/seguridad/alertas-qr"));
      cambiarPersonas((await consultar("/api/gestion/catalogo")).personas);
    }
  }
  useEffect(() => { void cargar().catch(e => cambiarError(e.message)); }, []);
  async function accion(ruta: string, cuerpo: Datos = { actual, codigo }) {
    if (ocupado) return;
    cambiarOcupado(true); cambiarError(""); cambiarMensaje(""); cambiarTemporal(null);
    try {
      const respuesta = await consultar(ruta, { method: "POST", body: JSON.stringify(cuerpo) });
      cambiarMensaje(respuesta.mensaje || "Operación completada.");
      cambiarActual(""); cambiarCodigo("");
      if (respuesta.uri) cambiarPreparacion(respuesta);
      if (respuesta.codigos) { cambiarCodigos(respuesta.codigos); cambiarPreparacion(null); }
      if (respuesta.clave_temporal) cambiarTemporal(respuesta);
      if (!obligatorio) await cargar();
    } catch (e) { cambiarError((e as Error).message); }
    finally { cambiarOcupado(false); }
  }
  function preparar(evento: FormEvent) { evento.preventDefault(); void accion("/api/seguridad/mfa/preparar"); }
  if (cambiarClave) return <CambiarClaveInicial requiereActual alCambiar={datos => {
    mostrarClave(false); alActualizar(datos); void cargar();
  }} alCerrar={alCerrar} />;
  return <main className="centro-seguridad">
    <header><div><h1>{obligatorio ? "Protege tu cuenta administradora" : "Seguridad de mi cuenta"}</h1>
      <p>{obligatorio ? "Activa la verificación en dos pasos para acceder al panel." : "Gestiona tus accesos, contraseñas y sesiones."}</p></div>
      {!obligatorio && <button className="secundario" onClick={alVolver}>Volver</button>}
      <button className="boton-texto" onClick={alCerrar}>Cerrar sesión</button></header>
    {error && <p className="aviso error" role="alert">{error}</p>}
    {mensaje && <p className="aviso" role="status">{mensaje}</p>}
    {!!codigos.length && <section className="panel">
      <h2>Guarda tus códigos de recuperación</h2><p>Cada código sirve una sola vez si pierdes acceso al autenticador. Se muestran únicamente ahora. Guárdalos en un lugar privado, separado de tu contraseña.</p>
      <ul className="codigos-recuperacion">{codigos.map(c => <li key={c}><code>{c}</code></li>)}</ul>
      <button onClick={async () => {
        cambiarCodigos([]); alActualizar(await consultar("/api/acceso/actual"));
        if (obligatorio) alVolver();
      }}>He guardado mis códigos</button>
    </section>}
    {estado && !codigos.length && <section className="panel">
      <h2>Verificación en dos pasos</h2>
      <p>{estado.mfa_activo ? "Activa. Al ingresar usa el código de tu aplicación autenticadora o un código de recuperación." :
        "Usa una aplicación autenticadora compatible con TOTP, como Google Authenticator o Microsoft Authenticator."}</p>
      {!estado.mfa_activo && !preparacion && <form onSubmit={preparar} className="formulario-seguridad">
        <label>Contraseña actual<input type="password" autoComplete="current-password" value={actual} required maxLength={256} onChange={e => cambiarActual(e.target.value)} /></label>
        <button disabled={ocupado}>{ocupado ? "Preparando…" : "Configurar autenticador"}</button>
      </form>}
      {preparacion && <form className="formulario-seguridad" onSubmit={e => {
        e.preventDefault(); void accion("/api/seguridad/mfa/confirmar", { codigo });
      }}>
        <p>Escanea el QR con tu autenticador. La configuración vence en 10 minutos.</p>
        <div className="qr-configuracion"><QRCodeSVG value={preparacion.uri} size={200} /></div>
        <details><summary>Introducir clave manualmente</summary><code className="secreto-mfa">{preparacion.secreto}</code></details>
        <label>Código de 6 dígitos<input autoComplete="one-time-code" inputMode="numeric" pattern="[0-9]{6}" required value={codigo} maxLength={6} onChange={e => cambiarCodigo(e.target.value)} /></label>
        <button disabled={ocupado}>Verificar y activar</button>
      </form>}
    </section>}
    {!obligatorio && estado && <>
      <section className="panel"><h2>Contraseña y sesiones</h2>
        <p>Para operaciones sensibles confirma tu contraseña y, si está activo, el segundo factor. Usa un código nuevo para cada operación.</p>
        <div className="formulario-seguridad">
          <label>Contraseña actual<input type="password" autoComplete="current-password" value={actual} maxLength={256} onChange={e => cambiarActual(e.target.value)} /></label>
          <label>Código del autenticador o de recuperación<input autoComplete="one-time-code" value={codigo} maxLength={80} onChange={e => cambiarCodigo(e.target.value)} /></label>
        </div>
        <div className="acciones-seguridad"><button onClick={() => mostrarClave(true)}>Cambiar mi contraseña</button>
          <button className="secundario" disabled={ocupado || !actual} onClick={() => void accion("/api/seguridad/sesiones/cerrar-otras")}>Cerrar otras sesiones</button>
          {estado.mfa_activo && <button className="secundario" disabled={ocupado || !actual || !codigo} onClick={() => void accion("/api/seguridad/mfa/recuperacion")}>Renovar códigos de recuperación</button>}</div>
        <ul className="lista-sesiones">{sesiones.map(s => <li key={s.id}>
          <strong>{s.actual ? "Esta sesión" : "Otra sesión"}</strong> · Inicio: {new Date(s.creada).toLocaleString("es-PE")} · Última actividad: {new Date(s.actividad).toLocaleString("es-PE")}</li>)}</ul>
      </section>
      {estado.administrador && <section className="panel">
        <h2>Protección de cuentas y carnés</h2>
        <label>Persona<select value={persona} onChange={e => { cambiarPersona(e.target.value); cambiarTemporal(null); }}>
          <option value="">Selecciona una persona</option>{personas.map(p => <option key={p.id} value={p.id}>{p.nombre} · {p.codigo}</option>)}</select></label>
        <p>Usa la contraseña y el código de verificación indicados arriba. El restablecimiento cierra sesiones y conserva el segundo factor. Renovar el carné invalida el QR anterior inmediatamente.</p>
        <div className="acciones-seguridad">
          <button disabled={ocupado || !persona || !actual || !codigo} onClick={() => {
            if (window.confirm("¿Restablecer el acceso? Las sesiones de esta persona se cerrarán.")) void accion(`/api/seguridad/personas/${persona}/restablecer`);
          }}>Generar acceso temporal</button>
          <button className="secundario" disabled={ocupado || !persona || !actual || !codigo} onClick={() => {
            if (window.confirm("¿Revocar el carné anterior y emitir uno nuevo?")) void accion(`/api/seguridad/personas/${persona}/renovar-carne`);
          }}>Revocar y renovar carné</button>
        </div>
        {temporal && <aside className="aviso" role="status"><strong>Entrega personal · se muestra una sola vez</strong>
          <p>Usuario: <code>{temporal.usuario}</code></p><p>Contraseña temporal: <code>{temporal.clave_temporal}</code></p>
          <p>Vence: {new Date(temporal.vence).toLocaleString("es-PE")}</p><button onClick={() => cambiarTemporal(null)}>Ya entregué el acceso</button></aside>}
      </section>}
      {estado.administrador && <section className="panel"><h2>Auditoría de seguridad</h2>
        {!!alertas.length && <aside className="aviso error" role="status"><strong>Revisar intentos QR repetidos</strong>
          <p>Cinco o más rechazos similares durante los últimos 15 minutos. Son señales para revisión, no prueba de fraude.</p>
          <ul>{alertas.map((a,i) => <li key={i}>{a.intentos} intentos · {a.detalle}</li>)}</ul></aside>}
        <button className="boton-texto" disabled={ocupado} onClick={() => void cargar().catch(e => cambiarError(e.message))}>Actualizar eventos y alertas</button>
        <p>Eventos recientes. No se guardan contraseñas, códigos de verificación ni QR.</p>
        <ul className="lista-auditoria">{eventos.map(e => <li key={e.id}><strong>{e.accion.replaceAll("_", " ")}</strong>
          <small>{new Date(e.fecha).toLocaleString("es-PE")} · Cuenta {e.usuario_id || "no identificada"}</small><p>{e.detalle}</p></li>)}</ul>
        {eventos.length >= 50 && <button className="secundario" onClick={async () => {
          const mas = await consultar(`/api/seguridad/auditoria?antes=${eventos.at(-1)?.id}`); cambiarEventos([...eventos, ...mas]);
        }}>Cargar eventos anteriores</button>}
      </section>}
    </>}
  </main>;
}
