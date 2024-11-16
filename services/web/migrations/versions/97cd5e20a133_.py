"""empty message

Revision ID: 97cd5e20a133
Revises: 5b3e9874e3e1
Create Date: 2024-10-02 16:45:32.593690

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97cd5e20a133'
down_revision = '5b3e9874e3e1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('hotel', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lat', sa.FLOAT(), nullable=True))
        batch_op.add_column(sa.Column('long', sa.FLOAT(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('hotel', schema=None) as batch_op:
        batch_op.drop_column('long')
        batch_op.drop_column('lat')

    # ### end Alembic commands ###