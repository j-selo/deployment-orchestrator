import os
import psycopg

async def get_db():
    # Connect to the database using the URL from environment variables
    return await psycopg.AsyncConnection.connect(
        os.environ["DATABASE_URL"]
    )