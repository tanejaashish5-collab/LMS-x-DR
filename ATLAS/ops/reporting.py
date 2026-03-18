"""
Reporting Configuration for ATLAS Operations
Defines what metrics to track, report frequency, and alert thresholds.
Used by the orchestrator to generate daily and weekly reports.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class ReportFrequency(str, Enum):
    """How often a report is generated."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class AlertSeverity(str, Enum):
    """Severity level for metric alerts."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class MetricDefinition:
    """Single metric to track."""

    name: str
    description: str
    unit: str  # count, dollars, percent, hours
    source_table: str
    query_hint: str  # helps the reporting engine know what to query


@dataclass
class AlertThreshold:
    """Threshold that triggers an alert."""

    metric_name: str
    condition: str  # gt, lt, eq
    value: float
    severity: AlertSeverity
    message: str


@dataclass
class ReportConfig:
    """Complete report configuration."""

    report_id: str
    name: str
    frequency: ReportFrequency
    metrics: List[MetricDefinition]
    alerts: List[AlertThreshold] = field(default_factory=list)
    recipients: List[str] = field(default_factory=list)
    send_channel: str = "email"  # email, slack, both


# =============================================
# Daily Report Configuration
# =============================================

DAILY_REPORT = ReportConfig(
    report_id="atlas_daily",
    name="ATLAS Daily Operations Report",
    frequency=ReportFrequency.DAILY,
    recipients=["ashish@forgevoicestudio.com"],
    send_channel="email",
    metrics=[
        # Scout metrics
        MetricDefinition(
            name="opportunities_found",
            description="New opportunities discovered today",
            unit="count",
            source_table="atlas_opportunities",
            query_hint="COUNT(*) WHERE discovered_at >= today",
        ),
        MetricDefinition(
            name="avg_opportunity_score",
            description="Average Sonnet score of today's opportunities",
            unit="score",
            source_table="atlas_opportunities",
            query_hint="AVG(sonnet_score) WHERE discovered_at >= today",
        ),
        MetricDefinition(
            name="top_verticals",
            description="Most common verticals discovered today",
            unit="list",
            source_table="atlas_opportunities",
            query_hint="GROUP BY target_vertical ORDER BY COUNT DESC LIMIT 5",
        ),
        # Forge metrics
        MetricDefinition(
            name="pages_built",
            description="Landing pages built today",
            unit="count",
            source_table="atlas_agent_logs",
            query_hint="COUNT(*) WHERE agent='forge' AND action='build_landing_page' AND created_at >= today",
        ),
        MetricDefinition(
            name="pages_deployed",
            description="Landing pages successfully deployed",
            unit="count",
            source_table="atlas_agent_logs",
            query_hint="COUNT(*) WHERE agent='forge' AND status='success' AND created_at >= today",
        ),
        # Mercury metrics
        MetricDefinition(
            name="distributions_sent",
            description="Channel distributions completed today",
            unit="count",
            source_table="atlas_agent_logs",
            query_hint="COUNT(*) WHERE agent='mercury' AND action='distribute_landing_page' AND created_at >= today",
        ),
        MetricDefinition(
            name="channels_used",
            description="Distribution channels used today",
            unit="list",
            source_table="atlas_agent_logs",
            query_hint="DISTINCT channels from mercury distribute logs today",
        ),
        # Vault metrics
        MetricDefinition(
            name="budget_spent_today",
            description="Total spend across all agents today",
            unit="dollars",
            source_table="atlas_agent_logs",
            query_hint="SUM(cost_usd) WHERE created_at >= today",
        ),
        MetricDefinition(
            name="budget_remaining",
            description="Remaining daily budget",
            unit="dollars",
            source_table="atlas_budget",
            query_hint="daily_limit - budget_spent_today",
        ),
    ],
    alerts=[
        AlertThreshold(
            metric_name="budget_spent_today",
            condition="gt",
            value=20.0,
            severity=AlertSeverity.WARNING,
            message="Daily spend exceeded $20 USD. Review agent activity.",
        ),
        AlertThreshold(
            metric_name="budget_remaining",
            condition="lt",
            value=5.0,
            severity=AlertSeverity.CRITICAL,
            message="Less than $5 USD remaining in daily budget. Conservation mode.",
        ),
        AlertThreshold(
            metric_name="opportunities_found",
            condition="lt",
            value=1.0,
            severity=AlertSeverity.WARNING,
            message="No opportunities found today. Check Scout configuration.",
        ),
        AlertThreshold(
            metric_name="pages_deployed",
            condition="lt",
            value=0.0,
            severity=AlertSeverity.INFO,
            message="No pages deployed today. Check Forge pipeline.",
        ),
    ],
)


# =============================================
# Weekly Report Configuration
# =============================================

WEEKLY_REPORT = ReportConfig(
    report_id="atlas_weekly",
    name="ATLAS Weekly Business Report",
    frequency=ReportFrequency.WEEKLY,
    recipients=["ashish@forgevoicestudio.com"],
    send_channel="email",
    metrics=[
        MetricDefinition(
            name="total_opportunities_week",
            description="Total opportunities discovered this week",
            unit="count",
            source_table="atlas_opportunities",
            query_hint="COUNT(*) WHERE discovered_at >= week_start",
        ),
        MetricDefinition(
            name="high_score_opportunities",
            description="Opportunities scoring 70+ this week",
            unit="count",
            source_table="atlas_opportunities",
            query_hint="COUNT(*) WHERE sonnet_score >= 70 AND discovered_at >= week_start",
        ),
        MetricDefinition(
            name="total_pages_built",
            description="Landing pages built this week",
            unit="count",
            source_table="atlas_agent_logs",
            query_hint="COUNT(*) WHERE agent='forge' AND created_at >= week_start",
        ),
        MetricDefinition(
            name="total_distributions",
            description="Total distributions this week",
            unit="count",
            source_table="atlas_agent_logs",
            query_hint="COUNT(*) WHERE agent='mercury' AND created_at >= week_start",
        ),
        MetricDefinition(
            name="weekly_spend",
            description="Total spend this week",
            unit="dollars",
            source_table="atlas_agent_logs",
            query_hint="SUM(cost_usd) WHERE created_at >= week_start",
        ),
        MetricDefinition(
            name="pipeline_value",
            description="Total estimated pipeline value",
            unit="dollars",
            source_table="atlas_opportunities",
            query_hint="SUM of estimated deal sizes for qualified opportunities",
        ),
        MetricDefinition(
            name="vertical_breakdown",
            description="Opportunities by vertical this week",
            unit="list",
            source_table="atlas_opportunities",
            query_hint="GROUP BY target_vertical WHERE discovered_at >= week_start",
        ),
        MetricDefinition(
            name="cost_per_opportunity",
            description="Average cost per qualified opportunity",
            unit="dollars",
            source_table="atlas_agent_logs",
            query_hint="weekly_spend / total_opportunities_week",
        ),
    ],
    alerts=[
        AlertThreshold(
            metric_name="weekly_spend",
            condition="gt",
            value=100.0,
            severity=AlertSeverity.WARNING,
            message="Weekly spend exceeded $100 USD. Review efficiency.",
        ),
        AlertThreshold(
            metric_name="high_score_opportunities",
            condition="lt",
            value=3.0,
            severity=AlertSeverity.WARNING,
            message="Fewer than 3 high-score opportunities this week. Expand search.",
        ),
    ],
)


# =============================================
# Monthly Report Configuration
# =============================================

MONTHLY_REPORT = ReportConfig(
    report_id="atlas_monthly",
    name="ATLAS Monthly Executive Summary",
    frequency=ReportFrequency.MONTHLY,
    recipients=["ashish@forgevoicestudio.com"],
    send_channel="email",
    metrics=[
        MetricDefinition(
            name="total_opportunities_month",
            description="Total opportunities discovered this month",
            unit="count",
            source_table="atlas_opportunities",
            query_hint="COUNT(*) WHERE discovered_at >= month_start",
        ),
        MetricDefinition(
            name="conversion_rate",
            description="Opportunity to deal conversion rate",
            unit="percent",
            source_table="atlas_opportunities",
            query_hint="deals_closed / total_qualified * 100",
        ),
        MetricDefinition(
            name="revenue_generated",
            description="Total revenue from closed deals",
            unit="dollars",
            source_table="atlas_deals",
            query_hint="SUM(deal_value) WHERE closed_at >= month_start",
        ),
        MetricDefinition(
            name="total_spend",
            description="Total ATLAS operational spend",
            unit="dollars",
            source_table="atlas_agent_logs",
            query_hint="SUM(cost_usd) WHERE created_at >= month_start",
        ),
        MetricDefinition(
            name="roi",
            description="Return on investment (revenue / spend)",
            unit="ratio",
            source_table="computed",
            query_hint="revenue_generated / total_spend",
        ),
        MetricDefinition(
            name="active_clients",
            description="Clients currently in onboarding or delivery",
            unit="count",
            source_table="atlas_clients",
            query_hint="COUNT(*) WHERE status IN ('onboarding', 'building')",
        ),
    ],
)


# =============================================
# All Reports Indexed
# =============================================

ALL_REPORTS: Dict[str, ReportConfig] = {
    "daily": DAILY_REPORT,
    "weekly": WEEKLY_REPORT,
    "monthly": MONTHLY_REPORT,
}


# =============================================
# Helper Functions
# =============================================


def get_daily_report_config() -> ReportConfig:
    """Return the daily report configuration."""
    return DAILY_REPORT


def get_weekly_report_config() -> ReportConfig:
    """Return the weekly report configuration."""
    return WEEKLY_REPORT


def get_report_config(frequency: str) -> Optional[ReportConfig]:
    """
    Get report config by frequency.

    Args:
        frequency: One of daily, weekly, monthly

    Returns:
        ReportConfig or None.
    """
    return ALL_REPORTS.get(frequency.lower())


def get_alert_thresholds(
    report_id: str,
) -> List[AlertThreshold]:
    """Get all alert thresholds for a report."""
    report = ALL_REPORTS.get(report_id)
    if report is None:
        return []
    return report.alerts


def format_report_summary(report: ReportConfig) -> str:
    """Generate a human-readable summary of what a report tracks."""
    lines = [
        f"=== {report.name} ({report.frequency.value}) ===",
        f"Recipients: {', '.join(report.recipients)}",
        f"Channel: {report.send_channel}",
        "",
        "Metrics:",
    ]
    for metric in report.metrics:
        lines.append(f"  - {metric.name} ({metric.unit}): {metric.description}")

    if report.alerts:
        lines.append("")
        lines.append("Alerts:")
        for alert in report.alerts:
            lines.append(
                f"  - [{alert.severity.value.upper()}] "
                f"{alert.metric_name} {alert.condition} {alert.value}: "
                f"{alert.message}"
            )

    return "\n".join(lines)
