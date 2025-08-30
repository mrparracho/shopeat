# ShopEAT 🛒🎤

A real-time voice shopping assistant that leverages OpenAI Agent SDK for intelligent shopping guidance.

## 🚀 Features

- **Real-time Voice Communication**: Duplex voice interaction during shopping
- **AI-Powered Shopping Assistant**: OpenAI Agent SDK integration for smart recommendations
- **Streamlined PoC Architecture**: Simple, focused implementation for proof of concept

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   OpenAI API    │
│   (JavaScript)  │◄──►│   (Python)      │◄──►│   + Agent SDK   │
│                 │    │                 │    │                 │
│ • Voice UI      │    │ • FastAPI       │    │ • GPT Models    │
│ • Real-time     │    │ • WebSocket     │    │ • Function      │
│ • Shopping      │    │ • Voice Proc    │    │   Calling      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
shopeat/
├── backend/           # Python FastAPI backend
├── frontend/          # JavaScript frontend
├── shared/            # Common utilities
├── docs/              # Documentation & diagrams
├── docker-compose.yml # Development environment
└── README.md          # This file
```

## 🛠️ Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenAI API key

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Environment Variables
Create `.env` files in both `backend/` and `frontend/` directories:
```bash
OPENAI_API_KEY=your_api_key_here
```

## 🔧 Development

- **Backend**: FastAPI with WebSocket support for real-time communication
- **Frontend**: Vanilla JavaScript with WebRTC for voice capabilities
- **Communication**: WebSocket for real-time duplex communication
- **AI Integration**: OpenAI Agent SDK for intelligent shopping assistance

## 📊 PoC Goals

- [ ] Basic voice communication between frontend and backend
- [ ] OpenAI Agent SDK integration
- [ ] Simple shopping list management
- [ ] Real-time voice guidance
- [ ] Basic product recommendations

## 🤝 Contributing

This is a proof of concept. Focus on core functionality and simplicity.
