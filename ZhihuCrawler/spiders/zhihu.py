# -*- coding: utf-8 -*-
from json import loads
from scrapy import Spider, Request
from ZhihuCrawler.items import UserItem, AnswerItem
from ZhihuCrawler.cookies import load_cookies


class ZhihuSpider(Spider):
    def parse(self, response):
        pass

    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://www.zhihu.com/']

    # cookies
    # 这里使用selenium获取cookie
    # 为了避免账户被封，最好不要使用cookie进行爬虫
    # 如果需要用cookie，请在每个Request下面加上`cookies=self.zhihu_cookie`的参数
    zhihu_cookie = load_cookies()

    # 起始用户
    start_user = "liaoxuefeng"

    # 用户信息url
    user_url = "https://www.zhihu.com/api/v4/members/{user}?include={include}"

    # 用户查询参数
    user_query = "locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,\
    following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,\
    following_columns_count,avatar_hue,answer_count,articles_count,pins_count,question_count,columns_count,\
    commercial_question_count,favorite_count,favorited_count,logs_count,marked_answers_count,marked_answers_text,\
    message_thread_token,account_status,is_active,is_bind_phone,is_force_renamed,is_bind_sina,is_privacy_protected,\
    sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,\
    mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,\
    hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,\
    badge[?(type=best_answerer)].topics"

    # 关注列表的url
    follows_url = "https://www.zhihu.com/api/v4/members/{user}/followees?\
    include={include}&offset={offset}&limit={limit}"

    # 关注列表的查询参数
    follows_query = "data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following\
    %2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics"

    # 获取粉丝列表信息的url
    followers_url = "https://www.zhihu.com/api/v4/members/{user}/followers?include={include}\
    &offset={offset}&limit={limit}"

    # 粉丝列表的查询参数
    followers_query = "data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following\
    %2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics"

    # 回答按赞数排名的查询url
    answers_url = 'https://www.zhihu.com/api/v4/members/{user}/answers?include={include}'

    # 回答前20赞数的查询参数
    answer_query = 'data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2C\
    annotation_detail%2Ccollapse_reason%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2C\
    voteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Creview_info%2C\
    question%2Cexcerpt%2Cis_labeled%2Clabel_info%2Crelationship.is_authorized%2Cvoting%2Cis_author%2Cis_thanked%2C\
    is_nothelp%3Bdata%5B*%5D.author.badge%5B%3F(type%3Dbest_answerer)%5D.topics&offset={offset}&limit={limit}&sort_by=voteups'

    def start_requests(self):
        """
        重写start_requests方法，请求了用户查询、关注列表、粉丝列表（前20人）
        :return: 请求
        """
        yield Request(self.user_url.format(user=self.start_user, include=self.user_query),
                      callback=self.parse_user)
        yield Request(self.follows_url.format(user=self.start_user, include=self.follows_query, offset=0, limit=20),
                      callback=self.parse_follows)
        yield Request(self.followers_url.format(user=self.start_user, include=self.followers_query, offset=0, limit=20),
                      callback=self.parse_follows)

    def parse_user(self, response):
        """
        因为返回的是json格式的数据
        :param response: 网页响应数据
        :return: item，并返回该用户的关注 / 粉丝请求
        """
        result = loads(response.text)
        item = UserItem()
        # 用获取的字段为item定义的字段赋值
        for field in item.fields:
            item[field] = result.get(field, 'Undefined')
        # 返回用户信息
        yield item
        # 获取用户回答，按照点赞数排序
        yield Request(
            self.answers_url.format(user=result.get('url_token'), include=self.answer_query, offset=0, limit=20),
            callback=self.parse_answers
        )
        # 获取关注用户列表
        yield Request(
            self.follows_url.format(user=result.get('url_token'), include=self.follows_query, offset=0, limit=20),
            callback=self.parse_follows
        )
        # 获取粉丝列表
        yield Request(
            self.followers_url.format(user=result.get('url_token'), include=self.followers_query, offset=0, limit=20),
            callback=self.parse_follows
        )

    def parse_answers(self, response):
        """
        用户回答列表的解析
        :param response: 网页响应数据
        :return: 网页请求
        """
        results = loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                item = AnswerItem()
                for field in item.fields:
                    item[field] = result.get(field, 'Undefined')
                yield item
        if 'page' in results.keys() and not results.get('is_end'):
            next_page = results.get('paging').get('next')
            yield Request(next_page, callback=self.parse_answers)

    def parse_follows(self, response):
        """
        用户关注列表/粉丝列表的解析
        :param response: 网页响应数据
        :return: json格式包含data和page的数据
        """
        results = loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query),
                              callback=self.parse_user)
        if 'page' in results.keys() and not results.get('is_end'):
            next_page = results.get('paging').get('next')
            yield Request(next_page, self.parse_follows)
