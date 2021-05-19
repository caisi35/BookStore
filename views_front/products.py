import inspect
import logging
from werkzeug.exceptions import abort
from flask import (
    Blueprint, redirect, render_template, request, url_for, session, jsonify, flash
)
from models.choice_type import choice_book_type
from models.front_models import (
    index_model,
    get_book,
    get_user,
    add_card_model,
    get_user_cart,
    edit_cart_num,
    get_recommend_book_model,
    to_buy_model,
    update_addr,
    delete_addr,
    to_pay_model,
    pay_model,
    search_book_model,
    get_evaluate,
    get_recommend_user_book_model,
    get_recommend_cart_book_model,
    to_collection_model,
    is_collection_model,
    add_history,
    add_hits_cf,
)
from views_front.user import login_required
from utils import (
    Logger,
    get_dir_files,
)

bp = Blueprint('products', __name__)
logger = Logger('products.log')


@bp.route('/')
def index():
    """主页"""
    books, new_books, book_top, book_top2 = index_model()
    book_type_list = choice_book_type()
    banner_images = get_dir_files('static/images/banner')
    return render_template('front/index_products/index.html',
                           books=books,
                           new_books=new_books,
                           book_top=book_top,
                           book_top2=book_top2,
                           book_type_list=book_type_list,
                           banner_images=banner_images,
                           )


@bp.route('/product?<string:id>', methods=('GET', 'POST'))
def product(id):
    """展示product图书详情页"""
    book = get_book(id)
    page_size = 10
    page_count = 5
    evaluates, total, evaluates_details = get_evaluate(id, page_size=page_size)
    book_type_list = choice_book_type()
    user_id = session.get('user_id')
    is_collection = False
    if user_id:
        try:
            add_hits_cf(user_id, id)
            add_history(user_id, id)
            is_collection = is_collection_model(user_id, id)
        except Exception as e:
            logging.exception('[product]:[%s]\n[%s]' % (user_id, e))
    return render_template('front/index_products/product.html',
                           book=book,
                           book_type_list=book_type_list,
                           evaluates=evaluates,
                           total=total,
                           evaluates_details=evaluates_details,
                           active_page=0,
                           page_count=page_count,
                           page_size=page_size,
                           is_collection=is_collection,
                           )


@bp.route('/product_page', methods=('GET', 'POST'))
def product_page():
    """展示product图书详情页"""
    id = request.args.get('id')
    page = request.args.get('page', 0, int)
    book = get_book(id)
    page_size = 10
    page_count = 5
    if page:
        evaluates, total, evaluates_details = get_evaluate(id, page, page_size)
    else:
        evaluates = []
        total = 0
        evaluates_details = {'praise': 0, 'mid': 0, 'negative': 0}
    book_type_list = choice_book_type()
    user_id = session.get('user_id')
    is_collection = False
    if user_id:
        try:
            add_hits_cf(user_id, id)
            add_history(user_id, id)
            is_collection = is_collection_model(user_id, id)
        except Exception as e:
            logging.exception('[product]:[%s]\n[%s]' % (user_id, e))
    return render_template('front/index_products/product.html',
                           book=book,
                           book_type_list=book_type_list,
                           evaluates=evaluates,
                           total=total,
                           evaluates_details=evaluates_details,
                           active_page=page,
                           page_count=page_count,
                           page_size=page_size,
                           is_collection=is_collection,
                           )


@bp.route('/recommend_product/<string:id>')
def recommend_user(id=None):
    book_list = get_recommend_book_model(id)
    resp = jsonify(book_list)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@bp.route('/recommend_user')
@login_required
def recommend_product():
    user_id = session.get('user_id')
    book_list = get_recommend_user_book_model(user_id)
    resp = jsonify(book_list)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@bp.route('/product/add_to_cart', methods=['GET'])
@login_required
def add_to_cart():
    """将物品加入到购物车"""
    user_id = session.get('user_id')
    num = request.args.get('num', 0, type=int)
    book_id = request.args.get('book_id')
    result = add_card_model(user_id, book_id, num)
    book = get_book(book_id)
    book_type_list = choice_book_type()
    if isinstance(result, dict) and result.get('error'):  # 库存不足
        flash(result.get('error'))
        return redirect(url_for('products.product', id=book_id))
    return render_template('front/index_products/add_cart_success.html',
                           book=book,
                           num=num,
                           book_type_list=book_type_list,
                           )


@bp.route('/product/add_to_cart/recommend_for_cart')
@login_required
def recommend_for_cart():
    user_id = session.get('user_id')
    book_list = get_recommend_cart_book_model(user_id)
    resp = jsonify(book_list)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@bp.route('/to_collection', methods=['POST'])
@login_required
def to_collection():
    user_id = session.get('user_id')
    book_id = request.form.get('book_id')
    try:
        result = to_collection_model(user_id, book_id)
    except Exception as e:
        logging.exception('[to_collection][%s]:[%s]:\n[%s]' % (user_id, book_id, e))
        return abort(500)
    return jsonify(result)


@bp.route('/clear_collection', methods=['POST'])
@login_required
def clear_collection():
    user_id = session.get('user_id')
    book_id = request.form.get('book_id')
    try:
        result = to_collection_model(user_id, book_id, is_clear=True)
    except Exception as e:
        logging.exception('[to_collection][%s]:[%s]:\n[%s]' % (user_id, book_id, e))
        return abort(500)
    return jsonify(result)


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
    if method == 'deletes':
        book_id = request.form.getlist('book_id[]')
    else:
        book_id = request.form.get('book_id', '', type=str)
    user_id = session.get('user_id')
    try:
        result = edit_cart_num(user_id, book_id, input_count, method)
    except AttributeError as e:
        logging.exception('ADD_NUMBERS -> EDIT_CART_NUM [Eception]:%s', e)
        result = input_count
    logging.info('%s change cart num from %s to %s.', user_id, input_count, result)
    return jsonify(result=result)


# @bp.route('/count_buy', methods=('GET', 'POST'))
# @login_required
# def count_buy():
#     """购物车下单结算"""
#     books = request.form.getlist('data[]')
#     user_id = session.get('user_id')
#     books = from_cart_buy(books, user_id)
#     return jsonify(result=books)


@bp.route('/buy_list', methods=('GET', 'POST'))
@bp.route('/buy_now', methods=('GET', 'POST'))
@login_required
def buy():
    """购物车选择物品下单"""
    try:
        book_id = request.args.get('book_id')
        user_id = session.get('user_id')
        if 'buy_now' in request.url:
            result = to_buy_model(user_id, book_id, is_list=False)
            buy_now = True
        else:
            result = to_buy_model(user_id, book_id)
            buy_now = False
        logging.info('%s buy %s', user_id, book_id)
        if 'error' in result:
            raise ValueError
        return render_template('front/settle_pay/settle_from_list.html',
                               books=result.get('book_list'),
                               books_price=result.get('books_price'),
                               pay=result.get('pay'),
                               addr=result.get('addr'),
                               shipping_time=result.get('shipping_time'),
                               is_buy_now=buy_now,
                               )
    except ValueError:
        flash(result.get('error'))
        logging.error('buy find error: %s', result.get('error'))
        if 'buy_now' in request.url:
            return redirect(url_for('products.product', id=book_id))
        return redirect(url_for('products.cart'))
    except TypeError as e:
        flash('有已经下架了的图书？请删除后重试吧～')
        logging.error('buy find error: %s', e)
        return redirect(url_for('products.cart'))
    except Exception as e:
        flash('出现错误了？请稍后重试～')
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


@bp.route('/to_pay', methods=('POST', ))
@login_required
def to_pay():
    """结算页面的去支付方法"""
    book_ids = request.form.getlist('books[]')
    addr_id = request.form.get('addr_id')
    user_id = session.get('user_id')
    is_buy_now = request.form.get('is_buy_now')
    try:
        is_buy_now = bool(is_buy_now)
    except Exception:
        logging.exception('is_but_now type error!')
    order_no = to_pay_model(user_id, book_ids, addr_id, is_buy_now)
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
    page = request.values.get('page', 1, type=int)
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
