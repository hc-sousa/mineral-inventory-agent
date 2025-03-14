# Utility functions for supervisor
import os
import re
import json
from typing import List, Dict, Any
from django.conf import settings

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough

# Agent initialization and management
def create_supervisor_agent():
    """
    Create a langchain-based supervisor agent using either OpenAI or a local LLM server
    """
    try:
        # Check if we should use local LLM
        use_local_llm = getattr(settings, 'USE_LOCAL_LLM', False)
        
        if use_local_llm:
            # Use local LLM server configuration
            llm = ChatOpenAI(
                model=getattr(settings, 'LOCAL_LLM_MODEL', 'gpt-4'),
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
          "type": "gemstone"
        }
        </MINERAL_DATA>
        
        The JSON should use these field names if the information is available:
        - title: The name or title of the mineral specimen
        - minerals: The minerals present in the specimen (as an array)
        - type: The type (crystal, gemstone, fossil, rock, meteorite)
        - pricing_type: Either "auction" or "fixed"
        - currency: The currency code (USD, EUR, GBP)
        - starting_price: The starting price for auction items
        - reserve_price: The reserve price for auction items
        - buy_now_price: The buy now price
        - reserve_price_sale: Reserve price sale information
        - locality: The primary locality where the mineral was found
        - additional_locality: Additional locality information
        - special_characteristics: Special characteristics of the specimen
        - provenance: The provenance information
        - height: Height in mm
        - width: Width in mm
        - depth: Depth in mm
        - weight: Weight in grams
        - description: A description of the specimen
        
        Only include fields for which you have information. Use null for empty fields. Ensure the JSON is properly formatted with opening and closing braces.
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

def extract_mineral_data(response_text):
    """
    Extract structured mineral data from the response text if present
    """
    pattern = r'<MINERAL_DATA>(.*?)</MINERAL_DATA>'
    match = re.search(pattern, response_text, re.DOTALL)
    
    if match:
        try:
            # Extract the JSON string
            json_str = match.group(1).strip()
            
            # Ensure the JSON string is properly formatted with curly braces
            if not json_str.startswith("{"):
                json_str = "{" + json_str
            if not json_str.endswith("}"):
                json_str = json_str + "}"
                
            # Clean up the JSON string
            json_str = json_str.replace("\n", "").replace("\r", "")
            
            # Attempt to parse the JSON string
            try:
                mineral_data = json.loads(json_str)
            except json.JSONDecodeError:
                # If still failing, try to clean up more aggressively
                json_str = re.sub(r'\s+', ' ', json_str)
                json_str = json_str.replace('": ', '":"').replace(', "', '","')
                json_str = json_str.replace('null', 'null"')
                json_str = json_str.replace(':"null"', ':null')
                mineral_data = json.loads(json_str)
            
            # Get the entire matched text (including tags)
            full_match = match.group(0)
            
            # Remove the entire match from the response text
            clean_response = response_text.replace(full_match, '').strip()
            
            print("Extracted JSON string:", json_str)
            print("Parsed mineral data:", mineral_data)
            print("Original length:", len(response_text), "Cleaned length:", len(clean_response))
            
            return clean_response, mineral_data
        except Exception as e:
            print(f"Error processing mineral data: {str(e)}")
            print(f"Problematic JSON string: {json_str if 'json_str' in locals() else 'Not extracted'}")
            # Return the original text without the tags in case of an error
            clean_response = re.sub(pattern, '', response_text, flags=re.DOTALL).strip()
            return clean_response, {}
    
    return response_text, {}

def process_user_request(user_message: str, conversation_id: str = None) -> Dict[str, Any]:
    """
    Process a user request and return a response using the supervisor agent
    """
    try:
        # In a real implementation, you might want to retrieve or create a persistent 
        # agent instance based on the conversation_id
        get_response, conversation_history = create_supervisor_agent()
        
        if get_response is None:
            return {
                "success": False,
                "reply": "I'm sorry, I'm having trouble processing your request right now.",
                "message_id": None
            }
        
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
