import time

from models.db import ToMongo


def index_model():
    """主页内容"""
    mydb = ToMongo()
    # 轮播
    random_time = int(str(time.time())[-3:])
    books = get_reader_recommend(mydb, random_time)
    new_books = list(mydb.get_col('books').find({'is_off_shelf': 0}).skip(random_time).limit(12))
    book_top = list(mydb.get_col('books').find({'is_off_shelf': 0}).sort("pub_time", -1).limit(5))
    book_top2 = list(mydb.get_col('books').find({'is_off_shelf': 0}).sort("sales", -1).limit(5))
    mydb.close_conn()
    return books, new_books, book_top, book_top2


def get_reader_recommend(mydb, random_time, num=15):
    evaluate_book = mydb.get_col('evaluate').find({}, {'_id': '1'}).sort('comment').limit(num)
    book_list = []
    for i in evaluate_book:
        id = i['_id']
        if id:
            result = mydb.get_col('books').find_one({'is_off_shelf': 0, '_id': id})
            if result:
                book_list.append(result)
    if len(book_list) < num:
        result = list(mydb.get_col('books').find().skip(random_time).limit(num - len(book_list)))
        book_list.extend(result)
    return book_list


if __name__ == '__main__':
    index_model()