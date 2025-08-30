#!/usr/bin/env python3
"""
ShopEAT Backend - FastAPI server with OpenAI Agent SDK integration
"""

import os
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ShopEAT Backend",
    description="Real-time voice shopping assistant backend",
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
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logger.warning("OPENAI_API_KEY not found in environment variables")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

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

manager = ConnectionManager()

# Data models
class ShoppingItem(BaseModel):
    name: str
    quantity: int = 1
    category: str = "general"
    notes: str = ""

class VoiceMessage(BaseModel):
    audio_data: str  # Base64 encoded audio
    user_id: str
    session_id: str

# In-memory storage for PoC
shopping_list: list[ShoppingItem] = []
user_sessions: Dict[str, Any] = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "ShopEAT Backend is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "openai_configured": bool(openai.api_key),
        "active_connections": len(manager.active_connections),
        "shopping_items": len(shopping_list)
    }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time voice communication"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"Received from {client_id}: {message}")
            
            # Process message based on type
            if message.get("type") == "voice_input":
                # Handle voice input
                response = await process_voice_input(message, client_id)
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
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

async def process_voice_input(message: Dict[str, Any], client_id: str) -> Dict[str, Any]:
    """Process voice input using OpenAI"""
    try:
        if not openai.api_key:
            return {
                "type": "error",
                "message": "OpenAI API not configured"
            }
        
        # Extract audio data and convert to text (simplified for PoC)
        # In production, you'd use OpenAI's Whisper API here
        audio_data = message.get("audio_data", "")
        
        # For PoC, we'll simulate voice processing
        # In production, this would be:
        # response = openai.Audio.transcribe("whisper-1", audio_file)
        
        simulated_text = "I need to buy milk and bread"
        
        # Process with OpenAI for shopping assistance
        ai_response = await get_shopping_assistance(simulated_text, client_id)
        
        return {
            "type": "voice_response",
            "transcribed_text": simulated_text,
            "ai_response": ai_response,
            "timestamp": message.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Error processing voice input: {e}")
        return {
            "type": "error",
            "message": f"Error processing voice input: {str(e)}"
        }

async def get_shopping_assistance(text: str, client_id: str) -> str:
    """Get shopping assistance from OpenAI"""
    try:
        # Create a simple prompt for shopping assistance
        prompt = f"""
        You are a helpful shopping assistant. The user said: "{text}"
        
        Please provide helpful shopping guidance. Keep it brief and practical.
        If they mentioned items, suggest quantities and any related items they might need.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful shopping assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return "I'm having trouble connecting to my AI assistant right now. Please try again."

async def process_shopping_action(message: Dict[str, Any], client_id: str) -> Dict[str, Any]:
    """Process shopping-related actions"""
    action = message.get("action")
    
    if action == "add_item":
        item_data = message.get("item", {})
        item = ShoppingItem(**item_data)
        shopping_list.append(item)
        return {
            "type": "shopping_update",
            "action": "item_added",
            "item": item.dict(),
            "total_items": len(shopping_list)
        }
    
    elif action == "get_list":
        return {
            "type": "shopping_list",
            "items": [item.dict() for item in shopping_list],
            "total_items": len(shopping_list)
        }
    
    elif action == "clear_list":
        shopping_list.clear()
        return {
            "type": "shopping_update",
            "action": "list_cleared",
            "total_items": 0
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
