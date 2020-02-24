"""empty message

Revision ID: 8202d002b28f
Revises: d1998f22f25f
Create Date: 2018-10-09 08:08:04.288034

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8202d002b28f'
down_revision = 'd1998f22f25f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company', sa.Column('created_by', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'company', 'users', ['created_by'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'company', type_='foreignkey')
    op.drop_column('company', 'created_by')
    # ### end Alembic commands ###
