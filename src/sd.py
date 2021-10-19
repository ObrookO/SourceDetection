import os
import sys
from configparser import ConfigParser, NoSectionError, NoOptionError
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.mysql import Mysql


class SourceDetection:
    def __init__(self):
        self.url = 'https://github.com/'
        self.path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_builder = self.__get_db_builder()
        self.session = requests.Session()

        self.__get_config()
        self.__login()
        for item in self.keywords.split(','):
            self.__search(item)

    def __get_config(self):
        """
        解析配置文件
        """
        try:
            config = ConfigParser()
            config_path = self.path + '/conf/app.conf'
            config.read(config_path, encoding='utf-8')

            self.username = config.get('main', 'username')
            self.password = config.get('main', 'password')
            self.keywords = config.get('main', 'keywords')

        except (NoSectionError, NoOptionError):
            self.username = self.email = self.keywords = None

    def __get_db_builder(self):
        return Mysql()

    def __login(self):
        """
        登录github
        """
        login_url = self.url + 'login'
        login_res = self.session.get(url=login_url)
        if login_res.status_code != 200:
            print('Get Login Page Failed! <==========> Please check the network!')
            return

        bs = BeautifulSoup(login_res.text, 'lxml')
        token = bs.select_one('[name=authenticity_token]')['value']
        params = {
            'commit': 'Sign in',
            'utf8': '&#x2713;',
            'authenticity_token': token,
            'login': self.username,
            'password': self.password,
            'webauthn-support': 'supported'
        }

        post_url = self.url + 'session'
        post_res = self.session.post(url=post_url, data=params)
        if post_res.status_code != 200:
            print('Login Failed! <==========> Please check the username and password!')
            return

    def __search(self, keyword, page=1):
        """
        根据关键词搜索
        :param keyword: 关键词
        :param page: 页码，默认为1
        :return:
        """
        search_url = self.url + 'search?p=' + str(page) + '&q=' + keyword
        search_res = self.session.get(url=search_url)
        if search_res.status_code != 200:
            print('Search Failed! <==========> Keyword is ' + keyword + ', Page is ' + str(page) + '!')
            return

        '''
        获取仓库列表
        '''
        bs = BeautifulSoup(search_res.text, 'lxml')
        repo_list = bs.select('li.repo-list-item')
        data = []
        for r in repo_list:
            '''
            获取仓库所属用户的真实姓名、用户名、邮箱、仓库地址和更新时间
            '''
            repo_href = r.select_one('a.v-align-middle')['href']
            username, realname, email = self.__get_user_info(repo_href)
            repo_update_time = r.select_one('relative-time')['datetime']
            utc_time = datetime.strptime(repo_update_time, '%Y-%m-%dT%H:%M:%SZ')
            local_time = utc_time + timedelta(hours=8)
            data.append({
                'username': '' if username is None else username,
                'realname': '' if realname is None else realname,
                'email': '' if email is None else email,
                'href': self.url + repo_href.lstrip('/'),
                'last_update_at': local_time.strftime('%Y-%m-%d %H:%M:%S')
            })

        doc_res = self.db_builder.add(data)
        if doc_res:
            print('Add Records Success!')
        else:
            print('Add Records Failed!')

        '''
        获取剩余页的数据
        '''
        total_page_ele = bs.select_one('em[data-total-pages]')
        if total_page_ele is not None:
            total_page = total_page_ele['data-total-pages']
            if page <= int(total_page) - 1:
                self.__search(keyword, page + 1)

    def __get_user_info(self, url):
        """
        获取用户名、邮箱
        :param url: 用户的主页地址
        :return: 用户名、真实姓名、邮箱
        """
        realname, email = None, None

        username = url.split('/')[1]
        user_url = self.url + username

        user_info_res = self.session.get(url=user_url)
        if user_info_res.status_code == 200:
            bs = BeautifulSoup(user_info_res.text, 'lxml')
            name_ele = bs.select_one('span.p-name')
            email_ele = bs.select_one('a.u-email')

            if name_ele is not None:
                realname = name_ele.string

            if email_ele is not None:
                email = email_ele.string

        return username, realname, email


if __name__ == '__main__':
    sd = SourceDetection()
