import inspect
from flask import (
    Blueprint, render_template, request
)

from models import get_like_books
from models.choice_type import choice_book_type

bp = Blueprint('index_view', __name__)


@bp.route('/book_type')
def book_type():
    input_book_type = request.values.get('book_type')
    page = request.values.get('page', 1, type=int)
    page_size = request.values.get('page_size', 15, type=int)
    books, count = get_like_books(input_book_type, page, page_size, True)
    book_type_list = choice_book_type()
    return render_template('../tests/demo_html/products/../tests/demo_html/block/search.html',
                           def_url=inspect.stack()[0][3],
                           books=books,
                           key_word=input_book_type,
                           active_page=page,
                           total=count,
                           page_size=page_size,
                           page_count=5,
                           book_type_list=book_type_list
                           )

