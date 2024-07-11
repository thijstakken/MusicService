"""musictask actiontype

Revision ID: a6b7de1fa80b
Revises: 9b890059efab
Create Date: 2024-06-11 21:14:33.036800

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6b7de1fa80b'
down_revision = '9b890059efab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('music_task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('actiontype', sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('music_task', schema=None) as batch_op:
        batch_op.drop_column('actiontype')

    # ### end Alembic commands ###