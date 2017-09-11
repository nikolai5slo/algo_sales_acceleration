from collections import defaultdict

import sys
import pickle

import helpers.data as data
import helpers.graph as graph
import networkx as nx
import numpy as np

from helpers.helpers import dprint, readArgs, Result, MeasureTimer, printResults

from predictor import validate_buyers_for_products

(K, orderlim, saveto) = readArgs()

# Load orders
orders = data.cut_orders_by_repeated_buyers(data.load_orders(), orderlim)

buyers = set([order['buyer'] for order in orders])
all_c = len(buyers)

# Split orders into train and test sets
train, test = data.split_train_set(orders)

# Create test bipartite graph
B_test = graph.construct_bi_graph_buyer_product(test)
testBuyers, testProducts = nx.bipartite.sets(B_test)

category_buyers = defaultdict(lambda: defaultdict(int))
product_category = {order['product']: order['category'] for order in orders}

timer = MeasureTimer()

for order in train:
    category_buyers[order['category']][order['buyer']] += 1

def predict_category_buyers(testProducts, category_buyers, product_category, k):
    for product in testProducts:
        category = product_category[product]
        buyers = [buyer for buyer, count in category_buyers[category].items() if count > k]
        yield (product, buyers)

results = {}
for k in range(0, K):
    dprint("Running for k: ", k)
    with timer:
        predicted = predict_category_buyers(testProducts, category_buyers, product_category, k)

    scores = validate_buyers_for_products(B_test, predicted, all_c)
    #results[k] = tuple(np.average(list(scores), axis=0))
    results[k] = list(scores)

if saveto:
    with open(saveto, 'wb') as f:
        pickle.dump(Result(results, timer),f)


printResults(results)

print("Average time %s" % timer.getAverage())