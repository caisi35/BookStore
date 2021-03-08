from bson.objectid import ObjectId
from werkzeug.utils import secure_filename

from utils import format_time_second, ORDER_EFFECTIVE_TIME, get_now
from models import (
    ToMongo,
)

from models import get_book_for_id


def get_badge_model(user_id):
    status = [[0], [1], [2], [3]]
    badge = {}
    for s in status:
        badge[str(s[0])] = len(get_orders(user_id, s))
    return badge


def format_logistics(logistics):
    lit = []
    for logi in logistics:
        create_time = format_time_second(logi.get('create_time'))
        info = logi.get('info')
        lit.append({'create_time': create_time,
                    'info': info})
    return lit


def get_order_details_model(order_no, user_id):
    """获取订单详情"""
    update_status_to_5()  # 更新订单状态
    cur = ToMongo().get_col('order').find_one({'user_id': user_id, 'order_no': order_no})
    create_time = cur['create_time']
    effective_time = create_time + ORDER_EFFECTIVE_TIME
    is_processed = cur['is_processed']
    amount = cur['amount']
    order_id = cur['_id']
    order_no = cur['order_no']
    is_effective = cur['is_effective']
    address = cur['address']
    status = cur['orders_status']
    logistics = format_logistics(cur['logistics'])
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
    order_dict['create_time'] = format_time_second(create_time)
    order_dict['effective_time'] = format_time_second(effective_time)
    order_dict['is_processed'] = is_processed
    order_dict['amount'] = amount
    order_dict['order_no'] = order_no
    order_dict['is_effective'] = is_effective
    order_dict['address'] = address
    order_dict['status'] = status
    order_dict['logistics'] = logistics
    return order_dict


def delete_orders_model(user_id, orders_no):
    """用户删除多个订单"""
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
    """用户删除单个订单"""
    rel = False
    result = ToMongo().delete('order', {'order_no': order_no, 'user_id': user_id})
    if result.deleted_count:
        # 删除成功
        rel = True
    return rel


def format_query(user_id, status):
    """格式化获取订单查询语句"""
    query = {'user_id': user_id,
             'is_effective': 1,
             'orders_status': {'$in': status},
             }
    if len(status) < 2 and status[0] == 0:
        query.update({'create_time': {'$gt': get_now() - ORDER_EFFECTIVE_TIME}})
    return query


def get_orders(user_id, status):
    """获取用户订单信息"""
    query = format_query(user_id, status)
    result = ToMongo().get_col('order').find(query).sort('order_no', -1)
    orders = []
    result = list(result)
    for order in result:
        status = order['orders_status']
        amount = order['amount']
        order_no = order['order_no']
        create_time = order['create_time']
        effective_time = order['create_time'] + ORDER_EFFECTIVE_TIME
        books = order['books']
        book_info = []
        for book in books:
            book_num = book['book_num']
            # 图书下架后get_book查询不到信息，会抛出错误
            book_info.append({'book_num': book_num, 'books': get_book_for_id(book['book_id'])})
        orders.append({'status': status,
                       'amount': amount,
                       'order_no': order_no,
                       'create_time': format_time_second(create_time),
                       'book_info': book_info,
                       'effective_time': format_time_second(effective_time),
                       })
    return orders


def get_user_orders_model(user_id, orders_status):
    """
    查询用户订单信息
    orders_status:空-全部，待付款-0，待发货-1，待收货-2，待评价-3"""
    update_status_to_5()  # 更新订单状态
    if orders_status == 0:
        orders = get_orders(user_id, [orders_status])
        active = orders_status
    elif orders_status == 1:
        orders = get_orders(user_id, [orders_status])
        active = orders_status
    elif orders_status == 2:
        orders = get_orders(user_id, [orders_status])
        active = orders_status
    elif orders_status == 3:
        orders = get_orders(user_id, [orders_status])
        active = orders_status
    else:
        orders = get_orders(user_id, [0, 1, 2, 3, 4, 5, 6])
        active = -1
    return orders, active


def update_status_to_5():
    """将过期订单，状态更新为失效"""
    query = {'orders_status': 0,
             'create_time': {'$lt': get_now() - ORDER_EFFECTIVE_TIME},
             }
    new = {'$set': {'orders_status': 5}}
    mydb = ToMongo()
    result = mydb.update('order', query, new, is_one=False)
    return result.modified_count


def cancel_model(order_no, user_id):
    """用户取消订单"""
    mydb = ToMongo()
    query = {'order_no': order_no,
             'user_id': user_id}
    new = {'$set': {'orders_status': 5}}
    rel = mydb.update('order', query, new)
    return rel.modified_count


def refund_model(order_no, user_id):
    """用户申请退款"""
    mydb = ToMongo()
    query = {'order_no': order_no,
             'user_id': user_id}
    new = {'$set': {'orders_status': 6}}
    rel = mydb.update('order', query, new)
    return rel.modified_count


def save_img(order_no, img):
    """保存用户评论上传的图片"""
    s_img = secure_filename(img.filename)
    img_suffix = s_img.split('.')[-1]
    # 用户id+时间戳+后缀
    filepath = './static/images/evaluate/' + order_no + '.' + str(img_suffix)
    # filename = filepath.split('/')[-1]
    img.save(filepath)
    return filepath


def get_book_id(order_no):
    """获取订单的图书id"""
    mydb = ToMongo()
    books = mydb.get_col('order').find_one({'order_no': order_no})
    book_ids = []
    for book in books.get('books'):
        book_ids.append(book.get('book_id'))
    return book_ids


def evaluate_model(user_id, user_name, request):
    """用户评论模型"""
    rlt = {}
    order_no = request.form.get('order_no')
    star = int(request.form.get('star'))
    context = request.form.get('context')
    anonymous = request.form.get('anonymous')
    img = request.files.get('img')
    if not star:
        rlt['error'] = '评分不能为空'
        return rlt
    if img:
        img_path = save_img(order_no, img)
    else:
        img_path = ''
    create_time = get_now()
    book_ids = get_book_id(order_no)
    if anonymous:
        user_name = user_name[0] + '**'
    else:
        user_name = user_name[0] + '*' + user_name[-1]
    id_list = []
    mydb = ToMongo()
    for book_id in book_ids:
        value = {'$addToSet':
                     {'comment':
                          {'order_no': order_no,
                           'star': star,
                           'context': context,
                           'user_id': user_id,
                           'user_name': user_name,
                           'img_path': img_path,
                           'create_time': create_time
                           }
                      }
                 }
        result = mydb.update('evaluate', {'_id': ObjectId(book_id)}, value)
        if result.modified_count:
            id_list.append(result.modified_count)
        else:
            # 无评论时，直接插入
            rel = mydb.insert('evaluate',
                              {'_id': ObjectId(book_id),
                               'comment':
                                   [
                                       {'order_no': order_no,
                                        'star': star,
                                        'context': context,
                                        'user_id': user_id,
                                        'user_name': user_name,
                                        'img_path': img_path,
                                        'create_time': create_time
                                        }
                                   ]
                               })
            id_list.append(rel.inserted_id)
        # print(id_list)
    if len(id_list) != len(book_ids):
        # print(id_list)
        rlt['error'] = '评论失败，请重试！'
    return rlt


def update_status(order_no):
    """更新订单状态为交易完成"""
    mydb = ToMongo()
    result = mydb.update('order', {'order_no': order_no}, {'$set': {'orders_status': 4}})
    return result.modified_count


def update_status_user_id(order_no, user_id):
    """更新订单状态为待评论"""
    mydb = ToMongo()
    result = mydb.update('order', {'order_no': order_no, 'user_id': user_id}, {'$set': {'orders_status': 3}})
    return result.modified_count


if __name__ == '__main__':
    print(update_status_to_5())
