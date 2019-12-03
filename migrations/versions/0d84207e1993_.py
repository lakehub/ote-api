"""empty message

Revision ID: 0d84207e1993
Revises: 
Create Date: 2019-09-17 20:32:21.552004

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0d84207e1993'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blacklist_tokens',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('token', sa.String(length=500), nullable=False),
    sa.Column('blacklisted_on', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('public_id', sa.BigInteger(), nullable=True),
    sa.Column('email', sa.Unicode(length=255), nullable=True),
    sa.Column('phone_no', sa.String(length=13), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('role', sa.Integer(), nullable=True),
    sa.Column('password', sa.Unicode(length=255), nullable=True),
    sa.Column('image_uri', sa.String(length=255), nullable=True),
    sa.Column('push_notification_id', sa.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone_no')
    )
    op.drop_table('login')
    op.drop_table('user')
    op.drop_table('delivery_order')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('delivery_order',
    sa.Column('id', mysql.BIGINT(display_width=20), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('order_id', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('pickup_address', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('pickup_contact', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('pickup_contact_number', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('dropoff_address', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('dropoff_contact', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('dropoff_contact_number', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('item_value_cost', mysql.BIGINT(display_width=20), autoincrement=False, nullable=False),
    sa.Column('notes', mysql.TEXT(), nullable=False),
    sa.Column('delivery_fee', mysql.DOUBLE(asdecimal=True), nullable=False),
    sa.Column('invoice_id', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('mpesa_payment_id', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('date_created', mysql.BIGINT(display_width=20), autoincrement=False, nullable=False),
    sa.Column('order_status', mysql.VARCHAR(length=255), server_default=sa.text("'New'"), nullable=True),
    sa.Column('rider_id', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('rider_pickup_date', mysql.BIGINT(display_width=20), autoincrement=False, nullable=True),
    sa.Column('rider_delivery_date', mysql.BIGINT(display_width=20), autoincrement=False, nullable=True),
    sa.Column('rider_notes', mysql.TEXT(), nullable=True),
    sa.Column('user_feedback', mysql.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('user',
    sa.Column('id', mysql.BIGINT(display_width=20), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('firstname', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('lastname', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('phone_number', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('push_notificaiton_id', mysql.TEXT(), nullable=True),
    sa.Column('date_created', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('phone_number_verified', mysql.INTEGER(display_width=11), server_default=sa.text('0'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('login',
    sa.Column('id', mysql.BIGINT(display_width=20), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('email_address', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('password', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('role', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('status', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('date_created', mysql.BIGINT(display_width=20), autoincrement=False, nullable=False),
    sa.Column('last_login', mysql.BIGINT(display_width=20), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.drop_table('users')
    op.drop_table('blacklist_tokens')
    # ### end Alembic commands ###
