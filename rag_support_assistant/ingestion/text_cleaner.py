import re
from typing import List, Dict


class TextCleaner:
    def Clean(self, pages: List[Dict]) -> List[Dict]:
        cleaned_pages: List[Dict] = []

        for page in pages:
            text: str = page["text"]

            text = self._NormalizeWhitespace(text)
            text = self._RemoveNoise(text)

            cleaned_pages.append({
                "page_number": page["page_number"],
                "text": text
            })

        return cleaned_pages

    def _NormalizeWhitespace(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _RemoveNoise(self, text: str) -> str:
        text = re.sub(r"[^\x00-\x7F]+", " ", text)  # remove non-ascii
        text = re.sub(r"\s{2,}", " ", text)
        return text.strip()