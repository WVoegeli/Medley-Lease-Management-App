"""
Financial Analyst Agent - Revenue analysis, projections, and financial reporting.

Handles queries like:
- "What's the total monthly rent?"
- "Run revenue projections"
- "Compare tenant financials"
- "Generate financial report"
"""

import re
from typing import List, Dict, Any, Optional, Generator

from src.agents.base_agent import BaseAgent, AgentResponse, AgentContext, AgentMode


class FinancialAnalystAgent(BaseAgent):
    """
    Agent specialized in financial analysis and reporting.

    Capabilities:
    - Quick metrics (single-turn): total rent, average PSF, occupancy
    - Full analysis (multi-step): projections, benchmarking, trends
    - Tenant comparison and benchmarking
    - Report generation (Excel/PDF)
    """

    # Patterns that strongly indicate financial queries
    FINANCIAL_KEYWORDS = [
        "revenue", "rent", "income", "financial", "money",
        "dollar", "cost", "expense", "profit", "noi",
        "projection", "forecast", "budget", "psf", "per square foot",
        "occupancy", "vacancy", "cam", "total", "average", "sum",
        "compare", "benchmark", "analysis", "report"
    ]

    # Patterns for multi-step workflows
    FULL_ANALYSIS_PATTERNS = [
        r"full\s+(financial\s+)?analysis",
        r"complete\s+report",
        r"generate\s+report",
        r"quarterly\s+analysis",
        r"annual\s+review",
        r"run\s+analysis",
        r"comprehensive\s+analysis"
    ]

    @property
    def name(self) -> str:
        return "FinancialAnalystAgent"

    @property
    def description(self) -> str:
        return "Analyzes financial metrics, revenue projections, and generates reports"

    @property
    def trigger_patterns(self) -> List[str]:
        return [
            "total rent", "monthly rent", "annual rent",
            "revenue", "projection", "forecast",
            "financial analysis", "rent roll",
            "compare", "benchmark",
            "average rent", "occupancy",
            "generate report", "export"
        ]

    def can_handle(self, message: str, context: AgentContext) -> float:
        """
        Determine confidence for handling this message.

        High confidence for:
        - Direct financial questions (total rent, revenue, etc.)
        - Report generation requests
        - Tenant comparisons with financial focus
        """
        message_lower = message.lower()
        confidence = 0.0

        # Check for financial keywords
        keyword_matches = sum(
            1 for kw in self.FINANCIAL_KEYWORDS
            if kw in message_lower
        )
        if keyword_matches > 0:
            confidence += min(0.4, keyword_matches * 0.15)

        # Check trigger patterns
        if self._quick_pattern_match(message):
            confidence += 0.3

        # Check for full analysis patterns
        for pattern in self.FULL_ANALYSIS_PATTERNS:
            if re.search(pattern, message_lower):
                confidence += 0.2
                break

        # Check for specific numeric/financial requests
        if re.search(r'\b(how much|what is|calculate|compute)\b.*\b(rent|revenue|cost|income)\b', message_lower):
            confidence += 0.25

        # Check for comparison requests
        if re.search(r'\b(compare|versus|vs|benchmark)\b', message_lower):
            confidence += 0.15

        # Check for report generation
        if re.search(r'\b(report|export|excel|pdf)\b', message_lower):
            confidence += 0.2

        return min(1.0, confidence)

    def execute(self, message: str, context: AgentContext) -> AgentResponse:
        """Execute financial analysis based on the message."""
        message_lower = message.lower()

        try:
            # Determine the type of analysis requested
            if self._is_total_rent_query(message_lower):
                return self._handle_total_rent()

            elif self._is_projection_query(message_lower):
                return self._handle_projections()

            elif self._is_comparison_query(message_lower):
                tenants = self._extract_tenant_names(message, context)
                return self._handle_comparison(tenants)

            elif self._is_benchmark_query(message_lower):
                return self._handle_benchmarks()

            elif self._is_health_query(message_lower):
                return self._handle_portfolio_health()

            elif self._is_report_query(message_lower):
                return self._handle_report_request(message_lower)

            else:
                # General financial query - provide summary
                return self._handle_general_financial()

        except Exception as e:
            return AgentResponse(
                message=f"Error performing financial analysis: {str(e)}",
                is_complete=True,
                agent_name=self.name
            )

    def execute_guided(
        self,
        message: str,
        context: AgentContext
    ) -> Generator[AgentResponse, Optional[str], None]:
        """
        Multi-step guided workflow for comprehensive analysis.

        Steps:
        1. Confirm scope of analysis
        2. Generate analysis
        3. Offer report export
        """
        message_lower = message.lower()

        # Step 1: Confirm scope
        yield AgentResponse(
            message="I'll run a comprehensive financial analysis. This includes:\n"
                    "- Revenue summary and trends\n"
                    "- 12-month projections\n"
                    "- Tenant benchmarking\n"
                    "- Portfolio health score\n\n"
                    "Proceed with full analysis?",
            requires_confirmation=True,
            confirmation_prompt="Yes to proceed, or specify what to focus on",
            is_complete=False,
            mode=AgentMode.GUIDED,
            agent_name=self.name
        )

        # Wait for confirmation
        user_response = yield

        if user_response and user_response.lower() in ["no", "cancel", "stop"]:
            yield AgentResponse(
                message="Analysis cancelled.",
                is_complete=True,
                mode=AgentMode.GUIDED,
                agent_name=self.name
            )
            return

        # Step 2: Generate analysis
        try:
            analysis_data = self._generate_full_analysis()

            yield AgentResponse(
                message=self._format_full_analysis(analysis_data),
                data=analysis_data,
                requires_confirmation=True,
                confirmation_prompt="Export to Excel or PDF?",
                is_complete=False,
                mode=AgentMode.GUIDED,
                agent_name=self.name
            )

            # Wait for export decision
            export_response = yield

            if export_response and any(fmt in export_response.lower() for fmt in ["excel", "pdf", "yes"]):
                # Handle export
                export_format = "excel" if "excel" in export_response.lower() else "pdf"
                yield AgentResponse(
                    message=f"Report exported to reports/financial_analysis.{export_format}",
                    is_complete=True,
                    mode=AgentMode.GUIDED,
                    agent_name=self.name
                )
            else:
                yield AgentResponse(
                    message="Analysis complete. Let me know if you need anything else.",
                    is_complete=True,
                    mode=AgentMode.GUIDED,
                    agent_name=self.name
                )

        except Exception as e:
            yield AgentResponse(
                message=f"Error during analysis: {str(e)}",
                is_complete=True,
                mode=AgentMode.GUIDED,
                agent_name=self.name
            )

    # ============== Query Type Detection ==============

    def _is_total_rent_query(self, message: str) -> bool:
        """Check if asking for total/sum of rent."""
        patterns = [
            r"total\s+(monthly\s+)?rent",
            r"sum\s+of\s+rent",
            r"how much.*total",
            r"monthly\s+revenue",
            r"annual\s+rent",
            r"rent\s+roll"
        ]
        return any(re.search(p, message) for p in patterns)

    def _is_projection_query(self, message: str) -> bool:
        """Check if asking for projections/forecasts."""
        patterns = [
            r"project(ion)?s?",
            r"forecast",
            r"predict",
            r"future\s+revenue",
            r"next\s+(year|month|quarter)"
        ]
        return any(re.search(p, message) for p in patterns)

    def _is_comparison_query(self, message: str) -> bool:
        """Check if asking to compare tenants."""
        patterns = [
            r"compare",
            r"versus|vs\.?",
            r"difference\s+between",
            r"which\s+(tenant|one)\s+.*\s+(more|less|higher|lower)"
        ]
        return any(re.search(p, message) for p in patterns)

    def _is_benchmark_query(self, message: str) -> bool:
        """Check if asking for benchmarks."""
        patterns = [
            r"benchmark",
            r"average\s+(rent|psf)",
            r"median",
            r"ranking",
            r"top\s+\d+\s+tenant"
        ]
        return any(re.search(p, message) for p in patterns)

    def _is_health_query(self, message: str) -> bool:
        """Check if asking about portfolio health."""
        patterns = [
            r"portfolio\s+health",
            r"health\s+score",
            r"how.*portfolio.*doing"
        ]
        return any(re.search(p, message) for p in patterns)

    def _is_report_query(self, message: str) -> bool:
        """Check if asking for report generation."""
        patterns = [
            r"generate\s+report",
            r"export",
            r"create\s+.*\s+(report|excel|pdf)",
            r"download"
        ]
        return any(re.search(p, message) for p in patterns)

    # ============== Handler Methods ==============

    def _handle_total_rent(self) -> AgentResponse:
        """Handle total rent queries."""
        if self.sql_store is None:
            return self._no_database_response()

        try:
            # Get summary from database
            summary = self.sql_store.get_financial_summary()

            monthly = summary.get('total_monthly_rent', 0)
            annual = monthly * 12
            tenant_count = summary.get('tenant_count', 0)
            avg_psf = summary.get('average_psf', 0)

            message = (
                f"**Portfolio Rent Summary**\n\n"
                f"- **Monthly Rent:** ${monthly:,.2f}\n"
                f"- **Annual Rent:** ${annual:,.2f}\n"
                f"- **Active Tenants:** {tenant_count}\n"
                f"- **Average PSF:** ${avg_psf:.2f}\n"
            )

            return AgentResponse(
                message=message,
                data={
                    "monthly_rent": monthly,
                    "annual_rent": annual,
                    "tenant_count": tenant_count,
                    "average_psf": avg_psf
                },
                is_complete=True,
                agent_name=self.name
            )

        except Exception as e:
            return AgentResponse(
                message=f"Error calculating rent totals: {str(e)}",
                is_complete=True,
                agent_name=self.name
            )

    def _handle_projections(self) -> AgentResponse:
        """Handle revenue projection queries."""
        if self.sql_store is None:
            return self._no_database_response()

        try:
            from src.analytics.lease_analytics import LeaseAnalytics
            analytics = LeaseAnalytics(self.sql_store)

            projections = analytics.project_revenue(months_ahead=12)

            message = (
                f"**12-Month Revenue Projections**\n\n"
                f"- **Current Monthly:** ${projections.get('current_monthly', 0):,.2f}\n"
                f"- **Projected Monthly (12mo):** ${projections.get('projected_monthly', 0):,.2f}\n"
                f"- **Trend:** {projections.get('trend', 'stable')}\n"
                f"- **Revenue at Risk:** ${projections.get('revenue_at_risk', 0):,.2f}\n"
            )

            if projections.get('expiring_leases'):
                message += f"\n**Leases Expiring:** {len(projections['expiring_leases'])}\n"

            return AgentResponse(
                message=message,
                data=projections,
                is_complete=True,
                agent_name=self.name
            )

        except Exception as e:
            return AgentResponse(
                message=f"Error generating projections: {str(e)}",
                is_complete=True,
                agent_name=self.name
            )

    def _handle_comparison(self, tenant_names: List[str]) -> AgentResponse:
        """Handle tenant comparison queries."""
        if self.sql_store is None:
            return self._no_database_response()

        if len(tenant_names) < 2:
            return AgentResponse(
                message="Please specify at least two tenants to compare. "
                        "For example: 'Compare Summit Coffee and Medley Books'",
                is_complete=True,
                agent_name=self.name
            )

        try:
            from src.analytics.lease_analytics import LeaseAnalytics
            analytics = LeaseAnalytics(self.sql_store)

            comparison = analytics.compare_tenants(tenant_names)

            message = f"**Tenant Comparison**\n\n"
            for tenant in comparison.get('tenants', []):
                message += (
                    f"**{tenant['name']}**\n"
                    f"  - Rent/PSF: ${tenant.get('rent_psf', 0):.2f}\n"
                    f"  - Monthly Rent: ${tenant.get('monthly_rent', 0):,.2f}\n"
                    f"  - Square Feet: {tenant.get('square_feet', 0):,}\n\n"
                )

            return AgentResponse(
                message=message,
                data=comparison,
                is_complete=True,
                agent_name=self.name
            )

        except Exception as e:
            return AgentResponse(
                message=f"Error comparing tenants: {str(e)}",
                is_complete=True,
                agent_name=self.name
            )

    def _handle_benchmarks(self) -> AgentResponse:
        """Handle benchmark queries."""
        if self.sql_store is None:
            return self._no_database_response()

        try:
            from src.analytics.lease_analytics import LeaseAnalytics
            analytics = LeaseAnalytics(self.sql_store)

            benchmarks = analytics.get_tenant_benchmarks()

            message = (
                f"**Portfolio Benchmarks**\n\n"
                f"- **Median Rent/PSF:** ${benchmarks.get('median_psf', 0):.2f}\n"
                f"- **Average Rent/PSF:** ${benchmarks.get('average_psf', 0):.2f}\n"
                f"- **Highest Rent/PSF:** ${benchmarks.get('max_psf', 0):.2f}\n"
                f"- **Lowest Rent/PSF:** ${benchmarks.get('min_psf', 0):.2f}\n"
            )

            if benchmarks.get('top_tenants'):
                message += "\n**Top Tenants by Rent:**\n"
                for i, tenant in enumerate(benchmarks['top_tenants'][:5], 1):
                    message += f"  {i}. {tenant['name']} - ${tenant.get('monthly_rent', 0):,.2f}/mo\n"

            return AgentResponse(
                message=message,
                data=benchmarks,
                is_complete=True,
                agent_name=self.name
            )

        except Exception as e:
            return AgentResponse(
                message=f"Error retrieving benchmarks: {str(e)}",
                is_complete=True,
                agent_name=self.name
            )

    def _handle_portfolio_health(self) -> AgentResponse:
        """Handle portfolio health queries."""
        if self.sql_store is None:
            return self._no_database_response()

        try:
            from src.analytics.lease_analytics import LeaseAnalytics
            analytics = LeaseAnalytics(self.sql_store)

            health = analytics.calculate_portfolio_health_score()

            score = health.get('health_score', 0)
            status = health.get('health_status', 'unknown')

            # Emoji based on score
            if score >= 80:
                emoji = "🟢"
            elif score >= 60:
                emoji = "🟡"
            else:
                emoji = "🔴"

            message = (
                f"**Portfolio Health Score**\n\n"
                f"{emoji} **Score:** {score}/100 ({status})\n\n"
            )

            if health.get('recommendations'):
                message += "**Recommendations:**\n"
                for rec in health['recommendations'][:3]:
                    message += f"- {rec}\n"

            return AgentResponse(
                message=message,
                data=health,
                is_complete=True,
                agent_name=self.name
            )

        except Exception as e:
            return AgentResponse(
                message=f"Error calculating health score: {str(e)}",
                is_complete=True,
                agent_name=self.name
            )

    def _handle_report_request(self, message: str) -> AgentResponse:
        """Handle report generation requests."""
        return AgentResponse(
            message="I can generate financial reports in Excel or PDF format. "
                    "Would you like me to run a full analysis first, then export?",
            requires_confirmation=True,
            confirmation_prompt="Run full analysis and export?",
            is_complete=False,
            agent_name=self.name
        )

    def _handle_general_financial(self) -> AgentResponse:
        """Handle general financial queries with summary."""
        if self.sql_store is None:
            return self._no_database_response()

        try:
            summary = self.sql_store.get_financial_summary()

            message = (
                f"**Financial Overview**\n\n"
                f"I can help with:\n"
                f"- **Total rent:** ${summary.get('total_monthly_rent', 0):,.2f}/month\n"
                f"- Revenue projections\n"
                f"- Tenant comparisons\n"
                f"- Benchmarking analysis\n"
                f"- Portfolio health scores\n"
                f"- Report generation\n\n"
                f"What would you like to know more about?"
            )

            return AgentResponse(
                message=message,
                is_complete=True,
                agent_name=self.name
            )

        except Exception as e:
            return AgentResponse(
                message=f"Error retrieving financial data: {str(e)}",
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

    def _extract_tenant_names(self, message: str, context: AgentContext) -> List[str]:
        """Extract tenant names from message or context."""
        # This would ideally use NER or match against known tenants
        # For now, simple extraction based on common patterns
        tenants = []

        # Check context for mentioned tenants
        if context.metadata.get('mentioned_tenants'):
            tenants.extend(context.metadata['mentioned_tenants'])

        # Try to extract from message using patterns
        # Pattern: "compare X and Y" or "X vs Y"
        match = re.search(r'compare\s+([^,]+?)\s+(?:and|vs\.?|versus)\s+([^,]+?)(?:\s|$)', message.lower())
        if match:
            tenants.append(match.group(1).strip())
            tenants.append(match.group(2).strip())

        return tenants

    def _generate_full_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive financial analysis."""
        if self.sql_store is None:
            return {}

        from src.analytics.lease_analytics import LeaseAnalytics
        analytics = LeaseAnalytics(self.sql_store)

        return {
            "summary": self.sql_store.get_financial_summary(),
            "projections": analytics.project_revenue(months_ahead=12),
            "benchmarks": analytics.get_tenant_benchmarks(),
            "health": analytics.calculate_portfolio_health_score(),
            "opportunities": analytics.get_optimization_opportunities()
        }

    def _format_full_analysis(self, data: Dict[str, Any]) -> str:
        """Format full analysis data as readable message."""
        summary = data.get('summary', {})
        projections = data.get('projections', {})
        health = data.get('health', {})

        score = health.get('health_score', 0)
        if score >= 80:
            emoji = "🟢"
        elif score >= 60:
            emoji = "🟡"
        else:
            emoji = "🔴"

        return (
            f"**Comprehensive Financial Analysis**\n\n"
            f"**Current Portfolio:**\n"
            f"- Monthly Revenue: ${summary.get('total_monthly_rent', 0):,.2f}\n"
            f"- Active Tenants: {summary.get('tenant_count', 0)}\n"
            f"- Average PSF: ${summary.get('average_psf', 0):.2f}\n\n"
            f"**12-Month Projections:**\n"
            f"- Trend: {projections.get('trend', 'stable')}\n"
            f"- Revenue at Risk: ${projections.get('revenue_at_risk', 0):,.2f}\n\n"
            f"**Portfolio Health:**\n"
            f"{emoji} Score: {score}/100 ({health.get('health_status', 'unknown')})\n"
        )
