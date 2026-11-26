"""Extract page-cited Khmer passages from the project's source PDFs."""

import argparse
import json
import re
import unicodedata
from pathlib import Path

import pymupdf


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
KHMER_LETTERS = re.compile(r"[\u1780-\u17B3]")


def extract(source, pdf_path):
    with pymupdf.open(pdf_path) as document:
        for page in document:
            for index, block in enumerate(page.get_text("blocks", sort=True), 1):
                if block[6] != 0:
                    continue
                normalized = unicodedata.normalize("NFC", block[4])
                passage = " ".join(normalized.split())
                if len(KHMER_LETTERS.findall(passage)) < 30:
                    continue
                yield {
                    "passage_id": f"{source['id']}-p{page.number + 1}-b{index}",
                    "document_id": source["id"],
                    "document_title": source["title"],
                    "source_url": source["url"],
                    "pdf_page": page.number + 1,
                    "text": passage,
                }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="Process one source ID from data/sources.json.")
    args = parser.parse_args()
    sources = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))
    if args.source:
        sources = [source for source in sources if source["id"] == args.source]
        if not sources:
            parser.error(f"Unknown source ID: {args.source}")

    passages = []
    for source in sources:
        pdf_path = DATA / "pdfs" / f"{source['id']}.pdf"
        if not pdf_path.is_file():
            parser.error(f"Missing {pdf_path}. Download it from {source['url']}")
        records = list(extract(source, pdf_path))
        if not records:
            parser.error(f"No usable Khmer text in {pdf_path.name}. Check the PDF text layer.")
        print(f"{pdf_path.name}: {len(records)} candidate passages")
        passages.extend(records)

    filename = f"{args.source}.jsonl" if args.source else "passages.jsonl"
    output = DATA / "processed" / filename
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as stream:
        for passage in passages:
            stream.write(json.dumps(passage, ensure_ascii=False) + "\n")
    print(f"Wrote {len(passages)} candidate passages to {output}")


if __name__ == "__main__":
    main()
