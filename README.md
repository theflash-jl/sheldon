# Sheldon Catalog Parser

Prototype to parse supplier PDF catalogs and group raw text into product chunks.

## Usage

```
python parser.py <catalog.pdf> <supplier_name>
```

This outputs `parsed_chunks.json` containing a list of chunks with page number,
brand (taken from the page header) and supplier.

## Database Schema

The SQLite schema (`schema.sql`) defines tables for products, variants and price
information. The `products` table now includes optional `supplier` and `brand`
columns.

