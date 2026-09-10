"""Base de exemplo: um mini e-commerce em DuckDB. Compartilhada por todas as tarefas SQL."""

import duckdb

DDL = """
CREATE TABLE customers (
    customer_id INTEGER, name VARCHAR, country VARCHAR, created_at DATE
);
CREATE TABLE orders (
    order_id INTEGER, customer_id INTEGER, order_date DATE, status VARCHAR, amount DECIMAL(10,2)
);
CREATE TABLE order_items (
    order_id INTEGER, product_id INTEGER, qty INTEGER, unit_price DECIMAL(10,2)
);
"""

SEED = """
INSERT INTO customers VALUES
 (1,'Ana','PT','2025-01-10'),(2,'Bruno','BR','2025-02-15'),(3,'Carla','PT','2025-03-01'),
 (4,'Diego','ES','2025-03-20'),(5,'Eva','BR','2025-05-05'),(6,'Fabio','PT','2025-06-30');
INSERT INTO orders VALUES
 (100,1,'2025-06-01','completed',120.00),(101,1,'2025-06-15','completed',80.00),
 (102,2,'2025-06-20','cancelled',200.00),(103,2,'2025-07-02','completed',300.00),
 (104,3,'2025-07-10','completed',50.00),(105,3,'2025-08-01','pending',75.00),
 (106,4,'2025-08-05','completed',500.00),(107,1,'2025-08-20','completed',60.00),
 (108,2,'2025-09-01','completed',150.00),(109,3,'2025-09-03','completed',90.00);
INSERT INTO order_items VALUES
 (100,1,2,60.00),(101,2,1,80.00),(102,1,1,200.00),(103,3,3,100.00),(104,2,1,50.00),
 (105,1,1,75.00),(106,3,5,100.00),(107,2,1,60.00),(108,1,1,150.00),(109,2,1,90.00);
"""


def fresh_connection() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(":memory:")
    con.execute(DDL)
    con.execute(SEED)
    return con
