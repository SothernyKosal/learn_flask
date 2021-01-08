"""empty message

Revision ID: 769be23a7938
Revises: 53a052034967
Create Date: 2020-12-24 10:49:19.598737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '769be23a7938'
down_revision = '53a052034967'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'user', 'role', ['role_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_column('user', 'role_id')
    # ### end Alembic commands ###
