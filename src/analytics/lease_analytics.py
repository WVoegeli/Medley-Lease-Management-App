"""
Advanced lease analytics and reporting module.

Provides:
- Financial forecasting and projections
- Tenant comparison and benchmarking
- Occupancy trend analysis
- Revenue optimization insights
- Risk assessment
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


class LeaseAnalytics:
    """Advanced analytics for lease portfolio management."""

    def __init__(self, sql_store):
        """Initialize with SQL database store."""
        self.db = sql_store

    # ==================== Financial Projections ====================

    def project_revenue(self, months_ahead: int = 12) -> Dict[str, Any]:
        """Project revenue for the next N months considering expirations."""
        leases = self.db.get_all_leases(status='active')

        monthly_projections = []
        current_date = datetime.now()

        for month_offset in range(months_ahead):
            projection_date = current_date + timedelta(days=30 * month_offset)

            # Calculate revenue for this month
            month_revenue = 0
            active_in_month = 0

            for lease in leases:
                if lease['base_rent'] and lease['end_date']:
                    end_date = datetime.strptime(lease['end_date'], "%Y-%m-%d")

                    # Is lease still active this month?
                    if end_date >= projection_date:
                        month_revenue += lease['base_rent']
                        active_in_month += 1

            monthly_projections.append({
                'month': projection_date.strftime("%Y-%m"),
                'projected_revenue': round(month_revenue, 2),
                'active_leases': active_in_month
            })

        # Calculate trends
        revenues = [p['projected_revenue'] for p in monthly_projections]
        avg_revenue = statistics.mean(revenues) if revenues else 0
        revenue_trend = "declining" if revenues[-1] < revenues[0] else "stable" if revenues[-1] == revenues[0] else "growing"

        return {
            'projections': monthly_projections,
            'average_monthly_revenue': round(avg_revenue, 2),
            'trend': revenue_trend,
            'revenue_at_risk': round(revenues[0] - revenues[-1], 2) if revenues[0] > revenues[-1] else 0
        }

    def calculate_lease_value(self, lease_id: int) -> Dict[str, float]:
        """Calculate total value metrics for a lease."""
        lease = self.db.get_lease(lease_id)
        if not lease:
            return {}

        base_rent = lease.get('base_rent', 0) or 0
        term_months = lease.get('term_months', 0) or 0

        # Calculate various value metrics
        total_contract_value = base_rent * term_months
        average_monthly_value = base_rent
        annual_value = base_rent * 12

        # Calculate remaining value if end_date is available
        remaining_value = 0
        if lease.get('end_date'):
            end_date = datetime.strptime(lease['end_date'], "%Y-%m-%d")
            months_remaining = max(0, (end_date.year - datetime.now().year) * 12 +
                                  (end_date.month - datetime.now().month))
            remaining_value = base_rent * months_remaining

        return {
            'total_contract_value': round(total_contract_value, 2),
            'annual_value': round(annual_value, 2),
            'monthly_value': round(average_monthly_value, 2),
            'remaining_value': round(remaining_value, 2),
            'months_remaining': months_remaining if lease.get('end_date') else None
        }

    # ==================== Tenant Comparison ====================

    def compare_tenants(self, tenant_names: List[str]) -> Dict[str, Any]:
        """Compare multiple tenants across key metrics."""
        comparisons = []

        for tenant_name in tenant_names:
            leases = self.db.get_leases_by_tenant(tenant_name)

            if not leases:
                continue

            # Use most recent active lease
            active_leases = [l for l in leases if l['status'] == 'active']
            if not active_leases:
                continue

            lease = active_leases[0]

            tenant_data = {
                'tenant_name': tenant_name,
                'monthly_rent': lease.get('base_rent', 0),
                'annual_rent': lease.get('base_rent', 0) * 12 if lease.get('base_rent') else 0,
                'square_footage': lease.get('square_footage', 0),
                'rent_per_sqft': (lease.get('base_rent', 0) / lease.get('square_footage', 1)) if lease.get('square_footage') else 0,
                'lease_end': lease.get('end_date'),
                'term_months': lease.get('term_months'),
            }

            # Calculate days until expiration
            if lease.get('end_date'):
                end_date = datetime.strptime(lease['end_date'], "%Y-%m-%d")
                days_until = (end_date - datetime.now()).days
                tenant_data['days_until_expiration'] = max(0, days_until)

            comparisons.append(tenant_data)

        # Add comparative rankings
        if comparisons:
            # Rank by revenue
            sorted_by_revenue = sorted(comparisons, key=lambda x: x['annual_rent'], reverse=True)
            for i, tenant in enumerate(sorted_by_revenue):
                tenant['revenue_rank'] = i + 1

            # Rank by rent per sqft
            sorted_by_rate = sorted([t for t in comparisons if t['rent_per_sqft'] > 0],
                                   key=lambda x: x['rent_per_sqft'], reverse=True)
            for i, tenant in enumerate(sorted_by_rate):
                tenant['rate_rank'] = i + 1

        return {
            'tenants': comparisons,
            'count': len(comparisons)
        }

    def get_tenant_benchmarks(self) -> Dict[str, Any]:
        """Calculate benchmarks across all tenants."""
        revenue_by_tenant = self.db.get_revenue_by_tenant()

        if not revenue_by_tenant:
            return {}

        rents = [t['monthly_rent'] for t in revenue_by_tenant if t['monthly_rent']]
        sqft = [t['square_footage'] for t in revenue_by_tenant if t['square_footage']]
        rates = [t['rent_per_sqft'] for t in revenue_by_tenant if t['rent_per_sqft'] > 0]

        return {
            'median_monthly_rent': round(statistics.median(rents), 2) if rents else 0,
            'avg_monthly_rent': round(statistics.mean(rents), 2) if rents else 0,
            'median_square_footage': round(statistics.median(sqft), 2) if sqft else 0,
            'avg_square_footage': round(statistics.mean(sqft), 2) if sqft else 0,
            'median_rent_per_sqft': round(statistics.median(rates), 2) if rates else 0,
            'avg_rent_per_sqft': round(statistics.mean(rates), 2) if rates else 0,
            'highest_rent': round(max(rents), 2) if rents else 0,
            'lowest_rent': round(min(rents), 2) if rents else 0,
        }

    # ==================== Risk Assessment ====================

    def assess_portfolio_risk(self) -> Dict[str, Any]:
        """Assess risk factors across the lease portfolio."""
        all_leases = self.db.get_all_leases(status='active')

        if not all_leases:
            return {'risk_level': 'no_data', 'risks': []}

        risks = []
        risk_score = 0

        # Risk 1: Concentration risk (single tenant > 30% of revenue)
        summary = self.db.get_financial_summary()
        total_revenue = summary['monthly_revenue']

        for lease in all_leases:
            if lease['base_rent'] and total_revenue > 0:
                tenant_percentage = (lease['base_rent'] / total_revenue) * 100
                if tenant_percentage > 30:
                    risks.append({
                        'type': 'concentration',
                        'severity': 'high',
                        'tenant': lease['tenant_name'],
                        'description': f"{lease['tenant_name']} represents {tenant_percentage:.1f}% of total revenue"
                    })
                    risk_score += 3

        # Risk 2: Expiration clustering (>40% of revenue expiring in same quarter)
        expiring_90 = self.db.get_expiring_leases(90)
        expiring_revenue = sum(l['base_rent'] for l in expiring_90 if l['base_rent'])
        expiration_percentage = (expiring_revenue / total_revenue * 100) if total_revenue > 0 else 0

        if expiration_percentage > 40:
            risks.append({
                'type': 'expiration_clustering',
                'severity': 'high',
                'description': f"{expiration_percentage:.1f}% of revenue expires in next 90 days"
            })
            risk_score += 3
        elif expiration_percentage > 25:
            risks.append({
                'type': 'expiration_clustering',
                'severity': 'medium',
                'description': f"{expiration_percentage:.1f}% of revenue expires in next 90 days"
            })
            risk_score += 2

        # Risk 3: Below-market rates
        benchmarks = self.get_tenant_benchmarks()
        avg_rate = benchmarks.get('avg_rent_per_sqft', 0)

        for lease in all_leases:
            if lease['base_rent'] and lease['square_footage'] and avg_rate > 0:
                lease_rate = lease['base_rent'] / lease['square_footage']
                if lease_rate < avg_rate * 0.8:  # 20% below average
                    risks.append({
                        'type': 'below_market',
                        'severity': 'low',
                        'tenant': lease['tenant_name'],
                        'description': f"{lease['tenant_name']} paying ${lease_rate:.2f}/sqft vs market avg ${avg_rate:.2f}/sqft"
                    })
                    risk_score += 1

        # Determine overall risk level
        if risk_score >= 5:
            risk_level = 'high'
        elif risk_score >= 3:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risks': risks,
            'expiration_concentration': round(expiration_percentage, 2)
        }

    # ==================== Optimization Insights ====================

    def get_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Identify opportunities to optimize the lease portfolio."""
        opportunities = []

        benchmarks = self.get_tenant_benchmarks()
        avg_rate = benchmarks.get('avg_rent_per_sqft', 0)

        leases = self.db.get_all_leases(status='active')

        for lease in leases:
            if not lease['base_rent'] or not lease['square_footage']:
                continue

            lease_rate = lease['base_rent'] / lease['square_footage']

            # Opportunity 1: Below-market rent with upcoming expiration
            if lease['end_date']:
                end_date = datetime.strptime(lease['end_date'], "%Y-%m-%d")
                days_until = (end_date - datetime.now()).days

                if lease_rate < avg_rate * 0.9 and 0 < days_until <= 180:
                    potential_increase = (avg_rate - lease_rate) * lease['square_footage']
                    opportunities.append({
                        'type': 'rate_optimization',
                        'tenant': lease['tenant_name'],
                        'current_rate': round(lease_rate, 2),
                        'market_rate': round(avg_rate, 2),
                        'potential_monthly_increase': round(potential_increase, 2),
                        'potential_annual_increase': round(potential_increase * 12, 2),
                        'days_until_expiration': days_until,
                        'priority': 'high' if days_until <= 90 else 'medium'
                    })

        return sorted(opportunities, key=lambda x: x.get('potential_annual_increase', 0), reverse=True)

    # ==================== Trend Analysis ====================

    def analyze_expiration_timeline(self, months_ahead: int = 24) -> Dict[str, Any]:
        """Analyze lease expiration timeline."""
        leases = self.db.get_all_leases(status='active')

        timeline = defaultdict(lambda: {'count': 0, 'revenue': 0, 'tenants': []})
        current_date = datetime.now()

        for lease in leases:
            if not lease['end_date']:
                continue

            end_date = datetime.strptime(lease['end_date'], "%Y-%m-%d")

            # Group by quarter
            quarter_key = f"{end_date.year}-Q{(end_date.month-1)//3 + 1}"

            timeline[quarter_key]['count'] += 1
            timeline[quarter_key]['revenue'] += lease.get('base_rent', 0) or 0
            timeline[quarter_key]['tenants'].append(lease['tenant_name'])

        # Convert to sorted list
        sorted_timeline = sorted(
            [{'quarter': k, **v} for k, v in timeline.items()],
            key=lambda x: x['quarter']
        )

        return {
            'timeline': sorted_timeline,
            'total_expirations': sum(q['count'] for q in sorted_timeline)
        }

    # ==================== Portfolio Health ====================

    def calculate_portfolio_health_score(self) -> Dict[str, Any]:
        """Calculate overall portfolio health score (0-100)."""
        score = 100
        factors = []

        # Factor 1: Occupancy (-20 points if < 90%)
        summary = self.db.get_financial_summary()
        # Assuming 100% occupancy for now; would need total_property_sqft for actual calculation

        # Factor 2: Expiration risk (-15 points if high risk)
        risk = self.assess_portfolio_risk()
        if risk['risk_level'] == 'high':
            score -= 15
            factors.append({'factor': 'Expiration Risk', 'impact': -15, 'status': 'High risk'})
        elif risk['risk_level'] == 'medium':
            score -= 8
            factors.append({'factor': 'Expiration Risk', 'impact': -8, 'status': 'Medium risk'})

        # Factor 3: Below-market rates (-10 points if >30% of units below market)
        opportunities = self.get_optimization_opportunities()
        if len(opportunities) > len(self.db.get_all_leases(status='active')) * 0.3:
            score -= 10
            factors.append({'factor': 'Rent Optimization', 'impact': -10, 'status': 'Multiple below-market rates'})

        # Factor 4: Revenue trend (-15 points if declining)
        projections = self.project_revenue(12)
        if projections['trend'] == 'declining':
            score -= 15
            factors.append({'factor': 'Revenue Trend', 'impact': -15, 'status': 'Declining revenue'})

        # Determine health status
        if score >= 85:
            health_status = 'excellent'
        elif score >= 70:
            health_status = 'good'
        elif score >= 50:
            health_status = 'fair'
        else:
            health_status = 'poor'

        return {
            'health_score': max(0, score),
            'health_status': health_status,
            'factors': factors,
            'recommendations': self._generate_recommendations(risk, opportunities, projections)
        }

    def _generate_recommendations(self, risk_data, opportunities, projections) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Risk-based recommendations
        if risk_data['risk_level'] in ['high', 'medium']:
            recommendations.append(
                "Begin renewal negotiations early for leases expiring in next 90 days"
            )

        # Optimization recommendations
        if opportunities:
            top_opp = opportunities[0]
            recommendations.append(
                f"Prioritize rate discussion with {top_opp['tenant']} - potential ${top_opp['potential_annual_increase']:,.0f} annual increase"
            )

        # Revenue trend recommendations
        if projections['trend'] == 'declining':
            recommendations.append(
                "Develop retention strategy to address declining revenue trend"
            )

        if not recommendations:
            recommendations.append("Portfolio is healthy - continue monitoring key metrics")

        return recommendations
