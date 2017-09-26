import csv
import pickle

import numpy as np
from helpers.scoring import *
import os, sys

if len(sys.argv) > 1:
    runid=sys.argv[1]
else:
    print("Please specify runid")
    exit(1)

#runid='1505382358'
scorepath='results/' + runid + '/scores'
if not os.path.isdir(scorepath):
    os.mkdir(scorepath)

times = {}
with open('results/' + runid + '/predict_buyers.pkl', 'rb') as f:
    result = pickle.load(f)
    times['b'] = result.timer.getAvg()*1000
    print(result.timer.getAvg())

with open('results/' + runid + '/predict_buyers_random.pkl', 'rb') as f:
    result = pickle.load(f)
    times['bR'] = result.timer.getAvg() * 1000

with open('results/' + runid + '/predict_buyers_category.pkl', 'rb') as f:
    result = pickle.load(f)
    times['bC'] = result.timer.getAvg() * 1000

with open('results/' + runid + '/predict_buyers_mining.pkl', 'rb') as f:
    result = pickle.load(f)
    times['bM'] = result.timer.getAvg() * 1000

with open('results/' + runid + '/predict_buyers_hybrid.pkl', 'rb') as f:
    result = pickle.load(f)
    times['bH'] = result.timer.getAvg() * 1000

############ PRODUCTS
with open('results/' + runid + '/predict_products.pkl', 'rb') as f:
    result = pickle.load(f)
    times['p'] = result.timer.getAvg() * 1000
with open('results/' + runid + '/predict_products_random.pkl', 'rb') as f:
    result = pickle.load(f)
    times['pR'] = result.timer.getAvg() * 1000

with open('results/' + runid + '/predict_products_category.pkl', 'rb') as f:
    result = pickle.load(f)
    times['pC'] = result.timer.getAvg() * 1000

with open('results/' + runid + '/predict_products_mining.pkl', 'rb') as f:
    result = pickle.load(f)
    times['pM'] = result.timer.getAvg() * 1000


print(times)
with open(scorepath + '/times.csv', 'w') as f:
    w = csv.writer(f)
    w.writerow(list(times.keys()))
    w.writerow(list(times.values()))
