import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from db import ToConn, ToMongo, get_trash
from views.signIn import admin_login_required
from werkzeug.exceptions import abort
from bson.objectid import ObjectId


bp = Blueprint('admin', __name__, url_prefix='/admin')


# 管理主页
@bp.route('/', methods=('GET', 'POST'))
@admin_login_required
def admin():
    try:
        return render_template('admin/indexBase.html')
    except Exception as e:
        print('==============Admin login=================', e)
        return 'Error:'+str(e)


# 回收站
@bp.route('/trash', methods=('GET', 'POST'))
@admin_login_required
def trash():
    try:
        page = request.args.get('page', 1, int)
        try:
            # 为空时捕获错误
            pages, max_page = get_trash(page)
        except Exception as e:
            print(e)
            pages, max_page = 3, 3

        page_book = 20
        if page == 1:
            # 请求为默认的第一页
            books = ToMongo().get_col('trash').find().limit(page_book)
            active_page = 1
        else:
            books = ToMongo().get_col('trash').find().skip((page - 1) * page_book).limit(page_book)
            active_page = page
        return render_template('admin/trash.html', books=list(books), active_page=active_page, max_page=max_page)
    except Exception as e:
        print('==============Admin trash=================', e)
        return 'Error:'+str(e)


# 还原
@bp.route('/restores', methods=('GET', 'POST'))
@admin_login_required
def restores():
    try:
        book_id = request.args.get('book_id')
        book = ToMongo().get_col('trash').find_one({'_id': ObjectId(book_id)})
        result = ToMongo().insert('books', book)
        ds = ToMongo().delete('trash', {'_id': ObjectId(book_id)})
        if ds.deleted_count and result.inserted_id:
            return redirect(url_for('admin.trash'))
        else:
            flash('操作失败！')
            return redirect(url_for('admin.trash'))
    except Exception as e:
        print('=========book Admin restores=========', e)
        return abort(404)


# 删除
@bp.route('/trash_delete', methods=('GET', 'POST'))
@admin_login_required
def trash_delete():
    try:
        book_id = request.args.get('book_id')
        result = ToMongo().delete('trash', {'_id': ObjectId(book_id)})
        if result.modified_count:
            return redirect(url_for('admin.trash'))
        else:
            flash('操作失败！')
            return redirect(url_for('admin.trash'))
    except Exception as e:
        print('=========book Admin trash_delete=========', e)
        return abort(404)
