from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
request = Table('request', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('body', String(length=1200)),
    Column('timestamp', DateTime),
    Column('crop_type', String(length=40)),
    Column('processed', Boolean),
    Column('processed_time', DateTime),
    Column('request_queued', Boolean),
    Column('link', String(length=200)),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['request'].columns['request_queued'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['request'].columns['request_queued'].drop()
