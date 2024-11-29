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

# mongosh --host 172.31.42.144 --port 27017 -u root -p 1234 --authenticationDatabase admin 
# mongosh --host 0.0.0.0 --port 27017 -u root -p 1234 --authenticationDatabase admin

# mongosh (for your mongodb EC2 instance)
# use admin
# db.createUser({
#     user: "root",
#     pwd: "1234",
#     roles: [
#         { role: "userAdminAnyDatabase", db: "admin" },
#         { role: "readWriteAnyDatabase", db: "admin" }
#     ]
# })