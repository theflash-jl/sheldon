import fitz  # PyMuPDF
import os
import re
import json
from typing import List, Dict

def extract_text_blocks(pdf_path: str) -> List[Dict]:
    doc = fitz.open(pdf_path)
    blocks = []

    for page_num, page in enumerate(doc, start=1):
        for b in page.get_text("blocks"):
            x0, y0, x1, y1, text, block_no, _, _ = b
            cleaned_text = text.strip()
            if cleaned_text and not is_footer_text(cleaned_text):
                blocks.append({
                    "page": page_num,
                    "x": x0,
                    "y": y0,
                    "text": cleaned_text
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
            "x": current_chunk[0]["x"],
            "y": current_chunk[0]["y"],
            "text": "\n".join(b["text"] for b in current_chunk)
        })

    return chunks

def is_new_product_block(text: str) -> bool:
    # Detect new blocks using SKU pattern or strong keywords
    return bool(re.match(r"^\d{5}$", text.strip()))  # 5-digit SKU

def parse_pdf_to_chunks(pdf_path: str, output_json: str = None) -> List[Dict]:
    blocks = extract_text_blocks(pdf_path)
    chunks = group_blocks_into_chunks(blocks)

    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2)

    return chunks

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python parser.py path_to_pdf")
    else:
        pdf_file = sys.argv[1]
        parse_pdf_to_chunks(pdf_file, "parsed_chunks.json")