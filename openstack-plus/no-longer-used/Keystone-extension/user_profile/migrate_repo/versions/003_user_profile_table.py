'''
Created on May 16, 2014

@author: fmignini
'''





import sqlalchemy as sql


def upgrade(migrate_engine):
    meta = sql.MetaData()
    meta.bind = migrate_engine
    
    service_table = sql.Table(
        'user_profile',
        meta,
        sql.Column('user_id', sql.String(64), primary_key=True, nullable=False),
        sql.Column('timestamp', sql.TIMESTAMP, primary_key=True, nullable=False),
        sql.Column('graph', sql.Text(), nullable=False))
       
    service_table.create(migrate_engine, checkfirst=True)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = sql.MetaData()
    meta.bind = migrate_engine

    tables = ['user_profile']
    for t in tables:
        table = sql.Table(t, meta, autoload=True)
        table.drop(migrate_engine, checkfirst=True)
