import helpers.data as data
import helpers.graph as graph
import networkx as nx
import numpy as np
import helpers.weights as weights

from helpers.helpers import dprint

# Load orders
#TODO: Exclude orders in promotions
from predictor import predict_buyers_for_products, validate_buyers_for_products

orders = data.cut_orders_by_repeated_buyers(data.load_orders(), 15)
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
for k in range(0, 20):
    dprint("Running for k: ", k)
    w_fns = [
        weights.simple_weight(),
        weights.weight_rating(product_info),
        weights.weight_quantity(product_info),
        weights.weight_promotion(product_info)
    ]
    w_ws = [0.6, 0.2, 0.5, 0.1]
    predicted = predict_buyers_for_products(B, testProducts, weights.cutOffK(weights.combine_weights(w_fns, w_ws), k))
    scores = validate_buyers_for_products(B_test, predicted, all_c)
    results[k] = tuple(np.average(list(scores), axis=0))


for k, scores in results.items():
    print(str(k) + ', ' + ', '.join(map(lambda v: "{0:.1f}".format(v*100), scores)))
