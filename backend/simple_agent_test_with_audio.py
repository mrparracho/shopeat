#!/usr/bin/env python3
"""
Simple test script for OpenAI Agents SDK RealtimeAgent WITH AUDIO PLAYBACK
This will actually play the agent's voice responses so you can hear them!
"""

import asyncio
import os
import tempfile
from dotenv import load_dotenv
from agents.realtime import RealtimeAgent, RealtimeRunner, OpenAIRealtimeWebSocketModel

# Load environment variables
load_dotenv()

async def test_agent_with_audio():
    """Test RealtimeAgent with actual audio playback"""
    
    print("🎵 Testing RealtimeAgent with AUDIO PLAYBACK...")
    
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
            instructions="You are a helpful assistant. Keep responses brief and friendly. Respond in English."
        )
        print("✅ Agent created")
        
        # Create runner
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
            print("🎧 You should hear the agent speak!")
            
            event_count = 0
            full_transcript = ""
            audio_chunks = []
            
            async for event in session:
                event_count += 1
                print(f"📨 Event {event_count}: type={event.type}")
                
                # Capture audio data
                if event.type == "audio":
                    if hasattr(event, 'data'):
                        audio_chunks.append(event.data)
                        print(f"   🔊 Audio chunk received ({len(event.data)} bytes)")
                
                # Capture transcript deltas from raw_model_event data
                elif event.type == "raw_model_event":
                    if hasattr(event, 'data') and hasattr(event.data, 'type') and event.data.type == "transcript_delta":
                        if hasattr(event.data, 'delta'):
                            full_transcript += event.data.delta
                            print(f"   📝 Transcript: {event.data.delta}")
                # Also check direct transcript_delta events
                elif event.type == "transcript_delta":
                    if hasattr(event, 'delta'):
                        full_transcript += event.delta
                        print(f"   📝 Transcript: {event.delta}")
                    elif hasattr(event, 'data') and hasattr(event.data, 'delta'):
                        full_transcript += event.data.delta
                        print(f"   📝 Transcript: {event.data.delta}")
                
                # Show other event details
                elif hasattr(event, 'content') and event.content:
                    print(f"   Content: {event.content}")
                elif hasattr(event, 'data') and event.data:
                    print(f"   Data: {event.data}")
                
                # Stop after 50 events to avoid infinite loop
                if event_count >= 50:
                    print("⚠️  Stopping after 50 events")
                    break
            
            # Show final results
            if full_transcript:
                print(f"\n🤖 Agent responded: '{full_transcript}'")
                print(f"🎵 Audio chunks received: {len(audio_chunks)}")
                
                # Try to play audio if we have chunks
                if audio_chunks:
                    print("🔊 Attempting to play audio...")
                    await play_audio_chunks(audio_chunks)
                
                return True
            else:
                print("❌ No transcript received from RealtimeAgent")
                return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def play_audio_chunks(audio_chunks):
    """Attempt to play the audio chunks"""
    try:
        # Combine all audio chunks
        combined_audio = b''.join(audio_chunks)
        print(f"🎵 Combined audio: {len(combined_audio)} bytes")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(combined_audio)
            temp_file_path = temp_file.name
        
        print(f"💾 Audio saved to: {temp_file_path}")
        print("🎧 To hear the audio, you can:")
        print("   1. Open the file in an audio player")
        print("   2. Use: afplay " + temp_file_path)
        print("   3. Or install pygame/pyaudio for real-time playback")
        
        # Try to play with system command
        try:
            import subprocess
            result = subprocess.run(['afplay', temp_file_path], capture_output=True, timeout=5)
            if result.returncode == 0:
                print("✅ Audio played successfully!")
            else:
                print("⚠️  Audio playback failed, but file was saved")
        except Exception as e:
            print(f"⚠️  Couldn't auto-play: {e}")
            print("💡 Check the saved audio file manually")
        
    except Exception as e:
        print(f"❌ Error processing audio: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🎵 REALTIME AGENT TEST WITH AUDIO PLAYBACK 🎵")
    print("=" * 60)
    
    success = asyncio.run(test_agent_with_audio())
    
    if success:
        print("\n🎉 SUCCESS! Agent communication working with audio!")
    else:
        print("\n💥 FAILED! Check the errors above.")
    
    print("=" * 60)
