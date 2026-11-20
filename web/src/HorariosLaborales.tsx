import { useState } from "react";
import { Presentation, BriefcaseBusiness } from "lucide-react";
import { type Registro } from "./componentesGestion";
import { SemanaLaboral } from "./SemanaLaboral";
import "./HorariosLaborales.css";

export function HorariosLaborales({ catalogo, administrador, guardado }: {
  catalogo: Registro; administrador: boolean; guardado: (mensaje: string) => void;
}) {
  const [tipo, cambiarTipo] = useState("docente");
  const [pendiente, cambiarPendiente] = useState(false);
  function elegirTipo(valor: string) {
    if (valor === tipo) return;
    if (pendiente && !window.confirm("Hay cambios sin guardar. ¿Quieres descartarlos?")) return;
    cambiarPendiente(false);
    cambiarTipo(valor);
  }
  return <section className="panel horarios-laborales">
    <div className="separador-personal" role="group" aria-label="Tipo de personal">
      <button className="secundario" aria-pressed={tipo === "docente"} onClick={() => elegirTipo("docente")}>
        <Presentation size={20} />Docentes
      </button>
      <button className="secundario" aria-pressed={tipo === "administrativo"} onClick={() => elegirTipo("administrativo")}>
        <BriefcaseBusiness size={20} />Personal administrativo
      </button>
    </div>
    <SemanaLaboral key={tipo} tipo={tipo} catalogo={catalogo} administrador={administrador}
      guardado={guardado} alModificar={cambiarPendiente} />
  </section>;
}
