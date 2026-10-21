from .reporte_asistencia import construir_reporte_asistencia
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill


def construir_excel(filas, tipo, detalle=None, desde=None, hasta=None, filtros=""):
    if tipo == "asistencia":
        return construir_reporte_asistencia(filas, desde, hasta, filtros)
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Preplanilla estimada" if tipo == "preplanilla" else "Asistencia"
    columnas = list(filas[0]) if filas else ["nombre", "fecha", "estado"]
    hoja.append([columna.replace("_", " ").capitalize() for columna in columnas])
    for fila in filas:
        valores = []
        for columna in columnas:
            valor = fila.get(columna)
            if isinstance(valor, str) and valor.startswith(
                ("=", "+", "-", "@", "\t", "\r")
            ):
                valor = "'" + valor
            valores.append(valor)
        hoja.append(valores)
    for celda in hoja[1]:
        celda.font = Font(color="FFFFFF", bold=True)
        celda.fill = PatternFill("solid", fgColor="0B3C68")
    for columna in hoja.columns:
        hoja.column_dimensions[columna[0].column_letter].width = min(
            42, max(16, max((len(str(celda.value or "")) for celda in columna)) + 2)
        )
    hoja.freeze_panes = "A2"
    hoja.auto_filter.ref = hoja.dimensions
    if detalle is not None:
        diaria = libro.create_sheet("Detalle diario")
        campos = ["nombre", "codigo", "fecha", "entrada", "salida", "estado", "minutos_tardanza", "horas_programadas", "horas_permanencia"]
        diaria.append([campo.replace("_", " ").capitalize() for campo in campos])
        for fila in detalle:
            valores = []
            for campo in campos:
                valor = fila.get(campo)
                if isinstance(valor, str) and valor.startswith(("=", "+", "-", "@", "\t", "\r")):
                    valor = "'" + valor
                valores.append(valor)
            diaria.append(valores)
        for celda in diaria[1]:
            celda.font = Font(color="FFFFFF", bold=True)
            celda.fill = PatternFill("solid", fgColor="0B3C68")
        for columna in diaria.columns:
            diaria.column_dimensions[columna[0].column_letter].width = 24
        diaria.freeze_panes = "A2"
        diaria.auto_filter.ref = diaria.dimensions
    archivo = BytesIO()
    libro.save(archivo)
    archivo.seek(0)
    return archivo
