"""
Create a new user
"""

import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from lef.models.database.user import User
from lef.models.user import UserRole, UserStatus
import bcrypt

# Database configuration
DATABASE_URL = "postgresql://user:password@localhost:5432/lef_db"

def create_user(username: str, email: str, password: str, role: UserRole = UserRole.USER):
    """Create a new user"""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check if user already exists
        existing_user = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            print(f"User with username '{username}' or email '{email}' already exists")
            sys.exit(1)

        # Create new user
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        user = User(
            username=username,
            email=email,
            hashed_password=hashed.decode(),
            role=role,
            status=UserStatus.ACTIVE
        )
        session.add(user)
        session.commit()

        print(f"User '{username}' created successfully")
    except Exception as e:
        session.rollback()
        print(f"Error creating user: {e}")
        sys.exit(1)
    finally:
        session.close()

def main():
    parser = argparse.ArgumentParser(description="Create a new user")
    parser.add_argument("username", help="Username")
    parser.add_argument("email", help="Email address")
    parser.add_argument("password", help="Password")
    parser.add_argument(
        "--role",
        choices=[role.value for role in UserRole],
        default=UserRole.USER.value,
        help="User role"
    )

    args = parser.parse_args()
    create_user(
        username=args.username,
        email=args.email,
        password=args.password,
        role=UserRole(args.role)
    )

if __name__ == "__main__":
    main() 