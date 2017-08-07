import networkx as nx
import itertools
from helpers.helpers import dprint


def construct_bi_graph_buyer_product(orders):
    """ Constructs bipartite graph of buyers and products"""
    G = nx.Graph()
    dprint("Constructing bipartite graph...")

    buyers = [order[1] for order in orders]
    products = [order[2] for order in orders]

    # Add nodes to bipartite graph
    G.add_nodes_from(buyers, bipartite = 0)
    G.add_nodes_from(products, bipartite = 1)

    # Loop trough orders and add edges to bipartite graph
    for (_, buyer, product, _, _, _, _) in orders:
        G.add_edge(buyer, product)

    if(nx.is_bipartite(G)):
        dprint('Bipartite is constructed')
    else:
        dprint('Error not bipartite graph')
        exit(-1)

    return G


def construct_relation_graph(B, k = 0, set = 0, weight_fn = lambda i1, i2: 0):
    """ Construct relation graph"""
    dprint("Constructing relation graph...")
    # Get buyers and products
    sets = nx.bipartite.sets(B)

    # Get all combinations between (0 - buyers, 1 - products) set items
    combinations = itertools.combinations(sets[set], 2)

    G = nx.Graph()

    # Construct edges with weights
    edges = [(i1, i2, len(list(nx.common_neighbors(B, i1, i2))) + weight_fn(i1, i2)) for (i1, i2) in combinations]


    # Add edges to graph
    G.add_weighted_edges_from([edge for edge in edges if edge[2] >= k])

    dprint("Relation graph constructed")
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