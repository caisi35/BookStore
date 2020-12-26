import datetime
import collections

from models.db import (
    ToMongo
)


def get_sales_data():
    """获取销售量sales的数据"""
    data = ToMongo().get_col('books').find({'sales': {'$gt': 0}}).sort('sales', -1).limit(10)
    data_x = []
    data_y = []
    for i in data:
        data_x.append(i['title'])
        data_y.append(i['sales'])
    return data_x, data_y


def get_hits_data():
    """获取点击量hits的数据"""
    data = ToMongo().get_col('books').find({'hits': {'$gt': 0}}).sort('hits', -1).limit(10)
    data_x = []
    data_y = []
    for i in data:
        data_x.append(i['title'])
        data_y.append(i['hits'])
    return data_x, data_y


def get_n_avg(min, max):
    """获取价格区间"""
    list = [min, max]
    list.insert(1, list[0] / 2 + list[1] / 2)
    list.insert(1, list[0] / 2 + list[1] / 2)
    list.insert(-1, list[-1] / 2 + list[-2] / 2)
    list.insert(1, list[0] / 2 + list[1] / 2)
    list.insert(-1, list[-1] / 2 + list[-2] / 2)
    list.insert(3, list[2] / 2 + list[3] / 2)
    list.insert(5, list[4] / 2 + list[5] / 2)

    for i in range(1, len(list) - 1):
        list[i] = int(list[i])
    area_list = []
    for i in range(len(list) - 1):
        area_list.append([list[i], list[i + 1]])
    return area_list


def get_price():
    """
    # https://cloud.tencent.com/developer/article/1406368
    # 字符串转为数值
    # https://www.jb51.net/article/98385.htm
    # aggregate查询同字段的区间值
    :return:
    """
    pipeline = [
        {'$group': {'_id': "", 'max': {'$max': '$price'}, 'min': {'$min': '$price'}}},
    ]
    max_min = list(ToMongo().get_col('books').aggregate(pipeline))
    max = float(max_min[0]['max'])
    min = max_min[0]['min']
    list_n = get_n_avg(min, max)
    book_num = []
    sales_num = []
    for i in list_n:
        # print(i[0],i[1])
        if i[1] != max:
            qurey = [{'$match': {'price': {'$gte': i[0], '$lt': i[1]}}}, {'$sort': {'price': -1}}]
            r = ToMongo().get_col('books').aggregate(qurey)
        else:
            qurey = [{'$match': {'price': {'$gte': i[0], '$lte': i[1]}}}, {'$sort': {'price': -1}}]
            r = ToMongo().get_col('books').aggregate(qurey)
        r = list(r)
        book_num.append(len(r))

        sales = 0
        for i in r:
            try:
                if i['sales']:
                    sales = sales + i['sales']
            except:
                pass
        sales_num.append(sales)
    return book_num, sales_num, list_n


def get_visits():
    """获取访问量"""
    col = ToMongo().get_col('visits')
    # 获取30天的时间差
    date = (datetime.datetime.now() - datetime.timedelta(days=30))
    # 查询大于时间差的数据
    data = list(col.find({'date': {'$gte': date}}))
    # https://blog.csdn.net/qq_42184799/article/details/86311804
    # collections.OrderedDict()字典按插入顺序排序
    day_list = collections.OrderedDict()
    # 获取时间列表['04-25', '04-26', '04-27', '04-28']
    for i in range(0, 31):
        day = date.strftime("%m-%d")
        day_list[day] = 0
        date = date + datetime.timedelta(days=1)

    for d in data:
        d_farmat = d['date'].strftime("%m-%d")
        if d_farmat in day_list:
            day_list[d_farmat] = len(d['users_id'])
    x = []
    y = []
    for k, v in day_list.items():
        x.append(k)
        y.append(v)
    return x, y


def get_keyword():
    """
    获取搜索关键词数据
    :return:
    """
    kw = ToMongo().get_col('keyword').find({}, {'_id': 0})
    key = []
    value = []
    for k, v in list(kw)[0].items():
        key.append(k)
        value.append(v)
    return key, value