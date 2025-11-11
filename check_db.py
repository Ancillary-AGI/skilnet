#!/usr/bin/env python3
"""Check database tables and status"""

import sys
import os
sys.path.append('backend')

try:
    from backend.app.core.database import engine
    from sqlalchemy import text

    print("🔍 Checking database tables...")

    # Check if tables exist
    result = engine.execute(text('SELECT name FROM sqlite_master WHERE type="table"'))
    tables = [row[0] for row in result.fetchall()]

    print(f"📊 Found {len(tables)} tables:")
    for table in sorted(tables):
        print(f"  - {table}")

    # Check alembic version
    try:
        result = engine.execute(text('SELECT version_num FROM alembic_version'))
        version = result.fetchone()
        if version:
            print(f"🔖 Alembic version: {version[0]}")
        else:
            print("⚠️  No alembic version found")
    except Exception as e:
        print(f"⚠️  Could not check alembic version: {e}")

    print("✅ Database check complete")

except Exception as e:
    print(f"❌ Database check failed: {e}")
    import traceback
    traceback.print_exc()
