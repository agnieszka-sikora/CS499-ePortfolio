import os
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
import hashlib

class AnimalShelter:
    
    # CRUD operations and user management for the Animal Shelter database.
    
    def __init__(
        self,
        USER: str = None,
        PASS: str = None,
        HOST: str = None,
        PORT: int = None,
        DB: str = None,
        COL: str = None
    ):
        
        # Initialize MongoDB connection.
   
        self.USER = USER or os.getenv('AAC_USER', 'aacuser')
        self.PASS = PASS or os.getenv('AAC_PASS', 'SNHU1234')
        self.HOST = HOST or os.getenv('AAC_HOST', 'localhost')
        self.PORT = PORT or int(os.getenv('AAC_PORT', 27017))
        self.DB = DB or os.getenv('AAC_DB', 'AAC')
        self.COL = COL or os.getenv('AAC_COL', 'animals')

        try:
            self.client = MongoClient(
                f'mongodb://{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}',
                serverSelectionTimeoutMS=5000
            )
            self.database = self.client[self.DB]
            self.collection = self.database[self.COL]
            # Ensure unique index on username for users collection
            self.database['users'].create_index('username', unique=True)
            # Test connection
            self.client.admin.command('ping')
        except errors.PyMongoError as e:
            raise Exception(f"Could not connect to MongoDB: {e}")

    # Insert a new document into the collection.
    def create(self, data: dict) -> bool:
        if not data:
            raise ValueError("Nothing to save, because data parameter is empty")
        result = self.collection.insert_one(data)
        return bool(result.inserted_id)

    # Read documents matching searchData from the collection.
    def read(self, searchData: dict) -> list:
        if searchData is None:
            raise ValueError("Nothing to find, searchData is None")
        return list(self.collection.find(searchData))

    # Update documents matching searchData with updateData.
    def update(self, searchData: dict, updateData: dict) -> dict:
        if not searchData or not updateData:
            raise ValueError("Both searchData and updateData are required")
        result = self.collection.update_many(searchData, {"$set": updateData})
        return result.raw_result

    # Delete documents matching deleteData from the collection.
    def delete(self, deleteData: dict) -> dict:
        if not deleteData:
            raise ValueError("Nothing to delete, deleteData is empty")
        result = self.collection.delete_many(deleteData)
        return result.raw_result
    
    # User management methods
    def _hash_password(self, password: str) -> str:
        salt = os.getenv('AAC_SALT', 'static_salt')
        return hashlib.sha256((salt + password).encode('utf-8')).hexdigest()

    # Register a new user with a hashed password.
    def register_user(self, username: str, password: str) -> tuple:
        if not username or not password:
            return False, "Username and password required."
        try:
            hashed_pw = self._hash_password(password)
            self.database['users'].insert_one({'username': username, 'password': hashed_pw})
            return True, "User registered successfully."
        except errors.DuplicateKeyError:
            return False, "Username already exists."
        except Exception as e:
            return False, f"Registration failed: {e}"
    
    # Authenticate a user by checking the hashed password.
    def login_user(self, username: str, password: str) -> tuple:
        if not username or not password:
            return False, "Username and password required."
        hashed_pw = self._hash_password(password)
        user = self.database['users'].find_one({'username': username, 'password': hashed_pw})
        if user:
            return True, "Login successful."
        else:
            return False, "Invalid username or password."

if __name__ == "__main__":
    animal = AnimalShelter()
 


    

