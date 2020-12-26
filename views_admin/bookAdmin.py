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

bp = Blueprint('bookAdmin', __name__, url_prefix='/admin/bookAdmin')


@bp.route('/', methods=('GET', 'POST'))
@admin_login_required
def bookAdmin():
    """加载图书管理页"""
    try:
        page = request.args.get('page', 1, int)
        page_size = 20
        page_count = 5
        books, total = get_books_total(page, page_size)
        return render_template('admin/bookAdmin.html',
                               page_active="bookAdmin",
                               books=books,
                               active_page=page,
                               page_count=page_count,
                               page_size=page_size,
                               total=total,
                               )
    except Exception as e:
        print('==============Admin delete_user=================', e)
        return abort(404) + str(e)


@bp.route('/add_book', methods=('GET', 'POST'))
@admin_login_required
def add_book():
    """添加图书"""
    try:
        if request.method == 'POST':
            result = add_book_model(request)
            if result.inserted_id:
                book = get_book_for_id(result, inserted_id=True)
                return render_template('admin/bookDeatils.html',
                                       book=book)
            else:
                flash('操作失败')
                return redirect(request.url)
        return render_template('admin/addBook.html',
                               page_active="add_book")
    except Exception as e:
        print('=========book Admin add_book=========', e)
        return abort(404)


@bp.route('/search_book', methods=('GET',))
@admin_login_required
def search_book():
    """搜索模糊匹配功能"""
    try:
        page_size = 20
        word = request.args.get('kw')
        page = request.args.get('page', 0, type=int)

        books, total = get_like_books(word, page, page_size)
        return render_template('admin/bookAdmin.html',
                               books=list(books),
                               page_active="bookAdmin",
                               active_page=page,
                               page_count=5,
                               page_size=page_size,
                               total=total
                               )
    except Exception as e:
        print('=========book Admin search=========', e)
        return abort(404)


@bp.route('/bookDetails', methods=('GET', 'POST'))
@admin_login_required
def bookDetails():
    """图书详情"""
    try:
        book_id = request.args.get('book_id', '')
        book = get_book_for_id(book_id)
        return render_template('admin/bookDeatils.html',
                               book=book)
    except Exception as e:
        print('=========book Admin bookDetails=========', e)
        return abort(404)


@bp.route('/editBook', methods=('GET', 'POST'))
@admin_login_required
def editBook():
    """编辑图书"""
    try:
        if request.method == 'POST':
            next = request.form.get('next', '')
            result = edit_book_model(request)
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
        book_id = request.args.get('book_id', '')
        book = get_book_for_id(book_id)
        return render_template('admin/editBook.html',
                               book=book)
    except Exception as e:
        print('=========book Admin editBook=========', e)
        return abort(404)


@bp.route('/off_shelf', methods=('GET', 'POST'))
@admin_login_required
def off_shelf():
    """将图书下架"""
    try:
        book_id = request.args.get('book_id')
        result = book_off_shelf(book_id)
        if result.modified_count:
            return redirect(url_for('bookAdmin.bookAdmin'))
        else:
            flash('操作失败！')
            return redirect(url_for('bookAdmin.bookAdmin'))
    except Exception as e:
        print('=========book Admin off_shelf=========', e)
        return abort(404)


@bp.route('/off_shelf_books', methods=('GET', 'POST'))
@admin_login_required
def off_shelf_books():
    """已下架的图书"""
    try:
        page = request.args.get('page', 1, int)
        page_size = 20
        page_view = 5
        books, total = get_books_total(page, page_size, 1)
        return render_template('admin/offShelfBook.html',
                               page_active="off_shelf_books",
                               books=books,
                               active_page=page,
                               total=total,
                               page_size=page_size,
                               page_count=page_view,
                               )
    except Exception as e:
        print('=========book Admin off_shelf_books=========', e)
        return abort(404)


@bp.route('/on_shelf', methods=('GET', 'POST'))
@admin_login_required
def on_shelf():
    """将已经下架的图书重新上架"""
    try:
        book_id = request.args.get('book_id')
        result = book_off_shelf(book_id, 0)
        if result.modified_count:
            return redirect(url_for('bookAdmin.off_shelf_books'))
        else:
            flash('操作失败！')
            return redirect(url_for('bookAdmin.off_shelf_books'))
    except Exception as e:
        print('=========book Admin on_shelf=========', e)
        return abort(404)


@bp.route('/off_shelf_book_trash', methods=('GET', 'POST'))
@bp.route('/restores', methods=('GET', 'POST'))
@admin_login_required
def off_shelf_book_trash():
    try:
        book_id = request.args.get('book_id')
        if 'off_shelf_book_trash' in request.url:
            """下架的图书加入回收站"""
            result, ds = off_shelf_book_model(book_id)
            if ds.deleted_count and result.inserted_id:
                return redirect(url_for('bookAdmin.off_shelf_books'))
            else:
                flash('操作失败！')
                return redirect(url_for('bookAdmin.off_shelf_books'))
        else:
            """还原被删除图书"""
            result, ds = off_shelf_book_model(book_id, is_restores=True)
            if ds.deleted_count and result.inserted_id:
                return redirect(url_for('bookAdmin.book_trash'))
            else:
                flash('操作失败！')
                return redirect(url_for('bookAdmin.book_trash'))
    except Exception as e:
        print('=========book Admin restores=========', e)
        return abort(404)


@bp.route('/book_trash', methods=('GET', 'POST'))
@admin_login_required
def book_trash():
    """已删除图书"""
    try:
        page = request.args.get('page', 1, int)
        page_size = 20
        page_count = 5
        books, total = get_trash_books_total(page, page_size)
        return render_template('admin/trash.html',
                               page_active="book_trash",
                               books=list(books),
                               active_page=page,
                               page_size=page_size,
                               page_count=page_count,
                               total=total,
                               trash_type='/admin/bookAdmin/book_trash?page='
                               )
    except Exception as e:
        print('==============Admin book_trash=================', e)
        return 'Error:' + str(e)


@bp.route('/trash_delete', methods=('GET', 'POST'))
@admin_login_required
def trash_delete():
    """删除图书"""
    try:
        book_id = request.args.get('book_id')
        result = trash_delete_book(book_id)
        if result.modified_count:
            return redirect(url_for('admin.trash'))
        else:
            flash('操作失败！')
            return redirect(url_for('admin.trash'))
    except Exception as e:
        print('=========book Admin trash_delete=========', e)
        return abort(404)
