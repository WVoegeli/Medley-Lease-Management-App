"""
Metadata extraction for lease documents
Extracts structured data like tenant names, dates, rent amounts, etc.
"""

import re
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..parsing.docx_parser import ParsedDocument


@dataclass
class LeaseMetadata:
    """Structured metadata for a lease document"""
    tenant_name: str
    tenant_trade_name: str = ""
    landlord_name: str = ""
    premises_sqft: Optional[int] = None
    lease_term_years: Optional[int] = None
    commencement_date: Optional[str] = None
    expiration_date: Optional[str] = None
    year1_annual_rent: Optional[float] = None
    year1_monthly_rent: Optional[float] = None
    percentage_rent_rate: Optional[float] = None
    security_deposit: Optional[float] = None
    permitted_use: str = ""
    execution_date: Optional[str] = None
    source_file: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "tenant_name": self.tenant_name,
            "tenant_trade_name": self.tenant_trade_name,
            "landlord_name": self.landlord_name,
            "premises_sqft": self.premises_sqft,
            "lease_term_years": self.lease_term_years,
            "commencement_date": self.commencement_date,
            "expiration_date": self.expiration_date,
            "year1_annual_rent": self.year1_annual_rent,
            "year1_monthly_rent": self.year1_monthly_rent,
            "percentage_rent_rate": self.percentage_rent_rate,
            "security_deposit": self.security_deposit,
            "permitted_use": self.permitted_use,
            "execution_date": self.execution_date,
            "source_file": self.source_file
        }


class MetadataExtractor:
    """Extract structured metadata from lease documents"""

    def __init__(self):
        # Patterns for extracting data
        self.sqft_pattern = re.compile(
            r'(\d{1,3}(?:,\d{3})*)\s*(?:square\s*feet|sq\.?\s*ft\.?|SF)',
            re.IGNORECASE
        )
        self.currency_pattern = re.compile(
            r'\$\s*([\d,]+(?:\.\d{2})?)'
        )
        self.percentage_pattern = re.compile(
            r'(\d+(?:\.\d+)?)\s*%'
        )
        self.term_pattern = re.compile(
            r'(\d+)\s*(?:year|yr)s?\s*(?:term|lease)?',
            re.IGNORECASE
        )
        self.date_pattern = re.compile(
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
            r'\s+\d{1,2},?\s+\d{4}',
            re.IGNORECASE
        )

    def extract(self, doc: ParsedDocument) -> LeaseMetadata:
        """
        Extract metadata from a parsed document

        Args:
            doc: ParsedDocument to extract from

        Returns:
            LeaseMetadata with extracted values
        """
        # Start with values from data sheet
        data_sheet = doc.data_sheet

        metadata = LeaseMetadata(
            tenant_name=doc.tenant_name,
            source_file=doc.file_name
        )

        # Extract from data sheet
        metadata.tenant_trade_name = self._get_value(
            data_sheet, ["trade_name", "tenant_trade_name", "dba"]
        )
        metadata.landlord_name = self._get_value(
            data_sheet, ["landlord", "landlord_name"]
        )
        metadata.permitted_use = self._get_value(
            data_sheet, ["permitted_use", "use", "permitted_uses"]
        )

        # Extract square footage
        sqft_str = self._get_value(
            data_sheet, ["gla", "square_feet", "sqft", "premises_area", "rentable_area"]
        )
        if sqft_str:
            metadata.premises_sqft = self._parse_sqft(sqft_str)
        else:
            metadata.premises_sqft = self._extract_sqft_from_text(doc.full_text)

        # Extract lease term
        term_str = self._get_value(
            data_sheet, ["original_term", "term", "lease_term"]
        )
        if term_str:
            metadata.lease_term_years = self._parse_term(term_str)

        # Extract rent amounts
        rent_str = self._get_value(
            data_sheet, ["annual_minimum_rent", "year_1_rent", "annual_rent"]
        )
        if rent_str:
            metadata.year1_annual_rent = self._parse_currency(rent_str)

        monthly_rent_str = self._get_value(
            data_sheet, ["monthly_minimum_rent", "monthly_rent"]
        )
        if monthly_rent_str:
            metadata.year1_monthly_rent = self._parse_currency(monthly_rent_str)
        elif metadata.year1_annual_rent:
            metadata.year1_monthly_rent = metadata.year1_annual_rent / 12

        # Extract percentage rent
        pct_rent_str = self._get_value(
            data_sheet, ["percentage_rent", "percentage_rent_rate", "percentage"]
        )
        if pct_rent_str:
            metadata.percentage_rent_rate = self._parse_percentage(pct_rent_str)

        # Extract security deposit
        deposit_str = self._get_value(
            data_sheet, ["security_deposit", "deposit"]
        )
        if deposit_str:
            metadata.security_deposit = self._parse_currency(deposit_str)

        # Extract dates
        comm_date = self._get_value(
            data_sheet, ["commencement_date", "lease_commencement", "start_date"]
        )
        if comm_date:
            metadata.commencement_date = comm_date

        exp_date = self._get_value(
            data_sheet, ["expiration_date", "lease_expiration", "end_date"]
        )
        if exp_date:
            metadata.expiration_date = exp_date

        # Try to extract execution date from filename
        metadata.execution_date = self._extract_date_from_filename(doc.file_name)

        return metadata

    def _get_value(self, data: Dict[str, Any], keys: List[str]) -> str:
        """Get value from dict trying multiple keys"""
        for key in keys:
            if key in data:
                return str(data[key])
            # Try with underscores replaced
            key_lower = key.lower().replace(" ", "_")
            if key_lower in data:
                return str(data[key_lower])
        return ""

    def _parse_sqft(self, text: str) -> Optional[int]:
        """Parse square footage from text"""
        match = self.sqft_pattern.search(text)
        if match:
            sqft_str = match.group(1).replace(",", "")
            try:
                return int(sqft_str)
            except ValueError:
                pass

        # Try to find just a number
        numbers = re.findall(r'(\d{1,3}(?:,\d{3})*)', text)
        for num in numbers:
            try:
                value = int(num.replace(",", ""))
                if 100 < value < 100000:  # Reasonable range for retail sqft
                    return value
            except ValueError:
                pass

        return None

    def _extract_sqft_from_text(self, text: str) -> Optional[int]:
        """Extract square footage from document text"""
        # Look for patterns like "1,167 square feet" or "1167 SF"
        matches = self.sqft_pattern.findall(text)
        if matches:
            # Return the most common value or first one
            sqft_values = []
            for match in matches:
                try:
                    sqft_values.append(int(match.replace(",", "")))
                except ValueError:
                    pass

            if sqft_values:
                # Filter to reasonable range
                valid = [v for v in sqft_values if 100 < v < 100000]
                if valid:
                    return min(valid)  # Usually the smallest is the actual premises

        return None

    def _parse_term(self, text: str) -> Optional[int]:
        """Parse lease term in years"""
        match = self.term_pattern.search(text)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass

        # Try finding just a number
        numbers = re.findall(r'(\d+)', text)
        for num in numbers:
            try:
                value = int(num)
                if 1 <= value <= 30:  # Reasonable lease term
                    return value
            except ValueError:
                pass

        return None

    def _parse_currency(self, text: str) -> Optional[float]:
        """Parse currency amount"""
        match = self.currency_pattern.search(text)
        if match:
            amount_str = match.group(1).replace(",", "")
            try:
                return float(amount_str)
            except ValueError:
                pass

        # Try finding numbers without $
        numbers = re.findall(r'([\d,]+(?:\.\d{2})?)', text)
        for num in numbers:
            try:
                value = float(num.replace(",", ""))
                if value > 100:  # Reasonable minimum for rent
                    return value
            except ValueError:
                pass

        return None

    def _parse_percentage(self, text: str) -> Optional[float]:
        """Parse percentage value"""
        match = self.percentage_pattern.search(text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return None

    def _extract_date_from_filename(self, filename: str) -> Optional[str]:
        """Extract execution date from filename"""
        # Pattern: "8.3.23" or "08.03.23" or "8-3-23"
        date_patterns = [
            r'(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{2,4})',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                month, day, year = match.groups()
                # Convert 2-digit year to 4-digit
                if len(year) == 2:
                    year = "20" + year
                try:
                    # Validate date
                    date = datetime(int(year), int(month), int(day))
                    return date.strftime("%B %d, %Y")
                except ValueError:
                    pass

        return None


def extract_all_metadata(documents: List[ParsedDocument]) -> List[LeaseMetadata]:
    """
    Extract metadata from all documents

    Args:
        documents: List of ParsedDocument objects

    Returns:
        List of LeaseMetadata objects
    """
    extractor = MetadataExtractor()
    return [extractor.extract(doc) for doc in documents]
