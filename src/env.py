from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# --- MongoDB Configuration ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "DungeonCoreDB")  # Default database name