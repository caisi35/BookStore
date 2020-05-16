import string, random
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from bson.objectid import ObjectId
from db import ToConn, ToMongo, get_like_books
from views.signIn import admin_login_required
from werkzeug.exceptions import abort

bp = Blueprint('bookAdmin', __name__, url_prefix='/admin')


# 加载图书管理页
@bp.route('/bookAdmin', methods=('GET', 'POST'))
@admin_login_required
def bookAdmin():
    try:
        books = ToMongo().get_col('books').find()
        return render_template('admin/bookAdmin.html', books=list(books))
    except Exception as e:
        print('==============Admin delete_user=================', e)
        return abort(404) + str(e)


# 搜索模糊匹配功能
@bp.route('/search_book', methods=('GET',))
@admin_login_required
def search_book():
    try:
        word = request.args.get('kw')
        books = get_like_books(word)
        return render_template('admin/bookAdmin.html', books=list(books))
    except Exception as e:
        print('=========book Admin search=========', e)
        return abort(404)


# 图书详情
@bp.route('/bookDetails', methods=('GET', 'POST'))
@admin_login_required
def bookDetails():
    try:
        book_id = request.args.get('book_id', '')
        book = ToMongo().get_col('books').find({'_id': ObjectId(book_id)})
        return render_template('admin/bookDeatils.html', book=list(book)[0])
    except Exception as e:
        print('=========book Admin bookDetails=========', e)
        return abort(404)