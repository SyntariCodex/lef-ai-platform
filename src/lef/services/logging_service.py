"""
Logging and tracing service for AI Bridge System
"""

import asyncio
import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from pathlib import Path
from uuid import uuid4
import structlog
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from ..services.alert_service import AlertService, AlertSeverity
from ..services.monitoring_service import MonitoringService
from ..services.config_service import ConfigService

logger = logging.getLogger(__name__)

class LogEntry(BaseModel):
    """Log entry with metadata"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str
    message: str
    service: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[Dict[str, Any]] = None

class TraceSpan(BaseModel):
    """Trace span information"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    events: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "active"

class LoggingService:
    """Service for managing system logging and tracing"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.config_service = ConfigService()
        self.alert_service = AlertService()
        self.monitoring_service = MonitoringService()
        self._log_processor: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Initialize structured logger
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer()
            ]
        )
        self.logger = structlog.get_logger()
        
        # Initialize tracing
        self.tracer_provider = TracerProvider()
        self.tracer = trace.get_tracer(__name__)
        self.propagator = TraceContextTextMapPropagator()
        
        # Configure Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name=os.getenv("JAEGER_HOST", "localhost"),
            agent_port=int(os.getenv("JAEGER_PORT", "6831")),
            service_name="lef_system"
        )
        self.tracer_provider.add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )
        trace.set_tracer_provider(self.tracer_provider)
        
    async def start(self):
        """Start the logging service"""
        try:
            logger.info("Starting logging service")
            
            # Create log directory if it doesn't exist
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            # Start log processor
            self._log_processor = asyncio.create_task(self._process_logs())
            
            logger.info("Logging service started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start logging service: {e}")
            await self.alert_service.create_alert(
                title="Logging Service Start Failed",
                message=f"Failed to start logging service: {e}",
                severity=AlertSeverity.ERROR
            )
            raise
            
    async def _process_logs(self):
        """Process and store logs"""
        while not self._shutdown_event.is_set():
            try:
                # Process logs from queue
                # TODO: Implement log processing logic
                
                await asyncio.sleep(1)  # Process every second
                
            except Exception as e:
                logger.error(f"Error processing logs: {e}")
                await asyncio.sleep(5)
                
    def create_span(self, name: str, parent_span: Optional[Any] = None) -> Any:
        """Create a new trace span"""
        try:
            with self.tracer.start_as_current_span(
                name,
                parent=parent_span,
                attributes={"service": "lef_system"}
            ) as span:
                return span
        except Exception as e:
            logger.error(f"Failed to create span: {e}")
            return None
            
    def add_span_event(self, span: Any, name: str, attributes: Dict[str, Any] = None):
        """Add an event to a span"""
        try:
            if span:
                span.add_event(name, attributes or {})
        except Exception as e:
            logger.error(f"Failed to add span event: {e}")
            
    def end_span(self, span: Any, status: str = "ok", error: Optional[Exception] = None):
        """End a span"""
        try:
            if span:
                if error:
                    span.set_status(trace.Status(trace.StatusCode.ERROR))
                    span.record_exception(error)
                    span.set_attribute("error.message", str(error))
                else:
                    span.set_status(trace.Status(trace.StatusCode.OK))
                span.end()
        except Exception as e:
            logger.error(f"Failed to end span: {e}")
            
    async def log(
        self,
        level: str,
        message: str,
        service: str,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None
    ):
        """Log a message with metadata"""
        try:
            log_entry = LogEntry(
                level=level,
                message=message,
                service=service,
                trace_id=trace_id,
                span_id=span_id,
                context=context or {},
                error=error.__dict__ if error else None
            )
            
            # Log to structured logger
            self.logger.info(
                "log_entry",
                **log_entry.dict()
            )
            
            # Record metric
            await self.monitoring_service._record_metric(
                "log_entries",
                1,
                {"level": level, "service": service}
            )
            
            # Create alert for error logs
            if level == "ERROR":
                await self.alert_service.create_alert(
                    title=f"Error in {service}",
                    message=message,
                    severity=AlertSeverity.ERROR
                )
                
        except Exception as e:
            logger.error(f"Failed to log message: {e}")
            
    async def get_logs(
        self,
        service: Optional[str] = None,
        level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        trace_id: Optional[str] = None
    ) -> List[LogEntry]:
        """Get logs with optional filtering"""
        try:
            # TODO: Implement log retrieval logic
            return []
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return []
            
    async def get_trace(self, trace_id: str) -> List[TraceSpan]:
        """Get trace information"""
        try:
            # TODO: Implement trace retrieval logic
            return []
        except Exception as e:
            logger.error(f"Failed to get trace: {e}")
            return []
            
    async def shutdown(self):
        """Shutdown the logging service"""
        try:
            logger.info("Shutting down logging service")
            
            # Stop log processor
            if self._log_processor:
                self._shutdown_event.set()
                await self._log_processor
                self._log_processor = None
                
            logger.info("Logging service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during logging service shutdown: {e}")
            await self.alert_service.create_alert(
                title="Logging Service Shutdown Failed",
                message=f"Error during shutdown: {e}",
                severity=AlertSeverity.ERROR
            )
            raise 