"""
Embedder for creating vector representations of text
Uses OpenAI embeddings
"""

from typing import List, Optional
from openai import OpenAI
from tqdm import tqdm
import tiktoken

from config.settings import OPENAI_API_KEY, EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE


class Embedder:
    """Create embeddings using OpenAI's embedding models"""

    # Maximum tokens for embedding model
    MAX_TOKENS = 8000  # Leave some buffer below 8192 limit

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = EMBEDDING_MODEL,
        batch_size: int = EMBEDDING_BATCH_SIZE
    ):
        """
        Initialize the embedder

        Args:
            api_key: OpenAI API key (defaults to env var)
            model: Embedding model to use
            batch_size: Number of texts to embed per batch
        """
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.batch_size = batch_size
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def _truncate_text(self, text: str) -> str:
        """Truncate text to fit within token limit"""
        tokens = self.tokenizer.encode(text)
        if len(tokens) > self.MAX_TOKENS:
            tokens = tokens[:self.MAX_TOKENS]
            text = self.tokenizer.decode(tokens)
        return text

    def embed_text(self, text: str) -> List[float]:
        """
        Create embedding for a single text

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        text = self._truncate_text(text)
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding

    def embed_texts(self, texts: List[str], show_progress: bool = True) -> List[List[float]]:
        """
        Create embeddings for multiple texts

        Args:
            texts: List of texts to embed
            show_progress: Whether to show progress bar

        Returns:
            List of embedding vectors
        """
        all_embeddings = []

        # Truncate all texts first
        texts = [self._truncate_text(t) for t in texts]

        # Process one at a time to avoid batch token limits
        iterator = tqdm(texts, desc="Embedding texts") if show_progress else texts

        for text in iterator:
            try:
                response = self.client.embeddings.create(
                    input=text,
                    model=self.model
                )
                all_embeddings.append(response.data[0].embedding)
            except Exception as e:
                print(f"Error embedding text: {e}")
                # Return zero vector as fallback
                all_embeddings.append([0.0] * 1536)

        return all_embeddings

    def embed_query(self, query: str) -> List[float]:
        """
        Create embedding for a search query

        Args:
            query: Search query

        Returns:
            Embedding vector
        """
        return self.embed_text(query)
