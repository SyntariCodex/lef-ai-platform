"""
Tests for the monitoring service
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from src.lef.services.monitoring_service import MonitoringService, Metric, MetricPoint

@pytest.mark.asyncio
async def test_monitoring_service_initialization(monitoring_service):
    """Test monitoring service initialization"""
    assert monitoring_service.metrics is not None
    assert monitoring_service.health_checks is not None
    assert monitoring_service._collection_task is not None

@pytest.mark.asyncio
async def test_metric_collection(monitoring_service):
    """Test metric collection"""
    # Record a test metric
    monitoring_service._record_metric(
        "test_metric",
        42.0,
        labels={"test": "value"},
        unit="Count"
    )
    
    # Check if metric was recorded
    assert "test_metric" in monitoring_service.metrics
    metric = monitoring_service.metrics["test_metric"]
    assert len(metric.points) == 1
    assert metric.points[0].value == 42.0
    assert metric.points[0].labels == {"test": "value"}
    assert metric.points[0].unit == "Count"

@pytest.mark.asyncio
async def test_health_check_updates(monitoring_service):
    """Test health check updates"""
    # Update a health check
    monitoring_service._update_health_check(
        "system_health",
        {
            "status": "healthy",
            "components": {
                "test": "healthy"
            }
        }
    )
    
    # Check if health check was updated
    assert "system_health" in monitoring_service.health_checks
    check = monitoring_service.health_checks["system_health"]
    assert check.last_check is not None
    assert check.details["status"] == "healthy"

@pytest.mark.asyncio
async def test_cloudwatch_integration(monitoring_service, mock_cloudwatch):
    """Test CloudWatch integration"""
    with patch("boto3.client", return_value=mock_cloudwatch):
        # Record a metric
        monitoring_service._record_metric(
            "cloudwatch_test",
            42.0,
            labels={"test": "value"},
            unit="Count"
        )
        
        # Publish to CloudWatch
        await monitoring_service._publish_metrics_to_cloudwatch()
        
        # Verify CloudWatch call
        mock_cloudwatch.put_metric_data.assert_called_once()

@pytest.mark.asyncio
async def test_metric_cleanup(monitoring_service):
    """Test metric cleanup"""
    # Record old metrics
    old_time = datetime.utcnow() - timedelta(hours=2)
    monitoring_service.metrics["old_metric"] = Metric(
        name="old_metric",
        description="Test metric",
        type="gauge",
        points=[
            MetricPoint(
                timestamp=old_time,
                value=42.0,
                labels={"test": "value"}
            )
        ]
    )
    
    # Run cleanup
    await monitoring_service._cleanup_old_metrics()
    
    # Verify old metrics were cleaned up
    assert "old_metric" not in monitoring_service.metrics

@pytest.mark.asyncio
async def test_threshold_alerts(monitoring_service, alert_service):
    """Test threshold-based alerts"""
    # Set up a metric with threshold
    monitoring_service.metrics["threshold_test"] = Metric(
        name="threshold_test",
        description="Test metric with threshold",
        type="gauge",
        threshold=50.0
    )
    
    # Record a value above threshold
    monitoring_service._record_metric(
        "threshold_test",
        75.0,
        labels={"test": "value"}
    )
    
    # Verify alert was created
    assert len(alert_service.alerts) > 0
    assert "Metric Threshold Exceeded: threshold_test" in [a.title for a in alert_service.alerts] 