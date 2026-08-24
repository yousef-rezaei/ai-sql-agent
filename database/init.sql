-- =============================================
-- Customers
-- =============================================

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    country VARCHAR(100) NOT NULL
);


-- =============================================
-- Products
-- =============================================

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(100),
    price NUMERIC(10,2) NOT NULL
);


-- =============================================
-- Orders
-- =============================================

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date DATE NOT NULL,

    CONSTRAINT fk_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(id)
);


-- =============================================
-- Order Items
-- =============================================

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,

    CONSTRAINT fk_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id),

    CONSTRAINT fk_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
);


INSERT INTO customers (name, email, country)
VALUES
('Alice Smith', 'alice@example.com', 'Luxembourg'),
('John Miller', 'john@example.com', 'Germany'),
('Marie Dubois', 'marie@example.com', 'France'),
('David Brown', 'david@example.com', 'Belgium'),
('Emma Wilson', 'emma@example.com', 'Luxembourg');


INSERT INTO products (name, category, price)
VALUES
('Laptop', 'Electronics', 1200.00),
('Keyboard', 'Electronics', 80.00),
('Monitor', 'Electronics', 300.00),
('Office Chair', 'Furniture', 250.00),
('Desk', 'Furniture', 400.00);


INSERT INTO orders (customer_id, order_date)
VALUES
(1, '2026-07-01'),
(2, '2026-07-03'),
(1, '2026-07-05'),
(3, '2026-07-10'),
(4, '2026-07-15'),
(5, '2026-07-20');


INSERT INTO order_items (order_id, product_id, quantity)
VALUES
(1, 1, 1),
(1, 2, 2),

(2, 3, 2),

(3, 4, 1),

(4, 1, 1),
(4, 3, 1),

(5, 5, 1),

(6, 2, 3),
(6, 3, 1);


-- =============================================
-- Read-only user for AI Agent
-- =============================================

CREATE USER ai_reader
WITH PASSWORD 'reader_password';


GRANT CONNECT
ON DATABASE sales_db
TO ai_reader;


GRANT USAGE
ON SCHEMA public
TO ai_reader;


GRANT SELECT
ON ALL TABLES IN SCHEMA public
TO ai_reader;


ALTER DEFAULT PRIVILEGES
IN SCHEMA public
GRANT SELECT ON TABLES
TO ai_reader;