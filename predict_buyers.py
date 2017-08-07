import helpers.data as data
import helpers.graph as graph
import networkx as nx
import numpy as np

from helpers.helpers import dprint


def predict_buyers_for_products(B, products, k = 0):
    """ Do prediction for each products """

    # Construct graph with product nodes and buyer edges from bipartite graph
    G = graph.construct_relation_graph(B, k)


    for product in products:
        # Get all train buyers from product
        trainBuyers = nx.neighbors(B, product) if product in B.nodes() else []

        # Do prediction
        predictedBuyers = list(graph.common_neighbours(G, trainBuyers))

        # Return prediction
        yield product, predictedBuyers


def validate_buyers_for_products(B_test, predictions):

    for (product, predicted) in predictions:
        # Get actual future buyers for product
        testBuyers = nx.neighbors(B_test, product) if product in B.nodes() else []

        # Score
        if len(testBuyers) > 0:
            # Get true positives by intersection between predicted buyers set and test buyer set
            true_positives = set(predicted).intersection(testBuyers)

            # Get share of true positives among all predicted
            valid_predicted = len(true_positives) / len(predicted) if len(true_positives) > 0 else 0

            # Get share of true positives among actual test buyers
            valid_test = len(true_positives) / len(testBuyers) if len(true_positives) > 0 else 0

            # Return result
            yield valid_predicted, valid_test
        #elif len(predicted) <= 0:
            # If no buyer actually bought this product and we predicted that, then we are right
            #yield 1, 1

# Load orders
orders = data.load_orders()

# Split orders into train and test sets
train, test = data.split_train_set(orders)

# Construct bipartite graph from train set
B = graph.construct_bi_graph_buyer_product(train)

# Create test bipartite graph
B_test = graph.construct_bi_graph_buyer_product(test)

# Get all test products from test set
_, testProducts = nx.bipartite.sets(B_test)


results = {}
for k in range(0, 20):
    dprint("Running for k: ", k)
    predicted = predict_buyers_for_products(B, testProducts, k)
    scores = validate_buyers_for_products(B_test, predicted)
    results[k] = tuple(np.average(list(scores), axis=0))


for k, scores in results.items():
    print(k, ":", scores)