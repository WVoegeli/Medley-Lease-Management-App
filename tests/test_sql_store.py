"""
Unit tests for SQLStore database module.
"""

import pytest
import sqlite3
from pathlib import Path
import sys
import tempfile
import os

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.sql_store import SQLStore


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_leases.db")
        store = SQLStore(db_path=db_path)
        yield store
        store.close()


class TestTenantOperations:
    """Test tenant CRUD operations."""

    def test_add_tenant(self, temp_db):
        """Test adding a new tenant."""
        tenant_id = temp_db.add_tenant(
            tenant_name="Test Tenant",
            business_type="Retail",
            contact_email="test@example.com"
        )
        assert tenant_id > 0

    def test_add_duplicate_tenant(self, temp_db):
        """Test that adding duplicate tenant returns existing ID."""
        tenant_id1 = temp_db.add_tenant("Duplicate Tenant")
        tenant_id2 = temp_db.add_tenant("Duplicate Tenant")
        assert tenant_id1 == tenant_id2

    def test_get_tenant(self, temp_db):
        """Test retrieving tenant by name."""
        temp_db.add_tenant("Get Tenant Test", business_type="Coffee Shop")
        tenant = temp_db.get_tenant("Get Tenant Test")

        assert tenant is not None
        assert tenant['tenant_name'] == "Get Tenant Test"
        assert tenant['business_type'] == "Coffee Shop"

    def test_get_nonexistent_tenant(self, temp_db):
        """Test retrieving non-existent tenant."""
        tenant = temp_db.get_tenant("Nonexistent Tenant")
        assert tenant is None

    def test_get_all_tenants(self, temp_db):
        """Test retrieving all tenants."""
        temp_db.add_tenant("Tenant A")
        temp_db.add_tenant("Tenant B")
        temp_db.add_tenant("Tenant C")

        tenants = temp_db.get_all_tenants()
        assert len(tenants) == 3
        assert all('tenant_name' in t for t in tenants)


class TestLeaseOperations:
    """Test lease CRUD operations."""

    def test_add_lease(self, temp_db):
        """Test adding a new lease."""
        lease_id = temp_db.add_lease(
            tenant_name="Lease Test Tenant",
            lease_file="test_lease.docx",
            start_date="2024-01-01",
            end_date="2025-12-31",
            base_rent=2000.00,
            square_footage=1500.0
        )
        assert lease_id > 0

    def test_get_lease(self, temp_db):
        """Test retrieving lease by ID."""
        lease_id = temp_db.add_lease(
            tenant_name="Get Lease Test",
            lease_file="lease.docx",
            base_rent=2500.00
        )

        lease = temp_db.get_lease(lease_id)
        assert lease is not None
        assert lease['tenant_name'] == "Get Lease Test"
        assert lease['base_rent'] == 2500.00

    def test_get_nonexistent_lease(self, temp_db):
        """Test retrieving non-existent lease."""
        lease = temp_db.get_lease(99999)
        assert lease is None

    def test_get_leases_by_tenant(self, temp_db):
        """Test retrieving all leases for a tenant."""
        temp_db.add_lease("Multi Lease Tenant", "lease1.docx", base_rent=1000)
        temp_db.add_lease("Multi Lease Tenant", "lease2.docx", base_rent=1500)
        temp_db.add_lease("Other Tenant", "lease3.docx", base_rent=2000)

        leases = temp_db.get_leases_by_tenant("Multi Lease Tenant")
        assert len(leases) == 2

    def test_update_lease(self, temp_db):
        """Test updating lease information."""
        lease_id = temp_db.add_lease(
            "Update Test Tenant",
            "lease.docx",
            base_rent=1000
        )

        success = temp_db.update_lease(lease_id, base_rent=1500, status='renewed')
        assert success is True

        updated_lease = temp_db.get_lease(lease_id)
        assert updated_lease['base_rent'] == 1500
        assert updated_lease['status'] == 'renewed'

    def test_get_all_leases(self, temp_db):
        """Test retrieving all leases."""
        temp_db.add_lease("Tenant 1", "l1.docx", status='active')
        temp_db.add_lease("Tenant 2", "l2.docx", status='active')
        temp_db.add_lease("Tenant 3", "l3.docx", status='expired')

        all_leases = temp_db.get_all_leases()
        assert len(all_leases) == 3

        active_leases = temp_db.get_all_leases(status='active')
        assert len(active_leases) == 2


class TestExpirationTracking:
    """Test lease expiration and alert functionality."""

    def test_create_expiration_alerts(self, temp_db):
        """Test that expiration alerts are created automatically."""
        lease_id = temp_db.add_lease(
            "Alert Test Tenant",
            "lease.docx",
            end_date="2025-12-31"
        )

        # Check that alerts were created
        alerts = temp_db.execute_custom_query(
            "SELECT * FROM lease_alerts WHERE lease_id = ?",
            (lease_id,)
        )

        # Should have 3 alerts (90, 60, 30 days)
        assert len(alerts) == 3
        assert all(a['alert_type'] == 'expiration' for a in alerts)

    def test_get_expiring_leases(self, temp_db):
        """Test retrieving leases expiring soon."""
        # Add lease expiring in 60 days
        from datetime import datetime, timedelta
        expiry_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")

        temp_db.add_lease(
            "Expiring Tenant",
            "lease.docx",
            end_date=expiry_date,
            base_rent=2000
        )

        expiring = temp_db.get_expiring_leases(days_ahead=90)
        assert len(expiring) >= 1

    def test_dismiss_alert(self, temp_db):
        """Test dismissing an alert."""
        lease_id = temp_db.add_lease(
            "Dismiss Alert Test",
            "lease.docx",
            end_date="2025-12-31"
        )

        alerts = temp_db.get_active_alerts(days_ahead=365)
        if alerts:
            alert_id = alerts[0]['alert_id']
            temp_db.dismiss_alert(alert_id)

            # Verify alert was dismissed
            dismissed = temp_db.execute_custom_query(
                "SELECT status FROM lease_alerts WHERE alert_id = ?",
                (alert_id,)
            )
            assert dismissed[0]['status'] == 'dismissed'


class TestFinancialAnalytics:
    """Test financial analytics and reporting."""

    def test_get_financial_summary(self, temp_db):
        """Test financial summary calculation."""
        temp_db.add_lease("Tenant 1", "l1.docx", base_rent=2000, status='active', square_footage=1000)
        temp_db.add_lease("Tenant 2", "l2.docx", base_rent=3000, status='active', square_footage=1500)

        summary = temp_db.get_financial_summary()

        assert summary['active_leases'] == 2
        assert summary['monthly_revenue'] == 5000
        assert summary['annual_revenue'] == 60000
        assert summary['total_square_footage'] == 2500

    def test_get_revenue_by_tenant(self, temp_db):
        """Test revenue breakdown by tenant."""
        temp_db.add_lease("High Revenue", "l1.docx", base_rent=5000, status='active')
        temp_db.add_lease("Low Revenue", "l2.docx", base_rent=1000, status='active')

        revenue_data = temp_db.get_revenue_by_tenant()

        assert len(revenue_data) == 2
        # Should be sorted by rent (highest first)
        assert revenue_data[0]['tenant_name'] == "High Revenue"
        assert revenue_data[0]['monthly_rent'] == 5000
        assert revenue_data[0]['annual_rent'] == 60000

    def test_occupancy_rate(self, temp_db):
        """Test occupancy rate calculation."""
        temp_db.add_lease("T1", "l1.docx", square_footage=5000, status='active')
        temp_db.add_lease("T2", "l2.docx", square_footage=3000, status='active')

        occupancy = temp_db.get_occupancy_rate(total_property_sqft=10000)

        assert occupancy['total_property_sqft'] == 10000
        assert occupancy['leased_sqft'] == 8000
        assert occupancy['available_sqft'] == 2000
        assert occupancy['occupancy_rate'] == 80.0


class TestQueryLog:
    """Test query audit logging."""

    def test_log_query(self, temp_db):
        """Test logging a query."""
        temp_db.log_query(
            "What is the rent?",
            tenant_filter="Test Tenant",
            result_count=3,
            response_time_ms=150.5
        )

        logs = temp_db.execute_custom_query(
            "SELECT * FROM query_log WHERE query_text = ?",
            ("What is the rent?",)
        )

        assert len(logs) == 1
        assert logs[0]['tenant_filter'] == "Test Tenant"
        assert logs[0]['result_count'] == 3

    def test_popular_queries(self, temp_db):
        """Test getting popular queries."""
        # Log same query multiple times
        for _ in range(3):
            temp_db.log_query("Popular question")

        for _ in range(2):
            temp_db.log_query("Less popular question")

        popular = temp_db.get_popular_queries(limit=10)

        assert len(popular) >= 2
        # Most popular should be first
        assert popular[0]['query_text'] == "Popular question"
        assert popular[0]['query_count'] == 3


def test_database_initialization():
    """Test that database initializes with correct schema."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "schema_test.db")
        store = SQLStore(db_path=db_path)

        # Verify all tables exist
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
        """)

        tables = [row[0] for row in cursor.fetchall()]

        expected_tables = [
            'tenants', 'leases', 'financial_records',
            'lease_alerts', 'query_log'
        ]

        for table in expected_tables:
            assert table in tables

        conn.close()
        store.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
