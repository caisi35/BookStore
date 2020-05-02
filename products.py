from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, jsonify
)
from db import ToConn, ToMongo
from werkzeug.exceptions import abort
from user import login_required
from bson.objectid import ObjectId
import time, random, base64
from datetime import datetime, timedelta
bp = Blueprint('products', __name__)


# 主页
@bp.route('/')
def index():
    db = ToConn()
    user = db.get_db('select * from users').fetchone()
    mydb = ToMongo()
    books = mydb.get_col('books').find().limit(15)
    new_books = mydb.get_col('books').find().skip(15).limit(12)
    book_top = mydb.get_col('books').find().sort("price", -1).limit(5)
    book_top2 = mydb.get_col('books').find().sort("price_m", -1).limit(5)
    return render_template('products/index.html', user=user, books=books, new_books=new_books,
                           book_top=book_top, book_top2=book_top2)


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


# 展示product图书详情页,立即购买按钮
@bp.route('/product?<string:id>', methods=('GET', 'POST'))
def product(id):
    book = get_book(id)
    user_id = session.get('user_id')
    user = get_user(user_id)
    # post 请求提交需要加入到购物车的数据，并且加载成功页面
    if request.method == 'POST':
        if user_id is None:
            return redirect(url_for('user.login'))
        db = ToConn()
        num = request.form.get('num', 0, type=int)
        book_id = request.form.get('book_id')
        try:
            sql = 'select * from cart where book_id=%s and user_id=%s and is_effe=1'
            get_db = db.get_db(sql, (book_id, user_id)).fetchone()
            # 执行完查询后链接自动关闭了，所以要重新创建一个新的链接
            db2 = ToConn()
            if get_db:
                sql = 'update cart set book_num=book_num+%s where book_id=%s and user_id=%s'
                to_db = db2.to_db(sql, (int(num), book_id, user_id))
                to_db.commit()
                db2.to_close()
            else:
                sql = 'insert into cart(user_id, book_id, book_num) values (%s,%s,%s)'
                to_db = db2.to_db(sql, (user_id, book_id, num))
                to_db.commit()
                db2.to_close()
            return render_template('products/success.html', user=user, book=book, num=num)
        except Exception as e:
            print('===============', e)
            # 发生错误回滚
            to_db.rollback()
            db2.to_close()
            abort(403)
    return render_template('products/product.html', book=book, user=user)


# 购物车
@bp.route('/cart', methods=('GET', 'POST'))
@login_required
def cart():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('user.login'))
    user = get_user(user_id)
    books = []
    try:
        db = ToConn()
        sql = 'select book_id, book_num from cart where user_id=%s and is_effe=1'
        result = db.get_db(sql, (user_id,)).fetchall()
        books = []
        for book_id in result:
            b1 = get_book(book_id['book_id'])
            b1['book_num'] = book_id['book_num']
            b1['sum_price'] = round((int(book_id['book_num']) * float(b1['price'])), 2)
            books.append(b1)
    except Exception as e:
        print('========cart=========:', e)
    return render_template('products/cart.html', books=books, user=user)


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


# 下单购买、立即购买，由于不经过购物车，到直接结算
@bp.route('/buy', methods=('GET', 'POST'))
@login_required
def buy():
    user_id = session.get('user_id')
    book_id = request.args.get('book_id')
    book_num = request.args.get('num', 1, float)
    if user_id is None:
        return redirect(url_for('user.login'))
    book_list = []
    sum_price = 0.0
    freight = 0.0
    package = 1
    discount = 1.01
    sum_book = 0
    mydb = get_book(book_id)
    mydb['_id'] = book_id
    mydb['book_num'] = book_num
    mydb['sum_price'] = round(float(mydb['price']) * book_num, 2)
    book_list.append(mydb)
    sum_price = sum_price + round(float(mydb['price']) * book_num, 2)
    sum_book = sum_book + book_num
    return render_template('buyCart/buy_list.html',
                           user=get_user(session.get('user_id')),
                           books=book_list,
                           books_price={'sum_price': sum_price, 'freight': freight, 'package': package,
                                        'sum': round(sum_price + freight - discount, 2), 'discount': discount},
                           pay={'amount_pay': round(sum_price + freight - discount, 2), 'sum_book': sum_book,
                                'freight': freight})
    # return render_template('products/buy.html', book=book, user=user)


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
        return redirect(url_for('products.cart'))
        print('========count_buy=========:', e)

    if book_list:
        return jsonify(result=book_list)
    else:
        return jsonify()


# 购物车选择物品下单
@bp.route('/buy_list', methods=('GET', 'POST'))
@login_required
def buy_list():
    book_id = request.args.get('book_list')
    book_id_list = list(book_id.split(','))
    user_id = session.get('user_id')
    book_list = []
    sum_price = 0.0
    freight = 0.0
    package = 1
    discount = 1.01
    sum_book = 0
    try:
        user = get_user(session.get('user_id'))
        addr = ToMongo().get_col('address').find({'_id': ObjectId(user['address_default'])})
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
        return render_template('buyCart/buy_list.html',
                               user=user,
                               books=book_list,
                               books_price={'sum_price': sum_price, 'freight': freight, 'package': package,
                                            'sum': round(sum_price + freight - discount, 2), 'discount': discount},
                               pay={'amount_pay': round(sum_price + freight - discount, 2), 'sum_book': sum_book,
                                    'freight': freight},
                               address=addr,
                               shipping_time=datetime.now()+timedelta(days=3))
    except Exception as e:
        print('========buy_list=========:', e)
        return redirect(url_for('products.cart'))


# t添加与修改收货人信息
@bp.route('/address', methods=('POST',))
def address():
    try:
        name = request.form.get('name')
        tel = request.form.get('tel')
        province = request.form.get('province')
        city = request.form.get('city')
        details = request.form.get('details')
        user_id = session.get('user_id')
        mydb = ToMongo()
        value = {
            'user_id': user_id,
            'name': name,
            'tel': tel,
            'province': province,
            'city': city,
            'details': details,
        }
        address_default = mydb.insert('address', value).inserted_id
        conn = ToConn().to_execute()
        cur = conn.cursor()
        cur.execute('update users set address_default=%s where id=%s', (str(address_default), user_id))
    except Exception as e:
        conn.rollback()
        conn.close()
        print('========address=========:', e)
    else:
        conn.commit()
        conn.close()
    return redirect(request.referrer)


# 删除收货人信息
@bp.route('/addr_delete', methods=('GET', 'POST'))
def addr_delete():
    try:
        _id = request.form.get('_id')
        user_id = session.get('user_id')
        result = ToMongo().delete(col='address', doc={'_id': ObjectId(_id)}).raw_result
        if result['ok'] == 1:
            conn = ToConn().to_execute()
            cur = conn.cursor()
            cur.execute('update users set address_default=null where id=%s and address_default = %s', (user_id, _id))
        return jsonify(result=request.referrer)
    except Exception as e:
        print('========addr_delete=========:', e)


# 支付页面方法
@bp.route('/to_pay', methods=('GET', 'POST'))
@login_required
def to_pay():
    amount = request.form.get('amount_pay', 0.0, float)
    book_ids = request.form.getlist('books[]')
    order_no = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time()))) + str(random.randint(100001, 999999))
    mydb = ToMongo()
    user_id = session.get('user_id')
    create_time = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    books = []
    try:
        for book_id in book_ids:
            db = ToConn()
            sql = 'select book_num from cart where user_id=%s and book_id=%s and is_effe=1'
            book_num = db.get_db(sql, (user_id, book_id)).fetchone()
            books.append({'book_num': int(book_num['book_num']), 'book_id': book_id})
        v = {"amount": amount, "books": books, "order_no": order_no, "is_processed": 0, "user_id": user_id,
             "create_time": create_time, "is_effective": 1, }
        result = mydb.insert('order', v)
        if result:
            db = ToConn()
            conn = db.to_execute()
            cursor = conn.cursor()
            try:
                for book_id in book_ids:
                    # sql = 'update cart set is_effe=1 where user_id=%s and book_id=%s'
                    sql = 'delete from cart where user_id=%s and book_id=%s'
                    cursor.execute(sql, (user_id, book_id))
            except Exception as e:
                print('========to_pay=========事务处理失败:', e)
                conn.rollback()  # 事务回滚
            else:
                conn.commit()  # 事务提交
            db.to_close()
    except Exception as e:
        print('========to_pay=========:', e)
    return jsonify(result=order_no)


@bp.route('/pay', methods=('GET', 'POST'))
@login_required
def pay():
    user_id = session.get('user_id')
    if request.method == 'POST':
        pay_method = request.form.get('pay')
        if pay_method == '微信支付':
            print('==========', pay_method)
            return render_template('buyCart/go_pay.html', user=session.get('user_id'), pay_method=pay_method)
        elif pay_method == '支付宝支付':
            return render_template('buyCart/go_pay.html', user=session.get('user_id'), pay_method=pay_method)
        else:
            return redirect(url_for('products.cart'))
    else:
        mydb = ToMongo()
        images = []
        try:
            order_no = request.args.get('order_no')

            weixin_image = base64.b64encode(mydb.get_img('weixin.gif')).decode('utf-8')
            zhifubao_image = base64.b64encode(mydb.get_img('zhifubao.gif')).decode('utf-8')
            images.append({'data': weixin_image, 'name': '微信支付'})
            images.append({'data': zhifubao_image, 'name': '支付宝支付'})
            my_orders = mydb.get_col('order').find({"user_id": user_id, "is_effective": 1, 'order_no': order_no})
        except Exception as e:
            print('========pay=========:', e)
        return render_template('buyCart/pay.html', user=get_user(session.get('user_id')), orders=my_orders,
                               images=images)


@bp.route('/order', methods=('GET', 'POST'))
@login_required
def order():
    user = get_user(session.get('user_id'))
    try:
        order_no = request.args.get('order_no', '')
        mydb = ToMongo()
        myorder = mydb.get_col('order').find_one({'order_no': order_no, 'user_id': session.get('user_id')})
    except Exception as e:
        print('========order=========:', e)
    return render_template('buyCart/order.html', user=user, order_no=myorder, order_n=[1, 2, 3, 4])


# 搜索功能的模糊查询
def get_like_books(word):
    try:
        mydb = ToMongo()
        book_list = []
        mycol = mydb.get_col('books')
        books = mycol.find({'$or': [{'press': {"$regex": word}}, {'title': {"$regex": word}},
                                    {'subheading': {"$regex": word}}, {'author': {"$regex": word}}]})
        for book in books:
            book_list.append(book)
        return book_list
    except Exception as e:
        print('========get_like_books=========', e)


# 搜索功能
@bp.route('/search', methods=('GET', 'POST'))
def search():
    try:
        word = request.values.get('word')
    except Exception as e:
        print('=========search=========', e)
    books = get_like_books(word)
    # if request.method == 'POST':
    #     book_id = request.values.get('book_id')
    #     book = get_book(book_id)
    user_id = session.get('user_id')
    if request.method == 'POST':
        if user_id is None:
            return redirect(url_for('user.login'))
        db = ToConn()
        num = request.form.get('num', 1, type=int)
        book_id = request.form.get('book_id')
        try:
            sql = 'select * from cart where book_id=%s and user_id=%s and is_effe=1'
            get_db = db.get_db(sql, (book_id, user_id)).fetchone()
            # 执行完查询后链接自动关闭了，所以要重新创建一个新的链接
            db2 = ToConn()
            if get_db:
                sql = 'update cart set book_num=book_num+%s where book_id=%s and user_id=%s'
                to_db = db2.to_db(sql, (int(num), book_id, user_id))
                to_db.commit()
                db2.to_close()
            else:
                sql = 'insert into cart(user_id, book_id, book_num) values (%s,%s,%s)'
                to_db = db2.to_db(sql, (user_id, book_id, num))
                to_db.commit()
                db2.to_close()
            return render_template('products/success.html', user=get_user(user_id), book=get_book(book_id))
        except Exception as e:
            print('===============', e)
            # 发生错误回滚
            to_db.rollback()
            db2.to_close()
            abort(403)
    else:
        return render_template('products/search.html', books=books)
