from math import sqrt

from recommend import get_data


def sim_distance(prefs,person1,person2):
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1
    # print(si)
    if len(si) == 0:
        return 0
    squares = [pow(prefs[person1][item]-prefs[person2][item],2) for item in prefs[person1] if item in prefs[person2]]
    sum_of_squares=sum(squares)
    # print(squares)
    return 1/(1+sum_of_squares)


def sim_pearson(prefs, p1, p2):
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1
    #     print(si)
    if len(si) == 0:
        return 0

    n = len(si)
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))

    if den == 0:
        return 0
    r = num / den
    return r


def topMatches(prefs, person, n=5, similarity=sim_pearson):
    scores = [(similarity(prefs, person, other), other) for other in prefs if other != person]

    scores.sort()
    scores.reverse()

    return scores[0:n]


def getRecommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSums = {}

    for other in prefs:
        if other == person:
            continue

        sim = similarity(prefs, person, other)
        if sim < 0:
            #             print('\nSIM < 0:', other)
            continue
        #         print(sim)

        for item in prefs[other]:
            if item not in prefs[person] or prefs[person][item] == 0:  # 没有评过分的
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim

                simSums.setdefault(item, 0)
                simSums[item] += sim
    #             print(item, '|\n', prefs[person], '|\n', prefs[person][item], '\n')
    # print("\n {} ".format(totals))
    # print(" {} \n".format(simSums))

    rankings = [(total / simSums[item], item) for item, total in totals.items()]
    rankings.sort()
    rankings.reverse()
    return rankings


def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            result[item][person] = prefs[person][item]
    return result


if __name__ == '__main__':
    data = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
                          'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
                          'The Night Listener': 3.0},

            'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
                             'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
                             'You, Me and Dupree': 3.5},

            'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
                                 'Superman Returns': 3.5, 'The Night Listener': 4.0},

            'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
                             'The Night Listener': 4.5, 'Superman Returns': 4.0,
                             'You, Me and Dupree': 2.5},

            'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                             'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
                             'You, Me and Dupree': 2.0},

            'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                              'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},

            'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0}
            }
    # 基于用户
    critics = data
    user = getRecommendations(critics, 'Toby')
    print(user)
    #
    # # 基于物品
    movies = transformPrefs(critics)
    # print(data)
    # print(critics)
    product = getRecommendations(movies, 'You, Me and Dupree')
    print(product)