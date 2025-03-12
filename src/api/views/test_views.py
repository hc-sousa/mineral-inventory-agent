from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ParseError
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

class TestAgentChatView(APIView):
    """Test endpoint for chatting with the minerals agent"""
    
    def __init__(self):
        super().__init__()
        # Store chat history in memory for testing purposes
        self.chat_history = []
    
    def post(self, request):
        """Send a message to the agent and get a response"""
        try:
            # Explicitly check for valid JSON content
            if not request.data:
                return Response({
                    "status": "error", 
                    "error": "No JSON data provided. Expected format: {'message': 'your question here'}"
                }, status=400)
            
            message = request.data.get('message', '')
            if not message:
                return Response({
                    "status": "error", 
                    "error": "No message provided. Include 'message' field in your JSON request."
                }, status=400)
            
            # Simple mock response for testing
            mineral_keywords = ["quartz", "calcite", "feldspar", "mica", "mineral", "rock", "crystal"]
            
            if any(keyword in message.lower() for keyword in mineral_keywords):
                agent_response = f"This is a test response about minerals related to: '{message}'. In the future, this will be handled by the actual agent."
            else:
                agent_response = f"I'm a mineral expert assistant. I can help with mineral information. Your query: '{message}' doesn't seem to be about minerals."
                
            # Update chat history
            self.chat_history.append({"role": "user", "content": message})
            self.chat_history.append({"role": "agent", "content": agent_response})
            
            return Response({
                "status": "success",
                "response": agent_response,
                "chat_history": self.chat_history
            })
        except ParseError as e:
            return Response({
                "status": "error", 
                "error": "Invalid JSON format. Please send a properly formatted JSON request.",
                "detail": str(e)
            }, status=400)
        except Exception as e:
            import traceback
            return Response({
                "status": "error", 
                "error": str(e), 
                "traceback": traceback.format_exc()
            }, status=500)
    
    def get(self, request):
        """Get the current chat history"""
        return Response({
            "status": "success",
            "chat_history": self.chat_history
        })
    
    def delete(self, request):
        """Clear the chat history and reset the conversation"""
        self.chat_history = []
        return Response({
            "status": "success", 
            "message": "Chat history cleared"
        })

class TestMineralQueryView(APIView):
    """Test endpoint for specific mineral queries"""
    
    def post(self, request):
        """Query for specific mineral information"""
        try:
            mineral_name = request.data.get('mineral_name', '')
            query_type = request.data.get('query_type', 'general')
            
            if not mineral_name:
                return Response({"status": "error", "error": "No mineral name provided"}, status=400)
                
            # Connect to the database
            client = create_chromadb_client()
            collection = client.get_or_create_collection(name="minerals")
            
            # Form query based on query_type
            query_text = f"Information about {mineral_name}"
            if query_type == "hardness":
                query_text = f"What is the hardness of {mineral_name}?"
            elif query_type == "composition":
                query_text = f"What is the chemical composition of {mineral_name}?"
                
            # Query the database
            results = collection.query(
                query_texts=[query_text],
                n_results=3
            )
            
            return Response({
                "status": "success",
                "mineral": mineral_name,
                "query_type": query_type,
                "results": results
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"status": "error", "error": str(e)}, status=500)