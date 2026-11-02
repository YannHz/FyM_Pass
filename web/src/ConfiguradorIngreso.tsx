import { SelectorHora } from "./SelectorHora";
import { diasHorario, resumenHorario, type Tramo } from "./EditorHorario";

export function ConfiguradorIngreso({
  tramos,
  cambiar,
}: {
  tramos: Tramo[];
  cambiar: (valor: Tramo[]) => void;
}) {
  function alternar(dia: number) {
    cambiar(
      tramos.some((tramo) => tramo.dia_semana === dia)
        ? tramos.filter((tramo) => tramo.dia_semana !== dia)
        : [
            ...tramos,
            { dia_semana: dia, hora_entrada: "08:00", hora_salida: null },
          ].sort((a, b) => a.dia_semana - b.dia_semana),
    );
  }
  return (
    <div className="ingreso-directo">
      <div
        className="dias-configurables"
        role="group"
        aria-label="Días de ingreso"
      >
        {diasHorario.map((dia, indice) => (
          <button
            type="button"
            key={dia}
            aria-label={dia}
            aria-pressed={tramos.some((tramo) => tramo.dia_semana === indice)}
            onClick={() => alternar(indice)}
          >
            {dia.slice(0, 3)}
          </button>
        ))}
      </div>
      <div className="horas-ingreso-grupo">
        {tramos.map((tramo, indice) => (
          <div className="campo-hora" key={tramo.dia_semana}>
            <span>{diasHorario[tramo.dia_semana]}</span>
            <SelectorHora
              etiqueta={`Entrada del ${diasHorario[tramo.dia_semana]}`}
              valor={tramo.hora_entrada}
              alCambiar={(hora) =>
                cambiar(
                  tramos.map((valor, posicion) =>
                    posicion === indice
                      ? { ...valor, hora_entrada: hora, hora_salida: null }
                      : valor,
                  ),
                )
              }
            />
          </div>
        ))}
      </div>
      <p className="resumen-grupo" role="status">
        {resumenHorario(tramos)}
      </p>
    </div>
  );
}
