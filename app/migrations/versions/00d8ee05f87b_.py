"""empty message

Revision ID: 00d8ee05f87b
Revises: 
Create Date: 2018-09-28 17:10:02.691721

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00d8ee05f87b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('company',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=60), nullable=True),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.Column('address', sa.String(length=120), nullable=True),
    sa.Column('city', sa.String(length=60), nullable=True),
    sa.Column('post_code', sa.String(length=10), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_company_address'), 'company', ['address'], unique=False)
    op.create_index(op.f('ix_company_city'), 'company', ['city'], unique=False)
    op.create_table('programme',
    sa.Column('code', sa.String(length=10), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('code'),
    sa.UniqueConstraint('code')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=60), nullable=True),
    sa.Column('username', sa.String(length=60), nullable=True),
    sa.Column('first_name', sa.String(length=60), nullable=True),
    sa.Column('last_name', sa.String(length=60), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('telephone', sa.String(length=60), nullable=True),
    sa.Column('web', sa.String(length=120), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('programme_code', sa.String(length=10), nullable=True),
    sa.Column('profile_comment', sa.Text(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('is_external', sa.Boolean(), nullable=True),
    sa.Column('notify_new', sa.Boolean(), nullable=True),
    sa.Column('notify_interest', sa.Boolean(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['programme_code'], ['programme.code'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_first_name'), 'users', ['first_name'], unique=False)
    op.create_index(op.f('ix_users_last_name'), 'users', ['last_name'], unique=False)
    op.create_index(op.f('ix_users_telephone'), 'users', ['telephone'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_web'), 'users', ['web'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_web'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_telephone'), table_name='users')
    op.drop_index(op.f('ix_users_last_name'), table_name='users')
    op.drop_index(op.f('ix_users_first_name'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('programme')
    op.drop_index(op.f('ix_company_city'), table_name='company')
    op.drop_index(op.f('ix_company_address'), table_name='company')
    op.drop_table('company')
    # ### end Alembic commands ###
