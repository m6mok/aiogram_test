from aiosqlite import connect as aiosqlite_connect

from src.utils import Singleton


INIT_QUERY = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER UNIQUE,
        name TEXT,
        age INTEGER
    )
'''
ADD_USER_QUERY = '''
    INSERT OR IGNORE INTO users (user_id, name, age) 
    VALUES (?, ?, ?)
'''
GET_USERS_QUERY = 'SELECT user_id, name, age FROM users'


class Database(Singleton):
    def __init__(self, path: str):
        self.path = path

    async def init(self):
        async with aiosqlite_connect(self.path) as db:
            await db.execute(INIT_QUERY)
            await db.commit()

    async def add_user(self, user_id: int, name: str, age: int):
        async with aiosqlite_connect(self.path) as db:
            await db.execute(ADD_USER_QUERY, (user_id, name, age))
            await db.commit()

    async def get_users(self):
        async with aiosqlite_connect(self.path) as db:
            async with db.execute(GET_USERS_QUERY) as cursor:
                users = await cursor.fetchall()
                return users
