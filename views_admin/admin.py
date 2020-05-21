from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from models.db import ToConn, ToMongo, get_trash, get_page
from views_admin.signIn import admin_login_required
from werkzeug.exceptions import abort
from bson.objectid import ObjectId
from pyecharts import Bar
import pymongo

bp = Blueprint('admin', __name__, url_prefix='/admin')
REMOTE_HOST = "/static/assets/js"


# 管理主页
@bp.route('/', methods=('GET', 'POST'))
@admin_login_required
def admin():
    try:
        bar = hits_bar()
        return render_template('admin/indexBase.html',
                               myhitsbar=bar.render_embed(),
                               host=REMOTE_HOST,
                               script_list=bar.get_js_dependencies(),
                               )
    except Exception as e:
        print('==============Admin login=================', e)
        return 'Error:' + str(e)


# 获取点击量hits的数据
def get_hits_data():
    data = ToMongo().get_col('books').find({'hits': {'$gt': 0}}).sort('hits', pymongo.DESCENDING).limit(10)
    data_x = []
    data_y = []
    for i in data:
        data_x.append(i['title'])
        data_y.append(i['hits'])
    return data_x, data_y


# 实例化 点击量的柱形图
# 实例链接https://05x-docs.pyecharts.org/#/zh-cn/flask
def hits_bar():
    bar = Bar(title='点击量 TOP 10', height=300, width=300)
    data_x, data_y = get_hits_data()
    bar.add('', data_x, data_y, xaxis_rotate=45, is_xaxis_show=False, is_toolbox_show=False)
    return bar


# 回收站
@bp.route('/book_trash', methods=('GET', 'POST'))
@admin_login_required
def book_trash():
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
        print('==============Admin book_trash=================', e)
        return 'Error:' + str(e)


@bp.route('/user_trash', methods=('GET', 'POST'))
@admin_login_required
def user_trash():
    try:
        page = request.args.get('page', 1, int)
        page_user = 2
        if page == 1:
            # 请求为默认的第一页
            users = ToConn().get_db('select * from users where is_delete=1 limit %s', (page_user))
            active_page = 1
        else:
            users = ToConn().get_db('select * from users where is_delete=1 limit %s,%s',
                                    ((page - 1) * page_user, page_user))
            active_page = page
        try:
            # 为空时捕获错误
            pages, max_page = get_page(page_user, page)
        except Exception as e:
            print(e)
            pages, max_page = 3, 3
        return render_template('admin/trash.html', users=users)
    except Exception as e:
        print('==============Admin user_trash=================', e)
        return 'Error:' + str(e)


# 还原图书
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


# 还原用户
@bp.route('/restores_user', methods=('GET', 'POST'))
@admin_login_required
def restores_user():
    try:
        user_id = request.args.get('user_id')
        conn = ToConn().to_execute()
        result = conn.cursor().execute('update users set is_delete=0 where id=%s', (user_id,))
        if result:
            conn.commit()
            return redirect(url_for('admin.user_trash'))
        else:
            conn.rollback()
            flash('操作失败！')
            return redirect(url_for('admin.user_trash'))
    except Exception as e:
        print('=========book Admin restores_user=========', e)
        return abort(404)


# 删除图书
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
