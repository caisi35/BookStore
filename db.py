import pymysql.cursors
import pymongo
from bson.code import Code
from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
import urllib.request


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

    def get_db(self, sql, t=None):
        """
        执行查询数据库命令
        :param sql: SQL语句
        :param t: 需要替换的元祖tuple
        :return: 查询游标
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, t)
                return cursor
        # 关闭数据库连接
        finally:
            self.connection.cursor().close()
            self.connection.close()

    def to_execute(self):
        """
        执行execute 语句
        :return: 返回游标
        """
        try:
            return self.connection
        except Exception as e:
            print('===============to_execute===============\n', e)
        # finally:
        #     self.to_close()

    def to_db(self, sql, t=None):
        """
        执行操作数据库的命令
        :param sql: SQL语句
        :param t: 需要替换的元祖tuple
        :return: 返回数据库链接对象
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, t)
                return self.connection
        except Exception as e:
            print('===============to_db===============\n', e)

    def to_close(self):
        """
        关闭链接
        :return:
        """
        self.connection.cursor().close()
        self.connection.close()

    def get_cart(self, user_id):
        """
        查询用户购物车
        :param user_id: 用户id
        :return: 返回购物车list内容
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute('select * from cart where user_id=%s', (user_id,))
                return cursor.fetchall()
        except Exception as e:
            print('===============get_cart===============\n', e)
        self.to_close()


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
            print('===============get_col===============\n', e)

    def update(self, col, query, new, is_one=True):
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
            print('==============update================\n', e)

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
            print('==============insert================\n', e)

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
            print('==============delete================\n', e)

    def get_all_collections(self):
        """
        获取所有的集合
        :return: 集合名称列表
        """
        cls = self.mydb.list_collection_names()
        return cls

    def get_collection_keys(self, col):
        """
        获取所有的字段名称
        :param col: 集合名
        :return: 所有的字段列表
        """
        datas = self.mydb[col].find({})
        nameList = []
        for data in datas:
            for key in data.keys():
                if key not in nameList:
                    nameList.append(key)
        return nameList

    def get_collection_keys_map_reduce(self, col):
        """
        用map,reduce 查询集合的所有字段名
        :param col: 集合名称
        :return: 字段列表
        """
        map = Code("function() { for (var key in this) { emit(key, null); } }")
        reduce = Code("function(key, stuff) { return null; }")
        result = self.mydb[col].map_reduce(map, reduce, "results")
        return result.distinct('_id')

    def fuzzy_search(self, col, skey=None):
        """
        使用正则表达式进行关键字模糊查询
        :param col: 集合名
        :param skey: 关键字
        :return: 文档结果列表
        """
        dList = []
        try:
            if skey != None:
                cList = []  # 用于存储所有字段的模糊查询条件
                nameList = self.get_collection_keys_map_reduce(col)
                for name in nameList:
                    condition = {name: {"$regex": str(skey)}}
                    cList.append(condition)  # 将每个字段模糊查询条件压入数组
                datas = self.mydb[col].find(filter={"$or": cList})  # 用$or表示或的关系，$and表示与
            else:
                datas = self.mydb[col].find({})
            for d in datas:
                dList.append(d)
            return dList
        except Exception as e:
            print('==============fuzzy_search================\n', e)

    def insert_img(self, filename, data):
        """
        插入一个二进制图片
        :param filename:
        :param data:
        读取文件
        with open('./static/images/logo.png', 'rb') as file:
        data = file.read()
        file.close()
        """
        coll = self.mydb['images']
        result = coll.insert_one({'name': filename, 'data': data})
        return result

    def get_img(self, filename):
        """
        获取一个二进制的图像数据
        :param filename:
        :return:二进制

        # 数据库中的BSON数据写回文件
        ret = users.find_one({'name': 'zhifubao.jpg'})
        with open(os.path.join(os.getcwd(), 'new.png'), 'wb') as file:
        file.write(ret.get('data'))
        """
        try:
            coll = self.mydb['images']
            img = coll.find_one({'name': filename})
            # with open(filename, 'wb') as file:
            #     file.write(img.get('data'))
            #     file.close()
            return img.get('data')
        except Exception as e:
            print('==============get_img================\n', e)




class Spider:
    headers = {"User-Agent":
                   "Mozilla/5.0 (Windows; U; Windows NT 6.0 "
                   "x64; en-US; rv:1.9pre)Gecko / 2008072421 Minefield / 3.0.2pre"}
    count = 0

    def load_img(self, start_url):
        try:
            urls = []
            req = urllib.request.Request(start_url, headers=self.headers)
            data = urllib.request.urlopen(req)
            data = data.read()
            dammit = UnicodeDammit(data, ['utf-8', 'gbk'])
            data = dammit.unicode_markup
            soup = BeautifulSoup(data, 'lxml')
            images = soup.select('img')
            for image in images:
                try:
                    src = image['src']
                    url = urllib.request.urljoin(start_url, src)
                    if url not in urls:
                        urls.append(url)
                        print(url)
                        self.download(url)
                except Exception as e:
                    print('============load_img1==========', e)
        except Exception as e:
            print('============load_img2==========', e)

    def download(self, url):
        try:
            self.count += 1
            if url[len(url) - 4] == '.':
                ext = url[len(url) - 4:]
            else:
                ext = ''
            req = urllib.request.Request(url, headers=self.headers)
            data = urllib.request.urlopen(req, timeout=100)
            data = data.read()
            fobj = open('./static/images/spider/' + str(self.count) + ext, 'wb')
            fobj.write(data)
            fobj.close()
            print('download' + str(self.count) + ext)
        except Exception as e:
            print('============download==========', e)


if __name__ == '__main__':
    # with open('./static/images/spider/weixin.gif','rb') as f:
    #     data = f.read()
    #     f.close()
    # ToMongo().insert_img('weixin.gif', data)
    # ToMongo().get_img('logo.jpg')
    pass

