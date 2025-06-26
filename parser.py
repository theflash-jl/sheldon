import fitz  # PyMuPDF
import os
import re
import json
from typing import List, Dict


def extract_page_brand(page) -> str:
    """Return the page header assumed to contain the brand name."""
    header_candidates = []
    for b in page.get_text("blocks"):
        x0, y0, x1, y1, text, block_no, _ = b
        cleaned = text.strip()
        if cleaned and cleaned.isupper() and y0 < 100:
            header_candidates.append((y0, cleaned))
    if header_candidates:
        header_candidates.sort(key=lambda t: t[0])
        return header_candidates[0][1]
    return ""

def extract_text_blocks(pdf_path: str, supplier: str = "") -> List[Dict]:
    doc = fitz.open(pdf_path)
    blocks = []

    for page_num, page in enumerate(doc, start=1):
        brand = extract_page_brand(page)
        for b in page.get_text("blocks"):
            x0, y0, x1, y1, text, block_no, _ = b
            cleaned_text = text.strip()
            if cleaned_text and not is_footer_text(cleaned_text):
                blocks.append({
                    "page": page_num,
                    "brand": brand,
                    "supplier": supplier,
                    "x": x0,
                    "y": y0,
                    "text": cleaned_text,
                })
    return blocks

def is_footer_text(text: str) -> bool:
    return "TO PLACE AN ORDER" in text.upper() or "CUSTOMER PORTAL" in text.upper()

def group_blocks_into_chunks(blocks: List[Dict]) -> List[Dict]:
    # Sort by page and vertical position
    blocks.sort(key=lambda b: (b["page"], b["y"]))
    chunks = []
    current_chunk = []

    for block in blocks:
        if is_new_product_block(block["text"]):
            if current_chunk:
                chunks.append({
                    "page": current_chunk[0]["page"],
                    "brand": current_chunk[0]["brand"],
                    "supplier": current_chunk[0]["supplier"],
                    "x": current_chunk[0]["x"],
                    "y": current_chunk[0]["y"],
                    "text": "\n".join(b["text"] for b in current_chunk)
                })
                current_chunk = []
        current_chunk.append(block)

    # Append the last chunk
    if current_chunk:
        chunks.append({
            "page": current_chunk[0]["page"],
            "brand": current_chunk[0]["brand"],
            "supplier": current_chunk[0]["supplier"],
            "x": current_chunk[0]["x"],
            "y": current_chunk[0]["y"],
            "text": "\n".join(b["text"] for b in current_chunk)
        })

    return chunks

def is_new_product_block(text: str) -> bool:
    # Detect new blocks using SKU pattern or strong keywords
    return bool(re.match(r"^\d{5}$", text.strip()))  # 5-digit SKU

def parse_pdf_to_chunks(pdf_path: str, output_json: str = None, supplier: str = "") -> List[Dict]:
    blocks = extract_text_blocks(pdf_path, supplier)
    chunks = group_blocks_into_chunks(blocks)

    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2)

    return chunks

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python parser.py path_to_pdf supplier_name")
    else:
        pdf_file = sys.argv[1]
        supplier_name = sys.argv[2]
        parse_pdf_to_chunks(pdf_file, "parsed_chunks.json", supplier_name)
