import math
import operator


def get_user_click(rating_file):
    with open(rating_file) as fp:
        user_click = {}
        for line in fp:
            if 'userId' in line:
                continue

            item = line.strip().split(',')

            if len(item) < 4:
                continue

            [userid, itemid, rating, timestamp] = item

            if float(rating) < 3.0:
                continue

            if userid not in user_click:
                user_click[userid] = []
            user_click[userid].append(itemid)

        return user_click


def get_user_click_time(rating_file):
    with open(rating_file) as fp:
        user_click = {}
        user_click_time = {}
        for line in fp:
            if 'userId' in line:
                continue

            item = line.strip().split(',')

            if len(item) < 4:
                continue

            [userid, itemid, rating, timestamp] = item

            if userid + "_" + itemid not in user_click_time:
                user_click_time[userid + '_' + itemid] = int(timestamp)

            if float(rating) < 3.0:
                continue

            if userid not in user_click:
                user_click[userid] = []
            user_click[userid].append(itemid)

        return user_click, user_click_time


def get_item_info(item_file):
    with open(item_file, encoding='utf-8') as fp:
        item_info = {}
        for line in fp:
            if 'movieId' in line:
                continue

            item = line.strip().split(',')

            if len(item) < 3:
                continue

            if len(item) == 3:
                [itemid, title, genres] = item
            elif len(item) > 3:
                itemid = item[0]
                genres = item[-1]
                title = ",".join(item[1: -1])

            if itemid not in item_info:
                item_info[itemid] = [title, genres]

        return item_info


def item_cf():
    user_click, user_click_time = get_user_click_time(r'D:\Users\Desktop\ml-latest-small\ratings.csv')

    sim_info = cal_item_sim_sort(user_click, user_click_time)

    recom_result = cal_recom_result(sim_info, user_click)

    item_info = get_item_info(r'D:\Users\Desktop\ml-latest-small\movies.csv')
    debugitemsim(item_info, sim_info)
    print('')
    debug_recomresult(recom_result, item_info)

    return recom_result


def debugitemsim(item_info, sim_info):
    fixed_itemid = "1"
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


def debug_recomresult(recom_result, item_info):
    user_id = "1"
    if user_id not in recom_result:
        return

    for zuhe in sorted(recom_result[user_id].items(), key= lambda k: k[1], reverse=True):
        itemid, score = zuhe
        if itemid not in item_info:
            continue
        print(",".join(item_info[itemid]) + "\t" + str(score))



def cal_item_sim(user_click):
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
                co_appear[item_id_i][itemid_j] += base_contribute_score()

                co_appear.setdefault(itemid_j, {})
                co_appear[itemid_j].setdefault(item_id_i, 0)
                co_appear[itemid_j][item_id_i] += base_contribute_score()

    item_sim_score = {}
    for itemid_i, relate_item in co_appear.items():
        for itemid_j, co_time in relate_item.items():
            sim_score = co_time/math.sqrt(item_user_click_item[itemid_i] * item_user_click_item[itemid_j])
            item_sim_score.setdefault(itemid_i, {})
            item_sim_score[itemid_i].setdefault(itemid_j, 0)
            item_sim_score[itemid_i][itemid_j] = sim_score

    return item_sim_score


def cal_item_sim_sort(user_click, user_click_time):
    co_appear = {}
    item_user_click_item = {}
    for user, itemlist in user_click.items():
        for index_i in range(0, len(itemlist)):
            item_id_i = itemlist[index_i]
            item_user_click_item.setdefault(item_id_i, 0)
            item_user_click_item[item_id_i] += 1
            for index_j in range(index_i + 1, len(itemlist)):
                itemid_j = itemlist[index_j]

                if str(user) + '_' + str(index_j) not in user_click_time:
                    click_time_one = 0
                else:
                    click_time_one = user_click_time[user + '_' + item_id_i]

                if str(user) + '_' + str(index_j) not in user_click_time:
                    click_time_two = 0
                else:
                    click_time_two = user_click_time[str(user) + '_' + str(index_j)]

                co_appear.setdefault(item_id_i, {})
                co_appear[item_id_i].setdefault(itemid_j, 0)

                # co_appear[item_id_i][itemid_j] += base_contribute_score()
                # co_appear[item_id_i][itemid_j] += base_contribute_score(hits=len(itemlist))
                co_appear[item_id_i][itemid_j] += base_contribute_score(click_time_one=click_time_one, click_time_two= click_time_two)


                co_appear.setdefault(itemid_j, {})
                co_appear[itemid_j].setdefault(item_id_i, 0)
                # co_appear[itemid_j][item_id_i] += base_contribute_score()
                # co_appear[itemid_j][item_id_i] += base_contribute_score(hits=len(itemlist))
                co_appear[itemid_j][item_id_i] += base_contribute_score(click_time_one=click_time_one, click_time_two= click_time_two)



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


def base_contribute_score(hits=None, click_time_one=None, click_time_two=None):
    if hits:
        return 1/math.log1p(1 + hits)
    elif click_time_two and click_time_one:
        delata_time = abs(click_time_one - click_time_two)
        d = 60 * 60 * 24
        delata_time = delata_time / d
        return 1/(1 + delata_time)
    else:
        return 1


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


def user_cf():
    user_click, user_click_time = get_user_click_time(r'D:\Users\Desktop\ml-latest-small\ratings.csv')
    # print('user_click:\n', user_click.popitem())
    # ('610', ['1', '6', '16', '32', '47', '111', '112', '153',])
    # ('userId', ['movieId'])
    # print('user_click_time:\n', user_click_time.popitem())
    # ('610_170875', 1493846415) => ('userId_movieId', timestamp)

    item_click_by_user =transfer_user_click(user_click)
    # print('item_click_by_user:\n', item_click_by_user.popitem())  # ('163981', ['610']) => ('movieId', ['userId'])

    user_sim = cal_user_sim(item_click_by_user, user_click_time)
    # print('user_sim:\n', user_sim.popitem())
    # ('578', [('605', 0.00033670133146679516), ('600', 5.206942456428644e-05), ('606', 4.4411096467387e-05)])
    # ('userId', [('userId', sim)])

    recom_result = cal_recom_result_usercf(user_click, user_sim)
    # print('recom_result:\n', recom_result['1'])
    # ('610', {'1': 0.0, '3': 0.0, '6': 0.0, '47': 0.0, '50': 0.0, '58': 0.0, '150': 0.0, '165': 0.0})
    # ('userId', {'movieId': sim, 'movieId': sim})

    item_info = get_item_info(r'D:\Users\Desktop\ml-latest-small\movies.csv')

    debug_user_sim(user_sim)
    debug_recom_result(item_info, recom_result)

    return recom_result


def debug_user_sim(user_sim):
    topK = 5
    fix_user = "1"
    if fix_user not in user_sim:
        return
    for zuhe in user_sim[fix_user][:topK]:
        userid, score = zuhe
        print(fix_user + "\t sim_user" + userid + "\t" + str(score))


def debug_recom_result(item_info, recom_result):
    fix_user = "1"
    if fix_user not in recom_result:
        return

    for itemid in recom_result["1"]:
        if itemid not in item_info:
            continue
        recom_score = recom_result["1"][itemid]
        print('recom_result:' + ",".join(item_info[itemid]) + "\t" + str(recom_score))


def transfer_user_click(user_click):
    item_click_by_user = {}
    for user in user_click:
        item_list = user_click[user]
        for itemid in item_list:
            item_click_by_user.setdefault(itemid, [])
            item_click_by_user[itemid].append(user)

    return item_click_by_user


def cal_user_sim(item_click_by_user, user_click_time):
    co_appear = {}
    user_click_count = {}
    for itemid, user_list in item_click_by_user.items():
        for index_i in range(0, len(user_list)):
            user_i = user_list[index_i]
            user_click_count.setdefault(user_i, 0)
            user_click_count[user_i] += 1
            if user_i + "_" + itemid not in user_click_time:
                click_time_one = 0
            else:
                click_time_one = user_click_time[user_i + "_" + itemid]

            for index_j in range(index_i + 1, len(user_list)):
                user_j = user_list[index_j]
                if user_j + "_" + itemid not in user_click_time:
                    click_time_two = 0
                else:
                    click_time_two = user_click_time[user_j + "_" + itemid]

                co_appear.setdefault(user_i, {})
                co_appear[user_i].setdefault(user_j, 0)
                # co_appear[user_i][user_j] += base_contribute_score_usercf()
                # co_appear[user_i][user_j] += base_contribute_score_usercf(hits=len(user_list))
                co_appear[user_i][user_j] += base_contribute_score_usercf(click_time_one=click_time_one, click_time_two=click_time_two)

                co_appear.setdefault(user_j, {})
                co_appear[user_j].setdefault(user_i, 0)
                # co_appear[user_j][user_i] += base_contribute_score_usercf()
                # co_appear[user_i][user_j] += base_contribute_score_usercf(hits=len(user_list))
                co_appear[user_i][user_j] += base_contribute_score_usercf(click_time_one=click_time_one, click_time_two=click_time_two)

    user_sim_info = {}
    for user_i, relate_user in co_appear.items():
        user_sim_info.setdefault(user_i, {})
        for user_j, cotime in relate_user.items():
            user_sim_info[user_i].setdefault(user_j, 0)
            user_sim_info[user_i][user_j] = cotime/math.sqrt(user_click_count[user_i] * user_click_count[user_j])

    user_sim_info_sort = {}
    for user in user_sim_info:
        user_sim_info_sort[user] = sorted(user_sim_info[user].items(),
                                          key=lambda kv: kv[1], reverse=True)

    return user_sim_info_sort


def base_contribute_score_usercf(hits=None, click_time_one=None, click_time_two=None):
    if hits:
        return 1/math.log10(1 + hits)
    elif click_time_two and click_time_one:
        delta_time = abs(click_time_two - click_time_one)
        d = 60 * 60 * 24
        delta_time = delta_time / d
        return 1/(1 + delta_time)
    return 1


def cal_recom_result_usercf(user_click, user_sim):
    recom_result = {}
    for user, item_list in user_click.items():
        tmp_dict = {}
        for itemid in item_list:
            tmp_dict.setdefault(itemid, 1)
        recom_result.setdefault(user, {})
        for zuhe in user_sim[user][:3]:
            #  [('96', 0.15791081894849407), ('469', 0.1172771823445635), ('27', 0.08282266726133267)]
            userid_j, sim_score = zuhe
            if userid_j not in user_click:
                continue
            for itemid_j in user_click[userid_j][:5]:
                #  itemid_j ['1', '34', '50', '110', '150']
                recom_result[user].setdefault(itemid_j, sim_score)

    return recom_result


if __name__ == '__main__':
    import time
    start = time.time()
    result = item_cf()
    # print(result['1'])
    print('end time:%s' % (time.time() - start))
    exit()
    user_click = get_user_click(r'D:\Users\Desktop\ml-latest-small\ratings.csv')
    print(len(user_click))
    print(user_click['1'])
    item_info = get_item_info(r'D:\Users\Desktop\ml-latest-small\movies.csv')
    print(item_info['11'])
