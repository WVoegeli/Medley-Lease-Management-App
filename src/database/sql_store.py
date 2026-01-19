"""
SQLite database for structured lease metadata, analytics, and tracking.

This module provides persistent storage for:
- Lease metadata (tenants, terms, financials)
- Expiration tracking and alerts
- Financial analytics and reporting
- Query audit logs
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SQLStore:
    """Structured database for lease management and analytics."""

    def __init__(self, db_path: str = "data/leases.db"):
        """Initialize SQLite database with schema."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._init_database()

    def _init_database(self):
        """Create database schema if it doesn't exist."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Access columns by name

        cursor = self.conn.cursor()

        # Tenants table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                tenant_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_name TEXT UNIQUE NOT NULL,
                business_type TEXT,
                contact_email TEXT,
                contact_phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Leases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leases (
                lease_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                lease_file TEXT NOT NULL,
                start_date DATE,
                end_date DATE,
                term_months INTEGER,
                square_footage REAL,
                base_rent REAL,
                rent_frequency TEXT DEFAULT 'monthly',
                security_deposit REAL,
                renewal_options TEXT,
                special_provisions TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
            )
        """)

        # Financial records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financial_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                lease_id INTEGER NOT NULL,
                record_date DATE NOT NULL,
                record_type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lease_id) REFERENCES leases(lease_id)
            )
        """)

        # Lease alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lease_alerts (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                lease_id INTEGER NOT NULL,
                alert_type TEXT NOT NULL,
                alert_date DATE NOT NULL,
                days_notice INTEGER,
                message TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dismissed_at TIMESTAMP,
                FOREIGN KEY (lease_id) REFERENCES leases(lease_id)
            )
        """)

        # Query audit log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_text TEXT NOT NULL,
                tenant_filter TEXT,
                result_count INTEGER,
                response_time_ms REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leases_tenant ON leases(tenant_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leases_dates ON leases(start_date, end_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leases_status ON leases(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_date ON lease_alerts(alert_date, status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_financial_date ON financial_records(record_date)")

        self.conn.commit()
        logger.info(f"Database initialized at {self.db_path}")

    # ==================== Tenant Operations ====================

    def add_tenant(self, tenant_name: str, business_type: str = None,
                   contact_email: str = None, contact_phone: str = None) -> int:
        """Add a new tenant to the database."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO tenants (tenant_name, business_type, contact_email, contact_phone)
                VALUES (?, ?, ?, ?)
            """, (tenant_name, business_type, contact_email, contact_phone))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Tenant already exists, return existing ID
            cursor.execute("SELECT tenant_id FROM tenants WHERE tenant_name = ?", (tenant_name,))
            return cursor.fetchone()[0]

    def get_tenant(self, tenant_name: str) -> Optional[Dict]:
        """Get tenant information by name."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tenants WHERE tenant_name = ?", (tenant_name,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_tenants(self) -> List[Dict]:
        """Get all tenants."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tenants ORDER BY tenant_name")
        return [dict(row) for row in cursor.fetchall()]

    # ==================== Lease Operations ====================

    def add_lease(self, tenant_name: str, lease_file: str, **kwargs) -> int:
        """Add a new lease to the database."""
        tenant_id = self.add_tenant(tenant_name)

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO leases (
                tenant_id, lease_file, start_date, end_date, term_months,
                square_footage, base_rent, rent_frequency, security_deposit,
                renewal_options, special_provisions, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tenant_id,
            lease_file,
            kwargs.get('start_date'),
            kwargs.get('end_date'),
            kwargs.get('term_months'),
            kwargs.get('square_footage'),
            kwargs.get('base_rent'),
            kwargs.get('rent_frequency', 'monthly'),
            kwargs.get('security_deposit'),
            kwargs.get('renewal_options'),
            kwargs.get('special_provisions'),
            kwargs.get('status', 'active')
        ))
        self.conn.commit()

        lease_id = cursor.lastrowid

        # Create expiration alert if end_date is provided
        if kwargs.get('end_date'):
            self._create_expiration_alerts(lease_id, kwargs['end_date'])

        return lease_id

    def get_lease(self, lease_id: int) -> Optional[Dict]:
        """Get lease by ID with tenant information."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT l.*, t.tenant_name, t.business_type, t.contact_email
            FROM leases l
            JOIN tenants t ON l.tenant_id = t.tenant_id
            WHERE l.lease_id = ?
        """, (lease_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_leases_by_tenant(self, tenant_name: str) -> List[Dict]:
        """Get all leases for a specific tenant."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT l.*, t.tenant_name
            FROM leases l
            JOIN tenants t ON l.tenant_id = t.tenant_id
            WHERE t.tenant_name = ?
            ORDER BY l.start_date DESC
        """, (tenant_name,))
        return [dict(row) for row in cursor.fetchall()]

    def get_all_leases(self, status: str = None) -> List[Dict]:
        """Get all leases, optionally filtered by status."""
        cursor = self.conn.cursor()
        if status:
            cursor.execute("""
                SELECT l.*, t.tenant_name
                FROM leases l
                JOIN tenants t ON l.tenant_id = t.tenant_id
                WHERE l.status = ?
                ORDER BY l.end_date
            """, (status,))
        else:
            cursor.execute("""
                SELECT l.*, t.tenant_name
                FROM leases l
                JOIN tenants t ON l.tenant_id = t.tenant_id
                ORDER BY l.end_date
            """)
        return [dict(row) for row in cursor.fetchall()]

    def update_lease(self, lease_id: int, **kwargs) -> bool:
        """Update lease information."""
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        set_clause += ", updated_at = CURRENT_TIMESTAMP"
        values = list(kwargs.values()) + [lease_id]

        cursor = self.conn.cursor()
        cursor.execute(f"""
            UPDATE leases
            SET {set_clause}
            WHERE lease_id = ?
        """, values)
        self.conn.commit()
        return cursor.rowcount > 0

    # ==================== Expiration Tracking ====================

    def _create_expiration_alerts(self, lease_id: int, end_date: str):
        """Create alerts for lease expiration at 90, 60, and 30 days."""
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        alert_periods = [90, 60, 30]
        cursor = self.conn.cursor()

        for days in alert_periods:
            alert_date = end_dt - timedelta(days=days)
            cursor.execute("""
                INSERT INTO lease_alerts (lease_id, alert_type, alert_date, days_notice, message)
                VALUES (?, 'expiration', ?, ?, ?)
            """, (
                lease_id,
                alert_date.strftime("%Y-%m-%d"),
                days,
                f"Lease expires in {days} days"
            ))
        self.conn.commit()

    def get_active_alerts(self, days_ahead: int = 0) -> List[Dict]:
        """Get active alerts for the next N days."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT a.*, l.lease_file, t.tenant_name, l.end_date
            FROM lease_alerts a
            JOIN leases l ON a.lease_id = l.lease_id
            JOIN tenants t ON l.tenant_id = t.tenant_id
            WHERE a.status = 'pending'
            AND a.alert_date <= date('now', '+' || ? || ' days')
            ORDER BY a.alert_date
        """, (days_ahead,))
        return [dict(row) for row in cursor.fetchall()]

    def get_expiring_leases(self, days_ahead: int = 90) -> List[Dict]:
        """Get leases expiring within the next N days."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT l.*, t.tenant_name,
                   julianday(l.end_date) - julianday('now') as days_until_expiration
            FROM leases l
            JOIN tenants t ON l.tenant_id = t.tenant_id
            WHERE l.status = 'active'
            AND l.end_date IS NOT NULL
            AND julianday(l.end_date) - julianday('now') <= ?
            AND julianday(l.end_date) - julianday('now') >= 0
            ORDER BY l.end_date
        """, (days_ahead,))
        return [dict(row) for row in cursor.fetchall()]

    def dismiss_alert(self, alert_id: int):
        """Dismiss an alert."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE lease_alerts
            SET status = 'dismissed', dismissed_at = CURRENT_TIMESTAMP
            WHERE alert_id = ?
        """, (alert_id,))
        self.conn.commit()

    # ==================== Financial Analytics ====================

    def add_financial_record(self, lease_id: int, record_date: str,
                            record_type: str, amount: float, description: str = None):
        """Add a financial record (rent payment, fee, adjustment, etc.)."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO financial_records (lease_id, record_date, record_type, amount, description)
            VALUES (?, ?, ?, ?, ?)
        """, (lease_id, record_date, record_type, amount, description))
        self.conn.commit()
        return cursor.lastrowid

    def get_financial_summary(self) -> Dict[str, Any]:
        """Get overall financial summary."""
        cursor = self.conn.cursor()

        # Total active leases count
        cursor.execute("SELECT COUNT(*) FROM leases WHERE status = 'active'")
        active_leases = cursor.fetchone()[0]

        # Total monthly revenue (base rent only)
        cursor.execute("""
            SELECT SUM(base_rent) FROM leases
            WHERE status = 'active' AND rent_frequency = 'monthly'
        """)
        monthly_revenue = cursor.fetchone()[0] or 0

        # Total square footage leased
        cursor.execute("""
            SELECT SUM(square_footage) FROM leases WHERE status = 'active'
        """)
        total_sqft = cursor.fetchone()[0] or 0

        # Average rent per square foot
        avg_rent_per_sqft = (monthly_revenue / total_sqft) if total_sqft > 0 else 0

        # Expiring soon (next 90 days)
        expiring_soon = len(self.get_expiring_leases(90))

        return {
            'active_leases': active_leases,
            'monthly_revenue': round(monthly_revenue, 2),
            'annual_revenue': round(monthly_revenue * 12, 2),
            'total_square_footage': round(total_sqft, 2),
            'avg_rent_per_sqft': round(avg_rent_per_sqft, 2),
            'expiring_within_90_days': expiring_soon
        }

    def get_revenue_by_tenant(self) -> List[Dict]:
        """Get revenue breakdown by tenant."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                t.tenant_name,
                l.base_rent as monthly_rent,
                l.base_rent * 12 as annual_rent,
                l.square_footage,
                CASE
                    WHEN l.square_footage > 0 THEN l.base_rent / l.square_footage
                    ELSE 0
                END as rent_per_sqft
            FROM leases l
            JOIN tenants t ON l.tenant_id = t.tenant_id
            WHERE l.status = 'active' AND l.base_rent IS NOT NULL
            ORDER BY l.base_rent DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_occupancy_rate(self, total_property_sqft: float) -> Dict[str, float]:
        """Calculate occupancy rate."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT SUM(square_footage) FROM leases WHERE status = 'active'
        """)
        leased_sqft = cursor.fetchone()[0] or 0

        occupancy_rate = (leased_sqft / total_property_sqft * 100) if total_property_sqft > 0 else 0

        return {
            'total_property_sqft': total_property_sqft,
            'leased_sqft': leased_sqft,
            'available_sqft': total_property_sqft - leased_sqft,
            'occupancy_rate': round(occupancy_rate, 2)
        }

    # ==================== Query Audit Log ====================

    def log_query(self, query_text: str, tenant_filter: str = None,
                  result_count: int = 0, response_time_ms: float = 0):
        """Log a query for analytics."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO query_log (query_text, tenant_filter, result_count, response_time_ms)
            VALUES (?, ?, ?, ?)
        """, (query_text, tenant_filter, result_count, response_time_ms))
        self.conn.commit()

    def get_popular_queries(self, limit: int = 10) -> List[Dict]:
        """Get most common queries."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT query_text, COUNT(*) as query_count,
                   AVG(response_time_ms) as avg_response_time
            FROM query_log
            GROUP BY query_text
            ORDER BY query_count DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    # ==================== Utility Methods ====================

    def execute_custom_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute a custom SQL query."""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
