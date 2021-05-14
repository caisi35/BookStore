from bson.objectid import ObjectId
from models.db import ToMongo
from utils.time_model import (
    get_before_day,
    get_now,
    format_time_second,
)


def restore_stock(query, mydb):
    """恢复库存"""
    order = mydb.get_col('order').find_one(query)
    rel = []
    for book in order.get('books'):
        re = mydb.update('books', {'_id': ObjectId(book.get('book_id'))}, {'$inc': {'stock': book.get('book_num')}})
        rel.append({book.get('book_id'): re})
    return rel


def get_order(order_no):
    """获取订单详情"""
    conn = ToMongo()
    order = conn.get_col('order').find_one({'order_no': order_no})
    books = order.get('books')
    new_books = []
    for book in books:
        book_info = conn.get_col('books').find_one({'_id': ObjectId(book.get('book_id'))})
        book_num = book.get('book_num')
        new_books.append({'book': book_info, 'book_num': book_num})
    order['create_time'] = format_time_second(order.get('create_time'))
    order['books'] = new_books
    conn.close_conn()
    return order


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
        query = {"$or": [{'orders_status': order_status}]}
    elif order_status == 6:
        query = {'$and': [{'orders_status': order_status},
                          {'is_effective': 1}]}
    db_conn = ToMongo()
    order = db_conn.get_col('order').find(query).sort('create_time', -1).skip((page - 1) * page_size).limit(page_size)
    total = db_conn.get_col('order').find(query).count()
    order_list = list(order)
    books = []
    for order in order_list:
        order['create_time'] = format_time_second(order.get('create_time'))
        for book in order.get('books'):
            id = book.get('book_id')
            book_num = book.get('book_num')
            book = db_conn.get_col('books').find_one({'_id': ObjectId(id)})
            books.append({'book': book, 'num': book_num})
    db_conn.close_conn()
    return order_list, total, books


def order_handle_model(order_no, status, msg):
    """更新状态0到3"""
    if status == 0:
        # 确认已付款
        uptate_status_inc(order_no, 0, msg)
    elif status == 1:
        # 确认已发货
        uptate_status_inc(order_no, 1, msg)
    elif status == 2:
        # 后台为查看订单详情, 2=待收货
        uptate_status_inc(order_no, 2, msg)
    elif status == 3:
        # 后台为查看订单详情， 3=待评价
        uptate_status_inc(order_no, 3, msg)
    elif status == 6:   # 6=退款
        handle_refund(order_no, 6, msg)


def handle_refund(order_no, status, msg):
    """退款"""
    conn = ToMongo()
    # 还原库存
    query = {'order_no': order_no}
    restore_stock(query, conn)
    # 更新订单状态
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
