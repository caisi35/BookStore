from datetime import timedelta
from utils import format_time_second
from models import (
    ToMongo,
    get_book_for_id,
)
from utils import get_day_time
from models import get_book_for_id


def get_order_details_model(order_no, user_id):
    """获取订单详情"""
    cur = ToMongo().get_col('order').find_one({'user_id': user_id, 'order_no': order_no})
    create_time = cur['create_time']
    effective_time = create_time + get_day_time()
    is_processed = cur['is_processed']
    amount = cur['amount']
    order_id = cur['_id']
    order_no = cur['order_no']
    is_effective = cur['is_effective']
    address = cur['address']
    book_list = []
    for book in cur['books']:
        book_dict = {}
        book_dict['num'] = book['book_num']
        book_id = book['book_id']
        book_dict['book'] = get_book_for_id(book_id)
        book_list.append(book_dict)

    order_dict = {}
    order_dict['books'] = book_list
    order_dict['_id'] = order_id
    order_dict['create_time'] = create_time
    order_dict['effective_time'] = effective_time
    order_dict['is_processed'] = is_processed
    order_dict['amount'] = amount
    order_dict['order_no'] = order_no
    order_dict['is_effective'] = is_effective
    order_dict['address'] = address
    return order_dict


def delete_orders_model(user_id, orders_no):
    rel = False
    db = ToMongo()
    count = 0
    for order_no in orders_no:
        result = db.delete('order', {'order_no': order_no, 'user_id': user_id}).deleted_count
        count += result
    if count == len(orders_no):
        # 删除成功
        rel = True
    return rel


def user_delete_order(user_id, order_no):
    rel = False
    result = ToMongo().delete('order', {'order_no': order_no, 'user_id': user_id})
    if result.deleted_count:
        # 删除成功
        rel = True
    return rel


def get_user_orders_model(user_id):
    """查询用户订单信息"""
    result = ToMongo().get_col('order').find({'user_id': user_id, 'is_effective': 1}).sort('order_no', -1)
    orders = []
    result = list(result)
    for order in result:
        amount = order['amount']
        order_no = order['order_no']
        create_time = order['create_time']
        effective_time = order['create_time'] + get_day_time()
        books = order['books']
        book_info = []
        for book in books:
            book_num = book['book_num']
            # 图书下架后get_book查询不到信息，会抛出错误
            book_info.append({'book_num': book_num, 'books': get_book_for_id(book['book_id'])})
        orders.append({'amount': amount,
                       'order_no': order_no,
                       'create_time': format_time_second(create_time),
                       'book_info': book_info,
                       'effective_time': effective_time,
                       })
    return orders
