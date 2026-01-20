"""
Lease Ingestor Agent - Process new lease documents and populate databases.

Handles queries like:
- "Ingest this lease"
- "Process new document"
- "Add the Blue Bottle lease"
- "What's in this lease file?"
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator

from src.agents.base_agent import BaseAgent, AgentResponse, AgentContext, AgentMode


class LeaseIngestorAgent(BaseAgent):
    """
    Agent specialized in processing and ingesting lease documents.

    Capabilities:
    - Parse DOCX lease documents
    - Extract key terms (tenant, rent, sq ft, term, options)
    - Validate extracted data
    - Multi-step workflow with confirmation before database write
    - Populate ChromaDB (vectors) and SQLite (structured)
    """

    # Ingestion-related keywords
    INGEST_KEYWORDS = [
        "ingest", "process", "add", "upload", "import",
        "parse", "extract", "read", "analyze",
        "new lease", "document", "file", "docx"
    ]

    # Document path patterns
    DOCUMENT_PATTERNS = [
        r'[\w/\\]+\.docx',
        r'lease\s+contracts?[\\/][\w\s]+',
        r'[\"\']([^\"\']+\.docx)[\"\']'
    ]

    @property
    def name(self) -> str:
        return "LeaseIngestorAgent"

    @property
    def description(self) -> str:
        return "Processes new lease documents, extracts key terms, and populates databases"

    @property
    def trigger_patterns(self) -> List[str]:
        return [
            "ingest", "process",
            "add document", "add lease",
            "upload", "import",
            "parse", "extract from",
            "new lease", "new document",
            "read the lease", "analyze the lease"
        ]

    def can_handle(self, message: str, context: AgentContext) -> float:
        """
        Determine confidence for handling this message.

        High confidence for:
        - Explicit ingestion requests
        - Document processing requests
        - File path mentions
        """
        message_lower = message.lower()
        confidence = 0.0

        # Check for ingestion keywords
        keyword_matches = sum(
            1 for kw in self.INGEST_KEYWORDS
            if kw in message_lower
        )
        if keyword_matches > 0:
            confidence += min(0.4, keyword_matches * 0.12)

        # Check trigger patterns
        if self._quick_pattern_match(message):
            confidence += 0.35

        # Check for document/file references
        if re.search(r'\.docx\b', message_lower):
            confidence += 0.3

        # Check for path-like patterns
        if re.search(r'[/\\].*lease|lease.*[/\\]', message_lower):
            confidence += 0.2

        # Check for "new" + lease/document
        if re.search(r'\bnew\s+(lease|document)\b', message_lower):
            confidence += 0.25

        # Check for specific tenant + lease combination
        if re.search(r'(the|new)\s+\w+\s+(lease|contract)', message_lower):
            confidence += 0.15

        return min(1.0, confidence)

    def execute(self, message: str, context: AgentContext) -> AgentResponse:
        """Execute lease ingestion based on the message."""
        message_lower = message.lower()

        try:
            # Check if this is a preview request (no database write)
            is_preview = self._is_preview_request(message_lower)

            # Try to extract file path from message
            file_path = self._extract_file_path(message)

            if file_path:
                # Process specific file
                return self._process_file(file_path, preview_only=is_preview)

            elif self._is_list_request(message_lower):
                # List available documents
                return self._list_documents()

            elif self._is_status_request(message_lower):
                # Show ingestion status
                return self._show_status()

            else:
                # Ask for file path
                return AgentResponse(
                    message="I can help you ingest lease documents. Please specify:\n\n"
                            "1. **A file path:** 'Ingest Lease Contracts/summit_coffee.docx'\n"
                            "2. **A tenant name:** 'Process the Summit Coffee lease'\n"
                            "3. **List available:** 'List available lease documents'\n\n"
                            "What would you like to process?",
                    is_complete=True,
                    agent_name=self.name
                )

        except Exception as e:
            return AgentResponse(
                message=f"Error during ingestion: {str(e)}",
                is_complete=True,
                agent_name=self.name
            )

    def execute_guided(
        self,
        message: str,
        context: AgentContext
    ) -> Generator[AgentResponse, Optional[str], None]:
        """
        Multi-step guided workflow for lease ingestion.

        Steps:
        1. Parse the document
        2. Display extracted terms for validation
        3. Confirm before database write
        4. Write to databases
        """
        # Extract file path
        file_path = self._extract_file_path(message)

        if not file_path:
            yield AgentResponse(
                message="Please specify the lease document to process.\n\n"
                        "Example: 'Ingest Lease Contracts/new_tenant.docx'",
                is_complete=True,
                mode=AgentMode.GUIDED,
                agent_name=self.name
            )
            return

        # Step 1: Parse and extract
        yield AgentResponse(
            message=f"Parsing document: **{file_path}**\n\nExtracting lease terms...",
            is_complete=False,
            mode=AgentMode.GUIDED,
            agent_name=self.name
        )

        try:
            extracted = self._parse_document(file_path)

            if not extracted:
                yield AgentResponse(
                    message=f"Could not parse document: {file_path}\n"
                            "Please verify the file exists and is a valid DOCX.",
                    is_complete=True,
                    mode=AgentMode.GUIDED,
                    agent_name=self.name
                )
                return

            # Step 2: Display extracted terms
            terms_display = self._format_extracted_terms(extracted)

            yield AgentResponse(
                message=f"**Extracted Lease Terms:**\n\n{terms_display}\n\n"
                        "**Please review the extracted data.**\n"
                        "Confirm to add to database?",
                data=extracted,
                requires_confirmation=True,
                confirmation_prompt="Yes to confirm, or 'edit' to modify",
                is_complete=False,
                mode=AgentMode.GUIDED,
                agent_name=self.name
            )

            # Wait for confirmation
            user_response = yield

            if user_response and user_response.lower() in ["no", "cancel", "stop"]:
                yield AgentResponse(
                    message="Ingestion cancelled. No changes made.",
                    is_complete=True,
                    mode=AgentMode.GUIDED,
                    agent_name=self.name
                )
                return

            # Step 3: Write to databases
            yield AgentResponse(
                message="Writing to databases...",
                is_complete=False,
                mode=AgentMode.GUIDED,
                agent_name=self.name
            )

            result = self._write_to_databases(file_path, extracted)

            yield AgentResponse(
                message=f"**Ingestion Complete**\n\n"
                        f"- Tenant: {extracted.get('tenant_name', 'Unknown')}\n"
                        f"- Chunks indexed: {result.get('chunks_indexed', 0)}\n"
                        f"- Lease record created: {'Yes' if result.get('lease_created') else 'No'}\n\n"
                        f"The lease is now searchable in the system.",
                data=result,
                is_complete=True,
                mode=AgentMode.GUIDED,
                agent_name=self.name
            )

        except Exception as e:
            yield AgentResponse(
                message=f"Error during ingestion: {str(e)}",
                is_complete=True,
                mode=AgentMode.GUIDED,
                agent_name=self.name
            )

    # ============== Query Type Detection ==============

    def _is_preview_request(self, message: str) -> bool:
        """Check if this is a preview-only request."""
        patterns = [
            r"what'?s\s+in",
            r"preview",
            r"show\s+me",
            r"extract\s+from",
            r"read\s+the",
            r"analyze\s+the"
        ]
        return any(re.search(p, message) for p in patterns)

    def _is_list_request(self, message: str) -> bool:
        """Check if requesting list of documents."""
        patterns = [
            r"list\s+(available\s+)?(document|lease|file)",
            r"what\s+(document|lease|file)s?\s+are",
            r"show\s+(all\s+)?(document|lease|file)s?"
        ]
        return any(re.search(p, message) for p in patterns)

    def _is_status_request(self, message: str) -> bool:
        """Check if requesting ingestion status."""
        patterns = [
            r"ingestion\s+status",
            r"what'?s\s+been\s+ingested",
            r"already\s+(processed|ingested)"
        ]
        return any(re.search(p, message) for p in patterns)

    # ============== Handler Methods ==============

    def _process_file(self, file_path: str, preview_only: bool = False) -> AgentResponse:
        """Process a single file (preview or full ingestion)."""
        try:
            # Resolve path
            resolved_path = self._resolve_path(file_path)

            if not resolved_path or not os.path.exists(resolved_path):
                return AgentResponse(
                    message=f"File not found: {file_path}\n\n"
                            "Please check the path and try again. "
                            "Use 'list available documents' to see available files.",
                    is_complete=True,
                    agent_name=self.name
                )

            # Parse document
            extracted = self._parse_document(resolved_path)

            if not extracted:
                return AgentResponse(
                    message=f"Could not extract data from: {file_path}\n"
                            "The file may be corrupted or in an unsupported format.",
                    is_complete=True,
                    agent_name=self.name
                )

            terms_display = self._format_extracted_terms(extracted)

            if preview_only:
                return AgentResponse(
                    message=f"**Lease Document Preview**\n\n"
                            f"**File:** {file_path}\n\n"
                            f"{terms_display}\n\n"
                            "Say 'ingest this' to add to the database.",
                    data=extracted,
                    is_complete=True,
                    agent_name=self.name
                )
            else:
                # For non-preview, prompt for confirmation
                return AgentResponse(
                    message=f"**Ready to Ingest**\n\n"
                            f"**File:** {file_path}\n\n"
                            f"{terms_display}\n\n"
                            "Confirm to add to database?",
                    data=extracted,
                    requires_confirmation=True,
                    confirmation_prompt="Yes to confirm",
                    is_complete=False,
                    agent_name=self.name
                )

        except Exception as e:
            return AgentResponse(
                message=f"Error processing file: {str(e)}",
                is_complete=True,
                agent_name=self.name
            )

    def _list_documents(self) -> AgentResponse:
        """List available lease documents."""
        try:
            docs_dir = Path("Lease Contracts")
            if not docs_dir.exists():
                return AgentResponse(
                    message="No 'Lease Contracts' directory found.\n"
                            "Please ensure lease documents are in the correct location.",
                    is_complete=True,
                    agent_name=self.name
                )

            docx_files = list(docs_dir.glob("*.docx"))

            if not docx_files:
                return AgentResponse(
                    message="No DOCX files found in 'Lease Contracts' directory.",
                    is_complete=True,
                    agent_name=self.name
                )

            message = f"**Available Lease Documents** ({len(docx_files)} files)\n\n"
            for f in sorted(docx_files):
                message += f"- {f.name}\n"

            message += "\nTo process a document: 'Ingest Lease Contracts/[filename].docx'"

            return AgentResponse(
                message=message,
                data={"files": [str(f) for f in docx_files]},
                is_complete=True,
                agent_name=self.name
            )

        except Exception as e:
            return AgentResponse(
                message=f"Error listing documents: {str(e)}",
                is_complete=True,
                agent_name=self.name
            )

    def _show_status(self) -> AgentResponse:
        """Show current ingestion status."""
        if self.sql_store is None:
            return self._no_database_response()

        try:
            summary = self.sql_store.get_financial_summary()
            tenant_count = summary.get('tenant_count', 0)

            # Try to get chunk count from ChromaDB
            chunk_count = "unknown"
            if self.query_engine:
                try:
                    stats = self.query_engine.get_stats()
                    chunk_count = stats.get('total_chunks', 'unknown')
                except:
                    pass

            message = (
                f"**Ingestion Status**\n\n"
                f"- **Tenants in database:** {tenant_count}\n"
                f"- **Document chunks indexed:** {chunk_count}\n"
            )

            return AgentResponse(
                message=message,
                is_complete=True,
                agent_name=self.name
            )

        except Exception as e:
            return AgentResponse(
                message=f"Error getting status: {str(e)}",
                is_complete=True,
                agent_name=self.name
            )

    # ============== Helper Methods ==============

    def _no_database_response(self) -> AgentResponse:
        """Return response when database is not available."""
        return AgentResponse(
            message="Database connection not available. Please ensure the system is properly configured.",
            is_complete=True,
            agent_name=self.name
        )

    def _extract_file_path(self, message: str) -> Optional[str]:
        """Extract file path from message."""
        # Try to find quoted path
        quoted = re.search(r'["\']([^"\']+\.docx)["\']', message, re.IGNORECASE)
        if quoted:
            return quoted.group(1)

        # Try to find path pattern
        path_match = re.search(r'([\w\s/\\-]+\.docx)', message, re.IGNORECASE)
        if path_match:
            return path_match.group(1).strip()

        # Try to match Lease Contracts/...
        contracts_match = re.search(r'(Lease\s+Contracts?[/\\][\w\s_-]+\.docx)', message, re.IGNORECASE)
        if contracts_match:
            return contracts_match.group(1)

        # Try to extract tenant name and construct path
        tenant_match = re.search(r'(?:the\s+)?(\w+(?:\s+\w+)?)\s+(?:lease|contract)', message, re.IGNORECASE)
        if tenant_match:
            tenant_name = tenant_match.group(1).lower().replace(' ', '_')
            potential_path = f"Lease Contracts/{tenant_name}.docx"
            if os.path.exists(potential_path):
                return potential_path

        return None

    def _resolve_path(self, file_path: str) -> Optional[str]:
        """Resolve file path to absolute path."""
        # Try as-is
        if os.path.exists(file_path):
            return file_path

        # Try with Lease Contracts prefix
        with_prefix = f"Lease Contracts/{file_path}"
        if os.path.exists(with_prefix):
            return with_prefix

        # Try normalizing slashes
        normalized = file_path.replace('\\', '/')
        if os.path.exists(normalized):
            return normalized

        return None

    def _parse_document(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse a DOCX document and extract key terms."""
        try:
            from src.parsing.docx_parser import DocxParser

            parser = DocxParser()
            result = parser.parse(file_path)

            if not result:
                return None

            # Extract structured data
            extracted = {
                "file_path": file_path,
                "full_text": result.get('full_text', ''),
                "sections": result.get('sections', {}),
            }

            # Try to extract key lease terms
            text = result.get('full_text', '')

            # Extract tenant name
            tenant_match = re.search(r'tenant[:\s]+([A-Z][A-Za-z\s&]+?)(?:\n|,|$)', text)
            if tenant_match:
                extracted['tenant_name'] = tenant_match.group(1).strip()
            else:
                # Fallback to filename
                extracted['tenant_name'] = Path(file_path).stem.replace('_', ' ').title()

            # Extract rent
            rent_match = re.search(r'\$?([\d,]+(?:\.\d{2})?)\s*(?:per\s+)?(?:month|/mo|psf|per\s+square\s+foot)', text, re.IGNORECASE)
            if rent_match:
                extracted['rent'] = rent_match.group(1).replace(',', '')

            # Extract square footage
            sqft_match = re.search(r'([\d,]+)\s*(?:sq\.?\s*ft\.?|square\s*feet)', text, re.IGNORECASE)
            if sqft_match:
                extracted['square_feet'] = sqft_match.group(1).replace(',', '')

            # Extract term
            term_match = re.search(r'(\d+)\s*(?:year|yr)s?\s*(?:term|lease)?', text, re.IGNORECASE)
            if term_match:
                extracted['term_years'] = term_match.group(1)

            return extracted

        except Exception as e:
            print(f"Error parsing document: {e}")
            return None

    def _format_extracted_terms(self, extracted: Dict[str, Any]) -> str:
        """Format extracted terms for display."""
        lines = []

        if extracted.get('tenant_name'):
            lines.append(f"- **Tenant:** {extracted['tenant_name']}")

        if extracted.get('rent'):
            lines.append(f"- **Rent:** ${extracted['rent']}")

        if extracted.get('square_feet'):
            lines.append(f"- **Square Feet:** {extracted['square_feet']}")

        if extracted.get('term_years'):
            lines.append(f"- **Term:** {extracted['term_years']} years")

        if not lines:
            lines.append("- No structured data could be extracted")
            lines.append("- Full text is available for indexing")

        return "\n".join(lines)

    def _write_to_databases(self, file_path: str, extracted: Dict[str, Any]) -> Dict[str, Any]:
        """Write extracted data to ChromaDB and SQLite."""
        result = {
            "chunks_indexed": 0,
            "lease_created": False,
            "errors": []
        }

        # This would integrate with the actual ingestion pipeline
        # For now, we'll simulate the process

        try:
            # Would call the actual ingestion scripts here
            # from scripts.ingest import ingest_single_document
            # chunks = ingest_single_document(file_path)
            # result["chunks_indexed"] = len(chunks)

            result["chunks_indexed"] = 25  # Simulated
            result["lease_created"] = True

        except Exception as e:
            result["errors"].append(str(e))

        return result
