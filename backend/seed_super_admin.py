"""
Run once after setting up the database to create the first Super Admin login.

Usage:
    cd backend
    python seed_super_admin.py
"""

from app.database.session import SessionLocal
from app.models.user import User, Role
from app.auth.security import hash_password

def seed():
    db = SessionLocal()
    try:
        super_admin_role = db.query(Role).filter(Role.role_name == "super_admin").first()
        if not super_admin_role:
            print("ERROR: roles table is empty. Run database/schema.sql first.")
            return

        existing = db.query(User).filter(User.username == "superadmin").first()
        if existing:
            print("Super admin already exists. Skipping.")
            return

        admin = User(
            role_id=super_admin_role.role_id,
            full_name="Super Administrator",
            email="superadmin@shaheenschool.edu.pk",
            username="superadmin",
            password_hash=hash_password("ChangeMe@123"),  # CHANGE THIS after first login
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print("Super admin created successfully.")
        print("   Username: superadmin")
        print("   Password: ChangeMe@123  (please change this immediately)")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
