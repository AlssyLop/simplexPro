import aiosqlite
import os

DB_PATH = "simplexPro.db"

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    await db.execute("PRAGMA foreign_keys = ON")
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()

async def init_db():
    if not os.path.exists(DB_PATH):
        with open("simplexPro.sql", "r") as f:
            sql = f.read()
        async with aiosqlite.connect(DB_PATH) as db:
            await db.executescript(sql)
            await db.commit()
