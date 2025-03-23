"""
AI Bridge System for inter-AI communication
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from .models.system_state import SystemState
from .models.message import Message, MessageType, MessagePriority
from .models.bridge_status import BridgeStatus
from .services.alert_service import AlertService
from .services.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class AIBridge:
    """AI Bridge System for handling inter-AI communication"""
    
    def __init__(self):
        self.bridge_id = str(uuid.uuid4())
        self.status = BridgeStatus.INITIALIZING
        self.connections: Dict[str, Any] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.alert_service = AlertService()
        self.rate_limiter = RateLimiter()
        self._processing_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
    async def initialize(self):
        """Initialize the AI Bridge system"""
        try:
            logger.info(f"Initializing AI Bridge {self.bridge_id}")
            
            # Initialize Redis connection for message queuing
            self.redis = await self._init_redis()
            
            # Initialize connections to AI services
            await self._init_connections()
            
            # Start message processing
            await self.start_message_processing()
            
            self.status = BridgeStatus.ACTIVE
            logger.info("AI Bridge initialized successfully")
            
        except Exception as e:
            self.status = BridgeStatus.ERROR
            logger.error(f"Failed to initialize AI Bridge: {e}")
            await self.alert_service.create_alert(
                title="AI Bridge Initialization Failed",
                message=f"Failed to initialize AI Bridge: {e}",
                severity="ERROR"
            )
            raise
            
    async def _init_redis(self):
        """Initialize Redis connection"""
        try:
            import aioredis
            redis = await aioredis.create_redis_pool(
                'redis://localhost',
                encoding='utf-8',
                decode_responses=True
            )
            return redis
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
            
    async def _init_connections(self):
        """Initialize connections to AI services"""
        try:
            # Initialize connections to configured AI services
            services = await self._load_service_configs()
            for service_id, config in services.items():
                connection = await self._create_service_connection(service_id, config)
                self.connections[service_id] = connection
                
        except Exception as e:
            logger.error(f"Failed to initialize service connections: {e}")
            raise
            
    async def _load_service_configs(self) -> Dict[str, Dict]:
        """Load AI service configurations"""
        # TODO: Load from configuration file
        return {
            "analysis_service": {
                "url": "ws://localhost:8001",
                "timeout": 30,
                "retry_attempts": 3
            },
            "processing_service": {
                "url": "ws://localhost:8002",
                "timeout": 30,
                "retry_attempts": 3
            }
        }
        
    async def _create_service_connection(self, service_id: str, config: Dict) -> Any:
        """Create connection to an AI service"""
        try:
            import websockets
            connection = await websockets.connect(
                config["url"],
                ping_interval=None,
                close_timeout=config["timeout"]
            )
            return connection
        except Exception as e:
            logger.error(f"Failed to connect to service {service_id}: {e}")
            raise
            
    async def send_message(self, target_service: str, message: Message) -> bool:
        """Send a message to a target service"""
        try:
            if target_service not in self.connections:
                raise ValueError(f"Service {target_service} not connected")
                
            if not await self.rate_limiter.check_rate_limit(target_service):
                raise Exception("Rate limit exceeded")
                
            connection = self.connections[target_service]
            await connection.send(message.json())
            
            # Record message metrics
            await self.rate_limiter.record_message(target_service)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to {target_service}: {e}")
            await self.alert_service.create_alert(
                title="Message Send Failed",
                message=f"Failed to send message to {target_service}: {e}",
                severity="ERROR"
            )
            return False
            
    async def broadcast_state(self, state: SystemState):
        """Broadcast system state to all connected services"""
        try:
            message = Message(
                id=str(uuid.uuid4()),
                type=MessageType.STATE_UPDATE,
                priority=MessagePriority.HIGH,
                content=state.dict(),
                timestamp=datetime.utcnow()
            )
            
            for service_id in self.connections:
                await self.send_message(service_id, message)
                
        except Exception as e:
            logger.error(f"Failed to broadcast state: {e}")
            await self.alert_service.create_alert(
                title="State Broadcast Failed",
                message=f"Failed to broadcast state: {e}",
                severity="ERROR"
            )
            
    async def request_analysis(self, service_id: str, data: Dict) -> Optional[Dict]:
        """Request data analysis from a specific service"""
        try:
            message = Message(
                id=str(uuid.uuid4()),
                type=MessageType.ANALYSIS_REQUEST,
                priority=MessagePriority.MEDIUM,
                content=data,
                timestamp=datetime.utcnow()
            )
            
            if not await self.send_message(service_id, message):
                return None
                
            # Wait for response
            response = await self._wait_for_response(message.id)
            return response
            
        except Exception as e:
            logger.error(f"Failed to request analysis from {service_id}: {e}")
            await self.alert_service.create_alert(
                title="Analysis Request Failed",
                message=f"Failed to request analysis from {service_id}: {e}",
                severity="ERROR"
            )
            return None
            
    async def _wait_for_response(self, message_id: str, timeout: int = 30) -> Optional[Dict]:
        """Wait for a response to a specific message"""
        try:
            start_time = datetime.utcnow()
            while (datetime.utcnow() - start_time).seconds < timeout:
                response = await self.message_queue.get()
                if response.get("message_id") == message_id:
                    return response.get("content")
                await asyncio.sleep(0.1)
            return None
        except Exception as e:
            logger.error(f"Error waiting for response: {e}")
            return None
            
    async def _process_message(self, message: Message):
        """Process a single message from the queue"""
        try:
            # Validate message
            if not self._validate_message(message):
                logger.warning(f"Invalid message received: {message.id}")
                return
                
            # Process based on message type
            if message.type == MessageType.STATE_UPDATE:
                await self._handle_state_update(message)
            elif message.type == MessageType.ANALYSIS_REQUEST:
                await self._handle_analysis_request(message)
            elif message.type == MessageType.ERROR:
                await self._handle_error(message)
                
            # Update health metrics
            await self._update_health_metrics()
            
        except Exception as e:
            logger.error(f"Error processing message {message.id}: {e}")
            await self.alert_service.create_alert(
                title="Message Processing Failed",
                message=f"Error processing message {message.id}: {e}",
                severity="ERROR"
            )
            
    async def _process_messages(self):
        """Process messages from the queue"""
        while not self._shutdown_event.is_set():
            try:
                message = await self.message_queue.get()
                await self._process_message(message)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in message processing loop: {e}")
                await asyncio.sleep(1)
                
    async def start_message_processing(self):
        """Start the message processing loop"""
        self._processing_task = asyncio.create_task(self._process_messages())
        
    async def stop_message_processing(self):
        """Stop the message processing loop"""
        if self._processing_task:
            self._shutdown_event.set()
            await self._processing_task
            self._processing_task = None
            
    async def shutdown(self):
        """Shutdown the AI Bridge system"""
        try:
            logger.info("Shutting down AI Bridge")
            
            # Stop message processing
            await self.stop_message_processing()
            
            # Close service connections
            for service_id, connection in self.connections.items():
                try:
                    await connection.close()
                except Exception as e:
                    logger.error(f"Error closing connection to {service_id}: {e}")
                    
            # Close Redis connection
            if hasattr(self, 'redis'):
                self.redis.close()
                await self.redis.wait_closed()
                
            self.status = BridgeStatus.SHUTDOWN
            logger.info("AI Bridge shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            await self.alert_service.create_alert(
                title="Bridge Shutdown Failed",
                message=f"Error during shutdown: {e}",
                severity="ERROR"
            )
            raise 