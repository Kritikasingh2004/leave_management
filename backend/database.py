import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGO_DETAILS"))
db = client.get_database("leave_system")

users_collection = db.get_collection("users")
leaves_collection = db.get_collection("leaves")