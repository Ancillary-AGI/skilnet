import asyncio
import os
import sys
sys.path.insert(0, 'backend')
os.environ['DB_TYPE'] = 'sqlite'
os.environ['SQLITE_PATH'] = ':memory:'
os.environ['SECRET_KEY'] = 'test-secret-key'
os.environ['DEBUG'] = 'true'
os.environ['TESTING'] = 'true'

async def test_db():
    from app.core.database import init_database, create_tables, AsyncSessionLocal
    await init_database()
    await create_tables()
    async with AsyncSessionLocal() as session:
        result = await session.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = result.fetchall()
        print('Tables:', [table[0] for table in tables])

if __name__ == "__main__":
    asyncio.run(test_db())
