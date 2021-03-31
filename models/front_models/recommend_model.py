import time

from models import ToMongo
from recommend import (
    getRecommendations,
    get_data,
    transformPrefs,
)


def get_recommend_order_book_model(user_id):
    try:
        book = getRecommendations(transformPrefs(get_data()), user_id)
        print(book + 'aassa')
    except Exception as e:
        print(str(e) + '22222222222222')
    skip = str(time.time()).split('.')[-1][:4]
    conn = ToMongo()
    result = conn.get_col('books').find().skip(int(skip)).limit(2)
    book = []
    for b in result:
        id = str(b.get('_id'))
        img = b.get('img_url')
        title = b.get('title')
        author = b.get('author')
        book.append({'img': img,
                     'id': id,
                     'title': title,
                     'author': author})
    return book


def get_recommend_cart_book_model(user_id):
    try:
        book = getRecommendations(transformPrefs(get_data()), user_id)
        print(book + 'aassa')
    except Exception as e:
        print(str(e) + '22222222222222')
    skip = str(time.time()).split('.')[-1][:4]
    conn = ToMongo()
    result = conn.get_col('books').find().skip(int(skip)).limit(2)
    book = []
    for b in result:
        id = str(b.get('_id'))
        img = b.get('img_url')
        title = b.get('title')
        author = b.get('author')
        book.append({'img': img,
                     'id': id,
                     'title': title,
                     'author': author})
    return book