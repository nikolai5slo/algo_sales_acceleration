import hashlib
import os
import pickle

import networkx as nx
import itertools
from helpers.helpers import dprint


def construct_bi_graph_buyer_product(orders, name = 'Bipartite'):
    """ Constructs bipartite graph of buyers and products"""
    G = nx.Graph()
    G.name = name
    dprint("Constructing bipartite graph...")

    buyers = set([order['buyer'] for order in orders])
    products = set([order['product'] for order in orders])

    # Add nodes to bipartite graph
    G.add_nodes_from(buyers, bipartite = 0)
    G.add_nodes_from(products, bipartite = 1)

    # Loop trough orders and add edges to bipartite graph
    for order in orders:
        G.add_edge(order['buyer'], order['product'])

    if(nx.is_bipartite(G)):
        dprint('Bipartite is constructed')
    else:
        dprint('Error not bipartite graph')
        exit(-1)

    return G


def construct_relation_graph(B, k = 0, set = 0, weight_fn = lambda i1, i2, w: len(w), name=""):
    hash = hashlib.md5(nx.info(B).encode('utf-8')).hexdigest()
    filename = 'graph_' + hash + '_' + str(k) + name +'.pkl'
    if os.path.isfile('cache/' + filename) and False:
        with open('cache/' + filename, 'rb') as f:
            dprint("Relation graph loaded...")
            return pickle.load(f)

    """ Construct relation graph"""
    dprint("Constructing relation graph...")
    # Get buyers and products
    sets = nx.bipartite.sets(B)

    # Get all combinations between (0 - buyers, 1 - products) set items
    combinations = itertools.combinations(sets[set], 2)

    G = nx.Graph()

    # Construct edges with weights
    edges = [(i1, i2, weight_fn(i1, i2, list(nx.common_neighbors(B, i1, i2)))) for (i1, i2) in combinations]


    # Add edges to graph
    G.add_weighted_edges_from([edge for edge in edges if edge[2] and edge[2] >= k])

    dprint("Relation graph constructed")

    # Save to cache
    with open('cache/' + filename, 'wb') as f:
        pickle.dump(G, f)
    return G


def common_neighbours(G, nodes):
    """ Finds common neighbours of specified nodes """
    items = [set(nx.neighbors(G, node)) for node in nodes if node in G.nodes()]
    if(len(items) > 0):
        return set.intersection(*items)
    return {}

def all_neighbours(G, nodes):
    """ Finds common neighbours of specified nodes """
    items = [set(nx.neighbors(G, node)) for node in nodes if node in G.nodes()]
    if(len(items) > 0):
        return set.union(*items)
    return {}