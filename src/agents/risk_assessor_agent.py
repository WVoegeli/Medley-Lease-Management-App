"""
Risk Assessor Agent - Portfolio risk analysis and health monitoring.

Handles queries like:
- "What are the risks?"
- "Check co-tenancy exposure"
- "Portfolio health check"
- "Expiring leases"
"""

import re
from typing import List, Dict, Any, Optional, Generator

from src.agents.base_agent import BaseAgent, AgentResponse, AgentContext, AgentMode


class RiskAssessorAgent(BaseAgent):
    """
    Agent specialized in portfolio risk assessment.

    Capabilities:
    - Co-tenancy clause analysis
    - Tenant concentration risk
    - Expiration clustering detection
    - Portfolio health scoring (0-100)
    - Mitigation recommendations
    """

    # Risk-related keywords
    RISK_KEYWORDS = [
        "risk", "danger", "concern", "problem", "issue",
        "exposure", "vulnerability", "threat",
        "co-tenancy", "cotenancy", "anchor",
        "expir", "expiration", "expire",
        "concentration", "diversification",
        "health", "score", "assessment"
    ]

    # Patterns for full assessment
    FULL_ASSESSMENT_PATTERNS = [
        r"full\s+(risk\s+)?assessment",
        r"complete\s+risk",
        r"comprehensive\s+risk",
        r"all\s+risks?",
        r"risk\s+report"
    ]

    @property
    def name(self) -> str:
        return "RiskAssessorAgent"

    @property
    def description(self) -> str:
        return "Assesses portfolio risks, co-tenancy exposure, and generates mitigation recommendations"

    @property
    def trigger_patterns(self) -> List[str]:
        return [
            "risk", "risks", "risky",
            "co-tenancy", "cotenancy",
            "exposure", "vulnerable",
            "expiring", "expiration",
            "health check", "health score",
            "portfolio health",
            "concentration",
            "what could go wrong"
        ]

    def can_handle(self, message: str, context: AgentContext) -> float:
        """
        Determine confidence for handling this message.

        High confidence for:
        - Risk-related questions
        - Co-tenancy queries
        - Expiration concerns
        - Portfolio health requests
        """
        message_lower = message.lower()
        confidence = 0.0

        # Check for risk keywords
        keyword_matches = sum(
            1 for kw in self.RISK_KEYWORDS
            if kw in message_lower
        )
        if keyword_matches > 0:
            confidence += min(0.5, keyword_matches * 0.15)

        # Check trigger patterns
        if self._quick_pattern_match(message):
            confidence += 0.3

        # Check for full assessment patterns
        for pattern in self.FULL_ASSESSMENT_PATTERNS:
            if re.search(pattern, message_lower):
                confidence += 0.2
                break

        # Specific risk-related questions
        if re.search(r'\b(what|any|are there)\b.*\brisk', message_lower):
            confidence += 0.3

        # Co-tenancy specific
        if re.search(r'co-?tenancy|anchor\s+tenant', message_lower):
            confidence += 0.25

        # Expiration specific
        if re.search(r'expir(ing|ation|e)|due\s+soon|coming\s+up', message_lower):
            confidence += 0.2

        return min(1.0, confidence)

    def execute(self, message: str, context: AgentContext) -> AgentResponse:
        """Execute risk assessment based on the message."""
        message_lower = message.lower()

        try:
            # Determine the type of risk query
            if self._is_cotenancy_query(message_lower):
                return self._handle_cotenancy()

            elif self._is_expiration_query(message_lower):
                return self._handle_expirations()

            elif self._is_concentration_query(message_lower):
                return self._handle_concentration()

            elif self._is_health_query(message_lower):
                return self._handle_portfolio_health()

            elif self._is_full_assessment(message_lower):
                return self._handle_full_assessment()

            else:
                # General risk query - provide overview
                return self._handle_general_risk()

        except Exception as e:
            return AgentResponse(
                message=f"Error performing risk assessment: {str(e)}",
                is_complete=True,
                agent_name=self.name
            )

    def execute_guided(
        self,
        message: str,
        context: AgentContext
    ) -> Generator[AgentResponse, Optional[str], None]:
        """
        Multi-step guided workflow for comprehensive risk assessment.

        Steps:
        1. Run all risk checks
        2. Display risk matrix
        3. Offer mitigation recommendations
        """
        # Step 1: Announce analysis
        yield AgentResponse(
            message="I'll perform a comprehensive portfolio risk assessment, including:\n"
                    "- Co-tenancy clause exposure\n"
                    "- Tenant concentration analysis\n"
                    "- Expiration clustering\n"
                    "- Portfolio health scoring\n\n"
                    "This will analyze all active leases. Proceed?",
            requires_confirmation=True,
            confirmation_prompt="Yes to proceed",
            is_complete=False,
            mode=AgentMode.GUIDED,
            agent_name=self.name
        )

        # Wait for confirmation
        user_response = yield

        if user_response and user_response.lower() in ["no", "cancel", "stop"]:
            yield AgentResponse(
                message="Assessment cancelled.",
                is_complete=True,
                mode=AgentMode.GUIDED,
                agent_name=self.name
            )
            return

        # Step 2: Run full assessment
        try:
            assessment = self._generate_full_assessment()

            yield AgentResponse(
                message=self._format_risk_matrix(assessment),
                data=assessment,
                requires_confirmation=True,
                confirmation_prompt="Generate mitigation recommendations?",
                is_complete=False,
                mode=AgentMode.GUIDED,
                agent_name=self.name
            )

            # Wait for recommendation request
            rec_response = yield

            if rec_response and rec_response.lower() in ["yes", "y", "sure", "ok"]:
                recommendations = self._generate_recommendations(assessment)
                yield AgentResponse(
                    message=recommendations,
                    is_complete=True,
                    mode=AgentMode.GUIDED,
                    agent_name=self.name
                )
            else:
                yield AgentResponse(
                    message="Assessment complete. Let me know if you need recommendations later.",
                    is_complete=True,
                    mode=AgentMode.GUIDED,
                    agent_name=self.name
                )

        except Exception as e:
            yield AgentResponse(
                message=f"Error during assessment: {str(e)}",
                is_complete=True,
                mode=AgentMode.GUIDED,
                agent_name=self.name
            )

    # ============== Query Type Detection ==============

    def _is_cotenancy_query(self, message: str) -> bool:
        """Check if asking about co-tenancy."""
        patterns = [
            r"co-?tenancy",
            r"anchor\s+tenant",
            r"tenant\s+dependency",
            r"if\s+.+\s+leaves"
        ]
        return any(re.search(p, message) for p in patterns)

    def _is_expiration_query(self, message: str) -> bool:
        """Check if asking about expirations."""
        patterns = [
            r"expir(ing|ation|e)",
            r"due\s+soon",
            r"coming\s+up",
            r"ending\s+soon",
            r"lease\s+end",
            r"when.*end"
        ]
        return any(re.search(p, message) for p in patterns)

    def _is_concentration_query(self, message: str) -> bool:
        """Check if asking about concentration."""
        patterns = [
            r"concentration",
            r"diversif",
            r"too\s+much.*one",
            r"reliance",
            r"depend.*on\s+one"
        ]
        return any(re.search(p, message) for p in patterns)

    def _is_health_query(self, message: str) -> bool:
        """Check if asking about portfolio health."""
        patterns = [
            r"health\s+(check|score)",
            r"portfolio\s+health",
            r"how.*portfolio",
            r"overall\s+status"
        ]
        return any(re.search(p, message) for p in patterns)

    def _is_full_assessment(self, message: str) -> bool:
        """Check if asking for full assessment."""
        return any(re.search(p, message) for p in self.FULL_ASSESSMENT_PATTERNS)

    # ============== Handler Methods ==============

    def _handle_cotenancy(self) -> AgentResponse:
        """Handle co-tenancy risk queries."""
        if self.sql_store is None:
            return self._no_database_response()

        try:
            from src.analytics.lease_analytics import LeaseAnalytics
            analytics = LeaseAnalytics(self.sql_store)

            risk_data = analytics.assess_portfolio_risk()
            cotenancy_risks = [
                r for r in risk_data.get('risks', [])
                if 'co-tenancy' in r.get('type', '').lower()
                or 'anchor' in r.get('description', '').lower()
            ]

            if not cotenancy_risks:
                message = (
                    "**Co-Tenancy Risk Assessment**\n\n"
                    "🟢 No significant co-tenancy risks detected.\n\n"
                    "No active leases have triggered co-tenancy clause concerns."
                )
            else:
                message = "**Co-Tenancy Risk Assessment**\n\n"
                for risk in cotenancy_risks:
                    severity = risk.get('severity', 'medium')
                    emoji = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🟢"
                    message += f"{emoji} **{severity.upper()}:** {risk.get('description', 'Unknown risk')}\n"

                exposure = sum(r.get('exposure', 0) for r in cotenancy_risks)
                if exposure > 0:
                    message += f"\n**Total Revenue at Risk:** ${exposure:,.2f}/month\n"

            return AgentResponse(
                message=message,
                data={"cotenancy_risks": cotenancy_risks},
                is_complete=True,
                agent_name=self.name
            )

        except Exception as e:
            return AgentResponse(
                message=f"Error assessing co-tenancy risks: {str(e)}",
                is_complete=True,
                agent_name=self.name
            )

    def _handle_expirations(self) -> AgentResponse:
        """Handle expiration risk queries."""
        if self.sql_store is None:
            return self._no_database_response()

        try:
            expiring_30 = self.sql_store.get_expiring_leases(days_ahead=30)
            expiring_60 = self.sql_store.get_expiring_leases(days_ahead=60)
            expiring_90 = self.sql_store.get_expiring_leases(days_ahead=90)

            message = "**Lease Expiration Risk**\n\n"

            # Urgent (30 days)
            urgent = [l for l in expiring_30]
            if urgent:
                message += "🔴 **URGENT (Next 30 Days):**\n"
                for lease in urgent:
                    message += f"  - {lease.get('tenant_name', 'Unknown')}: {lease.get('days_until_expiration', '?')} days\n"
                message += "\n"
            else:
                message += "🟢 No leases expiring in next 30 days\n\n"

            # Warning (31-60 days)
            warning = [l for l in expiring_60 if l not in expiring_30]
            if warning:
                message += "🟡 **WARNING (31-60 Days):**\n"
                for lease in warning:
                    message += f"  - {lease.get('tenant_name', 'Unknown')}: {lease.get('days_until_expiration', '?')} days\n"
                message += "\n"

            # Upcoming (61-90 days)
            upcoming = [l for l in expiring_90 if l not in expiring_60]
            if upcoming:
                message += "🟢 **UPCOMING (61-90 Days):**\n"
                for lease in upcoming:
                    message += f"  - {lease.get('tenant_name', 'Unknown')}: {lease.get('days_until_expiration', '?')} days\n"

            if not expiring_90:
                message += "No leases expiring in the next 90 days.\n"

            return AgentResponse(
                message=message,
                data={
                    "urgent": urgent,
                    "warning": warning,
                    "upcoming": upcoming
                },
                is_complete=True,
                agent_name=self.name
            )

        except Exception as e:
            return AgentResponse(
                message=f"Error checking expirations: {str(e)}",
                is_complete=True,
                agent_name=self.name
            )

    def _handle_concentration(self) -> AgentResponse:
        """Handle concentration risk queries."""
        if self.sql_store is None:
            return self._no_database_response()

        try:
            from src.analytics.lease_analytics import LeaseAnalytics
            analytics = LeaseAnalytics(self.sql_store)

            risk_data = analytics.assess_portfolio_risk()
            concentration_risks = [
                r for r in risk_data.get('risks', [])
                if 'concentration' in r.get('type', '').lower()
            ]

            message = "**Concentration Risk Assessment**\n\n"

            if not concentration_risks:
                message += "🟢 Portfolio appears well-diversified.\n"
            else:
                for risk in concentration_risks:
                    severity = risk.get('severity', 'medium')
                    emoji = "🔴" if severity == "high" else "🟡"
                    message += f"{emoji} {risk.get('description', 'Concentration risk detected')}\n"

            # Add tenant breakdown
            summary = self.sql_store.get_financial_summary()
            if summary.get('tenant_count', 0) > 0:
                message += f"\n**Portfolio Composition:**\n"
                message += f"- Total Tenants: {summary.get('tenant_count', 0)}\n"
                # Add more breakdown if available

            return AgentResponse(
                message=message,
                data={"concentration_risks": concentration_risks},
                is_complete=True,
                agent_name=self.name
            )

        except Exception as e:
            return AgentResponse(
                message=f"Error assessing concentration: {str(e)}",
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

            # Determine emoji
            if score >= 80:
                emoji = "🟢"
                assessment = "Healthy"
            elif score >= 60:
                emoji = "🟡"
                assessment = "Moderate Risk"
            else:
                emoji = "🔴"
                assessment = "Needs Attention"

            message = (
                f"**Portfolio Health Score**\n\n"
                f"{emoji} **Score:** {score}/100\n"
                f"**Status:** {status} ({assessment})\n\n"
            )

            # Add component breakdown if available
            if health.get('components'):
                message += "**Score Components:**\n"
                for comp, value in health['components'].items():
                    message += f"  - {comp}: {value}\n"
                message += "\n"

            # Add recommendations
            if health.get('recommendations'):
                message += "**Key Recommendations:**\n"
                for rec in health['recommendations'][:3]:
                    message += f"  - {rec}\n"

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

    def _handle_full_assessment(self) -> AgentResponse:
        """Handle full risk assessment request."""
        if self.sql_store is None:
            return self._no_database_response()

        try:
            assessment = self._generate_full_assessment()
            return AgentResponse(
                message=self._format_risk_matrix(assessment),
                data=assessment,
                is_complete=True,
                agent_name=self.name
            )

        except Exception as e:
            return AgentResponse(
                message=f"Error running assessment: {str(e)}",
                is_complete=True,
                agent_name=self.name
            )

    def _handle_general_risk(self) -> AgentResponse:
        """Handle general risk queries with overview."""
        if self.sql_store is None:
            return self._no_database_response()

        try:
            from src.analytics.lease_analytics import LeaseAnalytics
            analytics = LeaseAnalytics(self.sql_store)

            risk_data = analytics.assess_portfolio_risk()
            risk_level = risk_data.get('risk_level', 'unknown')

            # Count by severity
            risks = risk_data.get('risks', [])
            high = len([r for r in risks if r.get('severity') == 'high'])
            medium = len([r for r in risks if r.get('severity') == 'medium'])
            low = len([r for r in risks if r.get('severity') == 'low'])

            message = (
                f"**Portfolio Risk Overview**\n\n"
                f"**Overall Risk Level:** {risk_level.upper()}\n\n"
                f"**Risk Summary:**\n"
                f"  🔴 High: {high}\n"
                f"  🟡 Medium: {medium}\n"
                f"  🟢 Low: {low}\n\n"
                f"I can provide detailed analysis on:\n"
                f"- Co-tenancy exposure\n"
                f"- Expiring leases\n"
                f"- Concentration risks\n"
                f"- Portfolio health score\n\n"
                f"What would you like to explore?"
            )

            return AgentResponse(
                message=message,
                data=risk_data,
                is_complete=True,
                agent_name=self.name
            )

        except Exception as e:
            return AgentResponse(
                message=f"Error assessing risks: {str(e)}",
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

    def _generate_full_assessment(self) -> Dict[str, Any]:
        """Generate comprehensive risk assessment."""
        if self.sql_store is None:
            return {}

        from src.analytics.lease_analytics import LeaseAnalytics
        analytics = LeaseAnalytics(self.sql_store)

        return {
            "risk_assessment": analytics.assess_portfolio_risk(),
            "health": analytics.calculate_portfolio_health_score(),
            "expirations": analytics.analyze_expiration_timeline(months_ahead=12),
            "expiring_30": self.sql_store.get_expiring_leases(days_ahead=30),
            "expiring_90": self.sql_store.get_expiring_leases(days_ahead=90)
        }

    def _format_risk_matrix(self, data: Dict[str, Any]) -> str:
        """Format risk assessment as a risk matrix."""
        risk_data = data.get('risk_assessment', {})
        health = data.get('health', {})
        expiring_30 = data.get('expiring_30', [])
        expiring_90 = data.get('expiring_90', [])

        score = health.get('health_score', 0)
        if score >= 80:
            health_emoji = "🟢"
        elif score >= 60:
            health_emoji = "🟡"
        else:
            health_emoji = "🔴"

        message = (
            f"**Comprehensive Risk Assessment**\n\n"
            f"**Portfolio Health:** {health_emoji} {score}/100\n\n"
            f"**Risk Matrix:**\n"
        )

        # List all risks by severity
        risks = risk_data.get('risks', [])
        high_risks = [r for r in risks if r.get('severity') == 'high']
        medium_risks = [r for r in risks if r.get('severity') == 'medium']

        if high_risks:
            message += "\n🔴 **HIGH RISK:**\n"
            for r in high_risks:
                message += f"  - {r.get('description', 'Unknown')}\n"

        if medium_risks:
            message += "\n🟡 **MEDIUM RISK:**\n"
            for r in medium_risks:
                message += f"  - {r.get('description', 'Unknown')}\n"

        if not high_risks and not medium_risks:
            message += "\n🟢 No significant risks identified.\n"

        # Add expiration summary
        message += f"\n**Expiration Summary:**\n"
        message += f"  - Next 30 days: {len(expiring_30)} leases\n"
        message += f"  - Next 90 days: {len(expiring_90)} leases\n"

        return message

    def _generate_recommendations(self, data: Dict[str, Any]) -> str:
        """Generate mitigation recommendations."""
        health = data.get('health', {})
        risk_data = data.get('risk_assessment', {})
        expiring_30 = data.get('expiring_30', [])

        message = "**Mitigation Recommendations**\n\n"

        # Priority actions
        priority = 1

        # Urgent expirations
        if expiring_30:
            message += f"**{priority}. Address Expiring Leases (Urgent)**\n"
            message += f"   {len(expiring_30)} leases expiring within 30 days.\n"
            message += "   Action: Initiate renewal discussions immediately.\n\n"
            priority += 1

        # High risks
        high_risks = [r for r in risk_data.get('risks', []) if r.get('severity') == 'high']
        for risk in high_risks[:2]:
            message += f"**{priority}. {risk.get('type', 'Risk').title()}**\n"
            message += f"   {risk.get('description', '')}\n"
            if risk.get('mitigation'):
                message += f"   Action: {risk.get('mitigation')}\n"
            message += "\n"
            priority += 1

        # Health recommendations
        if health.get('recommendations'):
            for rec in health['recommendations'][:2]:
                message += f"**{priority}. {rec}**\n\n"
                priority += 1

        if priority == 1:
            message += "No critical actions needed at this time. Continue monitoring."

        return message
