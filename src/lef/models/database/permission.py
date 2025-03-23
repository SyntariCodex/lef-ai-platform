"""
Database model for permissions
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from ..base import Base

class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    category = Column(String)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    approval_level = Column(Integer, default=1)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('permissions.id'))
    metadata = Column(JSON, default=dict)

    # Relationships
    parent = relationship('Permission', remote_side=[id], backref='children')
    users = relationship('User', secondary='user_permissions', back_populates='permissions')

    def to_dict(self):
        """Convert permission to dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'requires_approval': self.requires_approval,
            'approval_level': self.approval_level,
            'parent_id': str(self.parent_id) if self.parent_id else None,
            'metadata': self.metadata,
            'children': [child.to_dict() for child in self.children]
        }

    @classmethod
    def from_dict(cls, data):
        """Create permission from dictionary"""
        return cls(
            id=uuid.UUID(data['id']) if 'id' in data else uuid.uuid4(),
            name=data['name'],
            description=data.get('description'),
            category=data.get('category'),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.utcnow(),
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else datetime.utcnow(),
            is_active=data.get('is_active', True),
            requires_approval=data.get('requires_approval', False),
            approval_level=data.get('approval_level', 1),
            parent_id=uuid.UUID(data['parent_id']) if 'parent_id' in data and data['parent_id'] else None,
            metadata=data.get('metadata', {})
        )

    def has_child(self, permission_name: str) -> bool:
        """Check if permission has a child with the given name"""
        return any(child.name == permission_name for child in self.children)

    def get_child(self, permission_name: str) -> Optional['Permission']:
        """Get child permission by name"""
        for child in self.children:
            if child.name == permission_name:
                return child
        return None

    def add_child(self, permission: 'Permission') -> bool:
        """Add a child permission"""
        if not self.has_child(permission.name):
            permission.parent_id = self.id
            return True
        return False

    def remove_child(self, permission_name: str) -> bool:
        """Remove a child permission by name"""
        for child in self.children:
            if child.name == permission_name:
                child.parent_id = None
                return True
        return False

    def get_all_children(self) -> List['Permission']:
        """Get all child permissions recursively"""
        children = []
        for child in self.children:
            children.append(child)
            children.extend(child.get_all_children())
        return children

    def get_all_parents(self) -> List['Permission']:
        """Get all parent permissions recursively"""
        parents = []
        current = self.parent
        while current:
            parents.append(current)
            current = current.parent
        return parents

    def is_child_of(self, permission_name: str) -> bool:
        """Check if permission is a child of the given permission name"""
        return any(parent.name == permission_name for parent in self.get_all_parents())

    def is_parent_of(self, permission_name: str) -> bool:
        """Check if permission is a parent of the given permission name"""
        return any(child.name == permission_name for child in self.get_all_children()) 