# ShopEAT Quick Start Guide 🚀

Get ShopEAT running in under 5 minutes!

## Prerequisites

- **Python 3.9+** installed
- **Node.js 18+** installed  
- **OpenAI API key** (get one at [platform.openai.com](https://platform.openai.com))

## Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd shopeat

# Run the setup script
./setup.sh
```

## Option 2: Manual Setup

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp env.example .env
# Edit .env and add your OpenAI API key

# Start the backend
python main.py
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp env.example .env

# Start the frontend
npm start
```

## Option 3: Docker Setup

```bash
# Create environment file
cp backend/env.example backend/.env
# Edit backend/.env and add your OpenAI API key

# Start with Docker Compose
docker-compose up --build
```

## Verify Installation

1. **Backend**: Open [http://localhost:8000/health](http://localhost:8000/health)
2. **Frontend**: Open [http://localhost:3000](http://localhost:3000)

## Test the System

1. Open the frontend in your browser
2. Click the microphone button and speak
3. Say "I need to buy milk and bread"
4. Watch the AI assistant respond!

## Troubleshooting

### Common Issues

**Backend won't start:**
- Check if port 8000 is available
- Verify Python 3.9+ is installed
- Check OpenAI API key in .env file

**Frontend won't start:**
- Check if port 3000 is available
- Verify Node.js 18+ is installed
- Run `npm install` if dependencies are missing

**WebSocket connection failed:**
- Ensure backend is running on port 8000
- Check browser console for errors
- Verify CORS settings

**Voice recording not working:**
- Allow microphone access in browser
- Check browser console for WebRTC errors
- Try refreshing the page

### Getting Help

- Check the browser console for error messages
- Review the backend logs for Python errors
- Ensure all environment variables are set correctly

## Next Steps

- Customize the shopping categories in `shared/config.py`
- Add your own OpenAI prompts in `backend/main.py`
- Extend the frontend with additional features
- Integrate with external product databases

## Development Tips

- Backend auto-reloads on code changes
- Frontend uses http-server for simplicity
- Check `docs/architecture.md` for system details
- Use Docker for consistent development environment

Happy coding! 🛒🎤
