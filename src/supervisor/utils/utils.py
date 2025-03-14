# Utility functions for supervisor
import os
from typing import List, Dict, Any
from django.conf import settings

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain.memory import ConversationBufferMemory

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
        response = get_response(user_message)
        
        return {
            "success": True,
            "reply": response,
            "message_id": hash(f"{conversation_id}_{user_message}")  # Simple message ID generation
        }
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "reply": "I encountered an error while processing your request.",
            "message_id": None
        }
