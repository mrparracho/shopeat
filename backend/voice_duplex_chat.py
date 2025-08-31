#!/usr/bin/env python3
"""
Full Duplex Voice Chat with OpenAI RealtimeAgent
This script enables real-time voice conversation with the agent.
"""

import asyncio
import os
import pyaudio
import wave
import threading
import time
import tempfile
from queue import Queue
from dotenv import load_dotenv
import speech_recognition as sr
from agents.realtime import RealtimeAgent, RealtimeRunner, OpenAIRealtimeWebSocketModel

# Load environment variables
load_dotenv()

class VoiceDuplexChat:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.recording = False
        self.playing = False
        
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        
        # Queues for audio data
        self.input_queue = Queue()
        self.output_queue = Queue()
        
        # Streams
        self.input_stream = None
        self.output_stream = None
        
        # Agent setup
        self.agent = None
        self.runner = None
        
    def setup_agent(self):
        """Initialize the RealtimeAgent"""
        print("🤖 Setting up RealtimeAgent...")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
            
        self.agent = RealtimeAgent(
            name="Voice Assistant",
            instructions="You are a helpful voice assistant. IMPORTANT: Always respond with voice (audio) in addition to text. Keep responses brief and conversational. Generate both text transcript and audio output for every response."
        )
        
        self.runner = RealtimeRunner(
            starting_agent=self.agent,
            model=OpenAIRealtimeWebSocketModel()
        )
        
        print("✅ Agent ready!")
        
    def start_audio_streams(self):
        """Start input and output audio streams"""
        print("🎤 Starting audio streams...")
        
        # Input stream (microphone)
        self.input_stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
            stream_callback=self.audio_input_callback
        )
        
        # Output stream (speakers)
        self.output_stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            output=True,
            frames_per_buffer=self.CHUNK,
            stream_callback=self.audio_output_callback
        )
        
        self.input_stream.start_stream()
        self.output_stream.start_stream()
        print("✅ Audio streams active!")
        
    def audio_input_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio input (microphone)"""
        if self.recording:
            self.input_queue.put(in_data)
        return (in_data, pyaudio.paContinue)
        
    def audio_output_callback(self, out_data, frame_count, time_info, status):
        """Callback for audio output (speakers)"""
        if not self.output_queue.empty():
            out_data = self.output_queue.get()
        else:
            # Silence if no audio to play
            out_data = b'\x00' * (frame_count * self.CHANNELS * 2)
        return (out_data, pyaudio.paContinue)
        
    def record_audio(self, duration=5):
        """Record audio for a specified duration"""
        print(f"🎤 Recording for {duration} seconds...")
        self.recording = True
        
        frames = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            if not self.input_queue.empty():
                data = self.input_queue.get()
                frames.append(data)
            time.sleep(0.01)
            
        self.recording = False
        print("✅ Recording complete!")
        
        # Combine all frames
        audio_data = b''.join(frames)
        return audio_data
        
    def play_audio(self, audio_data):
        """Play audio data through speakers"""
        print("🔊 Playing audio...")
        self.playing = True
        
        # Split audio into chunks and queue for playback
        chunk_size = self.CHUNK * self.CHANNELS * 2  # 2 bytes per sample
        
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            # Pad with silence if chunk is too small
            if len(chunk) < chunk_size:
                chunk += b'\x00' * (chunk_size - len(chunk))
            self.output_queue.put(chunk)
            
        # Wait for audio to finish playing
        while not self.output_queue.empty():
            time.sleep(0.01)
            
        self.playing = False
        print("✅ Audio playback complete!")
        
    def audio_to_text(self, audio_data):
        """Convert audio data to text using speech recognition"""
        print("🔍 Converting audio to text...")
        
        # Create a temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_filename = temp_file.name
            
        # Save audio as WAV file
        with wave.open(temp_filename, 'wb') as wav_file:
            wav_file.setnchannels(self.CHANNELS)
            wav_file.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wav_file.setframerate(self.RATE)
            wav_file.writeframes(audio_data)
            
        # Use speech recognition
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(temp_filename) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
                print(f"🎤 You said: '{text}'")
                
                # Clean up temp file
                os.unlink(temp_filename)
                return text
                
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            os.unlink(temp_filename)
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            os.unlink(temp_filename)
            return None
            
    async def chat_with_agent(self, user_audio):
        """Send audio to agent and get response"""
        # Convert audio to text first
        user_text = self.audio_to_text(user_audio)
        if not user_text:
            return None, "Could not understand audio"
            
        print("🤖 Sending text to agent...")
        
        # Create a new session for each interaction
        async with await self.runner.run() as session:
            # Send the text to the agent
            await session.send_message(user_text)
            
            # Collect the agent's response
            response_audio = b''
            full_transcript = ""
            
            async for event in session:
                print(f"   📨 Event: {event.type}")
                
                if event.type == "raw_model_event":
                    # Check for transcript deltas
                    if (hasattr(event, 'data') and 
                        hasattr(event.data, 'type') and 
                        event.data.type == "transcript_delta"):
                        if hasattr(event, 'data') and hasattr(event.data, 'delta'):
                            full_transcript += event.data.delta
                            print(f"   📝 Agent: {event.data.delta}")
                            
                elif event.type == "audio":
                    # Collect audio data for playback
                    if hasattr(event, 'data'):
                        response_audio += event.data
                        print(f"   🔊 Audio chunk: {len(event.data)} bytes")
                        
                elif event.type == "transcript_delta":
                    # Direct transcript events
                    if hasattr(event, 'delta'):
                        full_transcript += event.delta
                        print(f"   📝 Agent: {event.delta}")
                        
                # Stop when we have a complete response
                # Wait for both transcript and audio, or timeout
                if full_transcript and len(full_transcript) > 10:
                    # Give extra time for audio to arrive
                    await asyncio.sleep(1)
                    break
                    
                    print(f"🤖 Agent said: '{full_transcript.strip()}'")
        print(f"🔊 Total audio collected: {len(response_audio)} bytes")
        
        if len(response_audio) == 0:
            print("⚠️  No audio data received - checking event types...")
            # Let's see what events we actually got
            async with await self.runner.run() as debug_session:
                await debug_session.send_message("Debug: What events do you send?")
                event_count = 0
                async for event in debug_session:
                    event_count += 1
                    print(f"   🔍 Debug Event {event_count}: {event.type}")
                    if hasattr(event, 'data'):
                        print(f"      Data type: {type(event.data)}")
                        if hasattr(event.data, 'type'):
                            print(f"      Data.type: {event.data.type}")
                    if event_count >= 20:
                        break
        
        return response_audio, full_transcript
        
    async def voice_conversation_loop(self):
        """Main conversation loop"""
        print("🎙️  Starting voice conversation...")
        print("💡 Press Ctrl+C to stop")
        
        try:
            while True:
                # Record user input
                user_audio = self.record_audio(duration=5)
                
                if len(user_audio) > 1000:  # Only process if we got meaningful audio
                    print("🎵 Processing your voice...")
                    
                    # Send to agent and get response
                    response_audio, transcript = await self.chat_with_agent(user_audio)
                    
                    if response_audio:
                        # Play agent's response
                        self.play_audio(response_audio)
                    else:
                        print("❌ No audio response from agent")
                        
                    print("\n" + "="*50 + "\n")
                    
                else:
                    print("🔇 No voice detected, try again...")
                    
        except KeyboardInterrupt:
            print("\n👋 Ending conversation...")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up audio resources"""
        print("🧹 Cleaning up...")
        
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            
        self.audio.terminate()
        
        # No session to close - each interaction creates its own
            
        print("✅ Cleanup complete!")

async def main():
    """Main function"""
    print("=" * 60)
    print("🎙️  VOICE DUPLEX CHAT WITH REALTIME AGENT 🎙️")
    print("=" * 60)
    
    chat = VoiceDuplexChat()
    
    try:
        # Setup agent
        chat.setup_agent()
        
        # Start audio streams
        chat.start_audio_streams()
        
        # Start conversation
        await chat.voice_conversation_loop()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        chat.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
