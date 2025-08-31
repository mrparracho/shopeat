#!/usr/bin/env python3
"""
ShopEAT Backend - FastAPI server with OpenAI Agents SDK RealtimeAgent integration
Real-time speech-to-speech voice shopping assistant
"""

import os
import json
import logging
import base64
import io
import asyncio
from typing import Dict, Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
from agents.realtime import RealtimeAgent, RealtimeRunner
from dotenv import load_dotenv
from openai.realtime.models import OpenAIRealtimeWebSocketModel

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ShopEAT Backend",
    description="Real-time speech-to-speech shopping assistant with OpenAI Agents SDK",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.warning("OPENAI_API_KEY not found in environment variables")
    client = None
else:
    client = OpenAI(api_key=openai_api_key)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.agent_runners: Dict[str, RealtimeRunner] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    def get_agent_runner(self, client_id: str) -> RealtimeRunner:
        """Get or create a RealtimeRunner for a client"""
        if client_id not in self.agent_runners:
            # Create shopping assistant agent
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
            
            # Create the runner with the agent
            runner = RealtimeRunner(
                starting_agent=shopping_agent,
                model=OpenAIRealtimeWebSocketModel()
            )
            
            self.agent_runners[client_id] = runner
            logger.info(f"Created new RealtimeRunner for client {client_id}")
        
        return self.agent_runners[client_id]

    def remove_agent_runner(self, client_id: str):
        """Remove a client's agent runner when they disconnect"""
        if client_id in self.agent_runners:
            del self.agent_runners[client_id]
            logger.info(f"Removed RealtimeRunner for client {client_id}")

manager = ConnectionManager()

# Data models
class ShoppingItem(BaseModel):
    name: str
    quantity: int = 1
    category: str = "general"
    notes: str = ""

class VoiceMessage(BaseModel):
    text: str
    user_id: str
    session_id: str

# In-memory storage for PoC
shopping_list: List[ShoppingItem] = []
user_sessions: Dict[str, Any] = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "ShopEAT RealtimeAgent Backend is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "openai_configured": bool(openai_api_key),
        "openai_agents_available": "agents.realtime" in str(type(manager)),
        "active_connections": len(manager.active_connections),
        "active_runners": len(manager.agent_runners),
        "shopping_items": len(shopping_list)
    }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time voice communication with RealtimeAgent"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"Received from {client_id}: {message}")
            
            # Process message based on type
            if message.get("type") == "voice_input":
                # Handle voice input with RealtimeAgent
                response = await process_voice_input_with_agent(message, client_id)
                await manager.send_personal_message(
                    json.dumps(response), websocket
                )
            
            elif message.get("type") == "shopping_action":
                # Handle shopping actions
                response = await process_shopping_action(message, client_id)
                await manager.send_personal_message(
                    json.dumps(response), websocket
                )
            
            else:
                # Echo back for testing
                await manager.send_personal_message(
                    json.dumps({"type": "echo", "data": message}), websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        manager.remove_agent_runner(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
        manager.remove_agent_runner(client_id)

async def process_voice_input_with_agent(message: Dict[str, Any], client_id: str) -> Dict[str, Any]:
    """Process voice input using OpenAI Agents SDK RealtimeAgent"""
    try:
        if not openai_api_key:
            return {
                "type": "error",
                "message": "OpenAI API not configured. Please set OPENAI_API_KEY in your .env file"
            }
        
        # Extract text from the message
        user_text = message.get("text", "")
        
        if not user_text:
            return {
                "type": "error",
                "message": "No text received from frontend"
            }
        
        logger.info(f"Processing user input with RealtimeAgent: {user_text}")
        
        # Get the client's RealtimeRunner
        runner = manager.get_agent_runner(client_id)
        
        # Start a session and send the user input
        async with await runner.run() as session:
            # Send the user message to the session
            await session.send_message(user_text)
            
            # Process the agent's response
            async for event in session:
                if event.type == "agent_message":
                    # Extract the agent's response
                    ai_response = event.content
                    logger.info(f"RealtimeAgent response: {ai_response}")
                    
                    # Process shopping items mentioned in user text
                    await process_shopping_from_response(user_text, ai_response)
                    
                    # Convert AI response to speech
                    speech_audio = await text_to_speech(ai_response)
                    
                    return {
                        "type": "voice_response",
                        "transcribed_text": user_text,
                        "ai_response": ai_response,
                        "speech_audio": speech_audio,
                        "timestamp": message.get("timestamp")
                    }
        
        # Fallback if no agent message received
        return {
            "type": "error",
            "message": "No response received from RealtimeAgent"
        }
        
    except Exception as e:
        logger.error(f"Error processing voice input with RealtimeAgent: {e}")
        return {
            "type": "error",
            "message": f"Error processing voice input: {str(e)}"
        }

async def process_shopping_from_response(user_text: str, ai_response: str):
    """Process shopping items mentioned in user text and add them to the list"""
    try:
        # Simple item detection (in production, you'd use more sophisticated NLP)
        user_text_lower = user_text.lower()
        
        # Common shopping items
        items_to_add = []
        
        if 'milk' in user_text_lower:
            items_to_add.append(('milk', 1, 'dairy'))
        if 'bread' in user_text_lower:
            items_to_add.append(('bread', 1, 'bakery'))
        if 'eggs' in user_text_lower:
            items_to_add.append(('eggs', 1, 'dairy'))
        if 'cheese' in user_text_lower:
            items_to_add.append(('cheese', 1, 'dairy'))
        if 'butter' in user_text_lower:
            items_to_add.append(('butter', 1, 'dairy'))
        if 'banana' in user_text_lower or 'bananas' in user_text_lower:
            items_to_add.append(('bananas', 1, 'produce'))
        if 'apple' in user_text_lower or 'apples' in user_text_lower:
            items_to_add.append(('apples', 1, 'produce'))
        if 'chicken' in user_text_lower:
            items_to_add.append(('chicken', 1, 'meat'))
        if 'beef' in user_text_lower:
            items_to_add.append(('beef', 1, 'meat'))
        if 'rice' in user_text_lower:
            items_to_add.append(('rice', 1, 'pantry'))
        if 'pasta' in user_text_lower:
            items_to_add.append(('pasta', 1, 'pantry'))
        
        # Add detected items to shopping list
        for name, quantity, category in items_to_add:
            # Check if item already exists
            existing_item = next((item for item in shopping_list if item.name.lower() == name.lower()), None)
            if not existing_item:
                new_item = ShoppingItem(name=name, quantity=quantity, category=category)
                shopping_list.append(new_item)
                logger.info(f"Added {name} to shopping list")
        
        # Update the shopping list in the response
        if items_to_add:
            logger.info(f"Added {len(items_to_add)} items to shopping list")
            
    except Exception as e:
        logger.error(f"Error processing shopping items: {e}")

async def text_to_speech(text: str) -> str:
    """Convert text to speech using OpenAI TTS"""
    try:
        if not client:
            return ""
        
        # Use OpenAI's TTS API
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
            input=text
        )
        
        # Convert the audio to base64 for transmission
        audio_bytes = response.content
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return audio_base64
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return ""

async def process_shopping_action(message: Dict[str, Any], client_id: str) -> Dict[str, Any]:
    """Process shopping-related actions"""
    action = message.get("action")
    
    if action == "add_item":
        item_data = message.get("item", {})
        item = ShoppingItem(**item_data)
        shopping_list.append(item)
        
        # Create voice confirmation
        confirmation_text = f"Added {item.name} to your shopping list"
        speech_audio = await text_to_speech(confirmation_text)
        
        return {
            "type": "shopping_update",
            "action": "item_added",
            "item": item.dict(),
            "total_items": len(shopping_list),
            "speech_audio": speech_audio,
            "message": confirmation_text
        }
    
    elif action == "get_list":
        return {
            "type": "shopping_list",
            "items": [item.dict() for item in shopping_list],
            "total_items": len(shopping_list)
        }
    
    elif action == "clear_list":
        shopping_list.clear()
        
        # Create voice confirmation
        confirmation_text = "Your shopping list has been cleared"
        speech_audio = await text_to_speech(confirmation_text)
        
        return {
            "type": "shopping_update",
            "action": "list_cleared",
            "total_items": 0,
            "speech_audio": speech_audio,
            "message": confirmation_text
        }
    
    else:
        return {
            "type": "error",
            "message": f"Unknown action: {action}"
        }

@app.get("/api/shopping-list")
async def get_shopping_list():
    """Get current shopping list"""
    return {"items": [item.dict() for item in shopping_list]}

@app.post("/api/shopping-list")
async def add_shopping_item(item: ShoppingItem):
    """Add item to shopping list"""
    shopping_list.append(item)
    return {"message": "Item added", "item": item.dict()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )