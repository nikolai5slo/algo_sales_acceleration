from functools import reduce

import numpy as np
import sys
import pickle

import helpers.data as data
import helpers.graph as graph
import networkx as nx
import helpers.weights as weights

from helpers.helpers import dprint, readArgs
from predictor import predict_products_for_buyers, predict_buyers_for_products, validate_buyers_for_products

(K, orderlim, saveto) = readArgs()

def combine_union(predictedBuyers, predictedProducts):
    product_buyers = {product: buyers for product, buyers in predictedBuyers}
    buyer_products = {buyer: products for buyer, products in predictedProducts}

    predicted = []
    for product, buyers in product_buyers.items():
        newbuyers = [buyer for buyer, products in buyer_products.items() if product in products]
        predicted.append((product, buyers + newbuyers))
    return predicted

def combine_intersect(predictedBuyers, predictedProducts):
    product_buyers = {product: buyers for product, buyers in predictedBuyers}
    buyer_products = {buyer: products for buyer, products in predictedProducts}

    predicted = [
        (product, list(filter(lambda buyer: buyer in buyer_products and product in buyer_products[buyer], buyers))) for
        product, buyers in product_buyers.items()
    ]

    return predicted

orders = data.cut_orders_by_repeated_buyers(data.load_orders(), orderlim)
#orders = list(filter(lambda o: o['promotion'] == None, orders))
buyers = set([order['buyer'] for order in orders])

# Split orders into train and test sets
train, test = data.split_train_set(orders)

# Construct bipartite graph from train set
B = graph.construct_bi_graph_buyer_product(train)

# Create test bipartite graph
B_test = graph.construct_bi_graph_buyer_product(test)

# Get all test products from test set
testBuyers, testProducts = nx.bipartite.sets(B_test)

all_c = len(buyers)

product_info = {order['product']: order for order in orders}

results = {}
for k2 in range(0, K):
    predictedProducts = predict_products_for_buyers(B, testBuyers,
                                                    weights.cutOffK(lambda i1, i2, buyers: len(buyers), k2))
    buyer_products = {buyer: products for buyer, products in predictedProducts}

    for k in range(0, K):
        dprint("Running for k: ", k, k2)

        predictedBuyers = predict_buyers_for_products(B, testProducts,
                                                      weights.cutOffK(lambda i1, i2, products: len(products), k))

        product_buyers = {product: buyers for product, buyers in predictedBuyers}


        predicted = [(product, list(filter(lambda buyer: buyer in buyer_products and product in buyer_products[buyer], buyers))) for product, buyers in product_buyers.items()]


        scores = validate_buyers_for_products(B_test, predicted, all_c)
        results[(k, k2)] = tuple(np.average(list(scores), axis=0))

if saveto:
    with open(saveto, 'wb') as f:
        pickle.dump((results),f)


for (k, k2), scores in results.items():
    print(str(k) + '_' + str(k2) + ', ' + ', '.join(map(lambda v: "{0:.1f}".format(v*100), scores)))
