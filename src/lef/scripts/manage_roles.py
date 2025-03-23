"""
Manage user roles
"""

import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from lef.models.database.user import User
from lef.models.user import UserRole, UserStatus

# Database configuration
DATABASE_URL = "postgresql://user:password@localhost:5432/lef_db"

def list_users_by_role(role: UserRole):
    """List users with a specific role"""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        users = session.query(User).filter(User.role == role).all()
        print(f"\nUsers with role '{role.value}':")
        print("-" * 50)
        for user in users:
            print(f"- {user.username} ({user.email})")
            print(f"  Status: {user.status.value}")
            print(f"  Created: {user.created_at}")
            if user.last_login:
                print(f"  Last login: {user.last_login}")
    except Exception as e:
        print(f"Error listing users: {e}")
        sys.exit(1)
    finally:
        session.close()

def change_user_role(username: str, new_role: UserRole):
    """Change a user's role"""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            print(f"User '{username}' not found")
            sys.exit(1)

        old_role = user.role
        user.role = new_role
        session.commit()
        print(f"Changed role for user '{username}' from '{old_role.value}' to '{new_role.value}'")
    except Exception as e:
        session.rollback()
        print(f"Error changing role: {e}")
        sys.exit(1)
    finally:
        session.close()

def list_all_roles():
    """List all available roles"""
    print("\nAvailable roles:")
    print("-" * 50)
    for role in UserRole:
        print(f"- {role.value}")

def main():
    parser = argparse.ArgumentParser(description="Manage user roles")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List users by role
    list_parser = subparsers.add_parser("list", help="List users with a specific role")
    list_parser.add_argument("role", choices=[role.value for role in UserRole], help="Role")

    # Change user role
    change_parser = subparsers.add_parser("change", help="Change a user's role")
    change_parser.add_argument("username", help="Username")
    change_parser.add_argument("role", choices=[role.value for role in UserRole], help="New role")

    # List all available roles
    subparsers.add_parser("list-all", help="List all available roles")

    args = parser.parse_args()

    if args.command == "list":
        list_users_by_role(UserRole(args.role))
    elif args.command == "change":
        change_user_role(args.username, UserRole(args.role))
    elif args.command == "list-all":
        list_all_roles()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 