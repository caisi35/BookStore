from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from bson.objectid import ObjectId
from db import ToMongo, get_like_books, get_pages
from views.signIn import admin_login_required
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

bp = Blueprint('bookAdmin', __name__, url_prefix='/admin/bookAdmin')


# 加载图书管理页
@bp.route('/', methods=('GET', 'POST'))
@admin_login_required
def bookAdmin():
    try:
        page = request.args.get('page', 1, int)
        pages, max_page = get_pages(page)
        page_book = 20
        if page == 1:
            # 请求为默认的第一页
            books = ToMongo().get_col('books').find({'is_off_shelf': 0}).limit(page_book)
            active_page = 1
        else:
            books = ToMongo().get_col('books').find({'is_off_shelf': 0}).skip((page - 1) * page_book).limit(page_book)
            active_page = page
        return render_template('admin/bookAdmin.html', books=list(books), pages=pages, active_page=active_page,
                               max_page=max_page)
    except Exception as e:
        print('==============Admin delete_user=================', e)
        return abort(404) + str(e)


# 添加图书
@bp.route('/add_book', methods=('GET', 'POST'))
@admin_login_required
def add_book():
    try:
        # POST 提交请求
        if request.method == 'POST':
            img = request.files['img']
            s_img = secure_filename(img.filename)
            # 随机文件名+后缀
            filepath = './static/images/book_img/' + s_img
            img.save(filepath)

            title = request.form.get('title', '')
            author = request.form.get('author', '')
            subheading = request.form.get('subheading', '')
            price = request.form.get('price', '')
            price_m = request.form.get('price_m', '')
            press = request.form.get('press', '')
            pub_time = request.form.get('pub_time', '')
            img_url = '/static/images/book_img/'+s_img
            v = {'title': title, 'author': author, 'subheading': subheading, 'price': price, 'price_m': price_m,
                         'press': press, 'pub_time': pub_time, 'img_url': img_url}
            result = ToMongo().insert('books', v)
            if result.inserted_id:
                book = ToMongo().get_col('books').find({'_id': result.inserted_id})
                return render_template('admin/bookDeatils.html', book=list(book)[0])
            else:
                flash('操作失败')
                print(request.url)
                return redirect(request.url)

        # GET 请求渲染
        return render_template('admin/addBook.html')
    except Exception as e:
        print('=========book Admin add_book=========', e)
        return abort(404)


# 搜索模糊匹配功能
@bp.route('/search_book', methods=('GET',))
@admin_login_required
def search_book():
    try:
        word = request.args.get('kw')
        books = get_like_books(word)
        return render_template('admin/bookAdmin.html', books=list(books), active_page=1)
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


# 编辑图书
@bp.route('/editBook', methods=('GET', 'POST'))
@admin_login_required
def editBook():
    try:
        # POST 提交请求
        if request.method == 'POST':
            next = request.form.get('next', '')
            book_id = request.form.get('book_id', '')
            title = request.form.get('title', '')
            author = request.form.get('author', '')
            subheading = request.form.get('subheading', '')
            price = request.form.get('price', '')
            price_m = request.form.get('price_m', '')
            press = request.form.get('press', '')
            pub_time = request.form.get('pub_time', '')
            img_url = request.form.get('img_url', '')
            q = {'_id': ObjectId(book_id)}
            v = {
                '$set': {'title': title, 'author': author, 'subheading': subheading, 'price': price, 'price_m': price_m,
                         'press': press, 'pub_time': pub_time, 'img_url': img_url}}
            result = ToMongo().update('books', q, v).modified_count
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

        # GET 请求渲染
        book_id = request.args.get('book_id', '')
        book = ToMongo().get_col('books').find({'_id': ObjectId(book_id)})
        return render_template('admin/editBook.html', book=list(book)[0])
    except Exception as e:
        print('=========book Admin editBook=========', e)
        return abort(404)


# 将图书下架
@bp.route('/off_shelf', methods=('GET', 'POST'))
@admin_login_required
def off_shelf():
    try:
        book_id = request.args.get('book_id')
        result = ToMongo().update('books', {'_id': ObjectId(book_id)}, {'$set': {'is_off_shelf': 1}})
        if result.modified_count:
            return redirect(url_for('bookAdmin.bookAdmin'))
        else:
            flash('操作失败！')
            return redirect(url_for('bookAdmin.bookAdmin'))
    except Exception as e:
        print('=========book Admin off_shelf=========', e)
        return abort(404)


# 已下架的图书
@bp.route('/off_shelf_books', methods=('GET', 'POST'))
@admin_login_required
def off_shelf_books():
    try:
        page = request.args.get('page', 1, int)
        pages, max_page = get_pages(page)
        page_book = 20
        if page == 1:
            # 请求为默认的第一页
            books = ToMongo().get_col('books').find({'is_off_shelf': 1}).limit(page_book)
            active_page = 1
        else:
            books = ToMongo().get_col('books').find({'is_off_shelf': 1}).skip((page - 1) * page_book).limit(page_book)
            active_page = page
        return render_template('admin/offShelfBook.html', books=list(books), active_page=active_page, max_page=max_page)
    except Exception as e:
        print('=========book Admin off_shelf_books=========', e)
        return abort(404)


# 将图书上架
@bp.route('/on_shelf', methods=('GET', 'POST'))
@admin_login_required
def on_shelf():
    try:
        book_id = request.args.get('book_id')
        result = ToMongo().update('books', {'_id': ObjectId(book_id)}, {'$set': {'is_off_shelf': 0}})
        if result.modified_count:
            return redirect(url_for('bookAdmin.off_shelf_books'))
        else:
            flash('操作失败！')
            return redirect(url_for('bookAdmin.off_shelf_books'))
    except Exception as e:
        print('=========book Admin on_shelf=========', e)
        return abort(404)


# 下架的图书加入回收站
@bp.route('/off_shelf_book_trash', methods=('GET', 'POST'))
@admin_login_required
def off_shelf_book_trash():
    try:
        book_id = request.args.get('book_id')
        book = ToMongo().get_col('books').find_one({'_id': ObjectId(book_id)})
        result = ToMongo().insert('trash', book)
        ds = ToMongo().delete('books', {'_id': ObjectId(book_id)})
        if ds.deleted_count and result.inserted_id:
            return redirect(url_for('bookAdmin.off_shelf_books'))
        else:
            flash('操作失败！')
            return redirect(url_for('bookAdmin.off_shelf_books'))
    except Exception as e:
        print('=========book Admin off_shelf_book_trash=========', e)
        return abort(404)
