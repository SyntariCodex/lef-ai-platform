"""
Health check and rate limiting for the AI Bridge System
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from collections import defaultdict

@dataclass
class RateLimit:
    max_requests: int
    window_seconds: int
    current_requests: int = 0
    window_start: float = 0.0

@dataclass
class HealthMetrics:
    total_messages: int = 0
    successful_messages: int = 0
    failed_messages: int = 0
    average_latency: float = 0.0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    service_status: Dict[str, bool] = None
    message_queue_size: int = 0
    active_connections: int = 0

class BridgeHealth:
    def __init__(self, rate_limit_config: Dict[str, int]):
        self.logger = logging.getLogger("LEF.BridgeHealth")
        self.rate_limits = defaultdict(
            lambda: RateLimit(
                max_requests=rate_limit_config.get("max_requests", 100),
                window_seconds=rate_limit_config.get("window_seconds", 60)
            )
        )
        self.metrics = HealthMetrics(
            service_status=defaultdict(lambda: True)
        )
        self.latency_history: List[float] = []
        self.max_history_size = 1000

    def check_rate_limit(self, service: str) -> bool:
        """Check if the service has exceeded its rate limit"""
        limit = self.rate_limits[service]
        current_time = time.time()

        # Reset window if it has expired
        if current_time - limit.window_start >= limit.window_seconds:
            limit.current_requests = 0
            limit.window_start = current_time

        # Check if limit is exceeded
        if limit.current_requests >= limit.max_requests:
            self.logger.warning(f"Rate limit exceeded for {service}")
            return False

        limit.current_requests += 1
        return True

    def record_message(self, success: bool, latency: float, error: Optional[str] = None):
        """Record message metrics"""
        self.metrics.total_messages += 1
        if success:
            self.metrics.successful_messages += 1
        else:
            self.metrics.failed_messages += 1
            self.metrics.last_error = error
            self.metrics.last_error_time = datetime.now()

        # Update latency history
        self.latency_history.append(latency)
        if len(self.latency_history) > self.max_history_size:
            self.latency_history.pop(0)
        
        # Update average latency
        self.metrics.average_latency = sum(self.latency_history) / len(self.latency_history)

    def update_service_status(self, service: str, is_healthy: bool):
        """Update the health status of a service"""
        self.metrics.service_status[service] = is_healthy
        if not is_healthy:
            self.logger.warning(f"Service {service} is unhealthy")

    def update_queue_size(self, size: int):
        """Update the current message queue size"""
        self.metrics.message_queue_size = size

    def update_active_connections(self, count: int):
        """Update the number of active connections"""
        self.metrics.active_connections = count

    def get_health_status(self) -> Dict:
        """Get the current health status of the bridge"""
        return {
            "status": "healthy" if self._is_healthy() else "degraded",
            "metrics": {
                "total_messages": self.metrics.total_messages,
                "successful_messages": self.metrics.successful_messages,
                "failed_messages": self.metrics.failed_messages,
                "average_latency": self.metrics.average_latency,
                "message_queue_size": self.metrics.message_queue_size,
                "active_connections": self.metrics.active_connections
            },
            "services": {
                service: {
                    "healthy": status,
                    "rate_limit": {
                        "current": self.rate_limits[service].current_requests,
                        "max": self.rate_limits[service].max_requests,
                        "window_seconds": self.rate_limits[service].window_seconds
                    }
                }
                for service, status in self.metrics.service_status.items()
            },
            "last_error": {
                "message": self.metrics.last_error,
                "timestamp": self.metrics.last_error_time.isoformat() if self.metrics.last_error_time else None
            }
        }

    def _is_healthy(self) -> bool:
        """Check if the bridge is healthy"""
        # Check if all services are healthy
        if not all(self.metrics.service_status.values()):
            return False

        # Check if message queue is not too full
        if self.metrics.message_queue_size > 900:  # 90% of max size
            return False

        # Check if there are active connections
        if self.metrics.active_connections == 0:
            return False

        # Check if error rate is not too high
        if self.metrics.total_messages > 0:
            error_rate = self.metrics.failed_messages / self.metrics.total_messages
            if error_rate > 0.1:  # More than 10% errors
                return False

        return True

    def get_rate_limit_status(self, service: str) -> Dict:
        """Get the current rate limit status for a service"""
        limit = self.rate_limits[service]
        return {
            "current_requests": limit.current_requests,
            "max_requests": limit.max_requests,
            "window_seconds": limit.window_seconds,
            "window_start": limit.window_start,
            "window_end": limit.window_start + limit.window_seconds
        } 