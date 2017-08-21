import helpers.data as data
import helpers.graph as graph
import networkx as nx
import numpy as np
import helpers.weights as weights

from helpers.helpers import dprint

# Load orders
from predictor import predict_buyers_for_products, validate_buyers_for_products

orders = data.cut_orders_by_repeated_buyers(data.load_orders(), 15)
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

results = [{}, {}]
for mi, m in enumerate([graph.all_neighbours, graph.common_neighbours]):
    for k in range(0, 20):
        dprint("Running for k: ", k)
        predicted = predict_buyers_for_products(B, testProducts, weights.cutOffK(weights.simple_weight(), k), m)
        scores = validate_buyers_for_products(B_test, predicted, all_c)
        results[mi][k] = tuple(np.average(list(scores), axis=0))


print("UNION")
for k, scores in results[0].items():
    print(str(k) + ', ' + ', '.join(map(lambda v: "{0:.1f}".format(v*100), scores)))
print()

print("INTERSECT")
for k, scores in results[1].items():
    print(str(k) + ', ' + ', '.join(map(lambda v: "{0:.1f}".format(v*100), scores)))
