#!/usr/bin/env python
"""
Data Access Object
"""

import pandas as pd
import sqlalchemy
import yaml


class Dao(object):
    """Simplified Data Access Object to query Postgres databases
    """

    def __init__(self, host, port, user, password, db, schema='public'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.schema = schema
        self.engine = sqlalchemy.create_engine(self.get_connection_string())

    def get_connection_string(self):
        return 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(self.user, self.password, self.host, self.port, self.db)

    def get_engine(self):
        return self.engine

    def change_schema(self, schema):
        self.schema = schema

    def run_query(self, query, autocommit=True):
        with self.engine.connect() as conn:
            if self.schema != 'public':
                conn.execute("SET search_path TO public, {}".format(self.schema))
            return conn.execute(sqlalchemy.text(query).execution_options(autocommit=autocommit))

    def download_from_query(self, query):
        with self.engine.connect() as conn:
            if self.schema != 'public':
                conn.execute("SET search_path TO public, {}".format(self.schema))
            return pd.read_sql(query, conn)

    def upload_from_dataframe(self, df, table_name, if_exists='replace', chunksize=1000000):
        df.to_sql(table_name, self.engine, schema=self.schema, if_exists=if_exists, index=False, chunksize=chunksize)

    def get_next_value(self, sequence):
        return int(self.run_query("SELECT nextval('{}')".format(sequence)).fetchone()[0])


class YmlDao(Dao):
    """Simplified Data Access Object which is initialized using
    a YML file containing the access credentials
    """

    def __init__(self, yaml_file, name):
        # Load "name" from YML file
        access_data = yaml.load(open(yaml_file, 'r'))[name]
        if 'schema' not in access_data:
            access_data['schema'] = 'public'
        # Initialize original Dao
        super(YmlDao, self).__init__(
            access_data['host'], access_data['port'], access_data['user'],
            access_data['password'], access_data['database'], access_data['schema']
        )


if __name__ == '__main__':
    dao = YmlDao('db.yml', 'adwords@localhost')
