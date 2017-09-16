from collections import defaultdict

import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

import helpers.data as data
import helpers.graph as graph
import networkx as nx
import numpy as np

from helpers.helpers import dprint, readArgs, Result, MeasureTimer, printResults

from predictor import validate_buyers_for_products
from sklearn import linear_model

(K, orderlim, saveto) = readArgs()

# Load orders
orders = data.cut_orders_by_repeated_buyers(data.load_orders(), orderlim)

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

timer = MeasureTimer()

for order in train:
    buyer_product_count[order['buyer']][order['product']] += order['quantity']

for order in test:
    buyer_product_test_count[order['buyer']][order['product']] += order['quantity']

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

        if KNeighborsRegressor == method:
            l = method(n_neighbors = 3)
        elif method == 1:
            l = make_pipeline(PolynomialFeatures(5), Ridge())
        else:
            l = method()

        if method == LogisticRegression:
            if sum(y > 0) <= 0:
                for k in krange:
                    yield (k, product, [])
                continue
            l.fit(X, y > 0)
        else:
            l.fit(X, y)


        Xtest = np.delete(Xytest, idx, 1)
        predicted = l.predict(Xtest)

        for k in krange:
            potentialBuyers = np.array(list(buyer_product_test_count.keys()))[predicted >= k]
            yield (k, product, potentialBuyers)

results = [{}, {}, {}, {}]
for idx, m in enumerate([linear_model.LinearRegression, RandomForestRegressor, KNeighborsRegressor, LogisticRegression]):
    with timer:
        all_predicted = predict_buyers_mining(testProducts, list(np.linspace(0, 1, K)), m)
    predicted = defaultdict(list)
    for p in all_predicted:
        predicted[p[0]].append(p[1:])

    for k, p in predicted.items():
        scores = validate_buyers_for_products(B_test, p, all_c)
        #results[idx][k] = tuple(np.average(list(scores), axis=0))
        results[idx][k] = list(scores)

if saveto:
    with open(saveto, 'wb') as f:
        pickle.dump(Result(results, timer),f)



print("LINEAR REGRESSION")
printResults(results[0])

print("RANDOM FOREST")
printResults(results[1])

print("KNN")
printResults(results[2])

print("LOGISTIC REGRESSION")
printResults(results[3])

print("Average time %s" % timer.getAverage())