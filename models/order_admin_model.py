from models.db import ToMongo
from utils.time_model import (
    get_before_day,
    get_now,
)


def orders_query_model(page, page_size, order_status):
    query = {}
    if order_status == 0:
        # 待付款订单
        query = {'$and': [{'orders_status': order_status},
                          {'is_effective': 1},
                          {'create_time': {'$gte': get_before_day()}}]}
    elif order_status == 1:
        query = {'$and': [{'orders_status': order_status},
                          {'is_effective': 1}]}
    elif order_status == 2:
        query = {'$and': [{'orders_status': order_status},
                          {'is_effective': 1}]}
    elif order_status == 3:
        query = {'$and': [{'orders_status': order_status},
                          {'is_effective': 1}]}
    elif order_status == 4:
        query = {'$and': [{'orders_status': order_status},
                          {'is_effective': 1}]}
    elif order_status == 5:
        # 失效订单
        query = {"$and": [{'create_time': {'$lt': get_before_day()}},
                          {'orders_status': {"$nin": [1, 2, 3, 4]}}]}
    elif order_status == 6:
        query = {'$and': [{'orders_status': order_status},
                          {'is_effective': 1}]}
    db_conn = ToMongo()
    order = db_conn.get_col('order').find(query).sort('create_time', -1).skip((page - 1) * page_size).limit(page_size)
    total = db_conn.get_col('order').find(query).count()
    order_list = list(order)
    db_conn.close_conn()
    return order_list, total


def order_handle_model(order_no, status, msg):
    """更新状态0到3"""
    if status == 0:
        # 确认已付款
        uptate_status_inc(order_no, 0, msg)
    elif status == 1:
        # 确认已发货
        uptate_status_inc(order_no, 1, msg)
    elif status == 2:
        # 后台为查看订单详情
        uptate_status_inc(order_no, 2, msg)
    elif status == 3:
        # 后台为查看订单详情
        uptate_status_inc(order_no, 3, msg)
    elif status == 6:
        handle_refund(order_no, 6, msg)


def handle_refund(order_no, status, msg):
    conn = ToMongo()
    result = conn.update('order', {'order_no': order_no, 'orders_status': status}, {"$set": {'orders_status': 5}})
    if result.modified_count:
        pass
    else:
        msg.update({'error': '更新失败'})
    conn.close_conn()


def uptate_status_inc(order_no, status, msg):
    conn = ToMongo()
    new = {"$inc": {'orders_status': 1}}
    if status == 0:
        new = {"$inc": {'orders_status': 1},
               "$addToSet": {'logistics':
                                 {'create_time': get_now(),
                                  'info': '商品已经下单'}}
               }
    elif status == 1:
        new = {"$inc": {'orders_status': 1},
               "$addToSet": {'logistics':
                                 {'create_time': get_now(),
                                  'info': '包裹正在等待揽收'}
                             }
               }
    result = conn.update('order',
                         {'order_no': order_no, 'orders_status': status},
                         new,
                         is_one=False)
    if result.modified_count:
        pass
    else:
        msg.update({'error': '更新失败'})
    conn.close_conn()


if __name__ == '__main__':
    print(uptate_status_inc('202103041646186388', 0, 'invalid'))
