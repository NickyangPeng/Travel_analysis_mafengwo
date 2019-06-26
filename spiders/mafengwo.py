import requests
from lxml import etree
import re

from db.mongodb import mongo


class MaFengWoSpider(object):

    def __init__(self, city):
        self.city = city
        self.url_pattern = "http://www.mafengwo.cn/search/s.php?q=" + city + "&p={}&t=poi&kt=1"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36"
        }

    def get_url_list(self):
        """获取url列表"""
        url_list = []
        for i in range(1, 21):
            url = self.url_pattern.format(i)
            url_list.append(url)
        return url_list

    def get_page_from_url(self, url):
        """根据url, 发送请求, 获取页面数据"""
        response = requests.get(url, headers=self.headers)
        # 返回响应的字符串数据
        return response.content.decode()

    def get_datas_from_page(self, page):
        """解析页面数据"""
        # 把页面转换为element对象, 就可以使用XPATH提取数据
        element = etree.HTML(page)
        # 获取包含景点信息的标签列表, xpath返回的是一个列表
        lis = element.xpath('//*[@id="_j_search_result_left"]/div/div/ul/li')
        # 遍历标签列表, 提取需要的数据
        # 定义列表, 用于存储数据
        data_list = []
        for li in lis:
            # 定义一个字典用于储存数据
            item = {}
            # 获取景点名称
            name = ''.join(li.xpath('./div/div[2]/h3/a//text()'))
            # 如果标题中, 没有景点就过滤掉
            if name.find("景点") == -1:
                continue
            # 去掉标题中的景点
            item['name'] = name.replace('景点 -', '')
            # print(item)
            # 提取景点地址
            item['address'] = li.xpath('./div/div[2]/ul/li[1]/a//text()')[0]
            # print(address)
            # 获取点评数量  点评(500)
            comments_num = li.xpath('./div/div[2]/ul/li[2]/a/text()')[0]
            # 提取点评中的数
            item['comments_num'] = int(re.findall(r'点评\((\d+)\)', comments_num)[0])
            # print(comments_num)
            # 获取游记数量 游记(50)
            travel_notes_num = li.xpath('./div/div[2]/ul/li[3]/a/text()')[0]
            item['travel_notes_num'] = int(re.findall(r'游记\((\d+)\)', travel_notes_num)[0])
            # 记录当前景点的城市
            item['city'] = self.city
            # print(item)
            data_list.append(item)

        return data_list

    def save_data(self, datas):
        """保存数据"""
        for data in datas:
            # 把景点名称,指定为数据库的主键
            data['_id'] = data['name']
            # 保存数据到数据库中
            mongo.save(data)

    def run(self):
        """程序的入口, 核心业务逻辑"""
        # 1. 准备url列表
        url_list = self.get_url_list()
        # print(url_list)
        # 2. 遍历url列表, 发送请求, 获取响应数据
        for url in url_list:
            page = self.get_page_from_url(url)
            # 3. 解析数据
            datas = self.get_datas_from_page(page)
            # 4. 保存数据
            self.save_data(datas)


if __name__ == '__main__':
    ms = MaFengWoSpider("广州")
    ms.run()
