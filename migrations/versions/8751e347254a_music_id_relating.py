"""music_id relating

Revision ID: 8751e347254a
Revises: 62499b9f27e1
Create Date: 2024-06-05 21:06:42.837751

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8751e347254a'
down_revision = '62499b9f27e1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('music_task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('music_id', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('music_task', schema=None) as batch_op:
        batch_op.drop_column('music_id')

    # ### end Alembic commands ###