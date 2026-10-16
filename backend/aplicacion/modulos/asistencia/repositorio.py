from datetime import timedelta
from sqlalchemy import select, update
from ...models import (
    Persona,
    ToleranciaRol,
    PuntoAsistencia,
    Marcado,
    PuestoAbierto,
    EventoPuesto,
)
from ...seguridad import resumir_token
from ...compartido.repositorio import RepositorioBase


class RepositorioAsistencia(RepositorioBase):

    def puesto_por_token(self, token):
        return self._base.scalar(
            select(PuestoAbierto).where(
                PuestoAbierto.token_hash == resumir_token(token)
            )
        )

    def primer_punto_de_sede(self, persona):
        return self._base.scalar(
            select(PuntoAsistencia)
            .where(PuntoAsistencia.sede_id == persona.sede_id)
            .order_by(PuntoAsistencia.id)
        )

    def puesto_abierto(self, hora_consulta, punto):
        return self._base.scalar(
            select(PuestoAbierto).where(
                PuestoAbierto.punto_id == punto.id,
                PuestoAbierto.activo.is_(True),
                PuestoAbierto.vence_en > hora_consulta,
            )
        )

    def bloquear_punto(self, punto):
        return self._base.execute(
            select(PuntoAsistencia)
            .where(PuntoAsistencia.id == punto.id)
            .with_for_update()
        ).scalar_one()

    def desactivar_puestos(self, punto):
        return self._base.execute(
            update(PuestoAbierto)
            .where(PuestoAbierto.punto_id == punto.id)
            .values(activo=False)
        )

    def eventos_recientes(self, despues, hora_consulta, puesto):
        return self._base.scalars(
            select(EventoPuesto)
            .where(
                EventoPuesto.puesto_id == puesto.id,
                EventoPuesto.id > despues,
                EventoPuesto.ocurrido_en > hora_consulta - timedelta(minutes=2),
            )
            .order_by(EventoPuesto.id)
            .limit(20)
        ).all()

    def tolerancia_vigente(self, local, persona):
        return self._base.scalar(
            select(ToleranciaRol)
            .where(
                ToleranciaRol.rol_id == persona.rol_id,
                ToleranciaRol.vigente_desde <= local.date(),
                ToleranciaRol.vigente_hasta.is_(None)
                | (ToleranciaRol.vigente_hasta >= local.date()),
            )
            .order_by(ToleranciaRol.vigente_desde.desc())
        )

    def bloquear_puesto(self, puesto):
        return self._base.scalar(
            select(PuestoAbierto)
            .where(PuestoAbierto.id == puesto.id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )

    def evento_por_identificador(self, datos):
        return self._base.scalar(
            select(EventoPuesto).where(
                EventoPuesto.identificador_evento == str(datos.identificador_evento)
            )
        )

    def bloquear_persona(self, persona):
        return self._base.scalar(
            select(Persona)
            .where(Persona.id == persona.id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )

    def ultimo_marcado_del_dia(self, inicio, persona):
        return self._base.scalar(
            select(Marcado)
            .where(
                Marcado.persona_id == persona.id,
                Marcado.ocurrido_en >= inicio,
                Marcado.ocurrido_en < inicio + timedelta(days=1),
            )
            .order_by(Marcado.ocurrido_en.desc(), Marcado.id.desc())
        )

    def evento_del_marcado(self, ultimo):
        return self._base.scalar(
            select(EventoPuesto).where(EventoPuesto.marcado_id == ultimo.id)
        )

    def ultimos_marcados_de_sede(self, persona):
        return self._base.execute(
            select(Marcado, Persona, EventoPuesto.resultado)
            .join(Persona, Marcado.persona_id == Persona.id)
            .join(PuntoAsistencia, Marcado.punto_id == PuntoAsistencia.id)
            .outerjoin(EventoPuesto, EventoPuesto.marcado_id == Marcado.id)
            .where(PuntoAsistencia.sede_id == persona.sede_id)
            .order_by(Marcado.id.desc())
            .limit(30)
        ).all()
