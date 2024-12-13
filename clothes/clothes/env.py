import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Your MongoDB settings
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'clothes_fit')
MONGO_DB_HOST = os.getenv('MONGO_DB_HOST', 'localhost')    
MONGO_DB_PORT = int(os.getenv('MONGO_DB_PORT', 27017))
MONGO_DB_USERNAME = os.getenv('MONGO_DB_USERNAME', 'root')
MONGO_DB_PASSWORD = os.getenv('MONGO_DB_PASSWORD', '1234')  
