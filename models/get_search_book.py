from .db import ToMongo


def get_like_books(word, page, page_size, book_type=None):
    """MongoDB搜索功能的模糊查询"""
    mydb = ToMongo()
    book_list = []
    mycol = mydb.get_col('books')
    if book_type:
        books = mycol.find({'first_type': word}).sort('hits', -1).skip((page - 1) * page_size).limit(page_size)
        count = mycol.find({'first_type': word}).count()
    else:
        query = [{'press': {"$regex": word}},
                 {'title': {"$regex": word}},
                 {'subheading': {"$regex": word}},
                 {'author': {"$regex": word}}]
        books = mycol.find({'$or': query}).sort('hits', -1).skip((page - 1) * page_size).limit(page_size)
        count = mycol.find({'$or': query}).count()
    for book in list(books):
        book_list.append(book)
    mydb.close_conn()
    return book_list, count
