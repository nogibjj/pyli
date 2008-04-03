#!/usr/bin/env python
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker
import os

#path
path = "/tmp"

#create engine
engine = create_engine('sqlite:///:memory:', echo=False)

#metadata
metadata = MetaData()

filesystem_table = Table('filesystem', metadata,
   Column('id', Integer, primary_key=True),
     Column('path', String(500)),
     Column('file', String(255)),
)

metadata.create_all(engine)

#mapped class
class Filesystem(object):

    def __init__(self, path, file):
        self.path = path
        self.file = file

    def __repr__(self):
        return "<Filesystem('%s','%s')>" % (self.path, self.file)

#mapper function
mapper(Filesystem,filesystem_table)

#create session
Session = sessionmaker(bind=engine, autoflush=True, transactional=True)
session = Session()

#crawl file system and populate database with results
for dirpath, dirnames, filenames in os.walk(path):
    for file in filenames:
        fullpath = os.path.join(dirpath, file)
        record = Filesystem(fullpath, file)
        session.save(record)

#commit to the database
session.commit()

#query
query = session.query(Filesystem)
for record in session.query(Filesystem):
    print "Database Record Number: %s, Path: %s , File: %s " \
    % (record.id,record.path, record.file)
