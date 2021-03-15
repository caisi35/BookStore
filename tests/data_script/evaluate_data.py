import random
from bson.objectid import ObjectId

from models import ToMongo
from models.front_models import get_book_id
from utils import get_now


def evaluate_model(user_id, user_name, request, book_ids):
    """用户评论模型"""
    rlt = {}
    order_no = request.get('order_no')
    star = int(request.get('star'))
    context = request.get('context')
    anonymous = request.get('anonymous')
    if not star:
        rlt['error'] = '评分不能为空'
        return rlt
    img_path = ''
    create_time = get_now()
    if anonymous:
        user_name = user_name[0] + '**'
    else:
        user_name = user_name[0] + '*' + user_name[-1]
    id_list = []
    mydb = ToMongo()
    for book_id in book_ids:
        value = {'$addToSet':
                     {'comment':
                          {'order_no': order_no,
                           'star': star,
                           'context': context,
                           'user_id': user_id,
                           'user_name': user_name,
                           'img_path': img_path,
                           'create_time': create_time
                           }
                      }
                 }
        result = mydb.update('evaluate', {'_id': ObjectId(book_id)}, value)
        if result.modified_count:
            id_list.append(result.modified_count)
        else:
            # 无评论时，直接插入
            rel = mydb.insert('evaluate',
                              {'_id': ObjectId(book_id),
                               'comment':
                                   [
                                       {'order_no': order_no,
                                        'star': star,
                                        'context': context,
                                        'user_id': user_id,
                                        'user_name': user_name,
                                        'img_path': img_path,
                                        'create_time': create_time
                                        }
                                   ]
                               })
            id_list.append(rel.inserted_id)
        # print(id_list)
    if len(id_list) != len(book_ids):
        # print(id_list)
        rlt['error'] = '评论失败，请重试！'
    mydb.close_conn()
    return rlt


def to_evaluate(order_no, star, context, book_ids):
    user_id = 5
    user_name = 'test'

    value = {'order_no': order_no,
             'star': star,
             'context': context,
             }
    evaluate_model(user_id, user_name, value, book_ids)


if __name__ == '__main__':
    stars = [1, 2, 3, 4, 5]
    count = 5
    mydb = ToMongo()
    for i in range(1, count):
        star = random.choice(stars)
        to_evaluate('202103052207612453',
                    star,
                    'test{}- star{}'.format(i, star),
                    book_ids=['5ee96be4360d930a489db21a'])
