import helpers.data as data
import helpers.graph as graph
import networkx as nx
import numpy as np
import helpers.weights as weights

from helpers.helpers import dprint

# Load orders
from predictor import predict_products_for_buyers, validate_products_for_buyers

orders = data.cut_orders_by_repeated_buyers(data.load_orders(), 20)
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
for k in range(0, 30):
    dprint("Running for k: ", k)
    predicted = predict_products_for_buyers(B, testBuyers, weights.cutOffK(lambda i1, i2, buyers: len(buyers), k))
    scores = validate_products_for_buyers(B_test, predicted, all_c)
    results[k] = tuple(np.average(list(scores), axis=0))


for k, scores in results.items():
    print(str(k) + ', ' + ', '.join(map(lambda v: "{0:.1f}".format(v*100), scores)))
