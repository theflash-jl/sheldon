import re
import json
import logging
from typing import List, Dict, Optional

import parser

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')

SKU_RE = re.compile(r"\b\d{5}\b")
BARCODE_RE = re.compile(r"(\d\s*){8,14}")
PRICE_RE = re.compile(r"\$(\d+\.\d{2})")
DIMENSION_RE = re.compile(r"\d+\s*(?:x|X|/|\\)\s*\d+.*(cm|mm|in)")


KNOWN_COLOURS = {
    'black', 'white', 'red', 'blue', 'green', 'grey', 'gray', 'silver', 'gold',
    'yellow', 'orange', 'pink', 'purple', 'brown', 'clear'
}

def clean_barcode(text: str) -> str:
    return re.sub(r"\s+", "", text)

def parse_prices(line: str) -> Optional[Dict[str, float]]:
    prices = PRICE_RE.findall(line)
    if not prices:
        return None
    prices = [float(p) for p in prices]
    result = {}
    if len(prices) >= 5:
        result['bulk_price'] = prices[2]
        result['srp'] = prices[3]
        result['rrp'] = prices[4]
    elif len(prices) >= 3:
        result['bulk_price'] = prices[0]
        result['srp'] = prices[1]
        result['rrp'] = prices[2]
    return result if result else None


def extract_variant_from_chunk(chunk: Dict) -> Dict:
    lines = [l.strip() for l in chunk['text'].splitlines() if l.strip()]
    result: Dict[str, Optional[str]] = {
        'sku': None,
        'title': None,
        'barcode': None,
        'bulk_price': None,
        'srp': None,
        'rrp': None,
        'packaging': None,
        'dimensions': None,
        'colour': None,
        'notes': []
    }

    found_title = False
    for line in lines:
        if result['sku'] is None:
            m = SKU_RE.search(line)
            if m:
                result['sku'] = m.group()
                continue
        m = BARCODE_RE.search(line)
        if result['barcode'] is None and m:
            result['barcode'] = clean_barcode(m.group())
            continue
        price_data = parse_prices(line)
        if price_data:
            for k, v in price_data.items():
                result[k] = v
            continue
        if line.lower().startswith('packaging'):
            result['packaging'] = line.replace('Packaging', '').strip()
            continue
        if line.lower().startswith('in/out'):
            result['notes'].append(line)
            continue
        if result['dimensions'] is None and DIMENSION_RE.search(line):
            result['dimensions'] = line
            continue
        if result['colour'] is None and line.lower() in KNOWN_COLOURS:
            result['colour'] = line
            continue
        if not found_title and not SKU_RE.search(line) and not line.isupper():
            result['title'] = line
            found_title = True
            continue
        else:
            result['notes'].append(line)

    return result


def extract_variants(chunks: List[Dict]) -> List[Dict]:
    variants = []
    for chunk in chunks:
        try:
            variant = extract_variant_from_chunk(chunk)
            if variant['sku']:
                variants.append(variant)
        except Exception as e:
            logging.error(f"Failed to parse chunk on page {chunk.get('page')}: {e}")
    return variants


def extract_from_pdf(pdf_path: str) -> List[Dict]:
    chunks = parser.parse_pdf_to_chunks(pdf_path)
    return extract_variants(chunks)


def main():
    import argparse
    parser_arg = argparse.ArgumentParser(description='Extract product data from PDF chunks')
    parser_arg.add_argument('pdf', help='Path to PDF catalog')
    parser_arg.add_argument('-o', '--output', help='Output JSON file')
    args = parser_arg.parse_args()

    variants = extract_from_pdf(args.pdf)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(variants, f, indent=2)
    else:
        print(json.dumps(variants, indent=2))


if __name__ == '__main__':
    main()
