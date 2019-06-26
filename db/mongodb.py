from pymongo import MongoClient
import pymongo


class Mongo(object):
    """
    定义一个类,用于操作MongoDB数据库
    """
    def __init__(self):
        """初始化操作"""
        # 链接MongoDB数据库
        self.client = MongoClient('mongodb://127.0.0.1:27017')
        # 获取操作的集合, travel:数据库名称, scenic:集合名称(相当于关系型数据库中表)
        self.collection = self.client['travel']['scenic']

    def save(self, data):
        """保存数据, 如果id重复自动覆盖"""
        self.collection.save(data)

    def find_scenic_count(self, city):
        """获取城市景点数量"""
        return self.collection.count({'city': city})

    def find_scenics(self, city_name, count=20):
        cursor = self.collection.find({'address': {'$regex': city_name}}, limit=count).\
            sort([('comments_num', pymongo.DESCENDING)])

        scenics = []
        for scenic in cursor:
            scenics.append(scenic)
        return scenics


# 创建一个用于操作数据库的对象
mongo = Mongo()
