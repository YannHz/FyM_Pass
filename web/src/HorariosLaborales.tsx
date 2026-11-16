import { useState } from "react";
import { Presentation, BriefcaseBusiness, Plus } from "lucide-react";
import "./HorariosLaborales.css";
import { ConfirmarHorario } from "./ConfirmarHorario";
import { FormularioGestion, type Formulario } from "./FormularioGestion";
import { diasHorario, resumenHorario } from "./EditorHorario";
import { Vacio, type Registro } from "./componentesGestion";

export function HorariosLaborales({ catalogo, administrador, guardado }: {
  catalogo: Registro; administrador: boolean; guardado: (mensaje: string) => void;
}) {
  const [formulario, cambiarFormulario] = useState<Formulario | null>(null);
  const [horario, cambiarHorario] = useState<Registro | null>(null);
  const [tipo, cambiarTipo] = useState("docente");
  const turnos: Record<string, string> = { manana: "Mañana", tarde: "Tarde", noche: "Noche", completo: "Jornada completa" };
  const laborales = catalogo.horarios.filter((dato: Registro) =>
    dato.activo && dato.tipo_personal === tipo && dato.tramos.length && dato.tramos.every((tramo: Registro) => tramo.hora_salida));
  function crear(copia?: Registro) {
    cambiarFormulario({
      titulo: copia ? "Configurar horario laboral" : "Crear horario laboral",
      accion: "Guardar y asignar",
      aviso: "Elige los días de trabajo y ajusta la entrada y salida. Después seleccionarás el personal y la fecha de inicio.",
      alGuardar: (respuesta, datos) => cambiarHorario({ ...datos, nombre: `${datos.tipo_personal === "docente" ? datos.carrera : "Administración"} · ${turnos[datos.turno]}`, id: respuesta.id }),
      ruta: copia ? `/api/gestion/horarios/${copia.id}` : "/api/gestion/horarios", metodo: copia ? "PUT" : "POST", requiereSalida: true,
      datos: {
        nombre: copia ? copia.nombre : "",
        tipo_personal: copia?.tipo_personal || tipo,
        carrera: copia?.carrera || "",
        turno: copia?.turno || "manana",
        tramos: copia ? copia.tramos : [0, 1, 2, 3, 4].map(dia => ({
          dia_semana: dia, hora_entrada: "08:00", hora_salida: "17:00",
        })),
      },
      campos: [
        { nombre: "carrera", etiqueta: "Carrera", requerido: true, longitudMaxima: 120,
          ayuda: "Nombre de la carrera a la que corresponde este horario.",
          visible: datos => datos.tipo_personal === "docente" },
        { nombre: "turno", etiqueta: "Turno", tipo: "select", requerido: true,
          opciones: Object.entries(turnos).map(([valor, texto]) => ({ valor, texto })) },
        { nombre: "tramos", etiqueta: "Días, entrada y salida", tipo: "horario-directo" },
      ],
      preparar: datos => ({ ...datos, carrera: datos.tipo_personal === "docente" ? datos.carrera : null,
        nombre: `${datos.tipo_personal === "docente" ? datos.carrera : "Administración"} · ${turnos[datos.turno]}`.slice(0, 100) }),
    });
  }
  return <section className="panel horarios-laborales">
    <div className="separador-personal" role="group" aria-label="Tipo de personal">
      <button className="secundario" aria-pressed={tipo === "docente"} onClick={() => cambiarTipo("docente")}>
        <Presentation size={21} /><span>Docentes<small>Por carrera y turno</small></span>
      </button>
      <button className="secundario" aria-pressed={tipo === "administrativo"} onClick={() => cambiarTipo("administrativo")}>
        <BriefcaseBusiness size={21} /><span>Personal administrativo<small>Secretarias y administradoras</small></span>
      </button>
    </div>
    <div className="cabecera"><div><h2>Horarios laborales</h2>
      <p>{tipo === "docente" ? "Organiza las carreras y turnos de los docentes." : "Organiza los turnos del personal administrativo."} Una entrada y salida general por día.</p></div>
      {administrador && <button onClick={() => crear()}><Plus size={16} />Crear horario {tipo === "docente" ? "docente" : "administrativo"}</button>}
    </div>
    <div className="tarjetas-laborales">{laborales.map((dato: Registro) =>
      <article className="horario-laboral" key={dato.id}>
        <div className="cabecera-tarjeta-horario"><span className="etiqueta">{tipo === "docente" ? "Carrera" : "Administración"}</span>
          <span className="turno-horario">{turnos[dato.turno] || dato.turno}</span></div>
        <h3>{tipo === "docente" ? dato.carrera || "Carrera por definir" : "Personal administrativo"}</h3>
        <p>{resumenHorario(dato.tramos)}</p>
        <div className="semana-laboral">{diasHorario.map((dia, i) => <span key={dia}
          data-activo={dato.tramos.some((t: Registro) => t.dia_semana === i)}>{dia.slice(0,3)}</span>)}</div>
        <details><summary>Ver personal asignado ({catalogo.personas.filter((p: Registro) => p.horario_id === dato.id).length})</summary>
          <ul>{catalogo.personas.filter((p: Registro) => p.horario_id === dato.id).map((p: Registro) =>
            <li key={p.id}>{p.nombre}<small>{p.rol}</small></li>)}</ul></details>
        {administrador && <div className="acciones">
          <button onClick={() => cambiarHorario(dato)}>Asignar personal</button>
          <button className="boton-texto" onClick={() => crear(dato)}>Configurar horario</button>
        </div>}
      </article>)}</div>
    {!laborales.length && <Vacio titulo="Crea el primer horario laboral" />}
    <p className="nota">Configura los días y las horas; después asigna el personal y confirma la fecha de inicio. El historial anterior se conserva.</p>
    {formulario && <FormularioGestion formulario={formulario}
      cerrar={() => cambiarFormulario(null)} guardado={guardado} />}
    {horario && <ConfirmarHorario horario={horario}
      personas={catalogo.personas.filter((persona: Registro) => persona.activa && persona.rol_codigo === horario.tipo_personal)}
      cerrar={() => cambiarHorario(null)} guardado={guardado} />}
  </section>;
}
