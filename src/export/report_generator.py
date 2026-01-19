"""
Report generation and export functionality.

Supports:
- PDF reports with financial summaries
- CSV exports of lease data
- Excel workbooks with multiple sheets
- Portfolio analytics reports
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import csv
import io


class ReportGenerator:
    """Generate reports and export data in various formats."""

    def __init__(self, sql_store, analytics=None):
        """
        Initialize report generator.

        Args:
            sql_store: SQLStore instance
            analytics: LeaseAnalytics instance (optional)
        """
        self.db = sql_store
        self.analytics = analytics

    # ==================== CSV Export ====================

    def export_leases_csv(self, status: str = None) -> str:
        """
        Export leases to CSV format.

        Args:
            status: Filter by status (optional)

        Returns:
            CSV data as string
        """
        leases = self.db.get_all_leases(status=status)

        if not leases:
            return ""

        # Define columns
        columns = [
            'lease_id', 'tenant_name', 'lease_file', 'start_date', 'end_date',
            'term_months', 'square_footage', 'base_rent', 'rent_frequency',
            'status', 'created_at'
        ]

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=columns, extrasaction='ignore')

        writer.writeheader()
        writer.writerows(leases)

        return output.getvalue()

    def export_financial_summary_csv(self) -> str:
        """Export financial summary to CSV."""
        revenue_data = self.db.get_revenue_by_tenant()

        if not revenue_data:
            return ""

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=revenue_data[0].keys())

        writer.writeheader()
        writer.writerows(revenue_data)

        return output.getvalue()

    def export_expiring_leases_csv(self, days_ahead: int = 90) -> str:
        """Export expiring leases to CSV."""
        expiring = self.db.get_expiring_leases(days_ahead=days_ahead)

        if not expiring:
            return ""

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=expiring[0].keys())

        writer.writeheader()
        writer.writerows(expiring)

        return output.getvalue()

    # ==================== Excel Export ====================

    def export_portfolio_excel(self, output_path: str):
        """
        Export comprehensive portfolio data to Excel workbook.

        Creates multiple sheets:
        - Leases: All lease data
        - Financial Summary: Revenue by tenant
        - Expiring: Leases expiring soon
        - Alerts: Active alerts
        """
        try:
            import pandas as pd

            # Create Excel writer
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:

                # Sheet 1: All Leases
                leases = self.db.get_all_leases()
                if leases:
                    df_leases = pd.DataFrame(leases)
                    df_leases.to_excel(writer, sheet_name='Leases', index=False)

                # Sheet 2: Financial Summary
                revenue = self.db.get_revenue_by_tenant()
                if revenue:
                    df_revenue = pd.DataFrame(revenue)
                    df_revenue.to_excel(writer, sheet_name='Revenue by Tenant', index=False)

                # Sheet 3: Expiring Leases
                expiring = self.db.get_expiring_leases(90)
                if expiring:
                    df_expiring = pd.DataFrame(expiring)
                    df_expiring.to_excel(writer, sheet_name='Expiring Soon', index=False)

                # Sheet 4: Active Alerts
                alerts = self.db.get_active_alerts(30)
                if alerts:
                    df_alerts = pd.DataFrame(alerts)
                    df_alerts.to_excel(writer, sheet_name='Active Alerts', index=False)

                # Sheet 5: Portfolio Summary
                summary = self.db.get_financial_summary()
                df_summary = pd.DataFrame([summary])
                df_summary.to_excel(writer, sheet_name='Portfolio Summary', index=False)

            return True

        except ImportError:
            raise ImportError("pandas and openpyxl required for Excel export. Install with: pip install pandas openpyxl")

    # ==================== PDF Export ====================

    def export_portfolio_pdf(self, output_path: str):
        """
        Generate comprehensive PDF report of portfolio.

        Includes:
        - Financial summary
        - Top tenants
        - Expiring leases
        - Portfolio health metrics
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.enums import TA_CENTER, TA_LEFT

            # Create PDF
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2C3E50'),
                spaceAfter=30,
                alignment=TA_CENTER
            )

            title = Paragraph("Medley Lease Portfolio Report", title_style)
            story.append(title)

            # Report date
            date_text = f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
            story.append(Paragraph(date_text, styles['Normal']))
            story.append(Spacer(1, 0.3 * inch))

            # Financial Summary Section
            story.append(Paragraph("Financial Summary", styles['Heading2']))
            summary = self.db.get_financial_summary()

            summary_data = [
                ['Metric', 'Value'],
                ['Active Leases', str(summary['active_leases'])],
                ['Monthly Revenue', f"${summary['monthly_revenue']:,.2f}"],
                ['Annual Revenue', f"${summary['annual_revenue']:,.2f}"],
                ['Total Square Footage', f"{summary['total_square_footage']:,.0f} sq ft"],
                ['Avg Rent per Sq Ft', f"${summary['avg_rent_per_sqft']:.2f}"],
                ['Expiring in 90 Days', str(summary['expiring_within_90_days'])]
            ]

            summary_table = Table(summary_data, colWidths=[3 * inch, 2.5 * inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(summary_table)
            story.append(Spacer(1, 0.5 * inch))

            # Top Tenants Section
            story.append(Paragraph("Top Tenants by Revenue", styles['Heading2']))
            revenue_data = self.db.get_revenue_by_tenant()[:10]  # Top 10

            if revenue_data:
                tenant_data = [['Tenant', 'Monthly Rent', 'Annual Rent', 'Sq Ft']]

                for tenant in revenue_data:
                    tenant_data.append([
                        tenant['tenant_name'],
                        f"${tenant['monthly_rent']:,.2f}",
                        f"${tenant['annual_rent']:,.2f}",
                        f"{tenant.get('square_footage', 0):,.0f}" if tenant.get('square_footage') else 'N/A'
                    ])

                tenant_table = Table(tenant_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch, 1 * inch])
                tenant_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ECC71')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT')
                ]))

                story.append(tenant_table)
                story.append(Spacer(1, 0.5 * inch))

            # Expiring Leases Section
            story.append(Paragraph("Leases Expiring in Next 90 Days", styles['Heading2']))
            expiring = self.db.get_expiring_leases(90)

            if expiring:
                expiring_data = [['Tenant', 'Expiration Date', 'Days Until', 'Monthly Rent']]

                for lease in expiring:
                    expiring_data.append([
                        lease['tenant_name'],
                        lease['end_date'],
                        f"{int(lease['days_until_expiration'])} days",
                        f"${lease.get('base_rent', 0):,.2f}" if lease.get('base_rent') else 'N/A'
                    ])

                expiring_table = Table(expiring_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
                expiring_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.Color(1, 0.9, 0.9)),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ALIGN', (2, 1), (-1, -1), 'RIGHT')
                ]))

                story.append(expiring_table)
            else:
                story.append(Paragraph("No leases expiring in the next 90 days.", styles['Normal']))

            story.append(Spacer(1, 0.5 * inch))

            # Portfolio Health (if analytics available)
            if self.analytics:
                story.append(PageBreak())
                story.append(Paragraph("Portfolio Health Analysis", styles['Heading2']))

                health = self.analytics.calculate_portfolio_health_score()

                health_text = f"""
                <b>Health Score:</b> {health['health_score']}/100 ({health['health_status'].upper()})<br/>
                <br/>
                <b>Recommendations:</b><br/>
                """

                for rec in health['recommendations']:
                    health_text += f"• {rec}<br/>"

                story.append(Paragraph(health_text, styles['Normal']))
                story.append(Spacer(1, 0.3 * inch))

                # Risk Assessment
                risk = self.analytics.assess_portfolio_risk()
                story.append(Paragraph("Risk Assessment", styles['Heading3']))

                risk_text = f"<b>Risk Level:</b> {risk['risk_level'].upper()}<br/><br/>"

                if risk['risks']:
                    risk_text += "<b>Identified Risks:</b><br/>"
                    for r in risk['risks']:
                        risk_text += f"• [{r['severity'].upper()}] {r['description']}<br/>"

                story.append(Paragraph(risk_text, styles['Normal']))

            # Build PDF
            doc.build(story)
            return True

        except ImportError:
            raise ImportError("reportlab required for PDF export. Install with: pip install reportlab")

    # ==================== Text Report ====================

    def generate_text_report(self) -> str:
        """Generate simple text report."""
        lines = []
        lines.append("=" * 60)
        lines.append("MEDLEY LEASE PORTFOLIO REPORT")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)
        lines.append("")

        # Financial Summary
        summary = self.db.get_financial_summary()
        lines.append("FINANCIAL SUMMARY")
        lines.append("-" * 60)
        lines.append(f"Active Leases:        {summary['active_leases']}")
        lines.append(f"Monthly Revenue:      ${summary['monthly_revenue']:,.2f}")
        lines.append(f"Annual Revenue:       ${summary['annual_revenue']:,.2f}")
        lines.append(f"Total Square Footage: {summary['total_square_footage']:,.0f} sq ft")
        lines.append(f"Avg Rent per Sq Ft:   ${summary['avg_rent_per_sqft']:.2f}")
        lines.append("")

        # Top Tenants
        lines.append("TOP 5 TENANTS BY REVENUE")
        lines.append("-" * 60)
        revenue_data = self.db.get_revenue_by_tenant()[:5]

        for i, tenant in enumerate(revenue_data, 1):
            lines.append(f"{i}. {tenant['tenant_name']:30} ${tenant['annual_rent']:>10,.2f}/year")

        lines.append("")

        # Expiring Leases
        expiring = self.db.get_expiring_leases(90)
        lines.append(f"LEASES EXPIRING IN NEXT 90 DAYS ({len(expiring)})")
        lines.append("-" * 60)

        for lease in expiring:
            days = int(lease['days_until_expiration'])
            lines.append(f"{lease['tenant_name']:30} {lease['end_date']} ({days} days)")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)


def export_to_file(content: str, output_path: str, format: str = 'txt'):
    """
    Export content to file.

    Args:
        content: Content to export
        output_path: Output file path
        format: File format (txt, csv)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return str(output_path)
