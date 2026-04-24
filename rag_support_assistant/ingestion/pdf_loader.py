import fitz  # PyMuPDF
from typing import List, Dict


class PdfLoader:
    def __init__(self, file_path: str) -> None:
        self._file_path: str = file_path

    def Load(self) -> List[Dict]:
        document = fitz.open(self._file_path)
        pages: List[Dict] = []

        for page_index in range(len(document)):
            page = document.load_page(page_index)
            text: str = page.get_text("text")

            pages.append({
                "page_number": page_index + 1,
                "text": text
            })

        document.close()
        return pages