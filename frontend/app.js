/**
 * ShopEAT Frontend - Main Application
 * Continuous bidirectional speech-to-speech shopping assistant
 */

class ShopEATApp {
    constructor() {
        this.ws = null;
        this.clientId = this.generateClientId();
        this.isListening = false;
        this.isProcessing = false;
        this.shoppingList = [];
        this.recognition = null;
        this.synthesis = null;
        this.continuousMode = false;
        this.hasSpokenGreeting = false;
        this.recognitionRestartAttempts = 0;
        this.maxRestartAttempts = 3;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.connectWebSocket();
        this.loadShoppingList();
        this.initSpeechRecognition();
        this.initSpeechSynthesis();
        
        // Auto-start the conversation after a short delay
        setTimeout(() => {
            this.startConversation();
        }, 1000);
    }

    generateClientId() {
        return 'client_' + Math.random().toString(36).substr(2, 9);
    }

    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';
            
            this.recognition.onstart = () => {
                this.isListening = true;
                this.recognitionRestartAttempts = 0; // Reset restart attempts on successful start
                this.updateListeningStatus(true);
                console.log('Speech recognition started successfully');
            };
            
            this.recognition.onresult = (event) => {
                let finalTranscript = '';
                let interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript;
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                if (interimTranscript) {
                    this.updateInterimTranscript(interimTranscript);
                }
                
                if (finalTranscript) {
                    this.processFinalTranscript(finalTranscript);
                }
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                
                // Don't restart for certain errors that indicate user action
                if (event.error === 'no-speech' || event.error === 'aborted') {
                    this.isListening = false;
                    this.updateListeningStatus(false);
                    return;
                }
                
                this.isListening = false;
                this.updateListeningStatus(false);
                
                // Only restart if we're in continuous mode and haven't exceeded max attempts
                if (this.continuousMode && this.recognitionRestartAttempts < this.maxRestartAttempts) {
                    this.recognitionRestartAttempts++;
                    console.log(`Restarting speech recognition (attempt ${this.recognitionRestartAttempts})`);
                    setTimeout(() => this.startContinuousListening(), 2000);
                } else if (this.recognitionRestartAttempts >= this.maxRestartAttempts) {
                    console.log('Max restart attempts reached, stopping automatic restarts');
                    this.continuousMode = false;
                    this.updateVoiceButton(false);
                }
            };
            
            this.recognition.onend = () => {
                console.log('Speech recognition ended');
                this.isListening = false;
                this.updateListeningStatus(false);
                
                // Only restart if we're in continuous mode, not processing, and haven't exceeded max attempts
                if (this.continuousMode && !this.isProcessing && this.recognitionRestartAttempts < this.maxRestartAttempts) {
                    this.recognitionRestartAttempts++;
                    console.log(`Restarting speech recognition on end (attempt ${this.recognitionRestartAttempts})`);
                    setTimeout(() => this.startContinuousListening(), 1000);
                } else if (this.recognitionRestartAttempts >= this.maxRestartAttempts) {
                    console.log('Max restart attempts reached, stopping automatic restarts');
                    this.continuousMode = false;
                    this.updateVoiceButton(false);
                }
            };
        }
    }

    initSpeechSynthesis() {
        if ('speechSynthesis' in window) {
            this.synthesis = window.speechSynthesis;
            
            // Wait for voices to load
            if (this.synthesis.getVoices().length === 0) {
                this.synthesis.onvoiceschanged = () => {
                    this.voicesLoaded = true;
                };
            } else {
                this.voicesLoaded = true;
            }
        }
    }

    startConversation() {
        if (!this.hasSpokenGreeting) {
            this.speakGreeting();
            this.hasSpokenGreeting = true;
        }
    }

    speakGreeting() {
        const greeting = "What are we ordering today?";
        this.speakResponse(greeting);
        
        // Start listening immediately after speaking
        setTimeout(() => {
            this.startContinuousListening();
        }, 2000); // Wait for speech to finish
    }

    setupEventListeners() {
        const toggleBtn = document.getElementById('voiceBtn');
        toggleBtn.addEventListener('click', () => this.toggleContinuousMode());
        
        document.getElementById('clearListBtn').addEventListener('click', () => {
            this.clearShoppingList();
        });

        document.getElementById('testBtn').addEventListener('click', () => {
            this.testConnection();
        });

        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadShoppingList();
        });
    }

    toggleContinuousMode() {
        if (this.continuousMode) {
            this.stopContinuousListening();
        } else {
            this.startContinuousListening();
        }
    }

    startContinuousListening() {
        if (!this.recognition) {
            this.addChatMessage('AI Assistant', 'Speech recognition not supported in this browser', 'assistant');
            return;
        }
        
        // Don't start if already listening
        if (this.isListening) {
            console.log('Already listening, skipping start request');
            return;
        }
        
        try {
            this.continuousMode = true;
            this.recognition.start();
            this.updateVoiceButton(true);
            this.updateListeningStatus(true);
            console.log('Starting speech recognition');
        } catch (error) {
            console.error('Error starting speech recognition:', error);
            // Try again after a short delay
            setTimeout(() => this.startContinuousListening(), 1000);
        }
    }

    stopContinuousListening() {
        this.continuousMode = false;
        this.recognitionRestartAttempts = 0; // Reset restart attempts
        
        if (this.recognition && this.isListening) {
            try {
                this.recognition.stop();
                console.log('Stopping speech recognition');
            } catch (error) {
                console.error('Error stopping speech recognition:', error);
            }
        }
        
        this.updateVoiceButton(false);
        this.updateListeningStatus(false);
    }

    processFinalTranscript(transcript) {
        if (!transcript.trim()) return;
        
        this.addChatMessage('You', transcript, 'user');
        this.sendVoiceInput(transcript);
        this.updateInterimTranscript('');
        
        // Set processing flag to prevent restart during processing
        this.isProcessing = true;
        
        // Send to backend for OpenAI processing
        this.sendToOpenAI(transcript);
    }

    sendToOpenAI(transcript) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            // If WebSocket is not connected, show error and stop processing
            this.addChatMessage('AI Assistant', 'Not connected to backend. Please check your connection.', 'assistant');
            this.isProcessing = false;
            return;
        }

        const message = {
            type: 'voice_input',
            text: transcript,
            timestamp: new Date().toISOString()
        };

        console.log('Sending to OpenAI via WebSocket:', message);
        this.ws.send(JSON.stringify(message));
    }

    updateInterimTranscript(transcript) {
        const interimDisplay = document.getElementById('interimTranscript');
        if (interimDisplay) {
            if (transcript.trim()) {
                interimDisplay.textContent = transcript;
                interimDisplay.classList.add('show');
            } else {
                interimDisplay.classList.remove('show');
            }
        }
    }

    updateListeningStatus(isListening) {
        const statusIndicator = document.getElementById('listeningStatus');
        if (statusIndicator) {
            if (isListening) {
                statusIndicator.innerHTML = `<i class="fas fa-volume-up"></i> Listening...`;
                statusIndicator.className = 'listening-status listening';
            } else {
                statusIndicator.innerHTML = `<i class="fas fa-volume-mute"></i> Not listening`;
                statusIndicator.className = 'listening-status';
            }
        }
    }

    updateVoiceButton(isActive) {
        const voiceBtn = document.getElementById('voiceBtn');
        const btnText = voiceBtn.querySelector('.btn-text');
        const icon = voiceBtn.querySelector('.mic-icon');
        
        if (isActive) {
            voiceBtn.classList.add('active');
            btnText.textContent = 'Stop Listening';
            icon.className = 'fas fa-stop mic-icon';
        } else {
            voiceBtn.classList.remove('active');
            btnText.textContent = 'Start Listening';
            icon.className = 'fas fa-microphone mic-icon';
        }
    }

    connectWebSocket() {
        const wsUrl = `ws://localhost:8000/ws/${this.clientId}`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                this.updateConnectionStatus('connected');
                console.log('WebSocket connected to backend');
            };

            this.ws.onmessage = (event) => {
                this.handleWebSocketMessage(event.data);
            };

            this.ws.onclose = () => {
                this.updateConnectionStatus('disconnected');
                console.log('WebSocket disconnected, attempting to reconnect...');
                setTimeout(() => this.connectWebSocket(), 3000);
            };

            this.ws.onerror = (error) => {
                this.updateConnectionStatus('disconnected');
                console.error('WebSocket error:', error);
            };

        } catch (error) {
            this.updateConnectionStatus('disconnected');
            console.error('Error creating WebSocket:', error);
        }
    }

    updateConnectionStatus(status) {
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.status-text');
        
        statusDot.className = 'status-dot ' + status;
        
        switch (status) {
            case 'connected':
                statusText.textContent = 'Connected';
                break;
            case 'disconnected':
                statusText.textContent = 'Disconnected';
                break;
            default:
                statusText.textContent = 'Connecting...';
        }
    }

    handleWebSocketMessage(data) {
        try {
            const message = JSON.parse(data);
            console.log('Received WebSocket message:', message);

            switch (message.type) {
                case 'voice_response':
                    this.handleVoiceResponse(message);
                    break;
                case 'shopping_update':
                    this.handleShoppingUpdate(message);
                    break;
                case 'shopping_list':
                    this.updateShoppingList(message.items || []);
                    break;
                case 'error':
                    this.addChatMessage('AI Assistant', `Error: ${message.message}`, 'assistant');
                    break;
                default:
                    console.log('Unknown message type:', message.type);
            }
            
            // Reset processing flag after receiving response
            this.isProcessing = false;
            
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
            this.isProcessing = false;
        }
    }

    handleVoiceResponse(message) {
        if (message.ai_response) {
            this.addChatMessage('AI Assistant', message.ai_response, 'assistant');
            this.speakResponse(message.ai_response);
        }
        
        if (message.transcribed_text) {
            console.log('Transcribed text:', message.transcribed_text);
        }
    }

    speakResponse(text) {
        if (!this.synthesis) return;
        
        try {
            // Stop any current speech
            this.synthesis.cancel();
            
            // Create speech utterance
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.9;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;
            
            // Set voice
            const voices = this.synthesis.getVoices();
            if (voices.length > 0) {
                // Prefer English voices
                const englishVoice = voices.find(voice => 
                    voice.lang.startsWith('en')
                ) || voices[0];
                utterance.voice = englishVoice;
            }
            
            // Speak the response
            this.synthesis.speak(utterance);
            
        } catch (error) {
            console.error('Error speaking response:', error);
        }
    }

    handleShoppingUpdate(message) {
        switch (message.action) {
            case 'item_added':
                this.addChatMessage('AI Assistant', `Added: ${message.item.name}`, 'assistant');
                this.speakResponse(`Added ${message.item.name} to your shopping list`);
                this.loadShoppingList();
                break;
            case 'list_cleared':
                this.addChatMessage('AI Assistant', 'Shopping list cleared', 'assistant');
                this.speakResponse('Your shopping list has been cleared');
                this.updateShoppingList([]);
                break;
        }
    }

    addChatMessage(sender, content, type) {
        const chatContainer = document.getElementById('chatContainer');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}`;
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <strong>${sender}:</strong> ${content}
            </div>
        `;
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    async loadShoppingList() {
        try {
            const response = await fetch('http://localhost:8000/api/shopping-list');
            if (response.ok) {
                const data = await response.json();
                this.updateShoppingList(data.items || []);
            }
        } catch (error) {
            console.error('Error loading shopping list:', error);
        }
    }

    updateShoppingList(items) {
        this.shoppingList = items;
        const shoppingListContainer = document.getElementById('shoppingList');
        
        if (items.length === 0) {
            shoppingListContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-shopping-basket" style="font-size: 3rem; color: var(--gray-300); margin-bottom: var(--space-4); display: block;"></i>
                    <p>🎯 Start by speaking naturally!</p>
                    <p>Try: "I need milk and bread"</p>
                </div>
            `;
        } else {
            shoppingListContainer.innerHTML = items.map(item => `
                <div class="shopping-item">
                    <div class="item-info">
                        <h4><i class="fas fa-tag"></i> ${item.name}</h4>
                        <div class="item-meta">
                            <span><i class="fas fa-hashtag"></i> Qty: ${item.quantity}</span>
                            <span><i class="fas fa-folder"></i> ${item.category}</span>
                            ${item.notes ? `<span><i class="fas fa-sticky-note"></i> ${item.notes}</span>` : ''}
                        </div>
                    </div>
                    <div class="item-actions">
                        <button onclick="app.removeShoppingItem('${item.name}')" title="Remove" class="remove-btn">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `).join('');
        }
    }

    async clearShoppingList() {
        this.shoppingList = [];
        this.updateShoppingList([]);
        
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }

        const message = {
            type: 'shopping_action',
            action: 'clear_list'
        };

        this.ws.send(JSON.stringify(message));
    }

    removeShoppingItem(itemName) {
        this.shoppingList = this.shoppingList.filter(item => item.name !== itemName);
        this.updateShoppingList(this.shoppingList);
        this.addChatMessage('AI Assistant', `Removed: ${itemName}`, 'assistant');
        this.speakResponse(`Removed ${itemName} from your shopping list`);
    }

    testConnection() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.addChatMessage('AI Assistant', '✅ WebSocket connection is working!', 'assistant');
        } else {
            this.addChatMessage('AI Assistant', '❌ WebSocket connection is not working', 'assistant');
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ShopEATApp();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && window.app && (!window.app.ws || window.app.ws.readyState !== WebSocket.OPEN)) {
        window.app.connectWebSocket();
    }
});