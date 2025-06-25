# PDF Catalog Parser

This project provides a simple script to convert a PDF catalog into a structured
JSON file or a set of SQL `INSERT` statements.

## Requirements

Install dependencies using pip:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python pdf_to_db.py catalog.pdf output.json
```

Use the `--sql` flag to generate SQL commands instead of JSON:

```bash
python pdf_to_db.py catalog.pdf output.sql --sql
```

The parser assumes each product is listed on a single line in the PDF with the
format `ID, Name, Variant, Price`. Adjust the parsing logic in
`pdf_to_db.py` to match your catalog's layout.
