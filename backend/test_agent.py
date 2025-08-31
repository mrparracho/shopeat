#!/usr/bin/env python3
"""
Test script for OpenAI Agents SDK RealtimeAgent functionality
"""

import asyncio
import os
from dotenv import load_dotenv
from agents.realtime import RealtimeAgent, RealtimeRunner

# Load environment variables
load_dotenv()

async def test_realtime_agent():
    """Test the RealtimeAgent functionality"""
    
    # Check if OpenAI API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return False
    
    try:
        # Create a shopping assistant agent
        shopping_agent = RealtimeAgent(
            name="Shopping Assistant",
            instructions="""You are a helpful, conversational shopping assistant. Your role is to:
            1. Help users build their shopping list through natural conversation
            2. Provide helpful shopping recommendations
            3. Keep responses natural, brief, and focused on shopping
            4. Ask follow-up questions to understand what else they need
            5. Be friendly and encouraging
            
            When users mention items, acknowledge that you're adding them and ask what else they need.
            Keep the conversation flowing naturally."""
        )
        
        print("✅ RealtimeAgent created successfully")
        
        # Create a runner with the agent
        runner = RealtimeRunner(
            starting_agent=shopping_agent
        )
        
        print("✅ RealtimeRunner created successfully")
        
        # Test with a simple input
        test_input = "I need milk and bread"
        print(f"\n🧪 Testing with input: '{test_input}'")
        
        # Start a session and send the user input
        async with await runner.run() as session:
            # Send the user message to the session
            await session.send_message(test_input)
            
            # Process the agent's response
            response_count = 0
            async for event in session:
                if event.type == "agent_message":
                    print(f"🤖 Agent response: {event.content}")
                    response_count += 1
                    break  # Just get the first response for testing
        
        if response_count > 0:
            print("✅ RealtimeAgent responded successfully!")
            return True
        else:
            print("❌ No response received from RealtimeAgent")
            return False
            
    except Exception as e:
        print(f"❌ Error testing RealtimeAgent: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing OpenAI Agents SDK RealtimeAgent...")
    success = asyncio.run(test_realtime_agent())
    
    if success:
        print("\n🎉 All tests passed! RealtimeAgent is working correctly.")
    else:
        print("\n💥 Tests failed. Please check the error messages above.")
