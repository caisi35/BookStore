from bson.objectid import ObjectId

from werkzeug.utils import secure_filename
from .db import (
    ToMongo
)


def off_shelf_book_model(book_id, is_restores=False):
    book = get_book_for_id(book_id)
    if not is_restores:
        result = ToMongo().insert('trash', book)
        ds = ToMongo().delete('books', {'_id': ObjectId(book_id)})
    else:
        result = ToMongo().insert('books', book)
        ds = ToMongo().delete('trash', {'_id': ObjectId(book_id)})
    return result, ds


def book_off_shelf(book_id, is_off_shelf=1):
    result = ToMongo().update('books',
                              {'_id': ObjectId(book_id)},
                              {'$set': {'is_off_shelf': is_off_shelf}})
    return result


def edit_book_model(request):
    book_id = request.form.get('book_id', '')
    title = request.form.get('title', '')
    author = request.form.get('author', '')
    subheading = request.form.get('subheading', '')
    price = request.form.get('price', int)
    price_m = request.form.get('price_m', '')
    press = request.form.get('press', '')
    pub_time = request.form.get('pub_time', '')
    img_url = request.form.get('img_url', '')
    q = {'_id': ObjectId(book_id)}
    v = {
        '$set': {'title': title, 'author': author, 'subheading': subheading, 'price': price, 'price_m': price_m,
                 'press': press, 'pub_time': pub_time, 'img_url': img_url}}
    result = ToMongo().update('books', q, v).modified_count
    return result


def get_book_for_id(id, inserted_id=False):
    if inserted_id:
        book = ToMongo().get_col('books').find({'_id': id.inserted_id})
        book_format = list(book)
    else:
        book_format = ToMongo().get_col('books').find_one({'_id': ObjectId(id)})
    return book_format


def add_book_model(request):
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
    img_url = '/static/images/book_img/' + s_img
    v = {'title': title,
         'author': author,
         'subheading': subheading,
         'price': price,
         'price_m': price_m,
         'press': press,
         'pub_time': pub_time,
         'img_url': img_url,
         }
    result = ToMongo().insert('books', v)
    return result


def get_books_total(page, page_size, is_off_shelf=0):
    books = ToMongo().get_col('books').find({'is_off_shelf': is_off_shelf}).skip((page - 1) * page_size).limit(
        page_size)
    total = ToMongo().get_col('books').find({'is_off_shelf': is_off_shelf}).count()
    return list(books), total


def get_trash_books_total(page, page_size):
    books = ToMongo().get_col('trash').find().skip((page - 1) * page_size).limit(page_size)
    total = ToMongo().get_col('trash').find().count()
    return list(books), total


def trash_delete_book(book_id):
    result = ToMongo().delete('trash', {'_id': ObjectId(book_id)})
    return result