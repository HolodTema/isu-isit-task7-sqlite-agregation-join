import sqlite3
import pandas as pd

connection = sqlite3.connect("mydb.db")
cursor = connection.cursor()

# create DB tables
cursor.execute("""
    CREATE TABLE IF NOT EXISTS positions (
        id INTEGER PRIMARY KEY NOT NULL UNIQUE,
        name TEXT NOT NULL
    );
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY NOT NULL UNIQUE,
        surname TEXT NOT NULL,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        position_id INTEGER NOT NULL,
        FOREIGN KEY (position_id) REFERENCES positions(id)
    );
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY NOT NULL UNIQUE,
        organization TEXT NOT NULL,
        phone TEXT NOT NULL
    );
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY NOT NULL UNIQUE,
        client_id INTEGER NOT NULL,
        employee_id INTEGER NOT NULL,
        cost INTEGER NOT NULL,
        date TEXT NOT NULL,
        is_finished INTEGER NOT NULL,
        FOREIGN KEY (client_id) REFERENCES clients(id),
        FOREIGN KEY (employee_id) REFERENCES employees(id)
    );
""")

list_positions = [
    (1, "CEO"),
    (2, "CTO"),
    (3, "Trainne PHP developer"),
    (4, "Senior COBOL developer")
]
list_employees = [
    (1, "Ivanov", "Ivan", "88005553535", 4),
    (2, "Sidorov", "Petr", "8474387487", 2),
    (3, "Petrov", "Alexey", "224947", 3),
    (4, "Romanov", "Nikolai", "8800000000", 1),
    (5, "Kostin", "Igor", "947439", 3)
]
list_orders = [
    (1, 4, 5, 90000, "2026-03-23 07:31", 1),
    (2, 3, 2, 8000000, "2026-03-23 20:45", 1),
    (3, 1, 3, 200000, "2026-03-23 05:30", 0),
    (4, 1, 1, 400000, "2026-03-23 23:58", 1),
    (5, 4, 2, 7000000, "2026-03-23 00:00", 0),
    (6, 2, 4, 10000, "2026-03-23 01:04", 1)
]
# clients table will be filled from .csv file later...

# fill DB from python-lists
cursor.executemany(
    "INSERT OR IGNORE INTO positions (id, name) VALUES (?, ?)",
    list_positions
)
cursor.executemany(
    "INSERT OR IGNORE INTO employees (id, surname, name, phone, position_id) VALUES (?, ?, ?, ?, ?)",
    list_employees
)
cursor.executemany(
    "INSERT OR IGNORE INTO orders (id, client_id, employee_id, cost, date, is_finished) VALUES (?, ?, ?, ?, ?, ?)",
    list_orders
)

connection.commit()

# also we can fill DB from csv-file using Pandas python-lib
# for example, I have file clients.csv - I am importing data from this file into DB
clients_from_csv = pd.read_csv('clients.csv')

clients_from_csv.columns = ['id', 'organization', 'phone']

clients_from_csv.to_sql('clients', connection, if_exists='replace', index=False)

connection.commit()

#print all tables
print("Positions:")
cursor.execute("""
    SELECT * FROM positions;
""")
print(cursor.fetchall())
print()

print("Clients:")
cursor.execute("""
    SELECT * FROM clients;
""")
print(cursor.fetchall())
print()

print("Employees:")
cursor.execute("""
    SELECT * FROM employees;
""")
print(cursor.fetchall())
print()

print("Orders:")
cursor.execute("""
    SELECT * FROM orders;
""")
print(cursor.fetchall())
print()



# Five simple requests to SQLite:
print("_____________________________")
print("FIVE SIMPLE REQUESTS TO SQLITE:")
print()

print("Count all the finished orders:")
cursor.execute("""
    SELECT COUNT(*) FROM orders WHERE orders.is_finished = 1;
""")
print(cursor.fetchall())
print()


print("Find max cost from all the orders")
cursor.execute("""
    SELECT MAX(cost) FROM orders;
""")
print(cursor.fetchone())
print()


print("Sum costs of the orders which are not finished:")
cursor.execute("""
    SELECT SUM(cost) FROM orders
        WHERE orders.is_finished = 0;
""")
print(cursor.fetchone())
print()


print("Find average value of the cost of the orders which client_id is 1 (google):")
cursor.execute("""
    SELECT AVG(cost) FROM orders 
        WHERE orders.client_id = 1;
""")
print(cursor.fetchone())
print()


print("Count all the orders which are finished and which employee_id is 2 (Sidorov):")
cursor.execute("""
    SELECT COUNT(*) FROM orders
        WHERE orders.is_finished = 1 AND orders.employee_id = 2;
""")
print(cursor.fetchone())
print()



# agregation requests
print("_______________________________")
print("3 REQUESTS WITH AGREGATION:")
print()

print("Show number of orders by client_id:")
print("Format (client_id, number_of_orders)")
cursor.execute("""
    SELECT client_id, COUNT(*) FROM orders
        GROUP BY client_id;
""")
print(cursor.fetchall())
print()


print("Show number of orders by employee_id which cost is more than 1_000_000:")
print("Format (employee_id, number_of_orders)")
cursor.execute("""
    SELECT employee_id, COUNT(*) FROM orders
        GROUP BY employee_id
        HAVING cost > 1000000;
""")
print(cursor.fetchall())
print()


print("Show average cost of orders group by clients:")
print("Format (client_id, average_cost_of_its_orders)")
cursor.execute("""
    SELECT client_id, AVG(cost) FROM orders
        GROUP BY client_id;
""")
print(cursor.fetchall())
print()



# Requests with JOIN and WHERE
print("_______________________")
print("Requests with JOIN and WHERE (joins and conditions):")
print()

print("Show info about orders clients of these orders (LEFT JOIN):")
print("Format (order_id, order_cost, client_id, client_organization, client_phone)")
cursor.execute("""
    SELECT orders.id, orders.cost, clients.id, clients.organization, clients.phone
        FROM orders
        LEFT JOIN clients ON orders.client_id = clients.id;
""")
print(cursor.fetchall())
print()


# here I used WITH AS to remember temp table to make many select operations
# otherwise I would make nested SELECT(SELECT()) - it is not nice.
print("count orders which cost is > 500_000 and which client has organization != 'google':")
print("WITH + LEFT JOIN + WHERE + COUNT")
cursor.execute("""
    WITH orders_with_client_organizations AS (
        SELECT orders.id, orders.cost, clients.organization FROM orders 
        LEFT JOIN clients ON orders.client_id = clients.id
    )

    SELECT COUNT(cost) FROM orders_with_client_organizations
    WHERE organization != 'google' AND cost > 500000;
""")
print(cursor.fetchall())
print()


print("sum costs of all the orders which employee has position = 'CEO':")
print("INNER JOIN + COUNT + WHERE")
cursor.execute("""
    SELECT SUM(orders.cost) FROM orders
    INNER JOIN employees ON orders.employee_id = employees.id
    INNER JOIN positions ON employees.position_id = positions.id
    WHERE positions.name = 'CEO';
""")
print(cursor.fetchall())
print()

