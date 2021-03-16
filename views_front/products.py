import inspect
import logging
from werkzeug.exceptions import abort
from flask import (
    Blueprint, redirect, render_template, request, url_for, session, jsonify
)
from models.choice_type import choice_book_type
from models.front_models import (
    index_model,
    get_book,
    get_user,
    add_card_model,
    get_user_cart,
    edit_cart_num,
    from_cart_buy,
    to_buy_model,
    update_addr,
    delete_addr,
    to_pay_model,
    pay_model,
    search_book_model,
    get_evaluate,
)
from views_front.user import login_required
from utils import (
    Logger
)
bp = Blueprint('products', __name__)
logger = Logger('products.log')


@bp.route('/')
def index():
    """主页"""
    books, new_books, book_top, book_top2 = index_model()
    book_type_list = choice_book_type()
    return render_template('front/index_products/index.html',
                           books=books,
                           new_books=new_books,
                           book_top=book_top,
                           book_top2=book_top2,
                           book_type_list=book_type_list,
                           )


@bp.route('/product?<string:id>', methods=('GET', 'POST'))
def product(id):
    """展示product图书详情页"""
    book = get_book(id)
    evaluates, total, evaluates_details = get_evaluate(id)
    book_type_list = choice_book_type()
    return render_template('front/index_products/product.html',
                           book=book,
                           book_type_list=book_type_list,
                           evaluates= evaluates,
                           total=total,
                           evaluates_details=evaluates_details
                           )


@bp.route('/product/add_to_cart', methods=['GET'])
@login_required
def add_to_cart():
    """将物品加入到购物车"""
    user_id = session.get('user_id')
    num = request.args.get('num', 0, type=int)
    book_id = request.args.get('book_id')
    add_card_model(user_id, book_id, num)
    book = get_book(book_id)
    book_type_list = choice_book_type()
    return render_template('front/index_products/add_cart_success.html',
                           book=book,
                           num=num,
                           book_type_list=book_type_list,
                           )


@bp.route('/cart', methods=('GET', 'POST'))
@login_required
def cart():
    """购物车"""
    try:
        user_id = session.get('user_id')
        books = get_user_cart(user_id)
        return render_template('front/index_products/cart.html',
                               books=books)
    except Exception as e:
        logging.exception(e)
        return abort(404)


@bp.route('/count_numbers', methods=['GET', 'POST'])
@login_required
def add_numbers():
    """购物车图书数量修改"""
    input_count = request.form.get('count_', 0, type=int)
    method = request.form.get('method_', '', type=str)
    book_id = request.form.get('book_id', '', type=str)
    user_id = session.get('user_id')
    count = edit_cart_num(user_id, book_id, input_count, method)
    logging.info('%s change cart num from %s to %s.', user_id, input_count, count)
    return jsonify(result=count)


@bp.route('/count_buy', methods=('GET', 'POST'))
@login_required
def count_buy():
    """购物车下单结算"""
    books = request.form.getlist('data[]')
    user_id = session.get('user_id')
    books = from_cart_buy(books, user_id)
    return jsonify(result=books)


@bp.route('/buy_list', methods=('GET', 'POST'))
@bp.route('/buy_now', methods=('GET', 'POST'))
@login_required
def buy():
    """购物车选择物品下单"""
    try:
        book_id = request.args.get('book_id')
        user_id = session.get('user_id')
        if 'buy_now' in request.url:
            book_list, books_price, pay, shipping_time, addr = to_buy_model(user_id, book_id, is_list=False)
        else:
            book_list, books_price, pay, shipping_time, addr = to_buy_model(user_id, book_id)
        logging.info('%s buy %s', user_id, book_id)
        return render_template('front/settle_pay/settle_from_list.html',
                               books=book_list,
                               books_price=books_price,
                               pay=pay,
                               addr=addr,
                               shipping_time=shipping_time)
    except Exception as e:
        logging.error('buy find error: %s', e)
        return redirect(url_for('products.cart'))


@bp.route('/address', methods=('POST',))
@login_required
def address():
    """添加与修改收货人信息"""
    try:
        user_id = session.get('user_id')
        update_addr(user_id, request)
        return redirect(request.referrer)
    except Exception as e:
        logging.error('"address" route find error: %s', e)
    return redirect(url_for('products.buy_list'))


@bp.route('/addr_delete', methods=('GET', 'POST'))
@login_required
def addr_delete():
    """删除收货人信息"""
    try:
        _id = request.form.get('_id')
        user_id = session.get('user_id')
        delete_addr(user_id, _id)
        return jsonify()
    except Exception as e:
        print('========addr_delete=========:', e)


@bp.route('/to_pay', methods=('GET', 'POST'))
@login_required
def to_pay():
    """结算页面的去支付方法"""
    amount = request.form.get('amount_pay', 0.0, float)
    book_ids = request.form.getlist('books[]')
    addr_id = request.form.get('addr_id')
    user_id = session.get('user_id')
    order_no = to_pay_model(user_id, amount, book_ids, addr_id)
    return jsonify(result=order_no)


@bp.route('/pay', methods=('GET', 'POST'))
@login_required
def pay():
    try:
        order_no = request.args.get('order_no')
        my_orders, images = pay_model(order_no)
        return render_template('front/settle_pay/pay.html', user=get_user(session.get('user_id')),
                               orders=my_orders,
                               images=images)
    except Exception as e:
        print('========pay=========:', e)
        return abort(403)


@bp.route('/search', methods=('GET',))
def search():
    """搜索功能"""
    word = request.values.get('word')
    page = request.values.get('page', 0, type=int)
    page_size = request.values.get('page_size', 15, type=int)
    try:
        books, count = search_book_model(word, page, page_size)
    except Exception as e:
        logging.exception('front -> products -> search -> search_book_model [Exception]:%s', e)
        return redirect('/')
    return render_template('front/index_products/search.html',
                           def_url=inspect.stack()[0][3],
                           books=books,
                           key_word=word,
                           active_page=page,
                           total=count,
                           page_size=page_size,
                           page_count=5,
                           search=True,
                           )
