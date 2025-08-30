# ShopEAT Architecture Documentation

## System Overview

ShopEAT is a real-time voice shopping assistant that combines modern web technologies with AI capabilities to provide an intuitive shopping experience.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                ShopEAT System                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐ │
│  │   Frontend      │    │    Backend      │    │      OpenAI Services    │ │
│  │   (JavaScript)  │◄──►│   (Python)      │◄──►│                         │ │
│  │                 │    │                 │    │ • GPT Models            │ │
│  │ • Voice UI      │    │ • FastAPI       │    │ • Whisper API           │ │
│  │ • Real-time     │    │ • WebSocket     │    │ • Function Calling      │ │
│  │ • Shopping      │    │ • Voice Proc    │    │ • Agent SDK             │ │
│  │ • WebRTC        │    │ • State Mgmt    │    │                         │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────┘ │
│           │                       │                        │               │
│           │                       │                        │               │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐ │
│  │   Browser       │    │   HTTP/WS       │    │      External APIs      │ │
│  │   APIs          │    │   Server        │    │                         │ │
│  │                 │    │                 │    │ • OpenAI API            │ │
│  │ • MediaDevices  │    │ • CORS          │    │ • Payment Gateway       │ │
│  │ • WebSocket     │    │ • Auth          │    │ • Product Database      │ │
│  │ • LocalStorage  │    │ • Rate Limiting │    │                         │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend (JavaScript/HTML5)

**Technology Stack:**
- Vanilla JavaScript (ES6+)
- HTML5 with semantic markup
- CSS3 with modern features (Grid, Flexbox, Animations)
- WebRTC for voice recording
- WebSocket for real-time communication

**Key Features:**
- Voice recording interface with visual feedback
- Real-time shopping list management
- AI chat interface
- Responsive design for mobile and desktop
- Progressive Web App capabilities

**Architecture Patterns:**
- Class-based component architecture
- Event-driven communication
- State management with local storage
- Modular JavaScript structure

### 2. Backend (Python/FastAPI)

**Technology Stack:**
- FastAPI for REST API and WebSocket support
- Python 3.9+ for modern language features
- WebSocket for real-time duplex communication
- OpenAI SDK for AI integration
- Pydantic for data validation
- **UV package manager** for fast dependency management

**Key Features:**
- RESTful API endpoints
- WebSocket connection management
- Voice processing pipeline
- Shopping list state management
- AI assistant integration

**Architecture Patterns:**
- Async/await for non-blocking operations
- WebSocket connection pooling
- Middleware for CORS and authentication
- Dependency injection for services

### 3. Package Management with UV

**UV Integration:**
- **Lightning-fast dependency resolution** (10-100x faster than pip)
- **Modern pyproject.toml** configuration
- **Built-in virtual environment management**
- **Development tools integration** (Black, isort, flake8, mypy, pytest)
- **Reliable dependency locking**

**Development Workflow:**
```bash
# Setup environment
uv venv
uv pip install -e '.[dev]'

# Development tasks
uv run black .          # Format code
uv run isort .          # Sort imports
uv run flake8 .         # Lint code
uv run mypy .           # Type checking
uv run pytest           # Run tests
uv run python main.py   # Start server
```

**Benefits:**
- Eliminates dependency conflicts
- Faster development cycles
- Consistent development environment
- Modern Python packaging standards

### 4. Communication Layer

**Protocols:**
- HTTP/HTTPS for REST API calls
- WebSocket for real-time bidirectional communication
- Base64 encoding for audio data transmission

**Data Flow:**
1. Frontend captures voice input via WebRTC
2. Audio data converted to Base64 and sent via WebSocket
3. Backend processes audio and sends to OpenAI
4. AI response returned via WebSocket
5. Frontend updates UI in real-time

### 5. AI Integration

**OpenAI Services:**
- GPT models for natural language understanding
- Whisper API for speech-to-text conversion
- Function calling for structured responses
- Agent SDK for intelligent shopping assistance

**AI Workflow:**
1. Voice input received and processed
2. Text sent to GPT for intent recognition
3. Shopping actions extracted and executed
4. Contextual responses generated
5. Real-time feedback provided to user

## Data Flow Architecture

```
User Voice Input
       ↓
   Frontend (WebRTC)
       ↓
   Audio Recording
       ↓
   Base64 Encoding
       ↓
   WebSocket Transmission
       ↓
   Backend Processing
       ↓
   OpenAI API Call
       ↓
   AI Response Generation
       ↓
   Shopping Action Execution
       ↓
   State Update
       ↓
   Real-time UI Update
```

## Security Considerations

### Frontend Security
- HTTPS enforcement for production
- Input validation and sanitization
- XSS protection through proper DOM manipulation
- CORS policy enforcement

### Backend Security
- API key management for OpenAI
- Rate limiting for API endpoints
- Input validation with Pydantic
- WebSocket connection authentication
- Environment variable protection

### Data Security
- No sensitive data stored in frontend
- Secure transmission over WebSocket
- API key rotation capabilities
- Audit logging for debugging

## Scalability Considerations

### Current PoC Limitations
- In-memory state storage
- Single WebSocket connection per client
- Basic error handling
- Limited concurrent user support

### Future Scalability Path
- Redis for distributed state management
- WebSocket connection pooling
- Load balancing for multiple backend instances
- Database integration for persistent storage
- Microservices architecture for specialized functions

## Performance Optimization

### Frontend Optimizations
- Lazy loading of components
- Efficient DOM manipulation
- Optimized audio processing
- Responsive design for various devices

### Backend Optimizations
- Async processing for I/O operations
- Connection pooling for WebSockets
- Efficient data serialization
- Caching strategies for AI responses

### UV Performance Benefits
- **Faster dependency installation** reduces development time
- **Eliminates dependency conflicts** improves reliability
- **Built-in caching** speeds up repeated operations
- **Parallel processing** for multiple package operations

## Monitoring and Observability

### Health Checks
- Backend health endpoint (`/health`)
- WebSocket connection status
- OpenAI API connectivity
- Frontend connection status

### Logging
- Structured logging with timestamps
- Error tracking and reporting
- Performance metrics collection
- User interaction analytics

## Development Workflow

### Local Development with UV
1. **Backend**: UV virtual environment with FastAPI
2. **Frontend**: Node.js with http-server
3. **Environment configuration** via .env files
4. **Hot reloading** for both services
5. **Development tools** integrated with UV

### Docker Development
1. Multi-service Docker Compose setup
2. Volume mounting for live code changes
3. Health checks for service monitoring
4. Network isolation for development

### Testing Strategy
- Unit tests for backend functions
- Integration tests for API endpoints
- Frontend component testing
- End-to-end voice interaction testing

### UV Development Commands
```bash
# Quick development setup
./dev.sh setup

# Code quality checks
./dev.sh all

# Individual tasks
./dev.sh format     # Format code
./dev.sh lint       # Lint code
./dev.sh test       # Run tests
./dev.sh start      # Start backend
```

## Deployment Considerations

### Production Requirements
- HTTPS with valid SSL certificates
- Environment-specific configurations
- Monitoring and alerting setup
- Backup and recovery procedures

### Infrastructure Options
- Container orchestration (Kubernetes)
- Serverless deployment (AWS Lambda)
- Traditional VPS deployment
- Cloud platform services (GCP, Azure)

## Future Enhancements

### Phase 2 Features
- User authentication and profiles
- Shopping history and analytics
- Product recommendations
- Voice synthesis for responses
- Multi-language support

### Phase 3 Features
- Mobile app development
- Offline capabilities
- Advanced AI features
- Integration with e-commerce platforms
- Social shopping features

## Conclusion

The ShopEAT architecture provides a solid foundation for a real-time voice shopping assistant while maintaining simplicity for the PoC phase. The modular design allows for easy expansion and the use of modern web technologies ensures a responsive and engaging user experience. The integration of UV package management significantly improves development velocity and reliability, making it an excellent choice for rapid prototyping and future development.
