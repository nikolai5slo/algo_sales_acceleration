import helpers.graph as graph
import networkx as nx

def predict_products_for_buyers(B, buyers, weight_fn = lambda x: len(x), neighbour_method = graph.all_neighbours):
    """ Do prediction for each products """

    # Construct graph with product nodes and buyer edges from bipartite graph
    G = graph.construct_relation_graph(B, 1, weight_fn, 'c05')

    for buyer in buyers:
        # Get all train products from buyer
        trainProducts = nx.neighbors(B, buyer) if buyer in B.nodes() else []

        # Do prediction
        predictedProducts = list(neighbour_method(G, trainProducts))

        # Return prediction
        yield buyer, predictedProducts


def validate_products_for_buyers(B_test, predictions, allProductsCount):

    for (buyer, predicted) in predictions:
        # Get actual future products for buyer
        testProducts = nx.neighbors(B_test, buyer) if buyer in B_test.nodes() else []

        # Score
        if len(testProducts) > 0:
            # Get true positives by intersection between predicted products set and test product set
            TP = set(predicted).intersection(testProducts)

            # Return sets (A, B, TP, I)
            yield len(predicted), len(testProducts), len(TP), allProductsCount




def predict_buyers_for_products(B, products, weight_fn = lambda x: len(x), neighbour_method = graph.all_neighbours):
    """ Do prediction for each products """

    # Construct graph with product nodes and buyer edges from bipartite graph
    G = graph.construct_relation_graph(B, 0, weight_fn, 'c05')


    for product in products:
        # Get all train buyers from product
        trainBuyers = nx.neighbors(B, product) if product in B.nodes() else []

        # Do prediction
        predictedBuyers = list(neighbour_method(G, trainBuyers))

        # Return prediction
        yield product, predictedBuyers


def validate_buyers_for_products(B_test, predictions, allBuyersCount):

    for (product, predicted) in predictions:
        # Get actual future buyers for product
        testBuyers = nx.neighbors(B_test, product) if product in B_test.nodes() else []

        # Score
        # Get true positives by intersection between predicted buyers set and test buyer set
        TP = set(predicted).intersection(testBuyers)

        # Return sets (A, B, TP, I)
        yield len(predicted), len(testBuyers), len(TP), allBuyersCount
