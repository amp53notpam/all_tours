"""empty message

Revision ID: 77a425786717
Revises: 42fe61492035
Create Date: 2025-02-11 10:11:02.223725

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '77a425786717'
down_revision = '42fe61492035'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('media', schema=None) as batch_op:
        batch_op.drop_constraint('media_lap_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'lap', ['lap_id'], ['id'], ondelete='cascade')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('media', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('media_lap_id_fkey', 'lap', ['lap_id'], ['id'], ondelete='SET NULL')

    # ### end Alembic commands ###
