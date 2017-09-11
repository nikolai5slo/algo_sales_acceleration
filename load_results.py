import csv
import pickle

import numpy as np
from helpers.scoring import *
import os


def saveToCsv(result, file):
    with open(file, 'w') as f:
        w = csv.writer(f)

        def calculateSC(sets):
            scs = map_many(SC1(), SC2(), SC3(), AtoI(), BtoI(), SC4(0.1))
            return np.average(list(map(expand(scs), sets)), axis=0)

        w.writerow(['k', '1', '2', '3', 'AI', 'BI', '4'])

        X = np.asarray([[k] + list(calculateSC(sets)) for k, sets in result.items()])

        w.writerows(X)

runid='1505153697'
scorepath='results/' + runid + '/scores'
if os.path.isdir(scorepath):
    os.mkdir(scorepath)

with open('results/' + runid + '/predict_buyers.pkl', 'rb') as f:
    result = pickle.load(f)
    for w, r in result.results[0].items():
        saveToCsv(r, scorepath + '/buyers_alln_%s.csv' % w)
    for w, r in result.results[1].items():
        saveToCsv(r, scorepath + '/buyers_commn_%s.csv' % w)
    print(result.timer.getAvg())

with open('results/' + runid + '/predict_products.pkl', 'rb') as f:
    result = pickle.load(f)
    for w, r in result.results[0].items():
        saveToCsv(r, scorepath + 'products_alln_%s.csv' % w)
    for w, r in result.results[1].items():
        saveToCsv(r, scorepath + 'products_commn_%s.csv' % w)
    print(result.timer.getAvg())

with open('results/' + runid + '/predict_buyers_random.pkl', 'rb') as f:
    result = pickle.load(f)
    saveToCsv(result.results, scorepath + '/buyers_random.csv')
    print(result.timer.getAvg())

with open('results/' + runid + '/predict_buyers_category.pkl', 'rb') as f:
    result = pickle.load(f)
    saveToCsv(result.results, scorepath + '/buyers_category.csv')
    print(result.timer.getAvg())

with open('results/' + runid + '/predict_buyers_mining.pkl', 'rb') as f:
    result = pickle.load(f)
    saveToCsv(result.results[0], scorepath + '/buyers_mining_LR.csv')
    saveToCsv(result.results[1], scorepath + '/buyers_mining_RF.csv')
    saveToCsv(result.results[2], scorepath + '/buyers_mining_KNN.csv')
    saveToCsv(result.results[3], scorepath + '/buyers_mining_LR.csv')
    print(result.timer.getAvg())

with open('results/' + runid + '/predict_buyers_combined.pkl', 'rb') as f:
    result = pickle.load(f)
    saveToCsv(result.results, scorepath + '/buyers_combined.csv')
    print(result.timer.getAvg())
