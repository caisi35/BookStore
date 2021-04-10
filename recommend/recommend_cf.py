import math
import operator
from bson.objectid import ObjectId

from models.db import ToMongo
from .get_book_data import get_visual_info

def get_user_click():
    conn = ToMongo()
    data = conn.get_col('hits_data').find({})
    user_click = {}
    for book in data:
        user_click[book.get('_id')] = book.get('book_ids')

    return user_click


def get_item_info():
    conn = ToMongo()
    data = conn.get_col('books').find({}, {'_id': 1, 'title': 1, 'first_type': 1, 'second_type': 1})
    item_info = {}
    for book in data:
        item_info[str(book.get('_id'))] = [book.get('title'), book.get('first_type')+','+book.get('second_type')]

    return item_info


def base_contribute_score(hits=None):
    if hits:
        return 1 / math.log10(1 + hits)
    else:
        return 1


def cal_item_sim_sort(user_click):
    co_appear = {}
    item_user_click_item = {}
    for user, itemlist in user_click.items():
        for index_i in range(0, len(itemlist)):
            item_id_i = itemlist[index_i]
            item_user_click_item.setdefault(item_id_i, 0)
            item_user_click_item[item_id_i] += 1
            for index_j in range(index_i + 1, len(itemlist)):
                itemid_j = itemlist[index_j]

                co_appear.setdefault(item_id_i, {})
                co_appear[item_id_i].setdefault(itemid_j, 0)
                # co_appear[item_id_i][itemid_j] += base_contribute_score()
                co_appear[item_id_i][itemid_j] += base_contribute_score(hits=len(itemlist))

                co_appear.setdefault(itemid_j, {})
                co_appear[itemid_j].setdefault(item_id_i, 0)
                # co_appear[itemid_j][item_id_i] += base_contribute_score()
                co_appear[itemid_j][item_id_i] += base_contribute_score(hits=len(itemlist))

    item_sim_score = {}
    for itemid_i, relate_item in co_appear.items():
        for itemid_j, co_time in relate_item.items():
            sim_score = co_time/math.sqrt(item_user_click_item[itemid_i] * item_user_click_item[itemid_j])
            item_sim_score.setdefault(itemid_i, {})
            item_sim_score[itemid_i].setdefault(itemid_j, 0)
            item_sim_score[itemid_i][itemid_j] = sim_score

    item_sim_score_sorted = {}
    for itemid in item_sim_score:
        item_sim_score_sorted[itemid] = sorted(item_sim_score[itemid].items(),
                                               key=operator.itemgetter(1), reverse=True)

    return item_sim_score_sorted


def cal_recom_result(sim_info, user_click):
    recom_info = {}
    for user in user_click:
        click_list = user_click[user]
        recom_info.setdefault(user, {})
        for itemid in click_list[:3]:
            if itemid not in sim_info:
                continue
            for itemsimzuhe in sim_info[itemid][:3]:
                itemsimid = itemsimzuhe[0]
                itemsimscore = itemsimzuhe[1]
                recom_info[user][itemsimid] = itemsimscore

    return recom_info


def debugitemsim(item_info, sim_info):
    fixed_itemid = "60606b10221e90994e5f2fd2"
    if fixed_itemid not in item_info:
        return

    [title_fix, genres_fix] = item_info[fixed_itemid]
    for zuhe in sim_info[fixed_itemid][:5]:
        itemid_sim = zuhe[0]
        sim_score = zuhe[1]
        if itemid_sim not in item_info:
            continue
        [title, genres] = item_info[itemid_sim]
        print(title_fix + "\t" + genres_fix + "\tsim:" + title + "\t" + genres + "\t" + str(sim_score))


def recommend_result(recom_result, item_info, user_click):
    user_id = "14"
    if user_id not in recom_result:
        return

    for zuhe in sorted(recom_result[user_id].items(), key= lambda k: k[1], reverse=True):
        itemid, score = zuhe
        if itemid not in item_info:
            continue
        # if itemid in user_click[user_id]:
            # print(itemid, user_click[user_id])
            # continue
        print(itemid, ",".join(item_info[itemid]) + "\t" + str(score))


def item_sim(sim_info, book_id, num):
    conn = ToMongo()

    fixed_itemid = book_id
    result = conn.get_col('books').find_one({'_id': ObjectId(book_id)})
    if not result:
        return
    data = []
    for zuhe in sim_info[fixed_itemid][:num]:
        itemid_sim = zuhe[0]
        # sim_score = zuhe[1]
        book = conn.get_col('books').find_one({'_id': ObjectId(itemid_sim)})
        data.append(book)
    return data


def item_cf(book_id=None, num=3):
    user_click = get_user_click()

    sim_info = cal_item_sim_sort(user_click)

    # recom_result = cal_recom_result(sim_info, user_click)

    # item_info = get_item_info()

    data = item_sim(sim_info, book_id=book_id, num=num)

    # recommend_result(recom_result, item_info, user_click)

    return data


if __name__ == '__main__':
    item_cf()
    exit()
    for user_id, recom in item_cf().items():
        print(user_id, recom)