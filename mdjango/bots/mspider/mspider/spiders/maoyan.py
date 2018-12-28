# -*- coding: utf-8 -*-
import scrapy
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from ..items import MovieItem
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor

from ..lilith import DataBase
import sqlite3

chrome_options = Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(chrome_options=chrome_options)
# database为原始数据库
# DataBase.link('../mdjango/database.db')

# 创建新的数据库
dtb = DataBase()
dtb.link('../mdjango/dtbase.db')
try:
    dtb.create_table()
except sqlite3.OperationalError:
    pass


class MaoyanSpider(scrapy.Spider):
    name = 'maoyan'
    allowed_domains = ['piaofang.maoyan.com']
    start_urls = ['http://piaofang.maoyan.com/rankings/year']
    driver.get(start_urls[0])

    # 存储爬取的电影信息
    resultList = []

    def parse(self, response):
        year_0 = 2019
        select_year = [2019, 2018, 2017, 2016, 2015]
        # 选择爬取年份, 2019表示爬取截止到现在中国电影总榜
        year_in = select_year[0]
        left_click = driver.find_element_by_xpath('//*[@id="tab-year"]/ul/li[' + str(year_0 - year_in) + ']')
        ActionChains(driver).move_to_element(left_click).perform()
        ActionChains(driver).double_click(left_click).perform()
        time.sleep(1)

        # 提取电影的href链接
        url_text = driver.page_source
        movie_herf = re.findall(r'data-com="hrefTo,href:\'(.*)\'\"', url_text)

        # url_list = []

        fatherUrl = 'http://piaofang.maoyan.com'
        # 这里修改需要爬取的条数
        for i in movie_herf:
            iurl = fatherUrl + i
            # url_list.append(iurl)
            yield response.follow(iurl, callback=self.detail_parse)

    # 进入电影的详细信息页爬取所需内容
    # 电影名、题材、上映时间、评分、票房信息、导演和演员
    def detail_parse(self, response):
        movie = MovieItem()
        # 电影名
        movie['name'] = response.xpath('//span[@class="info-title-content"]/text()').extract()[0]
        # 电影类型
        type = response.xpath('//p[@class="info-category"]/text()').extract()
        if type:
            type = type[0].split('\n')[1].strip()
        else:
            type = response.xpath('//span[@class="info-subtype ellipsis-1"]/text()').extract()
            if type:
                type = type[0]
            else:
                type = response.xpath('//span[@class="tv-types"]/text()').extract()[0]
        movie['type'] = type
        # 上映时间
        rlstime = response.xpath('//a/span[1]/text()').extract()
        if rlstime:
            movie['releasetime'] = rlstime[0]
        else:
            movie['releasetime'] = '--'
        # 星级评分
        # 五个等级：1-2，3-4，5-6，7-8，9-10
        # 爬取内容包括总评分和每个等级的比例及总评分人数
        star = response.xpath('//span[@class="rating-num"]/text()').extract()
        if star:
            movie['ratestar'] = star[0]
        else:
            movie['ratestar'] = '--'
        score_num = response.xpath('//p[@class="detail-score-count"]/text()').extract()
        # 评分人数
        if score_num:
            score_num = score_num[0].split("观众评分")[0]
            movie['score_num'] = score_num
            scoreflag = response.xpath('//div[@class="info-block"]/a/@href').extract()
            if scoreflag:
                # 猫眼各级评分人数占比
                score = response.xpath('//div[@class="percentbar"]/span/text()').extract()
                for i in range(0, 5):
                    label = 'score_' + str(9-2*i) + str(10-2*i)
                    movie[label] = score[2*i + 1]

        # 票房信息，包括首日、首周和总票房，如果有缺失项，用"--"补齐
        boxinfo = response.xpath('//div[@class="info-detail-row"]/div/p/span/text()').extract()
        if boxinfo:
            box = []
            for i in boxinfo:
                box.append(i)
                if i == '--':
                    box.append('--')
            cumbox = box[0] + box[1]
            if box[2] == '--':
                day1stbox = '--'
            else:
                day1stbox = box[2] + box[3]
            if box[4] == '--':
                week1stbox = '--'
            else:
                week1stbox = box[4] + box[5]
        else:
            cumbox = '--'
            day1stbox = '--'
            week1stbox = '--'
        movie['totalbox'] = cumbox
        movie['fdaybox'] = day1stbox
        movie['fweekbox'] = week1stbox

        # 爬取导演和演员信息需要进入新的网页
        actors_url = str(response).split(" ")[1].split(">")[0] + '/celebritylist'
        yield scrapy.Request(actors_url, meta={'movie': movie}, callback=self.director_parse)

    # 导演、演员信息
    def director_parse(self, response):
        movie = response.meta['movie']
        person_detail = response.xpath('//div[@class="panel-wrapper"]//span[@class="title-name"]/text()').extract()

        # 爬取网页中导演和演员信息
        findlabel = ['导演', '演员']
        if findlabel[0] in person_detail:
            dposition = person_detail.index(findlabel[0]) + 1
        else:
            dposition = -1
        if findlabel[1] in person_detail:
            aposition = person_detail.index(findlabel[1]) + 1
        else:
            aposition = -1
        # 如果没有导演，"--"填充
        if dposition == -1:
            director = '--'
        else:
            director = response.xpath('//div[@class="panel-wrapper"]/dl['+str(dposition)+']//div[@class="p-desc"]'
                                                                                         '/p[1]/text()').extract()
            if director:
                pass
            else:
                director = response.xpath('//div[@class="p-desc"]/p[' + str(dposition) + ']/text()').extract()
        movie['director'] = director
        # 没有演员，用"--"填充
        if aposition == -1:
            actor = '--'
        else:
            actor = response.xpath('//div[@class="panel-wrapper"]/dl[' + str(aposition) + ']//div/p[1]/text()').extract()

        # 因为有的电影演员很多，所以只选择了前10个出现的演员
        actorlen = 10
        if len(actor) <= actorlen:
            movie['actor'] = actor
        else:
            movie['actor'] = actor[:actorlen]
        # yield movie
        self.resultList.append(movie)

    # 将爬取的电影信息存入数据库
    def close(self, reason):
        for i in self.resultList:
            # print(i)
            filmInfo = {'date': i['releasetime'], 'boxoffice': i['totalbox'], 'score': i['ratestar'], 'name': i['name'],
                        'type': i['type']}
            # 数据库中有三个表film、actor、director，所以分别处理
            dtb.film_in(filmInfo)
            actorInfo = i['actor']
            for j in actorInfo:
                dtb.actor_in({'name': j}, filmInfo['name'])
            directorInfo = i['director']
            for j in directorInfo:
                dtb.director_in({'name': j}, filmInfo['name'])
