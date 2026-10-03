"""
ingest_regulations.py
Run this script once to ingest regulatory PDFs into pgvector.  
command = "python ingest_regulations.py"
"""

from pathlib import Path

from rag_pgvector import ingest_regulatory_pdfs


def main():
    data_dir = Path(__file__).resolve().parent / "Data"
    pdf_paths = []
    state_codes = []

    if not data_dir.is_dir():
        raise FileNotFoundError(f"Data folder not found: {data_dir}")

    for state_dir in sorted(path for path in data_dir.iterdir() if path.is_dir()):
        state_code = state_dir.name
        state_pdfs = sorted(
            path
            for path in state_dir.rglob("*")
            if path.is_file() and path.suffix.lower() == ".pdf"
        )
        pdf_paths.extend(str(path) for path in state_pdfs)
        state_codes.extend([state_code] * len(state_pdfs))

    if not pdf_paths:
        raise FileNotFoundError(f"No PDF files found under {data_dir}")

    ingest_regulatory_pdfs(pdf_paths, state_codes)
    print("Regulatory PDFs ingested into pgvector.")


if __name__ == "__main__":
    main()
