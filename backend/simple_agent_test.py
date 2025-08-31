#!/usr/bin/env python3
"""
Simple test script for OpenAI Agents SDK RealtimeAgent
Just basic communication - no shopping logic
"""

import asyncio
import os
from dotenv import load_dotenv
from agents.realtime import RealtimeAgent, RealtimeRunner, OpenAIRealtimeWebSocketModel

# Load environment variables
load_dotenv()

async def test_simple_agent():
    """Test basic RealtimeAgent communication"""
    
    print("🚀 Testing basic RealtimeAgent communication...")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        print("Please set your OpenAI API key in a .env file or environment variable")
        return
    
    print("✅ OpenAI API key found")
    
    try:
        # Create a simple agent
        agent = RealtimeAgent(
            name="Test Agent",
            instructions="You are a helpful assistant. Keep responses brief and friendly."
        )
        print("✅ Agent created")
        
        # Create runner with OpenAIRealtimeWebSocketModel
        runner = RealtimeRunner(
            starting_agent=agent,
            model=OpenAIRealtimeWebSocketModel()
        )
        print("✅ Runner created")
        
        # Test communication
        test_message = "Hello! How are you today?"
        print(f"\n🧪 Sending message: '{test_message}'")
        
        # Start session and send message
        async with await runner.run() as session:
            print("📡 Session started, sending message...")
            await session.send_message(test_message)
            
            print("🔄 Waiting for response...")
            event_count = 0
            full_transcript = ""
            async for event in session:
                event_count += 1
                print(f"📨 Event {event_count}: type={event.type}")
                
                # Show more details for certain event types
                if hasattr(event, 'content') and event.content:
                    print(f"   Content: {event.content}")
                if hasattr(event, 'data') and event.data:
                    print(f"   Data: {event.data}")
                
                # Capture transcript deltas
                if event.type == "transcript_delta":
                    if hasattr(event, 'delta'):
                        full_transcript += event.delta
                        print(f"   Transcript: {event.delta}")
                
                # Stop after 50 events to avoid infinite loop
                if event_count >= 50:
                    print("⚠️  Stopping after 50 events")
                    break
            
            if full_transcript:
                print(f"🤖 Agent responded: {full_transcript}")
                return True
            else:
                print("❌ No transcript received from RealtimeAgent")
                return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("SIMPLE REALTIME AGENT TEST")
    print("=" * 50)
    
    success = asyncio.run(test_simple_agent())
    
    if success:
        print("\n🎉 SUCCESS! Agent communication working!")
    else:
        print("\n💥 FAILED! Check the errors above.")
    
    print("=" * 50)
