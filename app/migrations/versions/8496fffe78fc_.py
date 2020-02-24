"""empty message

Revision ID: 8496fffe78fc
Revises: 67a39b381c32
Create Date: 2018-10-04 19:26:51.770414

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8496fffe78fc'
down_revision = '67a39b381c32'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('settings', sa.Column('contact_email', sa.String(length=60), nullable=True))
    op.add_column('settings', sa.Column('contact_name', sa.String(length=60), nullable=True))
    op.add_column('settings', sa.Column('notification_period', sa.Integer(), nullable=False))
    op.add_column('settings', sa.Column('subtitle', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('settings', 'subtitle')
    op.drop_column('settings', 'notification_period')
    op.drop_column('settings', 'contact_name')
    op.drop_column('settings', 'contact_email')
    # ### end Alembic commands ###
