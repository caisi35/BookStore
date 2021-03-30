import datetime
import collections

from models.db import (
    ToMongo
)

from utils import (
    get_30_day_before_timestamp,
    format_m_d,
    get_dawn_timestamp,
    get_now,

)


def get_sales_month():
    """获取访问量"""
    db_conn = ToMongo()
    col = db_conn.get_col('order')
    # 获取29天的时间差
    date = (datetime.datetime.now() - datetime.timedelta(days=29))
    # 查询大于时间差的数据
    before_30_day = get_30_day_before_timestamp()
    data = list(col.find({'create_time': {'$gte': before_30_day}}))

    # https://blog.csdn.net/qq_42184799/article/details/86311804
    # collections.OrderedDict()字典按插入顺序排序
    day_list = collections.OrderedDict()
    # 获取时间列表['04-25', '04-26', '04-27', '04-28']
    for i in range(0, 30):
        day = date.strftime("%m-%d")
        day_list[day] = 0
        date = date + datetime.timedelta(days=1)

    for d in data:
        d_farmat = format_m_d(d['create_time']) # 03-30

        if d_farmat in day_list:
            day_list[d_farmat] = day_list[d_farmat] + d['amount']

    x = []
    y = []
    for k, v in day_list.items():
        x.append(k)
        y.append(v)
    db_conn.close_conn()

    return x, y


def get_scales_order_data():
    """获取后台数据可视化的销售量和订单数据"""
    result = {}
    conn = ToMongo()

    day_order = conn.get_col('order').find({'$and': [
        {'create_time': {'$gte': get_dawn_timestamp()}},
        {'create_time': {'$lte': get_now()}},
        {'orders_status': {'$in': [1, 2, 3, 4]}}
    ]}).count()

    total_order = conn.get_col('order').find({'orders_status': {'$in': [1, 2, 3, 4]}}).count()

    pipeline = [
        {'$match': {'orders_status': {'$in': [1, 2, 3, 4]},
                    'create_time': {'$gte': get_dawn_timestamp(), '$lte': get_now()},
                    }},
         {'$group': {'_id': "", 'sum': {'$sum': '$amount'}}},
    ]
    day_amount_resp = list(conn.get_col('order').aggregate(pipeline))
    day_amount = .0
    if day_amount_resp:
        day_amount = day_amount_resp[0]['sum']

    pipe = [
        {'$match': {'orders_status': {'$in': [1, 2, 3, 4]}}},
        {'$group': {'_id': "", 'sum': {'$sum': '$amount'}}}
    ]
    total_amount = .0
    total_amount_resp = list(conn.get_col('order').aggregate(pipe))
    if total_amount_resp:
        total_amount = total_amount_resp[0]['sum']

    result.update({'day_order': day_order,
                   'total_order': total_order,
                   'day_amount': round(day_amount, 2),
                   'total_amount': round(total_amount, 2),
                   })

    return result


def get_sales_data():
    """获取销售量sales的数据"""
    my_conn = ToMongo()
    data = my_conn.get_col('books').find({'sales': {'$gt': 0}}).sort('sales', -1).limit(10)
    data_x = []
    data_y = []
    for i in data:
        data_x.append(i['title'])
        data_y.append(i['sales'])
    return data_x, data_y


def get_hits_data():
    """获取点击量hits的数据"""
    db_conn = ToMongo()
    data = db_conn.get_col('books').find({'hits': {'$gt': 0}}).sort('hits', -1).limit(10)
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
    db_conn = ToMongo()
    max_min = list(db_conn.get_col('books').aggregate(pipeline))
    max = float(max_min[0]['max'])
    min = max_min[0]['min']
    list_n = get_n_avg(min, max)
    book_num = []
    sales_num = []
    for i in list_n:
        # print(i[0],i[1])
        if i[1] != max:
            qurey = [{'$match': {'price': {'$gte': i[0], '$lt': i[1]}}}, {'$sort': {'price': -1}}]
            r = db_conn.get_col('books').aggregate(qurey)
        else:
            qurey = [{'$match': {'price': {'$gte': i[0], '$lte': i[1]}}}, {'$sort': {'price': -1}}]
            r = db_conn.get_col('books').aggregate(qurey)
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
    db_conn.close_conn()
    return book_num, sales_num, list_n


def get_visits():
    """获取访问量"""
    db_conn = ToMongo()
    col = db_conn.get_col('visits')
    # 获取29天的时间差
    date = (datetime.datetime.now() - datetime.timedelta(days=29))
    # 查询大于时间差的数据
    before_30_day = get_30_day_before_timestamp()
    data = list(col.find({'date': {'$gte': before_30_day}}))
    # https://blog.csdn.net/qq_42184799/article/details/86311804
    # collections.OrderedDict()字典按插入顺序排序
    day_list = collections.OrderedDict()
    # 获取时间列表['04-25', '04-26', '04-27', '04-28']
    for i in range(0, 30):
        day = date.strftime("%m-%d")
        day_list[day] = 0
        date = date + datetime.timedelta(days=1)

    for d in data:
        d_farmat = format_m_d(d['date'])
        if d_farmat in day_list:
            day_list[d_farmat] = len(d['users_id'])

    x = []
    y = []
    for k, v in day_list.items():
        x.append(k)
        y.append(v)
    db_conn.close_conn()
    return x, y


def get_keyword():
    """
    获取搜索关键词数据
    :return:
    """
    db_conn = ToMongo()
    kw = db_conn.get_col('keyword').find({}, {'_id': 0})
    key = []
    value = []
    for k, v in list(kw)[0].items():
        key.append(k)
        value.append(v)
    return key, value


if __name__ == '__main__':
    get_sales()
