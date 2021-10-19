import os
from configparser import ConfigParser, NoSectionError, NoOptionError

import pymysql


class Mysql:
    def __init__(self):
        self.path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.__get_config()
        self.cursor = None

        try:
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.passwd,
                database=self.dbname
            )
            self.cursor = self.conn.cursor()
        except pymysql.MySQLError as e:
            raise e

        self.__check_table()

    def __get_config(self):
        """
        解析配置文件
        """
        try:
            config = ConfigParser()
            config.read(self.path + '/conf/app.conf')
            self.host = config.get('mysql', 'host')
            self.user = config.get('mysql', 'user')
            self.passwd = config.get('mysql', 'pass')
            self.dbname = config.get('mysql', 'dbname')
        except (NoSectionError, NoOptionError):
            raise

    def __check_table(self):
        sql = '''
        SELECT * FROM `information_schema`.`TABLES` WHERE `TABLE_NAME` = 'source_detection' LIMIT 1
        '''
        self.cursor.execute(sql)
        if self.cursor.rowcount == 0:
            with open('../db.sql') as f:
                self.cursor.execute(f.read())

    def add(self, records):
        try:
            sql = ''
            if isinstance(records, list):
                columns = ','.join(records[0].keys())
                sql = 'INSERT INTO source_detection (%s) VALUES ' % columns

                for record in records:
                    values = "','".join(record.values())
                    sql = sql + '(' + values + '),'

                sql = sql.rstrip(',')
            elif isinstance(records, dict):
                columns = ','.join(records.keys())
                values = "','".join(records.values())
                sql = 'INSERT INTO source_detection (%s) VALUES (%s)' % (columns, values)

            print(sql + "\n")
            self.cursor.execute(sql)
        except pymysql.MySQLError as e:
            raise e
