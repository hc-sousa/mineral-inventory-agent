from rest_framework.views import APIView
from rest_framework.response import Response
from agents.minerals_agent.agent import create_chromadb_client

class TestMineralsAgentView(APIView):
    def get(self, request):
        try:
            client = create_chromadb_client()
            collection = client.get_or_create_collection(name="minerals")
            sample_id = "1"
            sample_doc = {"name": "Quartz", "hardness": 7}
            
            # ChromaDB expects documents to be strings
            # Store the actual data as metadata and use a text summary as the document
            collection.add(
                documents=["Quartz mineral with hardness of 7"],  # Document content as string
                metadatas=[sample_doc],  # Store full data as metadata
                ids=[sample_id]
            )
            
            docs = collection.get(ids=[sample_id])  # Changed from query={"ids": [sample_id]}
            return Response({"status": "success", "document": docs})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"status": "error", "error": str(e)}, status=500)