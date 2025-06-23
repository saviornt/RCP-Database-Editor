"""
MongoDB handler for RCP Database Editor.
"""
from pymongo import MongoClient, errors
from typing import Optional, Any

class MongoDBHandler:
    """Handles MongoDB connections and operations."""
    def __init__(self, uri: str, db_name: str, username: Optional[str] = None, password: Optional[str] = None) -> None:
        self.uri = uri
        self.db_name = db_name
        self.username = username
        self.password = password
        self.client: Optional[MongoClient] = None
        self.db = None

    def connect(self) -> bool:
        try:
            if self.username and self.password:
                self.client = MongoClient(
                    self.uri,
                    username=self.username,
                    password=self.password
                )
            else:
                self.client = MongoClient(self.uri)
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            print(f"Successfully connected to MongoDB: {self.db_name}")
            return True
        except errors.ConnectionFailure as e:
            print(f"MongoDB connection failed: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred during MongoDB connection: {e}")
            return False

    def close(self) -> None:
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")

    def insert_documents(self, collection_name: str, documents: list[dict]) -> tuple[bool, str]:
        if self.db is None:
            if not self.connect():
                return False, "Not connected to MongoDB."
        try:
            collection = self.db[collection_name]
            if not documents:
                return False, "No documents to insert."
            result = collection.insert_many(documents)
            print(f"Inserted {len(result.inserted_ids)} documents into '{collection_name}' collection.")
            return True, f"Successfully inserted {len(result.inserted_ids)} documents."
        except errors.PyMongoError as e:
            print(f"Error inserting documents: {e}")
            return False, f"Error inserting documents: {e}"
        except Exception as e:
            print(f"An unexpected error occurred during document insertion: {e}")
            return False, f"An unexpected error occurred: {e}"

    def delete_document(self, collection_name: str, document_id: Any) -> tuple[bool, str]:
        """Delete a document by _id from the specified collection."""
        if self.db is None:
            if not self.connect():
                return False, "Not connected to MongoDB."
        try:
            result = self.db[collection_name].delete_one({'_id': document_id})
            if result.deleted_count > 0:
                print(f"Deleted document {document_id} from '{collection_name}' collection.")
                return True, f"Deleted document {document_id}."
            else:
                return False, f"Document {document_id} not found."
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False, str(e)

    def update_document(self, collection_name: str, document_id: Any, new_data: dict) -> tuple[bool, str]:
        """Update a document by _id in the specified collection."""
        if self.db is None:
            if not self.connect():
                return False, "Not connected to MongoDB."
        try:
            result = self.db[collection_name].update_one({'_id': document_id}, {'$set': new_data})
            if result.modified_count > 0:
                print(f"Updated document {document_id} in '{collection_name}' collection.")
                return True, f"Updated document {document_id}."
            else:
                return False, f"Document {document_id} not found or no changes made."
        except Exception as e:
            print(f"Error updating document: {e}")
            return False, str(e)