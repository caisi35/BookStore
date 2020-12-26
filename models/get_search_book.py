from .db import ToMongo


def get_like_books(word, page, page_size, book_type=None):
    """MongoDB搜索功能的模糊查询"""
    try:
        mydb = ToMongo()
        book_list = []
        mycol = mydb.get_col('books')
        if book_type:
            books = mycol.find({'type': word}).sort('hits', -1).skip((page - 1) * page_size).limit(page_size)
            count = mycol.find({'type': word}).count()
        else:
            books = mycol.find({'$or': [{'press': {"$regex": word}},
                                        {'title': {"$regex": word}},
                                        {'subheading': {"$regex": word}},
                                        {'author': {"$regex": word}}]
                                }).sort('hits', -1).skip(page * page_size).limit(page_size)
            count = mycol.find({'$or': [{'press': {"$regex": word}},
                                        {'title': {"$regex": word}},
                                        {'subheading': {"$regex": word}},
                                        {'author': {"$regex": word}}]
                                }).count()
        for book in books:
            book_list.append(book)
        return book_list, count
    except Exception as e:
        print('========get_like_books=========', e)