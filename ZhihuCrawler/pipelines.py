# -*- coding: utf-8 -*-
from os.path import exists
from ZhihuCrawler.items import UserItem
from json import dump


class MyPipeline(object):
    def __init__(self, download_path: str):
        self.__download_path = download_path

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            download_path=crawler.settings.get('DOWNLOAD_PATH')
        )

    def process_item(self, item: UserItem, spider):
        file_name = self.__download_path + item['name'] + '_' + item['id'] + '.txt'
        if not exists(file_name):
            with open(file_name, 'w') as f:
                dump(dict(item), f,
                     ensure_ascii=False,
                     separators=(',', ': '),
                     indent=4,)
            print('用户【%s】的数据爬取完毕' % item['name'])
        return item
