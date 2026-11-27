"""retira grupos y carreras academicas heredados"""

from alembic import op
import sqlalchemy as sa


revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade():
    conexion = op.get_bind()
    vinculadas = conexion.scalar(sa.text("SELECT COUNT(*) FROM personas WHERE grupo_id IS NOT NULL"))
    grupos = conexion.scalar(sa.text("SELECT COUNT(*) FROM grupos"))
    carreras = conexion.scalar(sa.text("SELECT COUNT(*) FROM carreras"))
    if vinculadas or grupos or carreras:
        raise RuntimeError(
            "Hay datos academicos heredados en personas, grupos o carreras. "
            "Conserva un respaldo y revisa esos datos antes de aplicar la revision 0012."
        )
    op.drop_constraint("fk_personas_grupo", "personas", type_="foreignkey")
    op.drop_column("personas", "grupo_id")
    op.drop_table("grupos")
    op.drop_table("carreras")


def downgrade():
    op.create_table(
        "carreras",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sede_id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("codigo", sa.String(30), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["sede_id"], ["sedes.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("sede_id", "codigo", name="uq_carreras_sede_codigo"),
    )
    op.create_table(
        "grupos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("carrera_id", sa.Integer(), nullable=False),
        sa.Column("horario_id", sa.Integer()),
        sa.Column("codigo", sa.String(30), nullable=False),
        sa.Column("ciclo", sa.String(30), nullable=False),
        sa.Column("turno", sa.String(30), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["carrera_id"], ["carreras.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["horario_id"], ["horarios.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("carrera_id", "codigo", name="uq_grupos_carrera_codigo"),
    )
    op.add_column("personas", sa.Column("grupo_id", sa.Integer()))
    op.create_foreign_key(
        "fk_personas_grupo", "personas", "grupos", ["grupo_id"], ["id"], ondelete="RESTRICT"
    )
