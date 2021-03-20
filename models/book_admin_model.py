from bson.objectid import ObjectId

from werkzeug.utils import secure_filename
from .db import (
    ToMongo
)


def off_shelf_book_model(book_id, is_restores=False):
    """下架"""
    my_conn = ToMongo()
    book = get_book_for_id(book_id)
    if not is_restores:
        result = my_conn.insert('trash', book)
        ds = my_conn.delete('books', {'_id': ObjectId(book_id)})
    else:
        result = my_conn.insert('books', book)
        ds = my_conn.delete('trash', {'_id': ObjectId(book_id)})
    my_conn.close_conn()
    return result, ds


def book_off_shelf(book_id, is_off_shelf=1):
    """图书下架数据操作"""
    my_conn = ToMongo()
    result = my_conn.update('books',
                              {'_id': ObjectId(book_id)},
                              {'$set': {'is_off_shelf': is_off_shelf}})
    my_conn.close_conn()
    return result


def edit_book_model(request):
    """编辑图书信息"""
    book_id = request.form.get('book_id', '')
    title = request.form.get('title', '')
    author = request.form.get('author', '')
    subheading = request.form.get('subheading', '')
    price = request.form.get('price', int)
    price_m = request.form.get('price_m', '')
    stock = request.form.get('stock', 0, int)
    press = request.form.get('press', '')
    pub_time = request.form.get('pub_time', '')
    img_url = request.form.get('img_url', '')
    q = {'_id': ObjectId(book_id)}
    v = {
        '$set': {'title': title, 'author': author, 'subheading': subheading, 'price': price, 'price_m': price_m,
                 'press': press, 'pub_time': pub_time, 'img_url': img_url, 'stock': stock}}
    my_conn = ToMongo()
    result = my_conn.update('books', q, v).modified_count
    my_conn.close_conn()
    return result


def get_book_for_id(id, inserted_id=False):
    my_conn = ToMongo()
    if inserted_id:
        book = my_conn.get_col('books').find({'_id': id.inserted_id})
        book_format = list(book)
    else:
        book_format = my_conn.get_col('books').find_one({'_id': ObjectId(id)})
    my_conn.close_conn()
    return book_format


def add_book_model(request):
    """添加图书"""
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
    stock = request.form.get('stock', 0, int)
    press = request.form.get('press', '')
    pub_time = request.form.get('pub_time', '')
    img_url = '/static/images/book_img/' + s_img
    v = {'title': title,
         'author': author,
         'subheading': subheading,
         'price': price,
         'price_m': price_m,
         'stock': stock,
         'press': press,
         'pub_time': pub_time,
         'img_url': img_url,
         }
    my_conn = ToMongo()
    result = my_conn.insert('books', v)
    return result


def get_books_total(page, page_size, is_off_shelf=0):
    """获取图书总量"""
    my_conn = ToMongo()
    books = my_conn.get_col('books').find({'is_off_shelf': is_off_shelf}).skip((page - 1) * page_size).limit(
        page_size)
    total = my_conn.get_col('books').find({'is_off_shelf': is_off_shelf}).count()
    my_conn.close_conn()
    return list(books), total


def get_trash_books_total(page, page_size):
    """获取删除图书量"""
    my_conn = ToMongo()
    books = my_conn.get_col('trash').find().skip((page - 1) * page_size).limit(page_size)
    total = my_conn.get_col('trash').find().count()
    return list(books), total


def trash_delete_book(book_id):
    """永久删除图书"""
    my_conn = ToMongo()
    result = my_conn.delete('trash', {'_id': ObjectId(book_id)})
    return result