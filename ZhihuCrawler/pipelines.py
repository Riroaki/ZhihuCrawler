# -*- coding: utf-8 -*-
from os.path import exists
from os import mkdir
from ZhihuCrawler.items import UserItem, AnswerItem
from json import dump
from pymongo import MongoClient


class MyPipeline(object):
    def __init__(self, download_path: str,
                 use_db: bool,
                 mongodb_uri: str,
                 db_name: str,
                 user: str,
                 pwd: str):
        self.__download_path = download_path
        self.__use_db = use_db
        self.__db_uri = mongodb_uri
        self.__db_name = db_name
        self.__client = MongoClient(self.__db_uri)
        self.__db = self.__client[self.__db_name]
        self.__user = user
        self.__pwd = pwd

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            download_path=crawler.settings.get('DOWNLOAD_PATH'),
            use_db=crawler.settings.get('USE_DB'),
            mongodb_uri=crawler.settings.get('MONGO_URI'),
            db_name=crawler.settings.get('DB_NAME'),
            user=crawler.settings.get("USER_NAME"),
            pwd=crawler.settings.get("PASSWORD"),
        )

    def close_spider(self, spider):
        self.__client.close()

    def process_item(self, item, spider):
        # 可以选择存储到数据库
        if self.__use_db:
            self.__db['user'].update({'url_token': item["url_token"]}, {'$set': item}, True)
        # 也可以存储到本地data目录下txt文档
        else:
            # 用户个人信息
            if isinstance(item, UserItem):
                file_name = self.__download_path + item['name'] + '_' + item['id'] + '.txt'
                if not exists(file_name):
                    with open(file_name, 'w') as f:
                        dump(dict(item), f,
                             ensure_ascii=False,
                             separators=(',', ': '),
                             indent=4, )
                    print('用户【%s】的数据爬取完毕' % item['name'])
            # 用户回答信息
            elif isinstance(item, AnswerItem):
                author_name = item['author'].get('name')
                answer_folder = self.__download_path + author_name + '_answers/'
                if not exists(answer_folder):
                    mkdir(answer_folder)
                file_name = answer_folder + item['question'].get('title') + '.txt'
                if not exists(file_name):
                    with open(file_name, 'w') as f:
                        dump(dict(item), f,
                             ensure_ascii=False,
                             separators=(',', ': '),
                             indent=4)
        return item
