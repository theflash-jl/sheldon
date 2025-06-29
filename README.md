# Sheldon Parser

This repository contains a simple PDF parser using PyMuPDF.

## Usage

Place PDF files in `/data/pdfs/`. Run the parser by providing the PDF file name:

```bash
python parser.py <file.pdf>
```

The parsed chunks are saved as JSON under `/output/` with the same base name.

