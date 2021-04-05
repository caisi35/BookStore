from bson import ObjectId
from jieba.analyse import extract_tags

from models import ToMongo, ToConn

NOT_LIST = {'paper': 0, 'suit': 0, 'price_m': 0, '_id': 0, 'img_url': 0, 'create_time': 0, 'stock': 0,
            'si_off_shelf': 0, 'ISBN': 0, 'price': 0, 'img_urls': 0, 'packing': 0, 'pub_time': 0, 'press': 0,
            'format': 0, 'is_off_shelf': 0}
USER_NOT_IN = ['']


def get_book_text(id):
    conn = ToMongo()
    book = conn.get_col('books').find_one({'_id': ObjectId(id)}, NOT_LIST)
    conn.close_conn()
    text = ''
    for k, b in book.items():
        if isinstance(b, str):
            text = text + '。' + b
    return text


def get_user_text(id):
    user = ToConn().get_db('select hobbies,introduce,identity,age from users where id=%s', (id, )).fetchone()
    text = ''
    for k, u in user.items():
        text = text + '。' + u

    return text


def get_tags(text):
    result = extract_tags(sentence=text, topK=10, withWeight=True)
    return result


def get_like_books(word, book_id):
    """MongoDB搜索功能的模糊查询"""
    mydb = ToMongo()
    mycol = mydb.get_col('books')
    query = [
             {'title': {"$regex": word}},
             {'subheading': {"$regex": word}},
             {'author': {"$regex": word}},
             ]
    books = mycol.find_one({'$or': query, '$and':[{'_id': {'$ne': ObjectId(book_id)}}]})
    mydb.close_conn()
    return books


def recommend(book_id=None, user_id=None, num=2):
    text = ''
    if book_id:
        text = text + get_book_text(book_id)
    if user_id:
        text = text + get_user_text(user_id)

    tags = get_tags(text)

    result = []
    book_id_list = [book_id]

    for word, score in tags:
        if not word.isdigit():
            ret = get_like_books(word, book_id)

            if ret and str(ret.get('_id')) not in book_id_list:
                result.append(ret)
                book_id_list.append(str(ret.get('_id')))
        if len(result) >= num:
            break
    return result


if __name__ == '__main__':
    r = recommend('606907ebb9af4559e1ed0c8a', '5')
    print(r)
