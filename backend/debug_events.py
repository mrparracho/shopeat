#!/usr/bin/env python3
"""
Debug script to inspect RealtimeAgent events
"""

import asyncio
import os
from dotenv import load_dotenv
from agents.realtime import RealtimeAgent, RealtimeRunner, OpenAIRealtimeWebSocketModel

async def debug_events():
    """Debug all event types from RealtimeAgent"""
    
    print("🔍 Debugging RealtimeAgent events...")
    
    try:
        # Create agent and runner
        agent = RealtimeAgent(
            name="Debug Agent",
            instructions="Say hello back to the user."
        )
        runner = RealtimeRunner(
            starting_agent=agent,
            model=OpenAIRealtimeWebSocketModel()
        )
        
        print("✅ Agent and runner created")
        
        # Start session
        async with await runner.run() as session:
            print("📡 Session started")
            
            # Send message
            await session.send_message("Hello")
            print("📤 Message sent")
            
            # Collect all events
            events = []
            async for event in session:
                events.append(event)
                print(f"📨 Event: {event.type}")
                
                # Show event attributes
                attrs = [attr for attr in dir(event) if not attr.startswith('_')]
                print(f"   Attributes: {attrs}")
                
                # Show content if available
                if hasattr(event, 'content'):
                    print(f"   Content: {event.content}")
                
                # Stop after 10 events to see pattern
                if len(events) >= 10:
                    break
            
            print(f"\n📊 Total events collected: {len(events)}")
            print("Event types found:")
            for i, event in enumerate(events):
                print(f"  {i+1}. {event.type}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_events())
