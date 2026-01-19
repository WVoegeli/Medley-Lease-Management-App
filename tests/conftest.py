"""
Pytest configuration and shared fixtures.
"""

import pytest
import sys
from pathlib import Path
import tempfile
import os

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.sql_store import SQLStore


@pytest.fixture(scope="function")
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_leases.db")
        store = SQLStore(db_path=db_path)

        # Add some sample data
        _populate_test_data(store)

        yield store
        store.close()


def _populate_test_data(store: SQLStore):
    """Populate database with sample test data."""
    from datetime import datetime, timedelta

    # Add test tenants and leases
    store.add_lease(
        tenant_name="Summit Coffee",
        lease_file="summit_coffee.docx",
        start_date="2023-01-01",
        end_date=(datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d"),
        base_rent=3500.00,
        square_footage=2000.0,
        status='active'
    )

    store.add_lease(
        tenant_name="Medley Books",
        lease_file="medley_books.docx",
        start_date="2022-06-01",
        end_date=(datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"),
        base_rent=2800.00,
        square_footage=1800.0,
        status='active'
    )

    store.add_lease(
        tenant_name="Fitness First",
        lease_file="fitness_first.docx",
        start_date="2023-03-01",
        end_date=(datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
        base_rent=5000.00,
        square_footage=3500.0,
        status='active'
    )


@pytest.fixture(scope="function")
def sample_lease_data():
    """Sample lease data for testing."""
    return {
        'tenant_name': 'Test Cafe',
        'lease_file': 'test_cafe.docx',
        'start_date': '2024-01-01',
        'end_date': '2025-12-31',
        'term_months': 24,
        'square_footage': 1500.0,
        'base_rent': 2500.00,
        'rent_frequency': 'monthly',
        'status': 'active'
    }
