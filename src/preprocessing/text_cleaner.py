"""
Text preprocessing and cleaning for lease documents
"""

import re
from typing import List


class TextCleaner:
    """Clean and normalize text from lease documents"""

    def __init__(self):
        # Patterns for cleaning
        self.multiple_spaces = re.compile(r' +')
        self.multiple_newlines = re.compile(r'\n{3,}')
        self.page_numbers = re.compile(r'\n\s*-?\s*\d+\s*-?\s*\n')
        self.header_footer = re.compile(r'(CONFIDENTIAL|DRAFT|Page \d+)', re.IGNORECASE)

    def clean(self, text: str) -> str:
        """
        Clean and normalize text

        Args:
            text: Raw text from document

        Returns:
            Cleaned text
        """
        # Remove page numbers
        text = self.page_numbers.sub('\n', text)

        # Remove common header/footer text
        text = self.header_footer.sub('', text)

        # Normalize whitespace
        text = self.multiple_spaces.sub(' ', text)
        text = self.multiple_newlines.sub('\n\n', text)

        # Normalize line endings
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')

        # Strip leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)

        # Remove empty lines at start and end
        text = text.strip()

        return text

    def normalize_dates(self, text: str) -> str:
        """
        Normalize date formats to consistent format

        Args:
            text: Text containing dates

        Returns:
            Text with normalized dates
        """
        # Pattern for various date formats
        # Month DD, YYYY
        month_names = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
        date_pattern2 = re.compile(rf'({month_names})\s+(\d{{1,2}}),?\s+(\d{{4}})', re.IGNORECASE)

        # Normalize to consistent format (keep as-is for legal documents)
        # Just ensure consistent spacing
        text = date_pattern2.sub(r'\1 \2, \3', text)

        return text

    def normalize_currency(self, text: str) -> str:
        """
        Normalize currency formats

        Args:
            text: Text containing currency values

        Returns:
            Text with normalized currency
        """
        # Pattern for currency: $1,234.56 or $1234.56
        currency_pattern = re.compile(r'\$\s*([\d,]+(?:\.\d{2})?)')

        def normalize_amount(match):
            amount = match.group(1).replace(',', '')
            # Format with commas
            try:
                if '.' in amount:
                    whole, decimal = amount.split('.')
                    formatted = f"${int(whole):,}.{decimal}"
                else:
                    formatted = f"${int(amount):,}"
                return formatted
            except ValueError:
                return match.group(0)

        text = currency_pattern.sub(normalize_amount, text)
        return text

    def normalize_square_footage(self, text: str) -> str:
        """
        Normalize square footage references

        Args:
            text: Text containing square footage

        Returns:
            Text with normalized square footage
        """
        # Patterns: "1,234 sq ft", "1234 square feet", "1,234 SF"
        patterns = [
            (re.compile(r'([\d,]+)\s*(?:sq\.?\s*ft\.?|square\s*feet|SF)', re.IGNORECASE),
             lambda m: f"{m.group(1)} square feet")
        ]

        for pattern, replacement in patterns:
            text = pattern.sub(replacement, text)

        return text

    def clean_for_embedding(self, text: str) -> str:
        """
        Prepare text specifically for embedding

        Args:
            text: Text to prepare

        Returns:
            Text optimized for embedding
        """
        # Apply all cleanings
        text = self.clean(text)
        text = self.normalize_dates(text)
        text = self.normalize_currency(text)
        text = self.normalize_square_footage(text)

        # Remove excessive punctuation
        text = re.sub(r'[_]{3,}', '', text)
        text = re.sub(r'[.]{3,}', '...', text)

        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")

        return text

    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Handle common abbreviations in legal documents
        text = re.sub(r'\b(Mr|Mrs|Ms|Dr|Jr|Sr|Inc|Corp|LLC|Ltd)\.',
                      r'\1<PERIOD>', text)
        text = re.sub(r'\b(Art|Sec|Para|Ex|No)\.',
                      r'\1<PERIOD>', text)

        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # Restore periods in abbreviations
        sentences = [s.replace('<PERIOD>', '.') for s in sentences]

        return [s.strip() for s in sentences if s.strip()]
