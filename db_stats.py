import helpers.data as data
import pymysql
import config

# Create mysql connection
db = pymysql.connect(host=config.MYSQL_CONFIG['host'],  # your host, usually localhost
                     user=config.MYSQL_CONFIG['user'],  # your username
                     passwd=config.MYSQL_CONFIG['password'],  # your password
                     db=config.MYSQL_CONFIG['dbname'])  # name of the data base

# Connect to mysql
with db.cursor() as cur:
    # Execute sql query which gets all buyers who had ordered at least 20 orders
    cur.execute(
        "SELECT mb.orders.customer_email FROM mb.orders WHERE orders.customer_email IS NOT NULL GROUP BY orders.customer_email HAVING COUNT(*) > 10;")

    # Get all distinct buyers
    buyers = set(map(lambda x: x[0], cur.fetchall()))

    # Execute query which gets all ordered products with buyer, seller
    format_strings = ','.join(['%s'] * len(buyers))
    credentials = '262, 316, 880, 979, 1012, 1039, 1045, 1150, 1324, 1715, 1991, 2027, 30, 75, 124, 232, 346, 502, 523, 670, 754, 787, 790, 808, 820, 838, 883, 913, 982, 1069, 1102, 1162, 1165, 1189, 1210, 1213, 1288, 1300, 1348, 1366, 1381, 1408, 1427, 1506, 1572, 1611, 1635, 1769, 1775, 1820, 1838, 1868, 1964, 2015, 2024, 38, 628, 700, 793, 1048, 1072, 1192, 1216, 1231, 1387, 1420, 1429, 1641, 1670, 1910, 1940, 1967, 53, 631, 709, 796, 1075, 1201, 1225, 1237, 1463, 1679, 1727, 1841, 1973, 41, 703, 739, 799, 1078, 1198, 1219, 1234, 1432, 1673, 1733, 1871, 1970, 59, 712, 742, 802, 1081, 1204, 1222, 1240, 1438, 1664, 1709, 1721, 1976'
    cur.execute(
        # AVG(IF(ISNULL(feedback.rating),0,feedback.rating)) GROUP_BY order_items.id
        "SELECT orders.credential_id, customer_email, order_items.product_id, AVG(reviews.rating) FROM orders INNER JOIN order_items ON orders.id = order_items.order_id LEFT JOIN reviews ON reviews.product_id = order_items.product_id WHERE orders.customer_email IN (%s) AND orders.credential_id NOT IN (%s) GROUP BY order_items.id ORDER BY orders.status_shipped_at LIMIT 1000" % (
        format_strings, credentials),
        tuple(buyers))


    print(list(cur.fetchall()))