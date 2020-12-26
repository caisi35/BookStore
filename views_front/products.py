from flask import (
    Blueprint, redirect, render_template, request, url_for, session, jsonify
)
from models import ToConn, ToMongo, get_like_books
from models.choice_type import choice_book_type
from werkzeug.exceptions import abort
from views_front.user import login_required
from bson.objectid import ObjectId
import time, random, base64, inspect
from datetime import datetime, timedelta
from utils import format_time_second
bp = Blueprint('products', __name__)


# 主页
@bp.route('/')
def index():
    mydb = ToMongo()
    # 轮播
    books = mydb.get_col('books').find().limit(15)
    new_books = mydb.get_col('books').find().skip(15).limit(12)
    book_top = mydb.get_col('books').find().sort("price", -1).limit(5)
    book_top2 = mydb.get_col('books').find().sort("sales", -1).limit(5)
    book_type_list = choice_book_type()
    return render_template('products/index.html',
                           books=books,
                           new_books=new_books,
                           book_top=book_top,
                           book_top2=book_top2,
                           book_type_list=book_type_list)


# 获取图书信息
def get_book(id):
    mydb = ToMongo()
    mycol = mydb.get_col('books')
    book = mycol.find_one({'_id': ObjectId(id)})
    if book is None:
        abort(404, "Book id {0} Doesn't Exist.".format(id))
    if str(book['_id']) != str(id):
        abort(403)
    return book


# 获取用户信息
def get_user(id):
    db = ToConn()
    user = db.get_db('select * from users where id=%s', (id,)).fetchone()
    if user is None:
        return redirect(url_for('user.login'))
    if id != user['id']:
        return redirect(url_for('user.login'))
    return user


# 展示product图书详情页
@bp.route('/product?<string:id>', methods=('GET', 'POST'))
def product(id):
    book = get_book(id)
    # 添加点击量
    ToMongo().update('books', {'_id': ObjectId(book['_id'])}, {'$inc': {'hits': 1}})
    return render_template('products/product.html', book=book)


# 将物品加入到购物车
@bp.route('/product/add_to_cart', methods=('GET', 'POST'))
@login_required
def add_to_cart():
    user_id = session.get('user_id')
    if request.method == 'POST':
        db = ToConn()
        num = request.form.get('num', 0, type=int)
        book_id = request.form.get('book_id')
        try:
            # 查处用户的购物车是否有添加的物品
            sql = 'select * from cart where book_id=%s and user_id=%s and is_effe=1'
            get_db = db.get_db(sql, (book_id, user_id)).fetchone()
            # 执行完查询后链接自动关闭了，所以要重新创建一个新的链接
            db2 = ToConn()
            if get_db:
                # 购物车已有则将数量加入数据库
                sql = 'update cart set book_num=book_num+%s where book_id=%s and user_id=%s'
                to_db = db2.to_db(sql, (int(num), book_id, user_id))
                to_db.commit()
                db2.to_close()
            else:
                # 否则添加新的物品
                sql = 'insert into cart(user_id, book_id, book_num) values (%s,%s,%s)'
                to_db = db2.to_db(sql, (user_id, book_id, num))
                to_db.commit()
                db2.to_close()
            return render_template('products/addToCartSuccess.html', book=get_book(book_id), num=num)
        except Exception as e:
            print('===============', e)
            # 发生错误回滚
            to_db.rollback()
            db2.to_close()
            abort(404)


# 购物车
@bp.route('/cart', methods=('GET', 'POST'))
@login_required
def cart():
    try:
        user_id = session.get('user_id')
        db = ToConn()
        sql = 'select book_id, book_num from cart where user_id=%s and is_effe=1'
        result = db.get_db(sql, (user_id,)).fetchall()
        books = []
        for book_id in result:
            b1 = get_book(book_id['book_id'])
            b1['book_num'] = book_id['book_num']
            b1['sum_price'] = round((int(book_id['book_num']) * float(b1['price'])), 2)
            books.append(b1)
        return render_template('products/cart.html', books=books)
    except Exception as e:
        print('========cart=========:', e)
        return abort(404)


# 购物车图书数量修改
@bp.route('/count_numbers', methods=['GET', 'POST'])
@login_required
def add_numbers():
    count = request.form.get('count_', 0, type=int)
    method = request.form.get('method_', '', type=str)
    book_id = request.form.get('book_id', '', type=str)
    user_id = session.get('user_id')
    if method == 'adds':
        db = ToConn()
        sql = 'update cart set book_num=%s where user_id=%s and book_id=%s and is_effe=1'
        count = count + 1
        db.to_db(sql, (count, user_id, book_id)).commit()
        db.to_close()
        return jsonify(result=count)
    elif method == 'reduces' and count >= 1:
        db = ToConn()
        sql = 'update  cart set book_num=%s where user_id=%s and book_id=%s and is_effe=1'
        count = count - 1
        db.to_db(sql, (count, user_id, book_id)).commit()
        db.to_close()
        return jsonify(result=count)
    elif method == 'delete' and count == 1:
        db = ToConn()
        sql = 'delete from cart  where user_id=%s and book_id=%s and book_num=%s and is_effe=1'
        db.to_db(sql, (user_id, book_id, count)).commit()
        db.to_close()
        return jsonify(result=0)


# 购物车下单结算
@bp.route('/count_buy', methods=('GET', 'POST'))
@login_required
def count_buy():
    list = request.form.getlist('data[]')
    user_id = session.get('user_id')
    book_list = []
    try:
        for book_id in list:
            db = ToConn()
            sql = 'select book_num from cart where user_id=%s and book_id=%s and is_effe=1'
            book_num = db.get_db(sql, (user_id, book_id)).fetchone()
            mydb = get_book(book_id)
            mydb['_id'] = book_id
            mydb['book_num'] = book_num['book_num']
            mydb['sum_price'] = round(float(mydb['price']) * float(book_num['book_num']), 2)
            book_list.append(mydb)
    except Exception as e:
        print('========count_buy=========:', e)
        return redirect(url_for('products.cart'))

    if book_list:
        return jsonify(result=book_list)
    else:
        return jsonify()


# 结算
def get_buy(user_id, books_id, is_list=True):
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
            user = get_user(session.get('user_id'))
            if user['address_default'] is None or user['address_default'] is '':
                addr = {}
            else:
                address = ToMongo().get_col('address').find({'_id': ObjectId(user['address_default'])})
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
                book_list.append(mydb)
                sum_price = sum_price + round(float(mydb['price']) * float(book_num['book_num']), 2)
                sum_book = sum_book + int(book_num['book_num'])
            books_price = {'sum_price': sum_price, 'freight': freight, 'package': package,
                           'sum': round(sum_price + freight - discount, 2), 'discount': discount}
            pay = {'amount_pay': round(sum_price + freight - discount, 2), 'sum_book': sum_book,
                   'freight': freight}
            shipping_time = datetime.now() + timedelta(days=3)
            return book_list, books_price, pay, shipping_time, addr
        except Exception as e:
            print('========get_buy_list=========:', e)
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
            book_list.append(mydb)
            sum_price = sum_price + round(float(mydb['price']) * book_num, 2)
            sum_book = sum_book + book_num
            user = get_user(session.get('user_id'))
            addr = {}
            if user['address_default'] is None or user['address_default'] is '':
                addr = {}
            else:
                address = ToMongo().get_col('address').find({'_id': ObjectId(user['address_default'])})
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
            return book_list, books_price, pay, shipping_time, addr
        except Exception as e:
            print('========get_buy=========:', e)


# 购物车选择物品下单
@bp.route('/buy_list', methods=('GET', 'POST'))
@login_required
def buy_list():
    try:
        book_id = request.args.get('book_list')
        user_id = session.get('user_id')
        book_list, books_price, pay, shipping_time, addr = get_buy(user_id, book_id)
        return render_template('buyCart/buy_list.html',
                               books=book_list,
                               books_price=books_price,
                               pay=pay,
                               addr=addr,
                               shipping_time=shipping_time)
    except Exception as e:
        print('========buy_list=========:', e)
        return redirect(url_for('products.cart'))


# 下单购买、立即购买，由于不经过购物车，到直接结算
@bp.route('/buy_now', methods=('GET', 'POST'))
@login_required
def buy_now():
    book_id = request.args.get('book_id')
    user_id = session.get('user_id')
    book_list, books_price, pay, shipping_time, addr = get_buy(user_id, book_id, is_list=False)
    return render_template('buyCart/buy_list.html',
                           books=book_list,
                           books_price=books_price,
                           pay=pay,
                           addr=addr,
                           shipping_time=shipping_time)


# 添加与修改收货人信息
@bp.route('/address', methods=('POST',))
@login_required
def address():
    try:
        name = request.form.get('name')
        tel = request.form.get('tel')
        address_list = request.form.get('address').strip().split(' ')
        details = request.form.get('details')
        user_id = session.get('user_id')
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
        return redirect(request.referrer)
    except Exception as e:
        print('========address=========:', e)
    return redirect(url_for('products.buy_list'))


# 删除收货人信息
@bp.route('/addr_delete', methods=('GET', 'POST'))
@login_required
def addr_delete():
    try:
        _id = request.form.get('_id')
        user_id = session.get('user_id')
        conn = ToConn().to_execute()
        cur = conn.cursor()
        cur.execute('update users set address_default=null where id=%s and address_default = %s', (user_id, _id))
        result = ToMongo().delete(col='address', doc={'_id': ObjectId(_id)}).raw_result
        if result['ok'] == 1:
            # mongodb 删除成功提交
            conn.commit()
        else:
            # mongodb 删除失败回滚
            conn.rollback()
        return jsonify()
    except Exception as e:
        print('========addr_delete=========:', e)


# 结算页面的去支付方法
@bp.route('/to_pay', methods=('GET', 'POST'))
@login_required
def to_pay():
    amount = request.form.get('amount_pay', 0.0, float)
    book_ids = request.form.getlist('books[]')
    order_no = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time()))) + str(random.randint(100001, 999999))
    user_id = session.get('user_id')
    create_time = int(time.time())
    books = []
    try:
        # 获取收货地址,写入订单号详情
        address_cur = ToConn().get_db('select address_default from users where id=%s', (user_id,)).fetchone()
        address = ToMongo().get_col('address').find_one(
            {'user_id': user_id, '_id': ObjectId(address_cur['address_default'])})

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
             "exp_status": 0, }
        mydb = ToMongo()
        result = mydb.insert('order', v)
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
                    ToMongo().update('books', {'_id': ObjectId(book_id)}, {'$inc': {'sales': 1}})
            db.to_close()
    except Exception as e:
        print('========to_pay=========:', e)
    return jsonify(result=order_no)


@bp.route('/pay', methods=('GET', 'POST'))
@login_required
def pay():
    try:
        mydb = ToMongo()
        images = []
        order_no = request.args.get('order_no')
        weixin_image = base64.b64encode(mydb.get_img('weixin.gif')).decode('utf-8')
        zhifubao_image = base64.b64encode(mydb.get_img('zhifubao.gif')).decode('utf-8')
        images.append({'data': weixin_image, 'name': '微信支付'})
        images.append({'data': zhifubao_image, 'name': '支付宝支付'})
        my_orders = mydb.get_col('order').find({"is_effective": 1, 'order_no': order_no})
        return render_template('buyCart/pay.html', user=get_user(session.get('user_id')), orders=list(my_orders),
                               images=images)
    except Exception as e:
        print('========pay=========:', e)
        return abort(403)


# 订单号
@bp.route('/order', methods=('GET', 'POST'))
@login_required
def order():
    try:
        orderNo = request.args.get('order_no', '')
        mydb = ToMongo()
        myorder = mydb.get_col('order').find_one({'order_no': orderNo, 'user_id': session.get('user_id')})
        data = {'order_no': myorder.get('order_no'),
                'amount': myorder.get('amount'),
                'create_time': format_time_second(myorder.get('create_time'))}

        return render_template('buyCart/order.html', order_no=data)
    except Exception as e:
        print('========order=========:', e)
        return abort(403)


# 搜索功能
@bp.route('/search', methods=('GET',))
def search():
    try:
        word = request.values.get('word')
        page = request.values.get('page', 1, type=int)
        page_size = request.values.get('page_size', 15, type=int)
        if page != 0:
            page = page - 1
        # 如果输入不为空
        if word:
            # 添加关键字数据到数据库，用与绘制词云图
            ToMongo().update('keyword', {'_id': 'keyword'}, {'$inc': {word: 1}})
            books, count = get_like_books(word, page, page_size)
        # 如果输入为空，则显示点击量前十的
        else:
            books = ToMongo().get_col('books').find().sort('hits', -1).skip(page * page_size).limit(page_size)
            count = ToMongo().get_col('books').find().count()
        result_list = list(books)
        if page == 0:
            page = 1
        book_type_list = choice_book_type()
        return render_template('products/search.html',
                               def_url=inspect.stack()[0][3],
                               books=result_list,
                               key_word=word,
                               active_page=page,
                               total=count,
                               page_size=page_size,
                               page_count=5,
                               book_type_list=book_type_list,
                               search=True,
                               )
    except Exception as e:
        print('=========search=========', e)
        return redirect('/')
