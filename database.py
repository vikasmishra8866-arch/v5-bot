import aiosqlite

DB_NAME = "bot_database.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                points INTEGER DEFAULT 2
            )
        """)
        await db.commit()

async def get_or_create_user(user_id: int, username: str, first_name: str):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT points FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
        
        # New User - Give 2 Free Points
        await db.execute(
            "INSERT INTO users (user_id, username, first_name, points) VALUES (?, ?, ?, ?)",
            (user_id, username or "None", first_name, 2)
        )
        await db.commit()
        return 2

async def get_user_points(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT points FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def update_points(user_id: int, amount: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()

async def deduct_point(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET points = points - 1 WHERE user_id = ?", (user_id,))
        await db.commit()
