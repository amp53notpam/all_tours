"""empty message

Revision ID: bfcce9ee0cd7
Revises: ef6b71e9db83
Create Date: 2025-02-28 21:34:26.128493

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bfcce9ee0cd7'
down_revision = 'ef6b71e9db83'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('hotel', schema=None) as batch_op:
        batch_op.alter_column('email',
                              existing_type=sa.VARCHAR(length=32),
                              type_=sa.String(length=48),
                              existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('hotel', schema=None) as batch_op:
        batch_op.alter_column('email',
                              existing_type=sa.String(length=48),
                              type_=sa.VARCHAR(length=32),
                              existing_nullable=True)

    # ### end Alembic commands ###
