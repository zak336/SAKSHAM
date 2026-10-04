"""Run Alembic migration with explicit database URL"""
import os
import sys
from alembic import command
from alembic.config import Config

# Set Railway DATABASE_URL
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:ZkmAEoIlwhSsacQnkLEQHzgDqTrGPgqb@junction.proxy.rlwy.net:24287/railway"

# Create Alembic config
alembic_cfg = Config("alembic.ini")

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "current"
    
    if action == "current":
        command.current(alembic_cfg, verbose=True)
    elif action == "history":
        command.history(alembic_cfg, verbose=True)
    elif action == "upgrade":
        target = sys.argv[2] if len(sys.argv) > 2 else "head"
        command.upgrade(alembic_cfg, target)
    elif action == "downgrade":
        target = sys.argv[2] if len(sys.argv) > 2 else "-1"
        command.downgrade(alembic_cfg, target)
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
