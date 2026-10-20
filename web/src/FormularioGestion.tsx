import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Dialogo, type Registro } from './componentesGestion';
import { consultar, ErrorSolicitud } from './servicio';
export type Campo = {
    nombre: string;
    etiqueta: string;
    tipo?: string;
    opciones?: {
        valor: string | number;
        texto: string;
    }[];
    requerido?: boolean;
    numerico?: boolean;
    ayuda?: string;
    minimo?: number;
    maximo?: number;
    paso?: number;
    longitudMinima?: number;
    longitudMaxima?: number;
    patron?: string;
    avanzado?: boolean;
    visible?: (datos: Registro) => boolean;
};
export type Formulario = {
    titulo: string;
    ruta: string;
    accion?: string;
    campos: Campo[];
    datos: Registro;
    preparar?: (datos: Registro) => Registro;
};
type Tramo = {
    dia_semana: number;
    hora_entrada: string;
    hora_salida: string | null;
};
const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
function EditorTramos({ tramos, cambiar }: {
    tramos: Tramo[];
    cambiar: (tramos: Tramo[]) => void;
}) {
    function editar(indice: number, valores: Partial<Tramo>) { cambiar(tramos.map((tramo, actual) => actual === indice ? { ...tramo, ...valores } : tramo)); }
    return <div className="editor-tramos">{tramos.map((tramo, indice) => <fieldset className="fila-tramo" key={indice}><legend>Tramo {indice + 1}</legend><label>Día<select value={tramo.dia_semana} onChange={evento => editar(indice, { dia_semana: Number(evento.target.value) })}>{dias.map((dia, valor) => <option key={dia} value={valor}>{dia}</option>)}</select></label><label>Entrada<input type="time" required value={tramo.hora_entrada} onChange={evento => editar(indice, { hora_entrada: evento.target.value })}/></label><label>Salida opcional<input type="time" value={tramo.hora_salida || ''} onChange={evento => editar(indice, { hora_salida: evento.target.value || null })}/></label><button type="button" className="boton-texto" aria-label={`Quitar tramo ${indice + 1}`} onClick={() => cambiar(tramos.filter((_, actual) => actual !== indice))}>Quitar</button></fieldset>)}<button type="button" className="secundario" disabled={tramos.length >= 14} onClick={() => cambiar([...tramos, { dia_semana: 0, hora_entrada: '08:00', hora_salida: null }])}>Añadir tramo</button><small>Deja la salida vacía cuando solo se registra ingreso.</small></div>;
}
export function FormularioGestion({ formulario, cerrar, guardado }: {
    formulario: Formulario;
    cerrar: () => void;
    guardado: (mensaje: string) => void;
}) {
    const [datos, establecerDatos] = useState<Registro>({ ...formulario.datos });
    const [errores, establecerErrores] = useState<Record<string, string>>({});
    const [error, establecerError] = useState(''), [ocupado, establecerOcupado] = useState(false);
    useEffect(() => {
        const renovar = () => establecerError('');
        window.addEventListener('fym-sesion-renovada', renovar);
        return () => window.removeEventListener('fym-sesion-renovada', renovar);
    }, []);
    const referencia = useRef<HTMLFormElement>(null);
    const visibles = formulario.campos.filter(campo => !campo.visible || campo.visible(datos));
    function cambiar(campo: Campo, valor: unknown) { establecerDatos(anterior => ({ ...anterior, [campo.nombre]: campo.numerico && valor !== '' ? Number(valor) : valor })); establecerErrores(anterior => ({ ...anterior, [campo.nombre]: '' })); }
    function errorCampo(nombre: string) { return errores[nombre] || Object.entries(errores).find(([clave]) => clave.startsWith(nombre + '.'))?.[1]; }
    async function guardar(evento: FormEvent) {
        evento.preventDefault();
        if (ocupado)
            return;
        const fallos: Record<string, string> = {};
        if (datos.nombre_usuario && !datos.id && !datos.clave)
            fallos.clave = 'Introduce la contraseña para crear la cuenta.';
        if (datos.clave && !datos.nombre_usuario && formulario.ruta.endsWith('/personas'))
            fallos.nombre_usuario = 'Introduce el usuario de esta cuenta.';
        if (Array.isArray(datos.tramos)) {
            if (!datos.tramos.length)
                fallos.tramos = 'Añade al menos un tramo.';
            const repetidos = new Set<string>();
            for (const tramo of datos.tramos as Tramo[]) {
                const clave = `${tramo.dia_semana}-${tramo.hora_entrada}`;
                if (repetidos.has(clave))
                    fallos.tramos = 'No repitas la misma entrada en un día.';
                repetidos.add(clave);
                if (tramo.hora_salida && tramo.hora_salida <= tramo.hora_entrada)
                    fallos.tramos = 'Cada salida debe ser posterior a su entrada.';
            }
        }
        if ('alerta_porcentaje' in datos && Number(datos.alerta_porcentaje) <= Number(datos.observacion_porcentaje))
            fallos.alerta_porcentaje = 'La alerta debe superar el porcentaje de observación.';
        establecerErrores(fallos);
        if (Object.keys(fallos).length) {
            establecerError('Revisa los campos indicados.');
            return;
        }
        establecerOcupado(true);
        establecerError('');
        try {
            const salida = formulario.preparar ? formulario.preparar(datos) : datos;
            const respuesta = await consultar(formulario.ruta, { method: 'POST', body: JSON.stringify(salida) });
            guardado(respuesta.mensaje || 'Cambios guardados.');
            cerrar();
        }
        catch (problema) {
            establecerError((problema as Error).message);
            if (problema instanceof ErrorSolicitud) {
                establecerErrores(problema.campos);
                const primero = Object.keys(problema.campos)[0]?.split('.')[0];
                referencia.current?.querySelector<HTMLElement>(`[name="${primero}"]`)?.focus();
            }
        }
        finally {
            establecerOcupado(false);
        }
    }
    function presentar(campo: Campo) {
        const identificador = `campo-${campo.nombre}`, aviso = errorCampo(campo.nombre);
        const descripcion = [campo.ayuda ? `${identificador}-ayuda` : '', aviso ? `${identificador}-error` : ''].filter(Boolean).join(' ') || undefined;
        const maximos: Record<string, number> = { codigo: 30, nombres: 100, apellidos: 100, documento: 20, nombre: formulario.ruta.endsWith('/carreras') ? 120 : 100, ciclo: 30, turno: 30, referencia: 200, motivo: formulario.ruta.endsWith('/justificaciones') ? 1000 : formulario.ruta.endsWith('/dias-no-lectivos') ? 200 : 500, observacion: 500, modelo: 80 };
        const comunes = { id: identificador, name: campo.nombre, required: campo.requerido, 'aria-describedby': descripcion, 'aria-invalid': Boolean(aviso) };
        return <div className={`campo ${['textarea', 'dias', 'tramos'].includes(campo.tipo || '') ? 'ancho' : ''}`} key={campo.nombre}>
      {campo.tipo === 'booleano' ? <label className="opcion"><input type="checkbox" checked={Boolean(datos[campo.nombre])} onChange={evento => cambiar(campo, evento.target.checked)}/>{campo.etiqueta}</label> : campo.tipo === 'tramos' ? <fieldset aria-describedby={descripcion}><legend>{campo.etiqueta}</legend><EditorTramos tramos={datos[campo.nombre] || []} cambiar={valor => cambiar(campo, valor)}/></fieldset> : <><label htmlFor={identificador}>{campo.etiqueta}{campo.requerido && <span aria-hidden="true"> *</span>}</label>{campo.tipo === 'select' ? <select {...comunes} value={datos[campo.nombre] ?? ''} onChange={evento => cambiar(campo, evento.target.value)}>{campo.opciones?.map(opcion => <option key={opcion.valor} value={opcion.valor}>{opcion.texto}</option>)}</select> : campo.tipo === 'textarea' ? <textarea {...comunes} value={datos[campo.nombre] ?? ''} rows={3} minLength={3} maxLength={campo.longitudMaxima ?? maximos[campo.nombre]} onChange={evento => cambiar(campo, evento.target.value)}/> : <input {...comunes} type={campo.tipo || 'text'} value={datos[campo.nombre] ?? ''} min={campo.minimo} max={campo.maximo ?? (campo.nombre.includes('minutos') || campo.nombre.startsWith('rol_') ? 1440 : undefined)} step={campo.tipo === 'number' ? campo.paso ?? 1 : undefined} minLength={campo.longitudMinima} maxLength={campo.longitudMaxima ?? maximos[campo.nombre]} pattern={campo.patron} onChange={evento => cambiar(campo, evento.target.value)} autoComplete={campo.tipo === 'password' ? 'new-password' : undefined}/>}</>}
      {campo.ayuda && <small id={`${identificador}-ayuda`}>{campo.ayuda}</small>}{aviso && <small className="error-campo" id={`${identificador}-error`}>{aviso}</small>}
    </div>;
    }
    return <Dialogo titulo={formulario.titulo} cerrar={cerrar} bloqueado={ocupado}><form ref={referencia} onSubmit={guardar} className="formulario-gestion" aria-busy={ocupado}><fieldset disabled={ocupado}><div className="campos-formulario">{visibles.filter(campo => !campo.avanzado).map(presentar)}</div>{visibles.some(campo => campo.avanzado) && <details className="configuracion-avanzada"><summary>Configuración avanzada</summary>{visibles.filter(campo => campo.avanzado).map(presentar)}</details>}</fieldset>{error && <div className="aviso error" role="alert">{error}</div>}<footer className="acciones-dialogo"><button type="button" className="secundario" onClick={cerrar} disabled={ocupado}>Cancelar</button><button disabled={ocupado}>{ocupado ? 'Guardando…' : formulario.accion || (datos.id ? 'Guardar cambios' : 'Registrar')}</button></footer></form></Dialogo>;
}
