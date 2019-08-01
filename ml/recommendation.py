#  -*- coding: utf-8 -*-
#! /usr/bin/env python
#  Author locoder
#  Description : 推荐 (代码来自集体智慧编程第二章)

# 用户电影评价值数据
critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
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
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}

import math


def sim_distance(prefs , person1 , person2) :
    '''
    欧几里德距离计算
    :param prefs: 用户-物品评价值表
    :param person1: 用户1
    :param person2: 用户2
    :return:        用户1和用户2的相同物品评价的距离
    '''
    # 都评价了的商品
    si = {}

    for item in prefs[person1] :
        if item in prefs[person2] :
            si[item] = 1

    if len(si) == 0 : return 0

    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item] , 2) for item in prefs[person1] if item in prefs[person2]])

    # 一般的直接做sqrt操作，会导致相近的人值越小；如果取其倒数，但为了防止值为0的情况，分母需要+1
    return 1 / (1 + math.sqrt(sum_of_squares))

def pearson(prefs , person1 , person2) :
    '''
    皮尔逊相关度评价
    :param prefs: 用户-物品评价值表
    :param person1: 用户1
    :param person2: 用户2
    :return:        用户1和用户2的相关度，即两组数据对一条直线的拟合程度
    '''

    # 都评价了的商品
    si = {}

    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    n = len(si)

    if n == 0 : return 1

    # 评价和
    sum1 = sum(prefs[person1][item] for item in si)
    sum2 = sum(prefs[person2][item] for item in si)

    # 评价平方和
    sumSq1 = sum(pow(prefs[person1][item] , 2) for item in si)
    sumSq2 = sum(pow(prefs[person2][item] , 2) for item in si)

    # 评价值的平方和
    pSum = sum(prefs[person1][item] * prefs[person2][item] for item in si)

    num = pSum - (sum1 * sum2 / n)
    den = math.sqrt((sumSq1 - pow(sum1 , 2) / n) * (sumSq2 - pow(sum2 , 2) / n))

    if den == 0 : return 0

    return num / den

def printsimilarity(similarity = pearson) :
    used = {}
    for u1 in critics.keys() :
        used[u1] = []
        for u2 in critics.keys():
            if u2 in used and u1 in used[u2]: continue
            if u1 != u2 :
                used[u1].append(u2)
                v = similarity(critics , u1 , u2)
                print 'u1=%s , u2=%s : %f' % (u1 , u2 , v)


def topMatch(prefs , u , n = 5 , similarity = pearson) :
    scores = [(similarity(prefs , u , other) , other) for other in prefs.keys() if u != other]

    scores.sort()
    scores.reverse()
    return scores[0:n]

def getRecommendations(prefs , u , similarity = pearson) :
    # for other in prefs:
    pass



if __name__ == '__main__' :
    # print sim_distance(critics , 'Lisa Rose' , 'Michael Phillips')
    # print pearson(critics , 'Lisa Rose' , 'Michael Phillips')
    printsimilarity(pearson)
    print topMatch(critics , 'Lisa Rose')

