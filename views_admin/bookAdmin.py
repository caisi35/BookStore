import logging
from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from views_admin.signIn import admin_login_required
from models import (
    get_books_total,
    add_book_model,
    get_book_for_id,
    edit_book_model,
    book_off_shelf,
    off_shelf_book_model,
    get_trash_books_total,
    trash_delete_book,
    get_like_books
)
from utils import Logger

Logger('book_admin.log')

bp = Blueprint('bookAdmin', __name__, url_prefix='/admin/bookAdmin')


@bp.route('/', methods=('GET', 'POST'))
@admin_login_required
def bookAdmin():
    """加载图书管理页"""
    page = request.args.get('page', 1, int)
    page_size = 20
    page_count = 5
    try:
        books, total = get_books_total(page, page_size)
    except Exception as e:
        logging.exception('book_admin index get_books_total [Exception]:%s', e)
        return abort(404) + str(e)
    return render_template('admin/bookAdmin.html',
                           page_active="bookAdmin",
                           books=books,
                           active_page=page,
                           page_count=page_count,
                           page_size=page_size,
                           total=total,
                           )


@bp.route('/add_book', methods=('GET', 'POST'))
@admin_login_required
def add_book():
    """添加图书"""
    if request.method == 'POST':
        try:
            result = add_book_model(request)
        except Exception as e:
            logging.exception('book_admin add_book add_book_model [Exception]:%s', e)
            return abort(404) + str(e)
        if result.inserted_id:
            try:
                book = get_book_for_id(result, inserted_id=True)
            except Exception as e:
                logging.exception('book_admin add_book get_book_for_id [Exception]:%s', e)
                return abort(404) + str(e)
            return render_template('admin/bookDeatils.html',
                                   book=book)
        else:
            flash('操作失败')
            return redirect(request.url)
    return render_template('admin/addBook.html',
                           page_active="add_book")


@bp.route('/search_book', methods=('GET',))
@admin_login_required
def search_book():
    """搜索模糊匹配功能"""
    page_size = 20
    word = request.args.get('kw')
    page = request.args.get('page', 0, type=int)
    try:
        books, total = get_like_books(word, page, page_size)
    except Exception as e:
        logging.exception('book_admin -> search_book -> get_like_books [Exception]:%s', e)
        return abort(404) + str(e)
    return render_template('admin/bookAdmin.html',
                           books=list(books),
                           page_active="bookAdmin",
                           active_page=page,
                           page_count=5,
                           page_size=page_size,
                           total=total
                           )


@bp.route('/bookDetails', methods=('GET', 'POST'))
@admin_login_required
def bookDetails():
    """图书详情"""
    book_id = request.args.get('book_id', '')
    try:
        book = get_book_for_id(book_id)
    except Exception as e:
        logging.exception('book_admin -> book_details -> get_book_for_id [Exception]:%s', e)
        return abort(404) + str(e)
    return render_template('admin/bookDeatils.html',
                           book=book)


@bp.route('/editBook', methods=('GET', 'POST'))
@admin_login_required
def editBook():
    """编辑图书"""
    if request.method == 'POST':
        next = request.form.get('next', '')
        try:
            result = edit_book_model(request)
        except Exception as e:
            logging.exception('book_admin -> edit_book -> edit_book_model [Exception]:%s', e)
            return abort(404) + str(e)
        if result:
            # 成功重定向上一页
            return redirect(next)
        elif result == 0:
            flash('没有改变！')
            return redirect(request.referrer)
        else:
            # 失败重定向刷新
            flash('提交失败！')
            return redirect(request.referrer)
    # GET method
    book_id = request.args.get('book_id', '')
    try:
        book = get_book_for_id(book_id)
    except Exception as e:
        logging.exception('book_admin -> edit_book -> get_book_for_id [Exception]:%s', e)
        return abort(404) + str(e)
    return render_template('admin/editBook.html',
                           book=book)


@bp.route('/off_shelf', methods=('GET', 'POST'))
@admin_login_required
def off_shelf():
    """将图书下架"""
    book_id = request.args.get('book_id')
    try:
        result = book_off_shelf(book_id)
        if not result.modified_count:
            flash('操作失败！')
    except Exception as e:
        logging.exception('book_admin -> edit_book -> book_off_shelf [Exception]:%s', e)
        return abort(404) + str(e)
    return redirect(url_for('bookAdmin.bookAdmin'))


@bp.route('/off_shelf_books', methods=('GET', 'POST'))
@admin_login_required
def off_shelf_books():
    """已下架的图书"""
    page = request.args.get('page', 1, int)
    page_size = 20
    page_view = 5
    try:
        books, total = get_books_total(page, page_size, 1)
    except Exception as e:
        logging.exception('book_admin -> off_shelf_books -> get_books_total [Exception]:%s', e)
        return abort(404) + str(e)
    return render_template('admin/offShelfBook.html',
                           page_active="off_shelf_books",
                           books=books,
                           active_page=page,
                           total=total,
                           page_size=page_size,
                           page_count=page_view,
                           )


@bp.route('/on_shelf', methods=('GET', 'POST'))
@admin_login_required
def on_shelf():
    """将已经下架的图书重新上架"""
    book_id = request.args.get('book_id')
    try:
        result = book_off_shelf(book_id, 0)
        if not result.modified_count:
            flash('操作失败！')
    except Exception as e:
        logging.exception('book_admin -> on_shelf -> book_off_shelf [Exception]:%s', e)
        return abort(404) + str(e)
    return redirect(url_for('bookAdmin.off_shelf_books'))


@bp.route('/off_shelf_book_trash', methods=('GET', 'POST'))
@bp.route('/restores', methods=('GET', 'POST'))
@admin_login_required
def off_shelf_book_trash():
    """下架的图书删除"""
    book_id = request.args.get('book_id')
    if 'off_shelf_book_trash' in request.url:
        """下架的图书加入回收站"""
        try:
            result, ds = off_shelf_book_model(book_id)
            if ds.deleted_count and result.inserted_id:
                pass
            else:
                flash('操作失败！')
        except Exception as e:
            logging.exception('book_admin -> off_shelf_book_trash -> off_shelf_book_model [Exception]:%s', e)
            return abort(404)
        return redirect(url_for('bookAdmin.off_shelf_books'))
    else:
        """还原被删除图书"""
        try:
            result, ds = off_shelf_book_model(book_id, is_restores=True)
            if ds.deleted_count and result.inserted_id:
                pass
            else:
                flash('操作失败！')
        except Exception as e:
            logging.exception('book_admin -> off_shelf_book_trash -> off_shelf_book_model [Exception]:%s', e)
            return abort(404)
        return redirect(url_for('bookAdmin.book_trash'))


@bp.route('/book_trash', methods=('GET', 'POST'))
@admin_login_required
def book_trash():
    """已删除图书"""
    page = request.args.get('page', 1, int)
    page_size = 20
    page_count = 5
    try:
        books, total = get_trash_books_total(page, page_size)
    except Exception as e:
        logging.exception('book_admin -> book_trash -> get_trash_books_total [Exception]:%s', e)
        return 'Error:' + str(e)
    return render_template('admin/trash.html',
                           page_active="book_trash",
                           books=list(books),
                           active_page=page,
                           page_size=page_size,
                           page_count=page_count,
                           total=total,
                           trash_type='/admin/bookAdmin/book_trash?page='
                           )


@bp.route('/trash_delete', methods=('GET', 'POST'))
@admin_login_required
def trash_delete():
    """删除图书"""
    book_id = request.args.get('book_id')
    try:
        result = trash_delete_book(book_id)
        if not result.modified_count:
            flash('操作失败！')
    except Exception as e:
        logging.exception('book_admin -> trash_delete -> trash_delete [Exception]:%s', e)
        return abort(404)
    return redirect(url_for('admin.trash'))
