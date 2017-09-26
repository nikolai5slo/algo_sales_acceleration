from functools import reduce

import numpy as np
import sys
import pickle

import helpers.data as data
import helpers.graph as graph
import networkx as nx
import helpers.weights as weights

from helpers.helpers import dprint, readArgs, MeasureTimer, Result, printResults
from predictor import predict_products_for_buyers, predict_buyers_for_products, validate_buyers_for_products, \
    validate_products_for_buyers

(K, orderlim, saveto) = readArgs()


timer = MeasureTimer()

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

def methodIntersect(buyer_products, product_buyers):
    for product, buyers in product_buyers.items():
        yield (product, list(filter(lambda buyer: buyer in buyer_products and product in buyer_products[buyer], buyers)))
def methodUnion(buyer_products, product_buyers):
    for product, buyers in product_buyers.items():
        buyers += [buyer for buyer, products in buyer_products.items() if product in products]
        yield (product, set(buyers))

def methodIntersectProduct(buyer_products, product_buyers):
    for buyer, products in buyer_products.items():
        yield (buyer, list(filter(lambda product: product in product_buyers and buyer in product_buyers[product], products)))
def methodUnionProduct(buyer_products, product_buyers):
    for buyer, products in buyer_products.items():
        products += [product for product, buyers in product_buyers.items() if buyer in buyers]
        yield (buyer, set(products))

results = [{},{}]
for mi, m in enumerate([methodIntersect, methodUnion]):
    for k2 in range(0, K):
        with timer:
            predictedProducts = predict_products_for_buyers(B, testBuyers,
                                                            weights.cutOffK(weights.simple_weight(), k2))
            buyer_products = {buyer: products for buyer, products in predictedProducts}

            for k in map(int, np.linspace(230, 240, K)):
                dprint("Running for k: ", k, k2)

                predictedBuyers = predict_buyers_for_products(B, testProducts,
                                                              weights.cutOffK(weights.bipartite_products_weights(B), k))

                product_buyers = {product: buyers for product, buyers in predictedBuyers}


                predicted = list(m(buyer_products, product_buyers))


                #scores = validate_buyers_for_products(B_test, predicted, all_c)
                scores = validate_products_for_buyers(B_test, predicted, all_c)
                #results[(k, k2)] = tuple(np.average(list(scores), axis=0))
                results[mi][(k, k2)] = list(scores)

if saveto:
    with open(saveto, 'wb') as f:
        pickle.dump(Result(results, timer),f)


print('Intersect:')
printResults(results[0])

print('Union:')
printResults(results[1])

print("Average time %s" % timer.getAverage())