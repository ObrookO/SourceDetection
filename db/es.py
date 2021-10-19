import os
from configparser import ConfigParser, NoSectionError, NoOptionError
from elasticsearch import Elasticsearch, ConnectionError, ElasticsearchException


class ES:
    def __init__(self):
        self.path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.__get_config()

        try:
            self.es = Elasticsearch(hosts=self.host)
        except ConnectionError as e:
            raise e

    def __get_config(self):
        """
        解析配置文件
        """
        try:
            config = ConfigParser()
            config.read(self.path + '/conf/app.conf')
            self.host = config.get('es', 'host').split(',')
            self.index = config.get('es', 'index')
        except (NoSectionError, NoOptionError):
            raise

    def add(self, records):
        """
        添加数据
        :param records: 内容
        :return: bool
        """
        try:
            self.es.index(index=self.index, body=records)
            return True
        except ElasticsearchException as e:
            raise e
