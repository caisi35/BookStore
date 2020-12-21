from flask import (
    Blueprint, redirect, render_template, request, url_for, session, jsonify
)
from models.db import ToConn, ToMongo, get_like_books
from models.choice_type import choice_book_type
from werkzeug.exceptions import abort
from views_front.user import login_required
from bson.objectid import ObjectId
import time, random, base64, inspect
from datetime import datetime, timedelta

bp = Blueprint('index_view', __name__)


@bp.route('/book_type')
def book_type():
    input_book_type = request.values.get('book_type')
    page = request.values.get('page', 1, type=int)
    page_size = request.values.get('page_size', 15, type=int)
    books, count = get_like_books(input_book_type, page, page_size, True)
    book_type_list = choice_book_type()
    return render_template('products/search.html',
                           def_url=inspect.stack()[0][3],
                           books=books,
                           key_word=input_book_type,
                           active_page=page,
                           total=count,
                           page_size=page_size,
                           page_count=5,
                           book_type_list=book_type_list
                           )

