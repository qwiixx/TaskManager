import asyncpg
from typing import Optional, Any, List
from contextlib import asynccontextmanager

class Database:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5432,
        user: str = "postgres",
        password: str = "",
        database: str = "postgres",
    ):
        self._db_params = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }
        self._conn: Optional[asyncpg.Connection] = None

    async def connect(self) -> None:
        """Establish a connection to the database."""
        if not self._conn or self._conn.is_closed():
            try:
                self._conn = await asyncpg.connect(**self._db_params)
            except asyncpg.PostgresError as e:
                raise ConnectionError(f"Failed to connect to database: {str(e)}")

    async def disconnect(self) -> None:
        """Close the database connection."""
        if self._conn and not self._conn.is_closed():
            try:
                await self._conn.close()
            except asyncpg.PostgresError as e:
                raise ConnectionError(f"Failed to disconnect from database: {str(e)}")
            finally:
                self._conn = None

    @asynccontextmanager
    async def transaction(self):
        """Provide a context manager for database transactions."""
        if not self._conn or self._conn.is_closed():
            await self.connect()
        async with self._conn.transaction():
            yield
            await self._conn.commit()

    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """Execute a query and return all rows."""
        if not self._conn or self._conn.is_closed():
            await self.connect()
        try:
            return await self._conn.fetch(query, *args)
        except asyncpg.PostgresError as e:
            await self.disconnect()
            raise RuntimeError(f"Query execution failed: {str(e)}")

    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Execute a query and return the first row."""
        if not self._conn or self._conn.is_closed():
            await self.connect()
        try:
            return await self._conn.fetchrow(query, *args)
        except asyncpg.PostgresError as e:
            await self.disconnect()
            raise RuntimeError(f"Query execution failed: {str(e)}")

    async def fetchval(self, query: str, *args) -> Any:
        """Execute a query and return the first column of the first row."""
        if not self._conn or self._conn.is_closed():
            await self.connect()
        try:
            return await self._conn.fetchval(query, *args)
        except asyncpg.PostgresError as e:
            await self.disconnect()
            raise RuntimeError(f"Query execution failed: {str(e)}")

    async def execute(self, query: str, *args) -> str:
        """Execute a command (e.g., INSERT, UPDATE, DELETE) and return the result status."""
        if not self._conn or self._conn.is_closed():
            await self.connect()
        try:
            return await self._conn.execute(query, *args)
        except asyncpg.PostgresError as e:
            await self.disconnect()
            raise RuntimeError(f"Command execution failed: {str(e)}")

    # Optional: Allow using the class as an async context manager
    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.disconnect()