"""One-time seed script: creates the demo-college tenant and a super_admin user.
Run inside the container:
  docker compose exec api python scripts/seed_superadmin.py
"""

import asyncio
import uuid

from sqlalchemy import text

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.modules.colleges.models import College
from app.modules.entitlements import service as entitlements_service
from app.modules.tenants.models import Tenant
from app.modules.users.models import User, UserRole


async def main() -> None:
    async with AsyncSessionLocal() as db:
        # ── Tenant ────────────────────────────────────────────────────────
        tenant_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
        existing = await db.execute(
            text("SELECT id FROM tenants WHERE slug = 'demo-college'")
        )
        if existing.scalar_one_or_none() is None:
            tenant = Tenant(
                id=tenant_id,
                name="Demo College",
                slug="demo-college",
                is_active=True,
            )
            db.add(tenant)
            await db.flush()
            print("Created tenant: demo-college")
        else:
            print("Tenant demo-college already exists — skipping.")

        # ── Default college ───────────────────────────────────────────────
        college_id = uuid.UUID("00000000-0000-0000-0000-000000000101")
        existing_college = await db.execute(
            text("SELECT id FROM colleges WHERE tenant_id = :tenant_id AND slug = 'demo-college'"),
            {"tenant_id": tenant_id},
        )
        existing_college_id = existing_college.scalar_one_or_none()
        if existing_college_id is None:
            college = College(
                id=college_id,
                tenant_id=tenant_id,
                name="Demo College",
                code="DEMO",
                slug="demo-college",
                is_active=True,
            )
            db.add(college)
            await db.flush()
            print("Created college: demo-college")
        else:
            college_id = existing_college_id
            print("College demo-college already exists — skipping.")

        # ── Super admin ───────────────────────────────────────────────────
        user_id = uuid.UUID("00000000-0000-0000-0000-000000000002")
        existing_user = await db.execute(
            text("SELECT id FROM users WHERE email = 'admin@demo-college.com'")
        )
        if existing_user.scalar_one_or_none() is None:
            user = User(
                id=user_id,
                tenant_id=tenant_id,
                name="Super Admin",
                email="admin@demo-college.com",
                password_hash=hash_password("Admin@123"),
                role=UserRole.super_admin,
                is_active=True,
            )
            db.add(user)
            await db.flush()
            print("Created user: admin@demo-college.com / Admin@123")
        else:
            print("User admin@demo-college.com already exists — skipping.")

        # Initialize tenant settings and module entitlements.
        await entitlements_service.initialize_tenant(db, tenant_id)
        await db.commit()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
