from sqlalchemy import create_engine
import pandas as pd
import numpy as np


def load(conn, csv, table):
    csv = pd.read_csv(csv, encoding="utf-8", low_memory=False)
    if 'id' in csv.columns:
        csv.drop('id', axis=1, inplace=True)
    fields = ('word', 'sw', 'phonetic', 'definition',
              'translation', 'pos', 'collins', 'oxford',
              'tag', 'bnc', 'frq', 'exchange', 'detail',
              'audio')
    for field in fields:
        if field not in csv.columns:
            csv[field] = np.nan
    csv.dropna(subset=['word'], axis=0, inplace=True)
    csv.drop_duplicates(subset=['word'], inplace=True)
    csv.index = np.arange(1, len(csv) + 1)

    sql = ('CREATE TABLE IF NOT EXISTS {table} ('
           '`id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT,'
           '`word` VARCHAR(255) NOT NULL UNIQUE KEY,'
           '`sw` VARCHAR(255),'
           '`phonetic` VARCHAR(255),'
           '`definition` TEXT,'
           '`translation` TEXT,'
           '`pos` VARCHAR(64),'
           '`collins` SMALLINT DEFAULT 0,'
           '`oxford` SMALLINT DEFAULT 0,'
           '`tag` VARCHAR(64),'
           '`bnc` INT DEFAULT NULL,'
           '`frq` INT DEFAULT NULL,'
           '`exchange` TEXT,'
           '`detail` TEXT,'
           '`audio` TEXT,'
           '`frequency` INT DEFAULT 0,'
           'KEY(`sw`, `word`),'
           'KEY(`collins`),'
           'KEY(`oxford`),'
           'KEY(`tag`))').format(db=db, table=table)
    conn.execute(sql)
    csv.to_sql(name=table, con=conn, schema=db, if_exists='append', index='id')


if __name__ == "__main__":
    user = ''
    passwd = ''
    host = ''
    port = ''
    db = ''
    table = ''

    data = {'mini': r'.\data\mini.csv',
            'slim': r'.\data\slim.csv',
            'entire': r'.\data\entire.csv'}

    engine_str = ''.join(['mysql+pymysql://', user, ':',
                          passwd, '@', host, ':', str(port)])
    engine = create_engine(engine_str, echo=False)
    conn = engine.connect()

    sql = ('CREATE SCHEMA IF NOT EXISTS {db} '
           'CHARACTER SET utf8mb4 '
           'COLLATE utf8mb4_bin').format(db=db)
    conn.execute(sql)
    sql = 'USE {db}'.format(db=db)
    conn.execute(sql)

    for key, value in data.items():
        load(conn, value, key)
