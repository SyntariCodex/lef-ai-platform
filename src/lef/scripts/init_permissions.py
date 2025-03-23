"""
Initialize database with default permissions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from lef.models.database.permission import Permission
from lef.models.database.user import User
from lef.models.user import UserRole, UserStatus
import bcrypt

# Database configuration
DATABASE_URL = "postgresql://user:password@localhost:5432/lef_db"

# Default permissions
DEFAULT_PERMISSIONS = [
    {
        "name": "admin",
        "description": "Full system access",
        "category": "system",
        "requires_approval": False,
        "approval_level": 1,
        "children": [
            {
                "name": "manage_users",
                "description": "Manage user accounts",
                "category": "users",
                "requires_approval": True,
                "approval_level": 2,
                "children": [
                    {
                        "name": "create_users",
                        "description": "Create new users",
                        "category": "users",
                        "requires_approval": True,
                        "approval_level": 2
                    },
                    {
                        "name": "edit_users",
                        "description": "Edit user accounts",
                        "category": "users",
                        "requires_approval": True,
                        "approval_level": 2
                    },
                    {
                        "name": "delete_users",
                        "description": "Delete user accounts",
                        "category": "users",
                        "requires_approval": True,
                        "approval_level": 3
                    }
                ]
            },
            {
                "name": "manage_permissions",
                "description": "Manage system permissions",
                "category": "permissions",
                "requires_approval": True,
                "approval_level": 2,
                "children": [
                    {
                        "name": "create_permissions",
                        "description": "Create new permissions",
                        "category": "permissions",
                        "requires_approval": True,
                        "approval_level": 2
                    },
                    {
                        "name": "edit_permissions",
                        "description": "Edit permissions",
                        "category": "permissions",
                        "requires_approval": True,
                        "approval_level": 2
                    },
                    {
                        "name": "delete_permissions",
                        "description": "Delete permissions",
                        "category": "permissions",
                        "requires_approval": True,
                        "approval_level": 3
                    }
                ]
            },
            {
                "name": "manage_system",
                "description": "Manage system settings",
                "category": "system",
                "requires_approval": True,
                "approval_level": 2,
                "children": [
                    {
                        "name": "view_logs",
                        "description": "View system logs",
                        "category": "system",
                        "requires_approval": True,
                        "approval_level": 2
                    },
                    {
                        "name": "manage_backups",
                        "description": "Manage system backups",
                        "category": "system",
                        "requires_approval": True,
                        "approval_level": 3
                    }
                ]
            }
        ]
    },
    {
        "name": "manager",
        "description": "Team management access",
        "category": "team",
        "requires_approval": False,
        "approval_level": 1,
        "children": [
            {
                "name": "manage_team",
                "description": "Manage team members",
                "category": "team",
                "requires_approval": True,
                "approval_level": 2,
                "children": [
                    {
                        "name": "view_team",
                        "description": "View team information",
                        "category": "team",
                        "requires_approval": False,
                        "approval_level": 1
                    },
                    {
                        "name": "edit_team",
                        "description": "Edit team information",
                        "category": "team",
                        "requires_approval": True,
                        "approval_level": 2
                    }
                ]
            }
        ]
    },
    {
        "name": "user",
        "description": "Standard user access",
        "category": "general",
        "requires_approval": False,
        "approval_level": 1,
        "children": [
            {
                "name": "view_dashboard",
                "description": "View dashboard",
                "category": "general",
                "requires_approval": False,
                "approval_level": 1
            },
            {
                "name": "manage_profile",
                "description": "Manage own profile",
                "category": "profile",
                "requires_approval": False,
                "approval_level": 1
            }
        ]
    }
]

def create_permission_tree(permission_data, parent=None, session=None):
    """Create permission tree recursively"""
    permission = Permission(
        name=permission_data["name"],
        description=permission_data["description"],
        category=permission_data["category"],
        requires_approval=permission_data["requires_approval"],
        approval_level=permission_data["approval_level"]
    )
    session.add(permission)
    session.flush()

    if parent:
        parent.children.append(permission)

    for child_data in permission_data.get("children", []):
        create_permission_tree(child_data, permission, session)

def init_database():
    """Initialize database with default permissions and admin user"""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create default permissions
        for permission_data in DEFAULT_PERMISSIONS:
            create_permission_tree(permission_data, session=session)

        # Create default admin user
        admin_password = "admin123"  # Should be changed on first login
        hashed = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt())
        admin = User(
            username="admin",
            email="admin@lef.ai",
            hashed_password=hashed.decode(),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        session.add(admin)
        session.commit()

        print("Database initialized successfully")
    except Exception as e:
        session.rollback()
        print(f"Error initializing database: {e}")
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    init_database() 