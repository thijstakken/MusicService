"""base

Revision ID: 62499b9f27e1
Revises: 
Create Date: 2024-05-28 21:39:45.016466

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62499b9f27e1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('cloud_storage',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('protocol_type', sa.String(length=30), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('cloud_storage', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_cloud_storage_user_id'), ['user_id'], unique=False)

    op.create_table('music',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('url', sa.String(length=200), nullable=False),
    sa.Column('monitored', sa.Boolean(), nullable=False),
    sa.Column('interval', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('music', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_music_user_id'), ['user_id'], unique=False)

    op.create_table('music_task',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('complete', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('music_task', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_music_task_name'), ['name'], unique=False)

    op.create_table('ftp_storage',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('host', sa.String(length=250), nullable=False),
    sa.Column('port', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=30), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['cloud_storage.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('webdav_storage',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(length=250), nullable=False),
    sa.Column('directory', sa.String(length=250), nullable=False),
    sa.Column('username', sa.String(length=30), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['cloud_storage.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('webdav_storage')
    op.drop_table('ftp_storage')
    with op.batch_alter_table('music_task', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_music_task_name'))

    op.drop_table('music_task')
    with op.batch_alter_table('music', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_music_user_id'))

    op.drop_table('music')
    with op.batch_alter_table('cloud_storage', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_cloud_storage_user_id'))

    op.drop_table('cloud_storage')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))

    op.drop_table('user')
    # ### end Alembic commands ###
