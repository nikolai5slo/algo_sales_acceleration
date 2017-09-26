from collections import defaultdict

import networkx as nx
import numpy as np

import helpers.data as data
import pymysql
import config
import helpers.graph as graph

orders = data.cut_orders_by_repeated_buyers(data.load_orders(), 13)

# Degree
B = graph.construct_bi_graph_buyer_product(orders)
buyers, products = nx.bipartite.sets(B)
print("Povprečna stopnja vozlišč kupcev", sum(B.degree(buyers).values())/len(buyers))
print("Povprečna stopnja vozlišč izdelkov", sum(B.degree(products).values())/len(products))

# Additional statistical information
def getAverageCategoryCountPerBuyer():
    tmp = defaultdict(set)
    for o in orders:
        tmp[o['buyer']].add(o['category'])
    return np.average([len(l) for p, l in tmp.items()])

def getAveragePerBuyerFor(s):
    tmp = defaultdict(list)
    for o in orders:
        if o[s] is not None:
            tmp[o['buyer']].append(int(o[s]))
    return np.average([np.average(l) for p, l in tmp.items()])

print('Povprečno število kategorij v katerih kupuje posamezen kupec:', getAverageCategoryCountPerBuyer())
print('Povprečna cena izdelka, ki jih kupuje posamezen kupec:', getAveragePerBuyerFor('price'))
print('Povprečen rank izdelka ki jih kupuje posamezen kupec:', getAveragePerBuyerFor('rank'))

# Create mysql connection
db = pymysql.connect(host=config.MYSQL_CONFIG['host'],  # your host, usually localhost
                     user=config.MYSQL_CONFIG['user'],  # your username
                     passwd=config.MYSQL_CONFIG['password'],  # your password
                     db=config.MYSQL_CONFIG['dbname'])  # name of the data base

def fetch_execute(query, cur):
    ''' Execute query and fetch first value from first row'''
    cur.execute(query)
    return cur.fetchone()[0]

def countProducts(cur):
    # All products
    yield fetch_execute("SELECT COUNT(*) FROM products", cur)

    # Product wih marketplace 1
    yield fetch_execute("SELECT COUNT(*) FROM user_amazon_credentials INNER JOIN products ON products.credential_id = user_amazon_credentials.id WHERE marketplace_id = 1", cur)

    # Execute sql query which gets all buyers who had ordered at least 20 orders
    #cur.execute("SELECT mb.orders.customer_email FROM mb.orders WHERE orders.customer_email IS NOT NULL GROUP BY orders.customer_email HAVING COUNT(*) > 7")
    # Repated buyers with 7 or more orders
    buyers = set(map(lambda x: x[0], cur.fetchall()))

    #yield fetch_execute("SELECT COUNT(*) FROM user_amazon_credentials INNER JOIN products ON products.credential_id = user_amazon_credentials.id WHERE marketplace_id = 1", cur)

def countSellers(cur):
    # All sellers
    yield fetch_execute("SELECT COUNT(*) FROM user_amazon_credentials", cur)

    # Sellers in marketplace 1
    yield fetch_execute("SELECT COUNT(*) FROM user_amazon_credentials WHERE marketplace_id = 1", cur)

def countOrders(cur):
    yield fetch_execute("SELECT COUNT(*) FROM orders", cur)
    yield fetch_execute("SELECT COUNT(*) FROM user_amazon_credentials INNER JOIN orders ON orders.credential_id = user_amazon_credentials.id WHERE marketplace_id = 1", cur)

def countOrderItems(cur):
    yield fetch_execute("SELECT SUM(IFNULL(quantity_ordered, 1)) FROM mb.order_items;", cur)
    yield fetch_execute("SELECT SUM(IFNULL(quantity_ordered, 1)) FROM user_amazon_credentials INNER JOIN orders ON orders.credential_id = user_amazon_credentials.id INNER JOIN order_items ON order_items.order_id = orders.id WHERE marketplace_id = 1", cur)

def countBuyers(cur):
    yield fetch_execute("SELECT count( DISTINCT(customer_email)) FROM orders", cur)
    yield fetch_execute("SELECT count( DISTINCT(customer_email)) FROM user_amazon_credentials INNER JOIN orders ON orders.credential_id = user_amazon_credentials.id WHERE marketplace_id = 1", cur)


def print_latex_table_format(data):
    for d in data:
        addpercent = d + (d[2]*100 / d[1],)
        print('{\\tt %s} & %d & %d (%.1f\\%%) \\\\' % addpercent)
# Connect to mysql
with db.cursor() as cur:
    d = []
    d.append(('prodajalci',) + tuple(countSellers(cur)))
    d.append(('kupci',) + tuple(countBuyers(cur)))
    d.append(('produkti',) + tuple(countProducts(cur)))
    d.append(('naročila',) + tuple(countOrders(cur)))
    d.append(('naročeni produkti',) + tuple(countOrderItems(cur)))

    print_latex_table_format(d)













