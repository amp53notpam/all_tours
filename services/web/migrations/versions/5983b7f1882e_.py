"""empty message

Revision ID: 5983b7f1882e
Revises: 256a0a031bfb
Create Date: 2024-11-30 20:17:00.708373

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5983b7f1882e'
down_revision = '256a0a031bfb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('trip_image', schema=None) as batch_op:
        batch_op.add_column(sa.Column('img_width', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('img_height', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('img_type', sa.Enum('video', 'image', name='media_enum'), nullable=True))
    op.execute("UPDATE trip_image SET img_width = 1024")
    op.execute("UPDATE trip_image SET img_height= 683")
    op.execute("UPDATE trip_image SET img_type = 'image'")
    op.alter_column('trip_image', 'img_width', nullable=False)
    op.alter_column('trip_image', 'img_height', nullable=False)
    op.alter_column('trip_image', 'img_type', nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('trip_image', schema=None) as batch_op:
        batch_op.drop_column('img_type')
        batch_op.drop_column('img_height')
        batch_op.drop_column('img_width')

    # ### end Alembic commands ###