import os

from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

REDIS_PORT = 6379
REDIS_HOST = "localhost" if ENVIRONMENT == "development" else "redis-server"
