"""empty message

Revision ID: 7816c4e323a2
Revises: 48a0a31dc646
Create Date: 2024-11-19 22:56:48.476845

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7816c4e323a2'
down_revision = '48a0a31dc646'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('trip_image', schema=None) as batch_op:
        batch_op.alter_column('date',
                              existing_type=sa.DATE(),
                              type_=sa.TIMESTAMP(),
                              existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('trip_image', schema=None) as batch_op:
        batch_op.alter_column('date',
                              existing_type=sa.TIMESTAMP(),
                              type_=sa.DATE(),
                              existing_nullable=False)

    # ### end Alembic commands ###
