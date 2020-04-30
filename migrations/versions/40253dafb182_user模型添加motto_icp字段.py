"""user模型添加motto,icp字段

Revision ID: 40253dafb182
Revises: 
Create Date: 2020-04-29 20:45:02.221061

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '40253dafb182'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('icp', sa.String(length=128), nullable=True))
    op.add_column('user', sa.Column('motto', sa.String(length=128), nullable=True))
    op.alter_column('user', 'email_is_validate',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'email_is_validate',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.drop_column('user', 'motto')
    op.drop_column('user', 'icp')
    # ### end Alembic commands ###
