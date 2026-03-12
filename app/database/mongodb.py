from motor.motor_asyncio import AsyncIOMotorClient 

client = None
db = None

async def connect_to_mongodb(uri, db_name):
    global client, db
    client = AsyncIOMotorClient(uri)
    db = client[db_name]
    await db.metadata.create_index("url", unique=True)

async def disconnect_from_mongodb():
    global client, db
    if client:
        client.close()
    client = None
    db = None

def get_database():
    if db is None:
        raise Exception("Database is not connected yet.")
    return db