import argparse
import json
from pathlib import Path

import pdfplumber


def parse_pdf(pdf_path: Path):
    """Extract products from the PDF catalog.

    This example assumes each product entry is stored on a single line in the
    format:
    ``ID, Name, Variant, Price``.
    Adjust the parsing logic to match your catalog's layout.
    """
    products = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for line in text.splitlines():
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 4:
                    product = {
                        "id": parts[0],
                        "name": parts[1],
                        "variant": parts[2],
                        "price": parts[3],
                    }
                    products.append(product)
    return products


def save_json(data, out_path: Path):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_sql(data, out_path: Path):
    with open(out_path, "w", encoding="utf-8") as f:
        for item in data:
            values = (
                item["id"].replace("'", "''"),
                item["name"].replace("'", "''"),
                item["variant"].replace("'", "''"),
                item["price"],
            )
            f.write(
                "INSERT INTO products (id, name, variant, price) "
                f"VALUES ('{values[0]}', '{values[1]}', '{values[2]}', '{values[3]}');\n"
            )


def main():
    parser = argparse.ArgumentParser(description="Convert a PDF catalog to JSON or SQL script")
    parser.add_argument("pdf", type=Path, help="Path to the PDF catalog")
    parser.add_argument("out", type=Path, help="Output file path")
    parser.add_argument("--sql", action="store_true", help="Generate SQL INSERT statements instead of JSON")
    args = parser.parse_args()

    products = parse_pdf(args.pdf)
    if args.sql:
        save_sql(products, args.out)
    else:
        save_json(products, args.out)


if __name__ == "__main__":
    main()
