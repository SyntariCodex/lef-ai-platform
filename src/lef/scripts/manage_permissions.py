"""
Manage permissions for a user
"""

import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from lef.models.database.user import User
from lef.models.database.permission import Permission

# Database configuration
DATABASE_URL = "postgresql://user:password@localhost:5432/lef_db"

def list_user_permissions(username: str):
    """List permissions for a user"""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            print(f"User '{username}' not found")
            sys.exit(1)

        print(f"\nPermissions for user '{username}':")
        print("-" * 50)
        for permission in user.permissions:
            print(f"- {permission.name} ({permission.category})")
            if permission.description:
                print(f"  Description: {permission.description}")
            if permission.requires_approval:
                print(f"  Requires approval (Level: {permission.approval_level})")
    except Exception as e:
        print(f"Error listing permissions: {e}")
        sys.exit(1)
    finally:
        session.close()

def add_permission(username: str, permission_name: str):
    """Add a permission to a user"""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            print(f"User '{username}' not found")
            sys.exit(1)

        permission = session.query(Permission).filter(Permission.name == permission_name).first()
        if not permission:
            print(f"Permission '{permission_name}' not found")
            sys.exit(1)

        if permission in user.permissions:
            print(f"User '{username}' already has permission '{permission_name}'")
            sys.exit(1)

        user.permissions.append(permission)
        session.commit()
        print(f"Added permission '{permission_name}' to user '{username}'")
    except Exception as e:
        session.rollback()
        print(f"Error adding permission: {e}")
        sys.exit(1)
    finally:
        session.close()

def remove_permission(username: str, permission_name: str):
    """Remove a permission from a user"""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            print(f"User '{username}' not found")
            sys.exit(1)

        permission = session.query(Permission).filter(Permission.name == permission_name).first()
        if not permission:
            print(f"Permission '{permission_name}' not found")
            sys.exit(1)

        if permission not in user.permissions:
            print(f"User '{username}' does not have permission '{permission_name}'")
            sys.exit(1)

        user.permissions.remove(permission)
        session.commit()
        print(f"Removed permission '{permission_name}' from user '{username}'")
    except Exception as e:
        session.rollback()
        print(f"Error removing permission: {e}")
        sys.exit(1)
    finally:
        session.close()

def list_all_permissions():
    """List all available permissions"""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        permissions = session.query(Permission).all()
        print("\nAvailable permissions:")
        print("-" * 50)
        for permission in permissions:
            print(f"- {permission.name} ({permission.category})")
            if permission.description:
                print(f"  Description: {permission.description}")
            if permission.requires_approval:
                print(f"  Requires approval (Level: {permission.approval_level})")
    except Exception as e:
        print(f"Error listing permissions: {e}")
        sys.exit(1)
    finally:
        session.close()

def main():
    parser = argparse.ArgumentParser(description="Manage user permissions")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List permissions for a user
    list_parser = subparsers.add_parser("list", help="List permissions for a user")
    list_parser.add_argument("username", help="Username")

    # Add permission to a user
    add_parser = subparsers.add_parser("add", help="Add a permission to a user")
    add_parser.add_argument("username", help="Username")
    add_parser.add_argument("permission", help="Permission name")

    # Remove permission from a user
    remove_parser = subparsers.add_parser("remove", help="Remove a permission from a user")
    remove_parser.add_argument("username", help="Username")
    remove_parser.add_argument("permission", help="Permission name")

    # List all available permissions
    subparsers.add_parser("list-all", help="List all available permissions")

    args = parser.parse_args()

    if args.command == "list":
        list_user_permissions(args.username)
    elif args.command == "add":
        add_permission(args.username, args.permission)
    elif args.command == "remove":
        remove_permission(args.username, args.permission)
    elif args.command == "list-all":
        list_all_permissions()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 