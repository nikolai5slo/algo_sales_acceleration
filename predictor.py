import helpers.graph as graph
import networkx as nx

def predict_products_for_buyers(B, buyers, weight_fn = lambda x: len(x)):
    """ Do prediction for each products """

    # Construct graph with product nodes and buyer edges from bipartite graph
    G = graph.construct_relation_graph(B, 1, weight_fn, 'c05')

    for buyer in buyers:
        # Get all train products from buyer
        trainProducts = nx.neighbors(B, buyer) if buyer in B.nodes() else []

        # Do prediction
        predictedProducts = list(graph.all_neighbours(G, trainProducts))

        # Return prediction
        yield buyer, predictedProducts


def validate_products_for_buyers(B_test, predictions, allProductsCount):

    for (buyer, predicted) in predictions:
        # Get actual future products for buyer
        testProducts = nx.neighbors(B_test, buyer) if buyer in B_test.nodes() else []

        # Score
        if len(testProducts) > 0:
            # Get true positives by intersection between predicted products set and test product set
            valid = set(predicted).intersection(testProducts)

            # Get share of true positives among all predicted
            valid_predicted = len(valid) / len(predicted) if len(valid) > 0 else 0

            # Get share of true positives among actual test buyers
            valid_test = len(valid) / len(testProducts) if len(valid) > 0 else 0

            # Get share of predicted among all buyers
            predicted_all = len(predicted) / allProductsCount if len(predicted) > 0 else 0

            # Get share of actual buyers among all buyers
            test_all = len(testProducts) / allProductsCount if len(testProducts) > 0 else 0

            # Return result
            yield valid_predicted, valid_test, predicted_all, test_all
        #elif len(predicted) <= 0:
            # If no buyer actually bought this product and we predicted that, then we are right
            #yield 0, 0, 0, 1




def predict_buyers_for_products(B, products, weight_fn = lambda x: len(x)):
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
        testBuyers = nx.neighbors(B_test, product) if product in B_test.nodes() else []

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
