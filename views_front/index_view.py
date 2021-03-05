import inspect
import logging
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify
)

from models import get_like_books
from models.choice_type import choice_book_type
from utils import Logger

Logger('index_view.log')
bp = Blueprint('index_view', __name__)


@bp.route('/get_nav_data')
def get_nav_data():
    input_book_type = request.values.get('book_type')
    page = request.values.get('page', 1, type=int)
    page_size = request.values.get('page_size', 15, type=int)
    books, count = get_like_books(input_book_type, page, page_size, True)
    book_type_list = choice_book_type()
    logging.info('input book type is: %s', input_book_type)
    return render_template('front/index_products/search.html',
                           def_url=inspect.stack()[0][3],
                           books=books,
                           key_word=input_book_type,
                           active_page=page,
                           total=count,
                           page_size=page_size,
                           page_count=5,
                           book_type_list=book_type_list
                           )


# @bp.route('/get_book')
# def get_book():
#     return render_template('../demo/demo_html/angularjs.html')


@bp.route('/get_book_type')
def get_book_type():
    book_type_list = choice_book_type()
    # 解决跨域问题：https://blog.csdn.net/weixin_42902669/article/details/90728697
    resp = jsonify(book_type_list)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    # resp.headers['"Access-Control-Allow-Methods"'] = '"PUT,POST,GET,DELETE,OPTIONS"'
    return resp