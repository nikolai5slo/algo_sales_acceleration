from collections import defaultdict

from sklearn.ensemble import RandomForestRegressor

import helpers.data as data
import helpers.graph as graph
import networkx as nx
import numpy as np

from helpers.helpers import dprint

from predictor import validate_buyers_for_products
from sklearn import linear_model

# Load orders
orders = data.cut_orders_by_repeated_buyers(data.load_orders(), 15)

buyers = set([order['buyer'] for order in orders])
products = list(set([order['product'] for order in orders]))
all_c = len(buyers)

# Split orders into train and test sets
train, test = data.split_train_set(orders)

# Create test bipartite graph
B_test = graph.construct_bi_graph_buyer_product(test)
testBuyers, testProducts = nx.bipartite.sets(B_test)

buyer_product_count = defaultdict(lambda: defaultdict(int))
buyer_product_test_count = defaultdict(lambda: defaultdict(int))

for order in train:
    buyer_product_count[order['buyer']][order['product']] += 1

for order in test:
    buyer_product_test_count[order['buyer']][order['product']] += 1

def predict_buyers_mining(testProducts, krange = [0], method = linear_model.LinearRegression):
    i = 0
    Xy = []
    for buyer, prts in buyer_product_count.items():
        products_count = [int(prts[p]) for p in products]
        Xy.append(products_count)

    Xytest = []
    for buyer, prts in buyer_product_test_count.items():
        products_count = [int(prts[p]) for p in products]
        Xytest.append(products_count)

    Xy = np.array(Xy)
    Xytest = np.array(Xytest)

    for product in testProducts:
        dprint(i/len(testProducts))
        i+=1

        # Train
        idx = products.index(product)
        X = np.delete(Xy, idx, 1)
        y = Xy[:,idx]

        l = method()
        l.fit(X, y)


        Xtest = np.delete(Xytest, idx, 1)
        predicted = l.predict(Xtest)

        for k in krange:
            potentialBuyers = np.array(list(buyer_product_count.keys()))[predicted > k]
            yield (k, product, potentialBuyers)

results = [{}, {}]
for idx, m in enumerate([linear_model.LinearRegression, RandomForestRegressor]):
    all_predicted = predict_buyers_mining(testProducts, list(np.linspace(0, 1, 20)), m)
    predicted = defaultdict(list)
    for p in all_predicted:
        predicted[p[0]].append(p[1:])

    for k, p in predicted.items():
        scores = validate_buyers_for_products(B_test, p, all_c)
        results[idx][k] = tuple(np.average(list(scores), axis=0))

print("LINEAR REGRESSION")
for k, scores in results[0].items():
    print("{0:.2f}".format(k) + ', ' + ', '.join(map(lambda v: "{0:.1f}".format(v*100), scores)))

print("RANDOM FOREST")
for k, scores in results[1].items():
    print("{0:.2f}".format(k) + ', ' + ', '.join(map(lambda v: "{0:.1f}".format(v*100), scores)))
