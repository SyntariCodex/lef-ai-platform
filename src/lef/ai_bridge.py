"""
AI Bridge System - Handles communication between different AI services
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml
import websockets
import aiohttp
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import jwt
import aioredis
from dataclasses import dataclass
from enum import Enum
import time
from .bridge_health import BridgeHealth

class BridgeState(Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DEGRADED = "degraded"
    ERROR = "error"
    SHUTDOWN = "shutdown"

@dataclass
class Message:
    id: str
    source: str
    target: str
    content: Dict[str, Any]
    priority: int
    timestamp: str
    signature: Optional[str] = None

class AIBridge:
    def __init__(self, config_path: Optional[Path] = None):
        self.state = BridgeState.INITIALIZING
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        self.message_queue = asyncio.Queue(maxsize=self.config["message_queue"]["max_size"])
        self.connections = {}
        self.encryption_key = self._generate_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        self.redis = None
        self._setup_security()
        self.health = BridgeHealth(self.config["security"]["rate_limiting"])

    def _load_config(self, config_path: Optional[Path] = None) -> Dict:
        """Load AI bridge configuration"""
        if config_path and config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        
        # Default configuration
        return {
            "connections": {
                "claude": {
                    "endpoint": "wss://claude-api-endpoint/v1/ws",
                    "timeout": 30,
                    "retry_attempts": 3
                },
                "grok": {
                    "endpoint": "https://api.grok.x/v1",
                    "timeout": 30,
                    "retry_attempts": 3
                },
                "novaeus": {
                    "endpoint": "wss://novaeus-endpoint/v1/ws",
                    "timeout": 30,
                    "retry_attempts": 3
                }
            },
            "message_queue": {
                "max_size": 1000,
                "retention_period": 3600
            },
            "security": {
                "encryption_enabled": True,
                "signature_verification": True,
                "rate_limiting": {
                    "max_requests": 100,
                    "window_seconds": 60
                }
            }
        }

    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("LEF.AIBridge")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        fh = logging.FileHandler("logs/ai_bridge.log")
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger

    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for secure communication"""
        return Fernet.generate_key()

    def _setup_security(self):
        """Setup security components"""
        if self.config["security"]["encryption_enabled"]:
            self.logger.info("Encryption enabled for secure communication")
        
        if self.config["security"]["signature_verification"]:
            self.logger.info("Signature verification enabled")

    async def initialize(self):
        """Initialize the AI Bridge system"""
        try:
            # Initialize Redis for message queue
            self.redis = await aioredis.create_redis_pool(
                "redis://localhost",
                encoding="utf-8",
                decode_responses=True
            )
            
            # Initialize connections to AI services
            for service, config in self.config["connections"].items():
                await self._initialize_connection(service, config)
            
            self.state = BridgeState.ACTIVE
            self.logger.info("AI Bridge system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI Bridge: {e}")
            self.state = BridgeState.ERROR
            raise

    async def _initialize_connection(self, service: str, config: Dict):
        """Initialize connection to an AI service"""
        try:
            if service == "claude":
                self.connections[service] = await websockets.connect(
                    config["endpoint"],
                    ping_interval=None
                )
            elif service == "grok":
                self.connections[service] = aiohttp.ClientSession()
            elif service == "novaeus":
                self.connections[service] = await websockets.connect(
                    config["endpoint"],
                    ping_interval=None
                )
            
            self.logger.info(f"Connected to {service} service")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {service}: {e}")
            raise

    async def send_message(self, message: Message) -> bool:
        """Send a message to the target AI service"""
        start_time = time.time()
        try:
            # Check rate limit
            if not self.health.check_rate_limit(message.target):
                raise Exception(f"Rate limit exceeded for {message.target}")
            
            # Encrypt message content if enabled
            if self.config["security"]["encryption_enabled"]:
                message.content = self._encrypt_message(message.content)
            
            # Add signature if enabled
            if self.config["security"]["signature_verification"]:
                message.signature = self._sign_message(message)
            
            # Add to message queue
            await self.message_queue.put(message)
            
            # Process message
            await self._process_message(message)
            
            # Record success
            latency = time.time() - start_time
            self.health.record_message(True, latency)
            
            return True
            
        except Exception as e:
            # Record failure
            latency = time.time() - start_time
            self.health.record_message(False, latency, str(e))
            self.logger.error(f"Failed to send message: {e}")
            return False

    def _encrypt_message(self, content: Dict) -> Dict:
        """Encrypt message content"""
        try:
            content_str = json.dumps(content)
            encrypted = self.fernet.encrypt(content_str.encode())
            return {"encrypted": encrypted.decode()}
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            raise

    def _sign_message(self, message: Message) -> str:
        """Sign message for verification"""
        try:
            content = json.dumps(message.content)
            return jwt.encode(
                {"content": content, "timestamp": message.timestamp},
                self.encryption_key,
                algorithm="HS256"
            )
        except Exception as e:
            self.logger.error(f"Message signing failed: {e}")
            raise

    async def _process_message(self, message: Message):
        """Process message from queue"""
        try:
            # Get connection for target service
            connection = self.connections.get(message.target)
            if not connection:
                raise ValueError(f"No connection available for {message.target}")
            
            # Send message based on service type
            if message.target in ["claude", "novaeus"]:
                await connection.send(json.dumps(message.__dict__))
            elif message.target == "grok":
                async with connection.post(
                    f"{self.config['connections']['grok']['endpoint']}/messages",
                    json=message.__dict__
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to send message to Grok: {response.status}")
            
            self.logger.info(f"Message sent to {message.target}")
            
            # Update health metrics
            self.health.update_service_status(message.target, True)
            self.health.update_queue_size(self.message_queue.qsize())
            self.health.update_active_connections(len(self.connections))
            
        except Exception as e:
            self.health.update_service_status(message.target, False)
            self.logger.error(f"Message processing failed: {e}")
            raise

    async def receive_message(self, service: str) -> Optional[Message]:
        """Receive message from an AI service"""
        start_time = time.time()
        try:
            connection = self.connections.get(service)
            if not connection:
                raise ValueError(f"No connection available for {service}")
            
            if service in ["claude", "novaeus"]:
                data = await connection.recv()
                message_data = json.loads(data)
            elif service == "grok":
                async with connection.get(
                    f"{self.config['connections']['grok']['endpoint']}/messages"
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to receive message from Grok: {response.status}")
                    message_data = await response.json()
            
            # Verify signature if enabled
            if self.config["security"]["signature_verification"]:
                if not self._verify_signature(message_data):
                    raise ValueError("Invalid message signature")
            
            # Decrypt content if enabled
            if self.config["security"]["encryption_enabled"]:
                message_data["content"] = self._decrypt_message(message_data["content"])
            
            # Record success
            latency = time.time() - start_time
            self.health.record_message(True, latency)
            
            return Message(**message_data)
            
        except Exception as e:
            # Record failure
            latency = time.time() - start_time
            self.health.record_message(False, latency, str(e))
            self.logger.error(f"Failed to receive message from {service}: {e}")
            return None

    def _verify_signature(self, message_data: Dict) -> bool:
        """Verify message signature"""
        try:
            if "signature" not in message_data:
                return False
            
            content = json.dumps(message_data["content"])
            payload = {"content": content, "timestamp": message_data["timestamp"]}
            
            jwt.decode(
                message_data["signature"],
                self.encryption_key,
                algorithms=["HS256"]
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Signature verification failed: {e}")
            return False

    def _decrypt_message(self, encrypted_content: Dict) -> Dict:
        """Decrypt message content"""
        try:
            decrypted = self.fernet.decrypt(encrypted_content["encrypted"].encode())
            return json.loads(decrypted.decode())
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            raise

    async def shutdown(self):
        """Shutdown the AI Bridge system"""
        try:
            # Close all connections
            for service, connection in self.connections.items():
                if service in ["claude", "novaeus"]:
                    await connection.close()
                elif service == "grok":
                    await connection.close()
            
            # Close Redis connection
            if self.redis:
                self.redis.close()
                await self.redis.wait_closed()
            
            self.state = BridgeState.SHUTDOWN
            self.logger.info("AI Bridge system shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown failed: {e}")
            raise

    def get_health_status(self) -> Dict:
        """Get the current health status of the bridge"""
        return self.health.get_health_status()

    def get_rate_limit_status(self, service: str) -> Dict:
        """Get the current rate limit status for a service"""
        return self.health.get_rate_limit_status(service) 