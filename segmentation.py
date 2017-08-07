import itertools

import numpy as np

import helpers.data as data
import helpers.graph as graph
import networkx as nx
import community

def segmentation(B, B_test, k):
    # Get each side from bipartite graph
    sets = nx.bipartite.sets(B_test)

    # Construct full graph with product nodes and relations between them
    G = graph.construct_relation_graph(B, k, 0)

    # Partition graph (with community library)
    parts = community.best_partition(G, resolution = 0.3)
    # Define score function
    def score(partitions, all_products):
        # Generate all combinations between products
        for i1, i2 in itertools.combinations(all_products, 2):
            # If pair of product have common neighbour
            if i1 in partitions and i2 in partitions:
                com_neig = list(nx.common_neighbors(B_test, i1, i2))
                if len(com_neig) > 0:
                    if partitions[i1] == partitions[i2]:
                        # Score if they are from same partition
                        yield len(com_neig) / (len(list(nx.neighbors(B_test, i1))) + len(list(nx.neighbors(B_test, i2))))
                    else:
                        yield 0
                else:
                    yield (partitions[i1] != partitions[i2])

    scores = list(score(parts, sets[0]))
    return np.average(scores), len(set(parts.values()))

# Get data with additional parameters
orders = data.load_orders()

# Split data into train and test
train, test = data.split_train_set(orders)

# Construct bipartite graph buyer <--> product
B = graph.construct_bi_graph_buyer_product(train)

# Create test bipartite graph
B_test = graph.construct_bi_graph_buyer_product(test)


res = [segmentation(B, B_test, k) for k in range(0, 10)]
print(res)