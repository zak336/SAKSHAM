"""Seed tenant module entitlements for existing tenants.

Revision ID: 0005
Revises: 0004
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Ensure every existing tenant has a settings row.
    op.execute(
        sa.text(
            """
            INSERT INTO tenant_settings (tenant_id)
            SELECT id
            FROM tenants
            ON CONFLICT (tenant_id) DO NOTHING
            """
        )
    )

    # Give every existing tenant an explicit entitlement row
    # for every active module.
    #
    # Core modules are enabled.
    # Optional modules are disabled until explicitly subscribed.
    op.execute(
        sa.text(
            """
            INSERT INTO tenant_modules (
                id,
                tenant_id,
                module_id,
                enabled,
                config,
                enabled_at,
                disabled_at
            )
            SELECT
                gen_random_uuid(),
                t.id,
                m.id,
                m.is_core,
                '{}'::jsonb,
                CASE
                    WHEN m.is_core THEN NOW()
                    ELSE NULL
                END,
                CASE
                    WHEN m.is_core THEN NULL
                    ELSE NOW()
                END
            FROM tenants t
            CROSS JOIN modules m
            WHERE m.is_active = TRUE
            ON CONFLICT (tenant_id, module_id) DO NOTHING
            """
        )
    )


def downgrade() -> None:
    # Remove only entitlement rows created for currently existing tenants.
    # Do not remove the module catalog itself.
    op.execute(
        sa.text(
            """
            DELETE FROM tenant_modules
            WHERE tenant_id IN (
                SELECT id FROM tenants
            )
            """
        )
    )