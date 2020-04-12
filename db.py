import pymysql.cursors
import pymongo


class ToConn:
    def __init__(self):
        self.connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            db='bookstore',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    # 查询数据库信息
    def get_db(self, sql, t=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, t)
                return cursor
        # 关闭数据库连接
        finally:
            self.connection.close()

    # 执行操作命令
    def to_db(self, sql, t=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, t)
                return self.connection
        finally:
            pass


class ToMongo:
    def __init__(self):
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mydb = myclient['products']

    def get_col(self, col):
        """
        获取集合
        :param col:
        :return: 返回集合对象
        """
        try:
            result = self.mydb[col]
            return result
        except Exception as e:
            print('==============================\n', e)

    def update(self,col, query, new, is_one=True):
        """
        修改
        :param col: 集合名称
        :param query: 匹配修改文档
        :param new: 需要修改为新的文档
        :param is_one: 是否只修改一个，默认为是
        :return: 返回修改的结果
        """
        try:
            mycol = self.mydb[col]
            if is_one:
                result = mycol.update_one(query, new)
            else:
                result = mycol.update_many(query, new)
            return result
        except Exception as e:
            print('==============================\n', e)

    def insert(self, col, value):
        """
        插入新数据
        :param col: 插入的集合名称
        :param value: 插入的数据值
        :return: 返回插入结果
        """
        try:
            mycol = self.mydb[col]
            if type(value) == dict:
                result = mycol.insert_one(value)
            else:
                result = mycol.insert_many(value)
            return result
        except Exception as e:
            print('==============================\n', e)

    def delete(self, col, doc, is_one=True):
        """
        删除
        :param col: 集合名称
        :param doc: 筛选需要删除的文档
        :param is_one: 否只删除一个，默认为是
        :return: 删除结果
        """
        try:
            mycol = self.mydb[col]
            if is_one:
                result = mycol.delete_one(doc)
            else:
                result = mycol.delete_many(doc)
            return result
        except Exception as e:
            print('==============================\n', e)



