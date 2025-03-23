"""
Database model for users
"""

from sqlalchemy import Column, String, Enum, DateTime, Boolean, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from ..base import Base
from ..user import UserRole, UserStatus

# Association table for user permissions
user_permissions = Table(
    'user_permissions',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
    Column('permission', String)
)

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    last_activity = Column(DateTime)
    last_password_change = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    ip_address = Column(String)
    user_agent = Column(String)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String)
    password_reset_token = Column(String)
    password_reset_expires = Column(DateTime)
    api_keys = Column(JSON, default=list)
    session_tokens = Column(JSON, default=list)
    audit_log = Column(JSON, default=list)
    custom_fields = Column(JSON, default=dict)

    # Relationships
    permissions = relationship('Permission', secondary=user_permissions, back_populates='users')

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'last_password_change': self.last_password_change.isoformat() if self.last_password_change else None,
            'failed_login_attempts': self.failed_login_attempts,
            'locked_until': self.locked_until.isoformat() if self.locked_until else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'two_factor_enabled': self.two_factor_enabled,
            'api_keys': self.api_keys,
            'session_tokens': self.session_tokens,
            'audit_log': self.audit_log,
            'custom_fields': self.custom_fields,
            'permissions': [p.name for p in self.permissions]
        }

    @classmethod
    def from_dict(cls, data):
        """Create user from dictionary"""
        return cls(
            id=uuid.UUID(data['id']) if 'id' in data else uuid.uuid4(),
            username=data['username'],
            email=data['email'],
            hashed_password=data['hashed_password'],
            role=UserRole(data['role']) if 'role' in data else UserRole.VIEWER,
            status=UserStatus(data['status']) if 'status' in data else UserStatus.ACTIVE,
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.utcnow(),
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else datetime.utcnow(),
            last_login=datetime.fromisoformat(data['last_login']) if 'last_login' in data else None,
            last_activity=datetime.fromisoformat(data['last_activity']) if 'last_activity' in data else None,
            last_password_change=datetime.fromisoformat(data['last_password_change']) if 'last_password_change' in data else None,
            failed_login_attempts=data.get('failed_login_attempts', 0),
            locked_until=datetime.fromisoformat(data['locked_until']) if 'locked_until' in data else None,
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent'),
            two_factor_enabled=data.get('two_factor_enabled', False),
            two_factor_secret=data.get('two_factor_secret'),
            password_reset_token=data.get('password_reset_token'),
            password_reset_expires=datetime.fromisoformat(data['password_reset_expires']) if 'password_reset_expires' in data else None,
            api_keys=data.get('api_keys', []),
            session_tokens=data.get('session_tokens', []),
            audit_log=data.get('audit_log', []),
            custom_fields=data.get('custom_fields', {})
        ) 