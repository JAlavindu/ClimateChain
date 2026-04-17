import pymongo
import os

class MongoManager:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="climate_chain"):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db["transactions"]
        
    def setup_indexes(self):
        """Creates indexes on common querying fields for faster aggregation."""
        print("Setting up MongoDB indexes...")
        # Create an index on the items array for fast subset queries
        self.collection.create_index([("ITEMS", pymongo.ASCENDING)])
        
        # Create compound index for spatial-temporal querying (useful for the OLAP part later)
        self.collection.create_index([
            ("STATE", pymongo.ASCENDING), 
            ("YEAR", pymongo.ASCENDING),
            ("MONTH", pymongo.ASCENDING)
        ])
        print("Indexes created.")

    def insert_transactions(self, transactions_data: list):
        """Inserts a list of dictionaries into the collection."""
        if transactions_data:
            self.collection.insert_many(transactions_data)
            print(f"Inserted {len(transactions_data)} documents into NoSQL database.")
            
    def clear_database(self):
        """Drops the collection for fresh ingestion."""
        self.collection.drop()