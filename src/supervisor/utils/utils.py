# Utility functions for supervisor
from typing import List, Dict, Any
from django.conf import settings

from agents.utils.extract import extract_mineral_data
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Agent initialization and management
def create_supervisor_agent():
    """
    Create a langchain-based supervisor agent using either OpenAI or a local LLM server
    """
    try:
        # Check if we should use local LLM
        use_local_llm = settings.USE_LOCAL_LLM
        
        if use_local_llm:
            # Use local LLM server configuration
            llm = ChatOpenAI(
                model=settings.LOCAL_LLM_MODEL,
                temperature=0.7,
                openai_api_key=settings.LOCAL_LLM_API_KEY,
                openai_api_base=settings.LOCAL_LLM_BASE_URL
            )
            print("Using local LLM server")
        else:
            # Use OpenAI API
            llm = ChatOpenAI(
                model="gpt-4",
                temperature=0.7,
                api_key=settings.OPENAI_API_KEY,
            )
            print("Using OpenAI API")
        
        # Define the system message for the agent
        system_message = """
        You are a helpful Mineral Inventory Assistant. Your job is to help users with:
        
        1. Information about minerals, crystals, gemstones, and related topics.
        2. Assistance with cataloging and managing mineral collections.
        3. Providing guidance on mineral identification, characteristics, and value.
        
        Be informative, friendly, and concise in your responses.
        
        IMPORTANT: If the user provides information about a mineral, extract the relevant details and format them as a JSON object 
        enclosed between <MINERAL_DATA> and </MINERAL_DATA> tags at the end of your response.
        
        The JSON must be properly formatted with curly braces. For example:
        <MINERAL_DATA>
        {
          "title": "Emerald from Colombia",
          "minerals": ["Emerald", "Beryl"],
          "type": "gemstone",
          "pricing_type": "fixed",
          "currency": "USD",
          "starting_price": 200,
          "buy_now_price": 350,
          "height": 18,
          "width": 20,
          "depth": 2,
          "weight": 50
        }
        </MINERAL_DATA>
        
        The JSON should use these field names if the information is available:
        - title: The name or title of the mineral specimen
        - minerals: The minerals present in the specimen (as an array)
        - type: The type (crystal, gemstone, fossil, rock, meteorite)
        - pricing_type: Either "auction" or "fixed"
        - currency: The currency code (USD, EUR, GBP)
        - starting_price: The starting price for auction items or the regular price for fixed price items (numeric value)
        - reserve_price: The reserve price for auction items (numeric value)
        - buy_now_price: The buy now price (numeric value)
        - reserve_price_sale: Reserve price sale information
        - locality: The primary locality where the mineral was found
        - additional_locality: Additional locality information
        - special_characteristics: Special characteristics of the specimen
        - provenance: The provenance information
        - height: Height in mm (numeric value)
        - width: Width in mm (numeric value)
        - depth: Depth in mm (numeric value)
        - weight: Weight in grams (numeric value)
        - description: A description of the specimen
        
        SPECIAL INSTRUCTIONS:
        1. For PRICES: If a general price is mentioned, map it to either starting_price (for auctions) or buy_now_price (for fixed price) based on the pricing_type.
        2. For DIMENSIONS: If dimensions are mentioned in the format like "18x20x2mm", separate them into individual height, width, and depth fields.
        3. Always include numeric dimensions and weights as numeric values without units.
        4. Preserve information from previous exchanges when updating fields.
        
        Only include fields for which you have information. For price fields, always use numeric values (not strings), using 0 or null for unknown values. 
        Ensure the JSON is properly formatted with opening and closing braces.
        """
        
        # Create a simpler conversation history approach
        conversation_history = []
        
        def get_response(user_input):
            nonlocal conversation_history
            
            # Construct the full messages array with system message and conversation history
            messages = [SystemMessage(content=system_message)]
            messages.extend(conversation_history)
            messages.append(HumanMessage(content=user_input))
            
            # Get response from the model
            response = llm.invoke(messages)
            
            # Add the current exchange to history
            conversation_history.append(HumanMessage(content=user_input))
            conversation_history.append(AIMessage(content=response.content))
            
            # Keep history at a reasonable size (last 10 messages)
            if len(conversation_history) > 10:
                conversation_history = conversation_history[-10:]
                
            return response.content
        
        return get_response, conversation_history
        
    except Exception as e:
        print(f"Error creating supervisor agent: {str(e)}")
        # Fallback to a simple echo function if agent creation fails
        return None, None

def process_user_request(user_message: str, conversation_id: str = None, conversation_history: List[Dict] = None) -> Dict[str, Any]:
    """
    Process a user request and return a response using the supervisor agent
    """
    try:
        # Create a new agent instance
        get_response, agent_conversation_history = create_supervisor_agent()
        
        if get_response is None:
            return {
                "success": False,
                "reply": "I'm sorry, I'm having trouble processing your request right now.",
                "message_id": None
            }
        
        # If we have a client-provided conversation history, use it to initialize the agent
        if conversation_history and len(conversation_history) > 0:
            # Convert the conversation history format from the frontend to LangChain messages
            for message in conversation_history[:-1]:  # Exclude the latest user message which we'll send separately
                if message['role'] == 'user':
                    agent_conversation_history.append(HumanMessage(content=message['content']))
                elif message['role'] == 'assistant':
                    agent_conversation_history.append(AIMessage(content=message['content']))
        
        # Process the user message
        response_text = get_response(user_message)
        
        # Extract mineral data if present
        clean_response, mineral_data = extract_mineral_data(response_text)
        print(f"Clean response: {clean_response}")
        print(f"Mineral data: {mineral_data}")
        
        return {
            "success": True,
            "reply": clean_response,
            "message_id": hash(f"{conversation_id}_{user_message}"),  # Simple message ID generation
            "mineral_data": mineral_data
        }
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "reply": "I encountered an error while processing your request.",
            "message_id": None
        }
