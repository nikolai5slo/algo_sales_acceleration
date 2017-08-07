import hashlib
import os
from urllib.error import HTTPError
from amazon.api import AmazonAPI
import pickle
import time
from collections import defaultdict
import config

import pymysql
from helpers.helpers import dprint

def load_orders_from_db():
    """ Loads orders """
    # Create mysql connection
    db = pymysql.connect(host=config.MYSQL_CONFIG['host'],    # your host, usually localhost
                         user=config.MYSQL_CONFIG['user'],         # your username
                         passwd=config.MYSQL_CONFIG['password'],  # your password
                         db=config.MYSQL_CONFIG['dbname'])        # name of the data base

    # Connect to mysql
    with db.cursor() as cur:

        dprint("Fetching buyers...")
        # Execute sql query which gets all buyers who had ordered at least 20 orders
        cur.execute("SELECT mb.orders.customer_email FROM mb.orders WHERE orders.customer_email IS NOT NULL GROUP BY orders.customer_email HAVING COUNT(*) > 10;")

        # Get all distinct buyers
        buyers = set(map(lambda x: x[0], cur.fetchall()))

        dprint("Querying orders...")
        # Execute query which gets all ordered products with buyer, seller
        format_strings = ','.join(['%s'] * len(buyers))
        credentials = '262, 316, 880, 979, 1012, 1039, 1045, 1150, 1324, 1715, 1991, 2027, 30, 75, 124, 232, 346, 502, 523, 670, 754, 787, 790, 808, 820, 838, 883, 913, 982, 1069, 1102, 1162, 1165, 1189, 1210, 1213, 1288, 1300, 1348, 1366, 1381, 1408, 1427, 1506, 1572, 1611, 1635, 1769, 1775, 1820, 1838, 1868, 1964, 2015, 2024, 38, 628, 700, 793, 1048, 1072, 1192, 1216, 1231, 1387, 1420, 1429, 1641, 1670, 1910, 1940, 1967, 53, 631, 709, 796, 1075, 1201, 1225, 1237, 1463, 1679, 1727, 1841, 1973, 41, 703, 739, 799, 1078, 1198, 1219, 1234, 1432, 1673, 1733, 1871, 1970, 59, 712, 742, 802, 1081, 1204, 1222, 1240, 1438, 1664, 1709, 1721, 1976'
        cur.execute(
            #AVG(IF(ISNULL(feedback.rating),0,feedback.rating)) GROUP_BY order_items.id
            "SELECT orders.credential_id, customer_email, product_id FROM orders INNER JOIN order_items ON orders.id = order_items.order_id LEFT JOIN feedback ON feedback.order_id = orders.id WHERE orders.customer_email IN (%s) AND orders.credential_id NOT IN (%s) ORDER BY orders.status_shipped_at" % (format_strings, credentials),
            tuple(buyers))

        # Orders to list
        orders = list(map(lambda order: (order[0], hashlib.md5(order[1].encode('utf-8')).hexdigest(), order[2]), cur.fetchall()))

        # Print orders stat info
        dprint("Orders count: ", len(orders))
        dprint("Buyers count: ", len(buyers))

        return orders

def load_orders():
    """ Loads orders from cache if exists or gets from mysql and amazon api """

    # If cached exists
    if os.path.isfile('orders.pkl'):
        with open('orders.pkl', 'rb') as f:
            return pickle.load(f)

    # Get from database
    orders = load_orders_from_db()

    # Get additional data from amazon
    orders = get_additional_data_from_amz(orders)

    # Save to cache
    with open('orders.pkl', 'wb') as f:
        pickle.dump(orders, f)

    return orders


def split_train_set(orders):
    """ Split orders into train and test set"""

    helper_dict = defaultdict(int)
    train = []
    test = []

    for order in reversed(orders):
        if helper_dict[order[1]] <= 3:
            helper_dict[order[1]] += 1
            test.append(order)
        else:
            train.append(order)

    return train, test


def get_additional_data_from_amz(orders):
    # Create mysql connection
    db = pymysql.connect(host=config.MYSQL_CONFIG['host'],  # your host, usually localhost
                         user=config.MYSQL_CONFIG['user'],  # your username
                         passwd=config.MYSQL_CONFIG['password'],  # your password
                         db=config.MYSQL_CONFIG['dbname'])  # name of the data base

    with db.cursor() as cur:
        querylist = ','.join([ str(pid) for (_, _, pid) in orders ])
        cur.execute("SELECT id, asin FROM products WHERE id IN (%s)" % querylist)

        # Orders to list
        #products = {id: asin for (id, asin) in cur.fetchall()}
        products = list(cur.fetchall())

    # Setup amazon api
    amazon = AmazonAPI(config.AWS_CONFIG['key'], config.AWS_CONFIG['secret'], config.AWS_CONFIG['tag'])

    def groupBy(input, n):
        return [input[i:i + n] for i in range(0, len(input), n)]

    def getInfo(products):
        # Group products by 5 (limit of bulk action on amazon api)
        groups = groupBy(products, 5)
        p = 0
        for group in groups:
            dprint('Progress... %s' % (p / len(groups) * 100))

            ok = False
            # Try loop (try until is ok, no more throttling)
            while not ok:
                try:
                    # Create product lookup
                    res = amazon.lookup_bulk(ItemId=', '.join([ asin for (_, asin) in group ]))
                    ok = True
                except HTTPError as e:
                    dprint('Throttling... waiting...', e)
                    time.sleep(5)
            p += 1

            # Yield returned data
            for ((id, asin), r) in zip(group, res):
                yield (id, asin, r.product_type_name, r.list_price[0], r.sales_rank)

    # Get additional information for products
    productsifno = getInfo(products)

    # Create dictionary for easier merging orders
    resdict = { pi[0]: pi[1:] for pi in list(productsifno) }

    # Merge old orders with new products
    orders_adi = [order + resdict[order[2]] for order in orders if order[2] in resdict]

    dprint('Progress... 100%')
    return orders_adi