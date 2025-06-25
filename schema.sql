-- PRODUCTS TABLE
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    base_sku TEXT NOT NULL,
    tag TEXT,
    discontinued BOOLEAN DEFAULT 0
);

-- VARIANTS TABLE
CREATE TABLE IF NOT EXISTS variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    sku TEXT NOT NULL,
    barcode TEXT,
    design TEXT,
    dimensions TEXT,
    packaging TEXT,
    in_out TEXT,
    bulk_qty INTEGER,
    detail TEXT,
    discontinued BOOLEAN DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products (id)
);

-- PRICES TABLE
CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant_id INTEGER NOT NULL,
    currency TEXT DEFAULT 'AUD',
    wholesale REAL,
    trade REAL,
    bulk REAL,
    srp REAL,
    rrp REAL,
    FOREIGN KEY (variant_id) REFERENCES variants (id)
);

-- PRICE HISTORY TABLE
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant_id INTEGER NOT NULL,
    date DATE NOT NULL,
    currency TEXT DEFAULT 'AUD',
    wholesale REAL,
    trade REAL,
    bulk REAL,
    srp REAL,
    rrp REAL,
    FOREIGN KEY (variant_id) REFERENCES variants (id)
);