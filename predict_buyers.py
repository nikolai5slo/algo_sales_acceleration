from itertools import groupby

import helpers.data as data
import helpers.graph as graph
import networkx as nx
import numpy as np
import decimal

from helpers.helpers import dprint


def predict_buyers_for_products(B, products, k = 0, products_info = {}):
    """ Do prediction for each products """

    def wieght_rating(i1, i2, products):
        l = np.array([float(products_info[p]['rating']) if p in products_info and products_info[p]['rating'] != None else float(0) for p in products])
        sum = np.sum(l)
        if sum <= 0:
            return len(products)*2.5
        return len(products) + (sum/5)*5

    def weight_category(i1, i2, products):
        l = map(lambda pi: product_info[pi]['category'], products)
        g = [len(list(group)) for key, group in groupby(l)]
        if len(g) > 0:
            return len(products) + max(g)
        return len(products)

    def simple_weight(i1, i2, products):
        return len(products)



    # Construct graph with product nodes and buyer edges from bipartite graph
    G = graph.construct_relation_graph(B, k, 0, simple_weight, 'c05')


    for product in products:
        # Get all train buyers from product
        trainBuyers = nx.neighbors(B, product) if product in B.nodes() else []

        # Do prediction
        predictedBuyers = list(graph.all_neighbours(G, trainBuyers))

        # Return prediction
        yield product, predictedBuyers


def validate_buyers_for_products(B_test, predictions, allBuyersCount):

    for (product, predicted) in predictions:
        # Get actual future buyers for product
        testBuyers = nx.neighbors(B_test, product) if product in B.nodes() else []

        # Score
        if len(testBuyers) > 0:
            # Get true positives by intersection between predicted buyers set and test buyer set
            valid = set(predicted).intersection(testBuyers)

            # Get share of true positives among all predicted
            valid_predicted = len(valid) / len(predicted) if len(valid) > 0 else 0

            # Get share of true positives among actual test buyers
            valid_test = len(valid) / len(testBuyers) if len(valid) > 0 else 0

            # Get share of predicted among all buyers
            predicted_all = len(predicted) / allBuyersCount if len(predicted) > 0 else 0

            # Get share of actual buyers among all buyers
            test_all = len(testBuyers) / allBuyersCount if len(testBuyers) > 0 else 0

            # Return result
            yield valid_predicted, valid_test, predicted_all, test_all
        #elif len(predicted) <= 0:
            # If no buyer actually bought this product and we predicted that, then we are right
            #yield 0, 0, 0, 1

# Load orders
#TODO: Exclude orders in promotions
orders = data.load_orders()
orders = list(filter(lambda o: o['promotion'] == None, orders))
buyers = set([order['buyer'] for order in orders])

#TODO: Better splitting (percent)
# Split orders into train and test sets
train, test = data.split_train_set(orders)

# Construct bipartite graph from train set
B = graph.construct_bi_graph_buyer_product(train)

# Create test bipartite graph
B_test = graph.construct_bi_graph_buyer_product(test)

# Get all test products from test set
testBuyers, testProducts = nx.bipartite.sets(B_test)

all_c = len(buyers)

product_info = {order['buyer']: order for order in orders}

results = {}
for k in range(1, 6):
    dprint("Running for k: ", k)
    predicted = predict_buyers_for_products(B, testProducts, k, product_info)
    scores = validate_buyers_for_products(B_test, predicted, all_c)
    results[k] = tuple(np.average(list(scores), axis=0))


for k, scores in results.items():
    print(str(k) + ', ' + ', '.join(map(lambda v: "{0:.1f}".format(v*100), scores)))
    #print(k, ":", scores)