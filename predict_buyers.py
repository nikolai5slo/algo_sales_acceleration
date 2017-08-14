import helpers.data as data
import helpers.graph as graph
import networkx as nx
import numpy as np
import helpers.weights as weights

from helpers.helpers import dprint


def predict_buyers_for_products(B, products, k = 0, weight_fn = lambda x: len(x)):
    """ Do prediction for each products """

    # Construct graph with product nodes and buyer edges from bipartite graph
    G = graph.construct_relation_graph(B, 0, weight_fn, 'c05')


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
orders = data.cut_orders_by_repeated_buyers(data.load_orders(), 20)
#orders = list(filter(lambda o: o['promotion'] == None, orders))
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

product_info = {order['product']: order for order in orders}

results = {}
for k in range(1, 10):
    dprint("Running for k: ", k)
    predicted = predict_buyers_for_products(B, testProducts, k, weights.cutOffK(weights.simple_weight(), k))
    scores = validate_buyers_for_products(B_test, predicted, all_c)
    results[k] = tuple(np.average(list(scores), axis=0))


for k, scores in results.items():
    print(str(k) + ', ' + ', '.join(map(lambda v: "{0:.1f}".format(v*100), scores)))
    #print(k, ":", scores)