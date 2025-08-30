# ShopEAT 🛒🎤

A real-time voice shopping assistant that leverages OpenAI Agent SDK for intelligent shopping guidance.

## 🚀 Features

- **Real-time Voice Communication**: Duplex voice interaction during shopping
- **AI-Powered Shopping Assistant**: OpenAI Agent SDK integration for smart recommendations
- **Streamlined PoC Architecture**: Simple, focused implementation for proof of concept
- **Fast Package Management**: UV for lightning-fast Python dependency management

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
├── backend/           # Python FastAPI backend (UV managed)
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
- UV package manager (auto-installed by setup script)

### Option 1: Automated Setup (Recommended)
```bash
./setup.sh
```

### Option 2: Manual Setup with UV

#### Backend Setup
```bash
cd backend

# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Set up environment
cp env.example .env
# Edit .env and add your OpenAI API key

# Start the backend
python main.py
```

#### Frontend Setup
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
- **Package Management**: UV for fast Python dependency management

## 🚀 UV Package Management

ShopEAT uses **UV** - the fastest Python package manager available:

### Key UV Commands
```bash
# Install dependencies
uv pip install -e .

# Install development dependencies
uv pip install -e '.[dev]'

# Add new package
uv add package-name

# Run commands in virtual environment
uv run python main.py
uv run pytest
uv run black .
uv run flake8 .
```

### Benefits of UV
- ⚡ **10-100x faster** than pip
- 🔒 **Reliable dependency resolution**
- 🐍 **Native virtual environment management**
- 📦 **Modern pyproject.toml support**
- 🚀 **Built-in caching and optimization**

## 📊 PoC Goals

- [ ] Basic voice communication between frontend and backend
- [ ] OpenAI Agent SDK integration
- [ ] Simple shopping list management
- [ ] Real-time voice guidance
- [ ] Basic product recommendations

## 🤝 Contributing

This is a proof of concept. Focus on core functionality and simplicity.

## 📚 Additional Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
