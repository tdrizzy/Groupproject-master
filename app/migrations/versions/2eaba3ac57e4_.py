"""empty message

Revision ID: 2eaba3ac57e4
Revises: 76e53bf2dfd4
Create Date: 2018-10-08 15:43:04.972131

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2eaba3ac57e4'
down_revision = '76e53bf2dfd4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company', sa.Column('accident_policy_flag', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('company_risk_assessed', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('data_contact_first_name', sa.String(length=30), nullable=True))
    op.add_column('company', sa.Column('data_contact_last_name', sa.String(length=30), nullable=True))
    op.add_column('company', sa.Column('data_contact_position', sa.String(length=30), nullable=True))
    op.add_column('company', sa.Column('data_contact_telephone', sa.String(length=30), nullable=True))
    op.add_column('company', sa.Column('data_policy_flag', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('data_policy_link', sa.String(length=120), nullable=True))
    op.add_column('company', sa.Column('data_training_flag', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('emergency_procedures_flag', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('health_policy_flag', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('health_policy_link', sa.String(length=120), nullable=True))
    op.add_column('company', sa.Column('hse_registered', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('ico_registration_number', sa.String(length=20), nullable=True))
    op.add_column('company', sa.Column('insured', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('la_registered', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('privacy_notice_flag', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('report_student_accidents_flag', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('report_student_illness_flag', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('risks_mitigated', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('risks_reviewed', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('security_measures_flag', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('security_policy_flag', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('security_policy_link', sa.String(length=120), nullable=True))
    op.add_column('company', sa.Column('student_insured', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('training_policy_flag', sa.Boolean(), nullable=True))
    op.add_column('company', sa.Column('training_policy_link', sa.String(length=120), nullable=True))
    op.add_column('company', sa.Column('web', sa.String(length=120), nullable=True))
    op.create_index(op.f('ix_company_web'), 'company', ['web'], unique=True)
    op.drop_index('ix_users_web', table_name='users')
    op.drop_column('users', 'web')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('web', mysql.VARCHAR(length=120), nullable=True))
    op.create_index('ix_users_web', 'users', ['web'], unique=True)
    op.drop_index(op.f('ix_company_web'), table_name='company')
    op.drop_column('company', 'web')
    op.drop_column('company', 'training_policy_link')
    op.drop_column('company', 'training_policy_flag')
    op.drop_column('company', 'student_insured')
    op.drop_column('company', 'security_policy_link')
    op.drop_column('company', 'security_policy_flag')
    op.drop_column('company', 'security_measures_flag')
    op.drop_column('company', 'risks_reviewed')
    op.drop_column('company', 'risks_mitigated')
    op.drop_column('company', 'report_student_illness_flag')
    op.drop_column('company', 'report_student_accidents_flag')
    op.drop_column('company', 'privacy_notice_flag')
    op.drop_column('company', 'la_registered')
    op.drop_column('company', 'insured')
    op.drop_column('company', 'ico_registration_number')
    op.drop_column('company', 'hse_registered')
    op.drop_column('company', 'health_policy_link')
    op.drop_column('company', 'health_policy_flag')
    op.drop_column('company', 'emergency_procedures_flag')
    op.drop_column('company', 'data_training_flag')
    op.drop_column('company', 'data_policy_link')
    op.drop_column('company', 'data_policy_flag')
    op.drop_column('company', 'data_contact_telephone')
    op.drop_column('company', 'data_contact_position')
    op.drop_column('company', 'data_contact_last_name')
    op.drop_column('company', 'data_contact_first_name')
    op.drop_column('company', 'company_risk_assessed')
    op.drop_column('company', 'accident_policy_flag')
    # ### end Alembic commands ###
