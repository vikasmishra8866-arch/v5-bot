import aiosqlite

DB_NAME = "bot_database.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                points INTEGER DEFAULT 0
            )
        ''')
        await db.commit()

async def get_or_create_user(user_id: int, username: str, first_name: str) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT points FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row is not None:
                return row[0]
            else:
                # Default 0 points on start
                await db.execute(
                    "INSERT INTO users (user_id, username, first_name, points) VALUES (?, ?, ?, ?)",
                    (user_id, username, first_name, 0)
                )
                await db.commit()
                return 0

async def get_user_points(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT points FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row is not None else 0

async def update_points(user_id: int, points_to_add: int):
    async with aiosqlite.connect(DB_NAME) as db:
        # Check if user exists first
        async with db.execute("SELECT points FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
        if row is not None:
            await db.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (points_to_add, user_id))
        else:
            await db.execute("INSERT INTO users (user_id, username, first_name, points) VALUES (?, ?, ?, ?)", (user_id, "", "", points_to_add))
        await db.commit()

async def deduct_point(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET points = MAX(0, points - 1) WHERE user_id = ?", (user_id,))
        await db.commit()
