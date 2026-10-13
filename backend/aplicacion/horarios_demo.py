from datetime import date, time
from sqlalchemy import select
from sqlalchemy.orm import Session
from aplicacion.database import motor
from aplicacion.models import Horario, TramoHorario, AsignacionHorario, Persona, ToleranciaRol


def preparar_horarios_demo():
    with Session(motor) as base:
        horario = base.scalar(select(Horario).where(Horario.nombre == 'DEMO - jornada 08 a 17'))
        if not horario:
            horario = Horario(nombre='DEMO - jornada 08 a 17', sede_id=1)
            base.add(horario)
            base.flush()
            for dia in range(7):
                base.add(TramoHorario(horario_id=horario.id, dia_semana=dia, hora_entrada=time(8), hora_salida=time(17)))
        for persona in base.scalars(select(Persona).where(Persona.codigo.like('DEMO-%'))):
            if not base.scalar(select(AsignacionHorario).where(AsignacionHorario.persona_id == persona.id)):
                base.add(AsignacionHorario(persona_id=persona.id, horario_id=horario.id, vigente_desde=date(2026, 10, 11)))
            if not base.scalar(select(ToleranciaRol).where(ToleranciaRol.rol_id == persona.rol_id)):
                base.add(ToleranciaRol(rol_id=persona.rol_id, minutos=10, vigente_desde=date(2026, 10, 11)))
        base.commit()
    print('Horarios ficticios preparados para las personas DEMO; no se cambiaron horarios existentes.')


if __name__ == '__main__':
    preparar_horarios_demo()
