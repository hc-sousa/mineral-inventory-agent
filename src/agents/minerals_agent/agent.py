import os
import chromadb
from django.conf import settings

def create_chromadb_client():
    persist_dir = settings.CHROMADB_PERSIST_DIRECTORY
    client = chromadb.PersistentClient(path=persist_dir)
    return client

def main():
    client = create_chromadb_client()
    collection = client.get_or_create_collection(name="minerals")
    print("ChromaDB client initialized. 'minerals' collection is ready.")

    sample_doc = {"name": "Quartz", "hardness": 7}
    
    # Update to use the proper ChromaDB parameter structure
    collection.add(
        documents=["Quartz mineral with hardness of 7"],
        metadatas=[sample_doc],
        ids=["1"]
    )
    print("Added sample mineral:", sample_doc)

    # Updated the get method to use ids parameter
    docs = collection.get(ids=["1"])
    print("Retrieved document:", docs)

if __name__ == "__main__":
    main()
