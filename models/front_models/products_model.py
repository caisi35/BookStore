import time
import logging
import base64
from datetime import timedelta, datetime
from bson.objectid import ObjectId

from models import (
    ToConn,
    ToMongo,
    get_like_books
)

from utils import (
    create_orders,
    format_time_second,
    get_now
)
from recommend import (
    get_data,
    getRecommendations,
    recommend as recommend_for_tags,
    get_visual_info,
    item_cf,
)


def add_history(user_id, book_id):
    """添加浏览历史"""
    conn = ToMongo()
    query = {'_id': str(user_id), 'book_ids': {'$nin': [book_id]}}
    ret = conn.update('history',
                      query,
                      {'$push': {'book_ids': book_id}})
    conn.close_conn()
    return ret.modified_count


def is_collection_model(user_id, book_id):
    """获取用户是否收藏该商品"""
    result = False
    conn = ToMongo()
    ret = conn.get_col('favorites').find_one({'_id': str(user_id), 'book_ids.book_id': {'$in': [book_id]}})
    conn.close_conn()
    if ret:
        result = True
    return result


def to_collection_model(user_id, book_id, is_clear=False):
    """添加、取消收藏"""
    conn = ToMongo()
    if is_clear:
        result = False
        query = {'_id': str(user_id), 'book_ids.book_id': {'$in': [book_id]}}
        ret = conn.update('favorites',
                          query,
                          {'$pull': {'book_ids': {'book_id': book_id}}})
        if ret.modified_count:
            result = True
    else:
        result = False
        query = {'_id': str(user_id), 'book_ids.book_id': {'$nin': [book_id]}}
        ret = conn.update('favorites',
                          query,
                          {'$push': {'book_ids': {'book_id': book_id, 'create_time': get_now()}}})
        if ret.modified_count:
            result = True
    conn.close_conn()
    return result


# Logger('./products_model.log')
def get_recommend_book_model(id=None, num=3):
    """根据图书内容推荐"""
    try:
        book = getRecommendations(get_data(), id)
    except Exception as e:
        # 系统冷启动
        book = None

    book_list = []

    if book:
        ret = get_visual_info(book)
        book_list.extend(ret)
    else:
        # 基于用户点击行为的 item-cf 推荐
        try:
            book = item_cf(id, num)
            ret = get_visual_info(book)
            book_list.extend(ret)
        except KeyError:
            # 没有登录的异常情况
            pass
    if len(book_list) < num:
        book = recommend_for_tags(id, num=num-len(book_list))
        ret = get_visual_info(book)
        book_list.extend(ret)
    return book_list


def get_recommend_user_book_model(id=None, num=2):
    try:
        book = getRecommendations(get_data(), id)
    except Exception as e:
        book = None
    book_list = []

    if book:
        ret = get_visual_info(book)
        book_list.extend(ret)
    if len(book_list) < num:
        book = recommend_for_tags(user_id=id, num=num-len(book_list))
        ret = get_visual_info(book)
        book_list.extend(ret)
    return book_list


def get_evaluate(book_id, page=0, page_size=10):
    """获取评论信息"""
    mydb = ToMongo()
    evaluates = mydb.get_col('evaluate').find_one({'_id': ObjectId(book_id)})
    lit = []
    star_dict = {'praise': 0, 'negative': 0, 'mid': 0}
    try:
        eval_comment = evaluates.get('comment')
        if page:
            page = page - 1
            eval_comment = eval_comment[page * page_size:page * page_size + page_size]
        else:
            eval_comment = eval_comment[page * page_size:page * page_size + page_size]
    except AttributeError:
        return [], 0, star_dict
    for evaluate in eval_comment:
        # print(evaluate)
        dit = {}
        # dit['order_no'] = evaluate['order_no']
        dit['star'] = evaluate['star']
        dit['context'] = evaluate['context']
        avatar_path = './static/images/avatar/' + get_user_avatar(evaluate['user_id'])
        dit['avatar'] = avatar_path
        dit['user_name'] = evaluate['user_name']
        dit['img_path'] = evaluate['img_path']
        dit['create_time'] = format_time_second(evaluate['create_time'])
        lit.append(dit)
    evaluates_details = get_evaluates_details(mydb, book_id, star_dict)
    mydb.close_conn()
    return lit, len(evaluates.get('comment')), star_dict


def get_evaluates_details(db, id, star_dict):
    r = db.get_col('evaluate').find_one({'_id': ObjectId(id)})
    for i in r.get('comment'):
        # print(i)
        if i.get('star') in [4, 5]:
            star_dict['praise'] += 1
        elif i.get('star') in [1, 2]:
            star_dict['negative'] += 1
        else:
            star_dict['mid'] += 1
    # print(star_dict)
    return star_dict


def get_user_avatar(user_id):
    """获取评论用户的头像"""
    mydb = ToConn()
    user_info = mydb.get_db('select avatar from users where id=%s', (user_id,)).fetchone()
    try:
        avatar = user_info.get('avatar')
    except AttributeError:
        avatar = ''
    return avatar


def search_book_model(word, page, page_size):
    """搜索图书"""
    db_conn = ToMongo()
    # 如果输入不为空
    if word:
        # 添加关键字数据到数据库，用与绘制词云图
        db_conn.update('keyword', {'_id': 'keyword'}, {'$inc': {word: 1}})
        books, count = get_like_books(word, page, page_size)
    # 如果输入为空，则显示点击量前十的
    else:
        books = db_conn.get_col('books').find({'is_off_shelf': 0}).sort('hits', -1).skip(page * page_size).limit(
            page_size)
        count = db_conn.get_col('books').find({'is_off_shelf': 0}).count()
    db_conn.close_conn()
    return books, count


def get_order_info(user_id, order_no):
    """获取订单信息"""
    mydb = ToMongo()
    myorder = mydb.get_col('order').find_one({'order_no': order_no, 'user_id': user_id})
    data = {'order_no': myorder.get('order_no'),
            'amount': myorder.get('amount'),
            'create_time': format_time_second(myorder.get('create_time'))}
    mydb.close_conn()
    return data


def pay_model(order_no):
    """订单支付"""
    mydb = ToMongo()
    images = []
    weixin_image = base64.b64encode(mydb.get_img('weixin.gif')).decode('utf-8')
    zhifubao_image = base64.b64encode(mydb.get_img('zhifubao.gif')).decode('utf-8')
    images.append({'data': weixin_image, 'name': '微信支付'})
    images.append({'data': zhifubao_image, 'name': '支付宝支付'})
    my_orders = mydb.get_col('order').find({"is_effective": 1, 'order_no': order_no})
    my_orders = list(my_orders)
    mydb.close_conn()
    return my_orders, images


def to_pay_model(user_id, amount, book_ids, addr_id):
    """去支付"""
    create_time = int(time.time())
    order_no = create_orders()
    books = []
    # 获取收货地址,写入订单号详情
    db_conn = ToMongo()
    address = db_conn.get_col('address').find_one(
        {'user_id': user_id, '_id': ObjectId(addr_id)})
    for book_id in book_ids:
        db = ToConn()
        sql = 'select book_num from cart where user_id=%s and book_id=%s and is_effe=1'
        book_num = db.get_db(sql, (user_id, book_id)).fetchone()
        if book_num:
            books.append({'book_num': int(book_num['book_num']), 'book_id': book_id})
        else:
            books.append({'book_num': 1, 'book_id': book_id})
    v = {"amount": amount,
         "books": books,
         "order_no": order_no,
         "is_processed": 0,
         "user_id": user_id,
         "create_time": create_time,
         "is_effective": 1,
         "address": address,
         "orders_status": 0,
         "pay_status": 0,
         "exp_status": 0,
         "logistics": [],  # 物流信息
         }
    result = db_conn.insert('order', v)
    if result:
        db = ToConn()
        conn = db.to_execute()
        cursor = conn.cursor()
        try:
            for book_id in book_ids:
                sql = 'delete from cart where user_id=%s and book_id=%s'
                cursor.execute(sql, (user_id, book_id))
        except Exception as e:
            print('========to_pay=========事务处理失败:', e)
            conn.rollback()  # 事务回滚
        else:
            conn.commit()  # 事务提交
            # 销量加1
            for book_id in book_ids:
                db_conn.update('books', {'_id': ObjectId(book_id)}, {'$inc': {'sales': 1}})
        db.to_close()
    db_conn.close_conn()
    return order_no


def delete_addr(user_id, _id):
    """删除收货地址"""
    conn = ToConn().to_execute()
    cur = conn.cursor()
    db_conn = ToMongo()
    cur.execute('update users set address_default=null where id=%s and address_default = %s', (user_id, _id))
    result = db_conn.delete(col='address', doc={'_id': ObjectId(_id)}).raw_result
    if result['ok'] == 1:
        conn.commit()
    else:
        conn.rollback()
    db_conn.close_conn()


def update_addr(user_id, request):
    """更换收货地址"""
    name = request.form.get('name')
    tel = request.form.get('tel')
    address_list = request.form.get('address').strip().split(' ')
    details = request.form.get('details')
    mydb = ToMongo()
    value = {
        'user_id': user_id,
        'name': name,
        'tel': tel,
        'province': address_list[0],
        'city': address_list[1],
        'district': address_list[2],
        'details': details,
    }
    conn = ToConn().to_execute()
    cur = conn.cursor()
    address_default = mydb.insert('address', value).inserted_id
    cur.execute('update users set address_default=%s where id=%s', (str(address_default), user_id))
    if address_default:
        conn.commit()
        conn.close()
    else:
        conn.rollback()
        conn.close()
    mydb.close_conn()


def to_buy_model(user_id, books_id, is_list=True):
    """结算"""
    db_conn = ToMongo()
    if is_list:
        book_id_list = list(books_id.split(','))
        book_list = []
        sum_price = 0.0
        freight = 0.0
        package = 1
        discount = 1.01
        sum_book = 0
        addr = {}
        try:
            user = get_user(user_id)
            logging.info('userinfo:%s', user)
            if user['address_default'] is None or user['address_default'] is '':
                addr = {}
            else:
                address = db_conn.get_col('address').find({'_id': ObjectId(user['address_default'])})
                for a in address:
                    addr['name'] = a['name']
                    addr['tel'] = a['tel']
                    addr['province'] = a['province']
                    addr['city'] = a['city']
                    addr['district'] = a['district']
                    addr['details'] = a['details']
                    addr['_id'] = user['address_default']
            for book_id in book_id_list:
                db = ToConn()
                sql = 'select book_num from cart where user_id=%s and book_id=%s and is_effe=1'
                book_num = db.get_db(sql, (user_id, book_id)).fetchone()
                mydb = get_book(book_id)
                mydb['_id'] = book_id
                mydb['book_num'] = int(book_num['book_num'])
                mydb['sum_price'] = round(float(mydb['price']) * float(book_num['book_num']), 2)
                if int(book_num.get('book_num')) > mydb.get('stock'):
                    return {'error': '{} 没有这么多库存啦～'.format(mydb.get('title'))}
                book_list.append(mydb)
                sum_price = sum_price + round(float(mydb['price']) * float(book_num['book_num']), 2)
                sum_book = sum_book + int(book_num['book_num'])
            books_price = {'sum_price': sum_price, 'freight': freight, 'package': package,
                           'sum': round(sum_price + freight - discount, 2), 'discount': discount}
            pay = {'amount_pay': round(sum_price + freight - discount, 2), 'sum_book': sum_book,
                   'freight': freight}
            shipping_time = datetime.now() + timedelta(days=3)
            db_conn.close_conn()
            return {'book_list': book_list, 'books_price': books_price, 'pay': pay, 'shipping_time': shipping_time,
                    'addr': addr}
        except Exception as e:
            db_conn.close_conn()
            logging.exception(e)
    else:
        try:
            book_num = 1
            book_list = []
            sum_price = 0.0
            freight = 0.0
            package = 1
            discount = 1.01
            sum_book = 0
            mydb = get_book(books_id)
            mydb['_id'] = books_id
            mydb['book_num'] = book_num
            mydb['sum_price'] = round(float(mydb['price']) * book_num, 2)
            if book_num > mydb.get('stock'):
                return {'error': '{} 没有这么多库存啦～'.format(mydb.get('title'))}
            book_list.append(mydb)
            sum_price = sum_price + round(float(mydb['price']) * book_num, 2)
            sum_book = sum_book + book_num
            user = get_user(user_id)
            addr = {}
            if user['address_default'] is None or user['address_default'] is '':
                addr = {}
            else:
                address = db_conn.get_col('address').find({'_id': ObjectId(user['address_default'])})
                for a in address:
                    addr['name'] = a['name']
                    addr['tel'] = a['tel']
                    addr['province'] = a['province']
                    addr['city'] = a['city']
                    addr['district'] = a['district']
                    addr['details'] = a['details']
                    addr['_id'] = user['address_default']
            books_price = {'sum_price': sum_price, 'freight': freight, 'package': package,
                           'sum': round(sum_price + freight - discount, 2), 'discount': discount}
            pay = {'amount_pay': round(sum_price + freight - discount, 2), 'sum_book': sum_book,
                   'freight': freight}
            shipping_time = datetime.now() + timedelta(days=3)
            db_conn.close_conn()
            return {'book_list': book_list, 'books_price': books_price, 'pay': pay, 'shipping_time': shipping_time,
                    'addr': addr}
        except Exception as e:
            db_conn.close_conn()
            print('========get_buy=========:', e)


def from_cart_buy(books, user_id):
    """购物车"""
    book_list = []
    for book_id in books:
        db = ToConn()
        sql = 'select book_num from cart where user_id=%s and book_id=%s and is_effe=1'
        book_num = db.get_db(sql, (user_id, book_id)).fetchone()
        mydb = get_book(book_id)
        mydb['_id'] = book_id
        mydb['book_num'] = book_num['book_num']
        mydb['sum_price'] = round(float(mydb['price']) * float(book_num['book_num']), 2)
        book_list.append(mydb)
    return book_list


def edit_cart_num(user_id, book_id, count=0, method='delete'):
    """编辑购物车数量"""
    db = ToConn()
    query = (count, user_id, book_id)
    sql = 'delete from cart  where book_num=%s and user_id=%s and book_id=%s and is_effe=1'
    if method == 'adds':
        sql = 'update cart set book_num=%s where user_id=%s and book_id=%s and is_effe=1'
        if count + 1 >= get_book(book_id).get('stock'):
            count = count
        else:
            count = count + 1
    elif method == 'reduces':
        sql = 'update  cart set book_num=%s where user_id=%s and book_id=%s and is_effe=1'
        count = count - 1
    elif method == 'deletes':
        sql = 'delete from cart where user_id=%s and is_effe=1 and book_id in %s'
        query = (user_id, book_id)
        count = 1
    db.to_db(sql, query).commit()
    db.to_close()
    logging.info('sql:[%s]', sql)
    return count


def get_user_cart(user_id):
    """获取购物物品信息"""
    db = ToConn()
    sql = 'select book_id, book_num from cart where user_id=%s and is_effe=1'
    result = db.get_db(sql, (user_id,)).fetchall()
    books = []
    for book_id in result:
        book_num = book_id.get('book_num')
        b1 = get_book(book_id.get('book_id'), False)
        b1['book_num'] = book_num
        b1['sum_price'] = round((int(book_num) * float(b1.get('price'))), 2)
        books.append(b1)
    return books


def add_card_model(user_id, book_id, num):
    """添加到购物车"""
    try:
        stock = int(get_book(book_id).get('stock'))  # 获取库存
        db = ToConn()
        # 查处用户的购物车是否有添加的物品
        sql = 'select * from cart where book_id=%s and user_id=%s and is_effe=1'
        get_db = db.get_db(sql, (book_id, user_id)).fetchone()
        # 执行完查询后链接自动关闭了，所以要重新创建一个新的链接
        db2 = ToConn()
        if get_db:
            if int(get_db.get('book_num')) + num > stock:
                return {'error': '没有这么多库存啦～'}
            # 购物车已有则将数量加入数据库
            sql = 'update cart set book_num=book_num+%s where book_id=%s and user_id=%s'
            to_db = db2.to_db(sql, (int(num), book_id, user_id))
            to_db.commit()
            db2.to_close()
        else:
            if num > stock:
                return {'error': '没有这么多库存啦～'}
            # 否则添加新的物品
            sql = 'insert into cart(user_id, book_id, book_num) values (%s,%s,%s)'
            to_db = db2.to_db(sql, (user_id, book_id, num))
            to_db.commit()
            db2.to_close()
            logging.info('%s：添加[%s：%s]到购物车', user_id, book_id, num)
    except Exception as e:
        print('===============', e)
        # 发生错误回滚
        to_db.rollback()
        db2.to_close()


def get_user(id):
    """获取用户信息"""
    db = ToConn()
    user = db.get_db('select * from users where id=%s', (id,)).fetchone()
    return user


def get_book(id, query_off_shelf=True):
    """获取图书信息"""
    mydb = ToMongo()
    mycol = mydb.get_col('books')
    if query_off_shelf:
        book = mycol.find_one({'_id': ObjectId(id), 'is_off_shelf': 0})
    else:
        book = mycol.find_one({'_id': ObjectId(id)})
    # 添加点击量
    mydb.update('books', {'_id': ObjectId(id)}, {'$inc': {'hits': 1}})
    mydb.close_conn()
    return book


def add_hits_cf(user_id, book_id):
    conn = ToMongo()
    result = conn.update('hits_data', {'_id': str(user_id),'book_ids': {'$nin': [book_id]}}, {'$push': {'book_ids': book_id}})
    conn.close_conn()

if __name__ == '__main__':
    print(get_recommend_book_model(''))
    # print(get_user_avatar(5))
