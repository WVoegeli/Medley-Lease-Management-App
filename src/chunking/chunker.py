"""
Document chunking for RAG system
Implements semantic and fixed-size chunking strategies
"""

import re
import uuid
from dataclasses import dataclass
from typing import List, Dict, Any
import tiktoken

from ..parsing.docx_parser import ParsedDocument
from ..preprocessing.text_cleaner import TextCleaner


@dataclass
class Chunk:
    """Represents a text chunk with metadata"""
    id: str
    content: str
    metadata: Dict[str, Any]
    token_count: int
    source_file: str
    section_type: str  # "article", "data_sheet", "exhibit", "rent_schedule", "general"
    section_name: str = ""
    chunk_index: int = 0


class Chunker:
    """
    Chunker for lease documents with support for:
    - Semantic chunking (by article/section boundaries)
    - Fixed-size chunking with overlap
    - Special handling for data sheets and rent schedules
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        min_chunk_size: int = 100
    ):
        """
        Initialize the chunker

        Args:
            chunk_size: Target size in tokens
            chunk_overlap: Overlap between chunks in tokens
            min_chunk_size: Minimum chunk size in tokens
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.text_cleaner = TextCleaner()

        # Use tiktoken for accurate token counting
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

        # Patterns for section detection
        self.article_pattern = re.compile(r'^ARTICLE\s+([IVXLCDM]+)', re.IGNORECASE)
        self.exhibit_pattern = re.compile(r'^EXHIBIT\s+([A-Z](?:-\d+)?)', re.IGNORECASE)
        self.section_pattern = re.compile(r'^(\d+\.\d+)\s+')

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))

    def chunk_document(self, doc: ParsedDocument) -> List[Chunk]:
        """
        Chunk a parsed document into smaller pieces

        Args:
            doc: ParsedDocument to chunk

        Returns:
            List of Chunk objects
        """
        chunks = []

        # 1. Create chunks for data sheet (high priority structured data)
        data_sheet_chunks = self._chunk_data_sheet(doc)
        chunks.extend(data_sheet_chunks)

        # 2. Create chunks for rent schedules from tables
        rent_chunks = self._chunk_rent_schedules(doc)
        chunks.extend(rent_chunks)

        # 3. Chunk by sections (articles, exhibits)
        section_chunks = self._chunk_by_sections(doc)
        chunks.extend(section_chunks)

        # Add chunk indices
        for i, chunk in enumerate(chunks):
            chunk.chunk_index = i

        return chunks

    def _chunk_data_sheet(self, doc: ParsedDocument) -> List[Chunk]:
        """Create dedicated chunks for data sheet content"""
        chunks = []

        if not doc.data_sheet:
            return chunks

        # Create a formatted data sheet chunk
        data_sheet_text = "DATA SHEET SUMMARY\n\n"
        for key, value in doc.data_sheet.items():
            formatted_key = key.replace("_", " ").title()
            data_sheet_text += f"{formatted_key}: {value}\n"

        # Clean the text
        data_sheet_text = self.text_cleaner.clean_for_embedding(data_sheet_text)

        chunk = Chunk(
            id=str(uuid.uuid4()),
            content=data_sheet_text,
            metadata={
                "tenant_name": doc.tenant_name,
                "source_file": doc.file_name,
                "section_type": "data_sheet",
                **doc.data_sheet
            },
            token_count=self.count_tokens(data_sheet_text),
            source_file=doc.file_name,
            section_type="data_sheet",
            section_name="Data Sheet"
        )
        chunks.append(chunk)

        return chunks

    def _chunk_rent_schedules(self, doc: ParsedDocument) -> List[Chunk]:
        """Create chunks for rent schedule tables"""
        chunks = []

        for table in doc.tables:
            if table.table_type == "rent_schedule":
                # Create a chunk for the rent schedule
                rent_text = f"RENT SCHEDULE for {doc.tenant_name}\n\n"
                rent_text += table.raw_text

                # Clean the text
                rent_text = self.text_cleaner.clean_for_embedding(rent_text)

                chunk = Chunk(
                    id=str(uuid.uuid4()),
                    content=rent_text,
                    metadata={
                        "tenant_name": doc.tenant_name,
                        "source_file": doc.file_name,
                        "section_type": "rent_schedule",
                        "table_headers": table.headers
                    },
                    token_count=self.count_tokens(rent_text),
                    source_file=doc.file_name,
                    section_type="rent_schedule",
                    section_name="Rent Schedule"
                )
                chunks.append(chunk)

        return chunks

    def _chunk_by_sections(self, doc: ParsedDocument) -> List[Chunk]:
        """Chunk document by article/section boundaries"""
        chunks = []

        for section_name, section_content in doc.sections.items():
            # Clean the content
            cleaned_content = self.text_cleaner.clean_for_embedding(section_content)
            token_count = self.count_tokens(cleaned_content)

            # Determine section type
            section_type = self._determine_section_type(section_name)

            # If section is small enough, create single chunk
            if token_count <= self.chunk_size:
                if token_count >= self.min_chunk_size:
                    chunk = Chunk(
                        id=str(uuid.uuid4()),
                        content=cleaned_content,
                        metadata={
                            "tenant_name": doc.tenant_name,
                            "source_file": doc.file_name,
                            "section_type": section_type,
                            "section_name": section_name
                        },
                        token_count=token_count,
                        source_file=doc.file_name,
                        section_type=section_type,
                        section_name=section_name
                    )
                    chunks.append(chunk)
            else:
                # Split large sections with overlap
                sub_chunks = self._split_large_section(
                    cleaned_content,
                    section_name,
                    section_type,
                    doc
                )
                chunks.extend(sub_chunks)

        return chunks

    def _split_large_section(
        self,
        content: str,
        section_name: str,
        section_type: str,
        doc: ParsedDocument
    ) -> List[Chunk]:
        """Split a large section into smaller chunks with overlap"""
        chunks = []

        # Split by paragraphs first
        paragraphs = content.split('\n\n')

        current_chunk_text = ""
        current_tokens = 0
        chunk_number = 1

        for para in paragraphs:
            para_tokens = self.count_tokens(para)

            # If adding this paragraph exceeds chunk size
            if current_tokens + para_tokens > self.chunk_size and current_chunk_text:
                # Save current chunk
                chunk = Chunk(
                    id=str(uuid.uuid4()),
                    content=current_chunk_text.strip(),
                    metadata={
                        "tenant_name": doc.tenant_name,
                        "source_file": doc.file_name,
                        "section_type": section_type,
                        "section_name": section_name,
                        "chunk_part": chunk_number
                    },
                    token_count=current_tokens,
                    source_file=doc.file_name,
                    section_type=section_type,
                    section_name=f"{section_name} (Part {chunk_number})"
                )
                chunks.append(chunk)
                chunk_number += 1

                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk_text)
                current_chunk_text = overlap_text + "\n\n" + para
                current_tokens = self.count_tokens(current_chunk_text)
            else:
                # Add paragraph to current chunk
                if current_chunk_text:
                    current_chunk_text += "\n\n" + para
                else:
                    current_chunk_text = para
                current_tokens += para_tokens

        # Save final chunk
        if current_chunk_text and self.count_tokens(current_chunk_text) >= self.min_chunk_size:
            chunk = Chunk(
                id=str(uuid.uuid4()),
                content=current_chunk_text.strip(),
                metadata={
                    "tenant_name": doc.tenant_name,
                    "source_file": doc.file_name,
                    "section_type": section_type,
                    "section_name": section_name,
                    "chunk_part": chunk_number
                },
                token_count=self.count_tokens(current_chunk_text),
                source_file=doc.file_name,
                section_type=section_type,
                section_name=f"{section_name} (Part {chunk_number})" if chunk_number > 1 else section_name
            )
            chunks.append(chunk)

        return chunks

    def _get_overlap_text(self, text: str) -> str:
        """Get the last portion of text for overlap"""
        tokens = self.tokenizer.encode(text)
        if len(tokens) <= self.chunk_overlap:
            return text

        overlap_tokens = tokens[-self.chunk_overlap:]
        return self.tokenizer.decode(overlap_tokens)

    def _determine_section_type(self, section_name: str) -> str:
        """Determine the type of section based on its name"""
        section_lower = section_name.lower()

        if 'article' in section_lower:
            return "article"
        elif 'exhibit' in section_lower:
            return "exhibit"
        elif 'data sheet' in section_lower:
            return "data_sheet"
        elif 'rent' in section_lower:
            return "rent_schedule"
        else:
            return "general"


def chunk_all_documents(documents: List[ParsedDocument], **kwargs) -> List[Chunk]:
    """
    Chunk all documents

    Args:
        documents: List of ParsedDocument objects
        **kwargs: Arguments to pass to Chunker

    Returns:
        List of all Chunk objects
    """
    chunker = Chunker(**kwargs)
    all_chunks = []

    for doc in documents:
        chunks = chunker.chunk_document(doc)
        all_chunks.extend(chunks)

    return all_chunks
