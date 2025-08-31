#!/usr/bin/env python3
"""
ShopEAT CLI - Command-line shopping assistant using OpenAI Agents SDK RealtimeAgent
Real-time conversational AI shopping experience
"""

import os
import asyncio
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from agents.realtime import RealtimeAgent, RealtimeRunner

# Load environment variables
load_dotenv()

class ShoppingItem:
    def __init__(self, name: str, quantity: int = 1, category: str = "general", notes: str = ""):
        self.name = name
        self.quantity = quantity
        self.category = category
        self.notes = notes
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "quantity": self.quantity,
            "category": self.category,
            "notes": self.notes
        }
    
    def __str__(self) -> str:
        return f"• {self.name} (x{self.quantity}) - {self.category}"

class ShoppingList:
    def __init__(self):
        self.items: List[ShoppingItem] = []
    
    def add_item(self, name: str, quantity: int = 1, category: str = "general", notes: str = ""):
        # Check if item already exists
        existing_item = next((item for item in self.items if item.name.lower() == name.lower()), None)
        if existing_item:
            existing_item.quantity += quantity
            print(f"✅ Updated quantity of {name} to {existing_item.quantity}")
        else:
            new_item = ShoppingItem(name, quantity, category, notes)
            self.items.append(new_item)
            print(f"✅ Added {name} to shopping list")
    
    def remove_item(self, name: str):
        self.items = [item for item in self.items if item.name.lower() != name.lower()]
        print(f"🗑️  Removed {name} from shopping list")
    
    def clear_list(self):
        self.items.clear()
        print("🧹 Shopping list cleared")
    
    def display(self):
        if not self.items:
            print("📝 Your shopping list is empty")
            return
        
        print("\n🛒 ** YOUR SHOPPING LIST **")
        print("=" * 40)
        
        # Group by category
        categories = {}
        for item in self.items:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)
        
        for category, items in categories.items():
            print(f"\n📂 {category.upper()}:")
            for item in items:
                print(f"  {item}")
        
        print(f"\n📊 Total items: {len(self.items)}")
        print("=" * 40)

class ShoppingAssistant:
    def __init__(self):
        self.shopping_list = ShoppingList()
        self.conversation_history = []
        
        # Check OpenAI API key
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            print("❌ OPENAI_API_KEY not found in environment variables")
            print("Please create a .env file with your OpenAI API key")
            return
        
        # Create the RealtimeAgent
        self.agent = RealtimeAgent(
            name="Shopping Assistant",
            instructions="""You are a helpful, conversational shopping assistant. Your role is to:
            1. Help users build their shopping list through natural conversation
            2. Provide helpful shopping recommendations and suggestions
            3. Keep responses natural, brief, and focused on shopping
            4. Ask follow-up questions to understand what else they need
            5. Be friendly, encouraging, and conversational
            6. Help organize items by categories (dairy, produce, meat, pantry, etc.)
            7. Suggest quantities when appropriate
            8. Ask if they need anything else after each addition
            
            When users mention items, acknowledge that you're adding them and ask what else they need.
            Keep the conversation flowing naturally and be genuinely helpful.
            
            Remember: You're having a real conversation, not just processing commands."""
        )
        
        # Create the RealtimeRunner
        self.runner = RealtimeRunner(
            starting_agent=self.agent
        )
        
        print("🤖 Shopping Assistant initialized successfully!")
    
    async def chat(self, user_input: str) -> str:
        """Chat with the RealtimeAgent"""
        try:
            # Start a session and send the user input
            async with await self.runner.run() as session:
                # Send the user message to the session
                await session.send_message(user_input)
                
                # Process the agent's response
                async for event in session:
                    if event.type == "agent_message":
                        ai_response = event.content
                        return ai_response
                
                return "I didn't receive a response from the agent."
                
        except Exception as e:
            return f"Error communicating with agent: {str(e)}"
    
    def process_shopping_items(self, user_text: str):
        """Process shopping items mentioned in user text"""
        user_text_lower = user_text.lower()
        
        # Common shopping items with categories
        items_to_add = []
        
        # Dairy
        if 'milk' in user_text_lower:
            items_to_add.append(('milk', 1, 'dairy'))
        if 'cheese' in user_text_lower:
            items_to_add.append(('cheese', 1, 'dairy'))
        if 'butter' in user_text_lower:
            items_to_add.append(('butter', 1, 'dairy'))
        if 'yogurt' in user_text_lower:
            items_to_add.append(('yogurt', 1, 'dairy'))
        if 'cream' in user_text_lower:
            items_to_add.append(('cream', 1, 'dairy'))
        
        # Produce
        if 'banana' in user_text_lower or 'bananas' in user_text_lower:
            items_to_add.append(('bananas', 1, 'produce'))
        if 'apple' in user_text_lower or 'apples' in user_text_lower:
            items_to_add.append(('apples', 1, 'produce'))
        if 'tomato' in user_text_lower or 'tomatoes' in user_text_lower:
            items_to_add.append(('tomatoes', 1, 'produce'))
        if 'lettuce' in user_text_lower:
            items_to_add.append(('lettuce', 1, 'produce'))
        if 'carrot' in user_text_lower or 'carrots' in user_text_lower:
            items_to_add.append(('carrots', 1, 'produce'))
        
        # Meat
        if 'chicken' in user_text_lower:
            items_to_add.append(('chicken', 1, 'meat'))
        if 'beef' in user_text_lower:
            items_to_add.append(('beef', 1, 'meat'))
        if 'pork' in user_text_lower:
            items_to_add.append(('pork', 1, 'meat'))
        if 'fish' in user_text_lower:
            items_to_add.append(('fish', 1, 'meat'))
        
        # Bakery
        if 'bread' in user_text_lower:
            items_to_add.append(('bread', 1, 'bakery'))
        if 'bagel' in user_text_lower or 'bagels' in user_text_lower:
            items_to_add.append(('bagels', 1, 'bakery'))
        if 'croissant' in user_text_lower or 'croissants' in user_text_lower:
            items_to_add.append(('croissants', 1, 'bakery'))
        
        # Pantry
        if 'rice' in user_text_lower:
            items_to_add.append(('rice', 1, 'pantry'))
        if 'pasta' in user_text_lower:
            items_to_add.append(('pasta', 1, 'pantry'))
        if 'oil' in user_text_lower:
            items_to_add.append(('cooking oil', 1, 'pantry'))
        if 'sauce' in user_text_lower:
            items_to_add.append(('pasta sauce', 1, 'pantry'))
        
        # Add detected items to shopping list
        for name, quantity, category in items_to_add:
            self.shopping_list.add_item(name, quantity, category)
    
    async def run(self):
        """Main conversation loop"""
        if not self.openai_api_key:
            return
        
        print("\n" + "=" * 50)
        print("🛒 WELCOME TO SHOPEAT CLI SHOPPING ASSISTANT!")
        print("=" * 50)
        print("🤖 I'm your AI shopping assistant. Let's build your shopping list together!")
        print("💡 Just tell me what you need, and I'll help you organize it.")
        print("📝 Type 'list' to see your current list, 'clear' to start over, or 'quit' to exit.")
        print("=" * 50)
        
        while True:
            try:
                # Get user input
                user_input = input("\n🫵 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Thanks for shopping with ShopEAT! Have a great day!")
                    break
                
                elif user_input.lower() == 'list':
                    self.shopping_list.display()
                    continue
                
                elif user_input.lower() == 'clear':
                    self.shopping_list.clear_list()
                    continue
                
                elif user_input.lower() == 'help':
                    print("\n📚 ** COMMANDS **")
                    print("• Just type what you need (e.g., 'I need milk and bread')")
                    print("• 'list' - Show your shopping list")
                    print("• 'clear' - Clear your shopping list")
                    print("• 'quit' - Exit the application")
                    continue
                
                # Process shopping items mentioned
                self.process_shopping_items(user_input)
                
                # Chat with the AI agent
                print("\n🤖 AI Assistant: ", end="", flush=True)
                ai_response = await self.chat(user_input)
                print(ai_response)
                
                # Add to conversation history
                self.conversation_history.append({
                    "user": user_input,
                    "ai": ai_response
                })
                
            except KeyboardInterrupt:
                print("\n\n👋 Thanks for shopping with ShopEAT! Have a great day!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again or type 'quit' to exit.")

async def main():
    """Main entry point"""
    assistant = ShoppingAssistant()
    await assistant.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
