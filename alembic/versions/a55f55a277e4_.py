"""empty message

Revision ID: a55f55a277e4
Revises: 
Create Date: 2022-08-10 17:21:15.576126

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a55f55a277e4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('annual_gdp',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('area_code', sa.String(length=64), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('number', sa.Float(), nullable=True),
    sa.Column('unit', sa.Enum('RMB', 'DOLLAR', name='money_unit'), nullable=True),
    sa.Column('created_time', sa.DateTime(), nullable=True),
    sa.Column('changed_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('year', 'area_code', sqlite_on_conflict='REPLACE')
    )
    op.create_index(op.f('ix_annual_gdp_area_code'), 'annual_gdp', ['area_code'], unique=False)
    op.create_table('annual_population',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('area_code', sa.String(length=64), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('number', sa.Float(), nullable=True),
    sa.Column('created_time', sa.DateTime(), nullable=True),
    sa.Column('changed_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('year', 'area_code', sqlite_on_conflict='REPLACE')
    )
    op.create_index(op.f('ix_annual_population_area_code'), 'annual_population', ['area_code'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_annual_population_area_code'), table_name='annual_population')
    op.drop_table('annual_population')
    op.drop_index(op.f('ix_annual_gdp_area_code'), table_name='annual_gdp')
    op.drop_table('annual_gdp')
    # ### end Alembic commands ###
