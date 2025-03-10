"""empty message

Revision ID: 240f75ba2413
Revises: ce198d01290b
Create Date: 2024-10-28 14:23:33.894338

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '240f75ba2413'
down_revision = 'ce198d01290b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test')
    with op.batch_alter_table('tour', schema=None) as batch_op:
        batch_op.add_column(sa.Column('trip_mode', sa.Enum('walking', 'bicycling', 'driving', name='mode_enum'), nullable=False, server_default="walking"))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tour', schema=None) as batch_op:
        batch_op.drop_column('trip_mode')

    op.create_table('test',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('trip_mode', postgresql.ENUM('walking', 'bicycling', 'driving', name='mode_enum'), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('id', name='test_pkey')
                    )
    # ### end Alembic commands ###
