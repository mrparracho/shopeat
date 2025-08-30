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
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.connectWebSocket();
        this.loadShoppingList();
        this.initSpeechRecognition();
        this.initSpeechSynthesis();
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
                this.updateListeningStatus(true);
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
                this.isListening = false;
                this.updateListeningStatus(false);
            };
            
            this.recognition.onend = () => {
                this.isListening = false;
                this.updateListeningStatus(false);
                
                if (this.continuousMode && !this.isProcessing) {
                    setTimeout(() => this.startContinuousListening(), 100);
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
        
        try {
            this.continuousMode = true;
            this.recognition.start();
            this.updateVoiceButton(true);
            this.updateListeningStatus(true);
        } catch (error) {
            console.error('Error starting speech recognition:', error);
        }
    }

    stopContinuousListening() {
        this.continuousMode = false;
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
        this.updateVoiceButton(false);
        this.updateListeningStatus(false);
    }

    processFinalTranscript(transcript) {
        if (!transcript.trim()) return;
        
        this.addChatMessage('You', transcript, 'user');
        this.sendVoiceInput(transcript);
        this.updateInterimTranscript('');
    }

    updateInterimTranscript(transcript) {
        const interimDisplay = document.getElementById('interimTranscript');
        if (interimDisplay) {
            interimDisplay.textContent = transcript;
            interimDisplay.style.display = transcript ? 'block' : 'none';
        }
    }

    updateListeningStatus(isListening) {
        const statusIndicator = document.getElementById('listeningStatus');
        if (statusIndicator) {
            statusIndicator.textContent = isListening ? '🎤 Listening...' : '🔇 Not listening';
            statusIndicator.className = isListening ? 'listening' : 'not-listening';
        }
    }

    updateVoiceButton(isActive) {
        const voiceBtn = document.getElementById('voiceBtn');
        const btnText = voiceBtn.querySelector('.btn-text');
        const icon = voiceBtn.querySelector('.mic-icon');
        
        if (isActive) {
            voiceBtn.classList.add('active');
            btnText.textContent = 'Stop Listening';
            icon.textContent = '🔇';
        } else {
            voiceBtn.classList.remove('active');
            btnText.textContent = 'Start Listening';
            icon.textContent = '🎤';
        }
    }

    sendVoiceInput(transcript) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            this.addChatMessage('AI Assistant', 'Not connected to backend', 'assistant');
            return;
        }

        const message = {
            type: 'voice_input',
            text: transcript,
            timestamp: new Date().toISOString()
        };

        this.ws.send(JSON.stringify(message));
    }

    connectWebSocket() {
        const wsUrl = `ws://localhost:8000/ws/${this.clientId}`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                this.updateConnectionStatus('connected');
            };

            this.ws.onmessage = (event) => {
                this.handleWebSocketMessage(event.data);
            };

            this.ws.onclose = () => {
                this.updateConnectionStatus('disconnected');
                setTimeout(() => this.connectWebSocket(), 3000);
            };

            this.ws.onerror = (error) => {
                this.updateConnectionStatus('disconnected');
            };

        } catch (error) {
            this.updateConnectionStatus('disconnected');
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

            switch (message.type) {
                case 'voice_response':
                    this.handleVoiceResponse(message);
                    break;
                case 'shopping_update':
                    this.handleShoppingUpdate(message);
                    break;
                case 'shopping_list':
                    this.updateShoppingList(message.items);
                    break;
                case 'error':
                    this.addChatMessage('AI Assistant', `Error: ${message.message}`, 'assistant');
                    break;
            }
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }

    handleVoiceResponse(message) {
        this.addChatMessage('AI Assistant', message.ai_response, 'assistant');
        this.speakResponse(message.ai_response);
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
                    <p>🎯 Start by speaking naturally!</p>
                    <p>Try: "I need milk and bread"</p>
                </div>
            `;
        } else {
            shoppingListContainer.innerHTML = items.map(item => `
                <div class="shopping-item">
                    <div class="item-info">
                        <h4>${item.name}</h4>
                        <div class="item-meta">
                            Qty: ${item.quantity} | Category: ${item.category}
                            ${item.notes ? `| Notes: ${item.notes}` : ''}
                        </div>
                    </div>
                    <div class="item-actions">
                        <button onclick="app.removeShoppingItem('${item.name}')" title="Remove">🗑️</button>
                    </div>
                </div>
            `).join('');
        }
    }

    async clearShoppingList() {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            this.addChatMessage('AI Assistant', 'Not connected to backend', 'assistant');
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