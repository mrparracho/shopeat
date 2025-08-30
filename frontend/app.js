/**
 * ShopEAT Frontend - Main Application
 * Real-time voice shopping assistant with WebSocket communication
 */

class ShopEATApp {
    constructor() {
        this.ws = null;
        this.clientId = this.generateClientId();
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.shoppingList = [];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.connectWebSocket();
        this.loadShoppingList();
    }

    generateClientId() {
        return 'client_' + Math.random().toString(36).substr(2, 9);
    }

    setupEventListeners() {
        // Voice button events
        const voiceBtn = document.getElementById('voiceBtn');
        voiceBtn.addEventListener('mousedown', () => this.startRecording());
        voiceBtn.addEventListener('mouseup', () => this.stopRecording());
        voiceBtn.addEventListener('mouseleave', () => this.stopRecording());
        
        // Touch events for mobile
        voiceBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startRecording();
        });
        voiceBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopRecording();
        });

        // Clear list button
        document.getElementById('clearListBtn').addEventListener('click', () => {
            this.clearShoppingList();
        });

        // Test connection button
        document.getElementById('testBtn').addEventListener('click', () => {
            this.testConnection();
        });

        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadShoppingList();
        });
    }

    connectWebSocket() {
        const wsUrl = `ws://localhost:8000/ws/${this.clientId}`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.updateConnectionStatus('connected');
                this.addChatMessage('System', 'Connected to ShopEAT backend!', 'assistant');
            };

            this.ws.onmessage = (event) => {
                this.handleWebSocketMessage(event.data);
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateConnectionStatus('disconnected');
                this.addChatMessage('System', 'Connection lost. Trying to reconnect...', 'assistant');
                
                // Attempt to reconnect after 3 seconds
                setTimeout(() => this.connectWebSocket(), 3000);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('disconnected');
            };

        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
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

    async startRecording() {
        if (this.isRecording) return;
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                this.processAudioRecording();
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            this.updateVoiceButton(true);
            this.updateVoiceFeedback('Recording...', true);
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            this.addChatMessage('System', 'Error: Could not access microphone. Please check permissions.', 'assistant');
        }
    }

    stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) return;
        
        this.mediaRecorder.stop();
        this.isRecording = false;
        this.updateVoiceButton(false);
        this.updateVoiceFeedback('Processing...', false);
        
        // Stop all audio tracks
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }

    async processAudioRecording() {
        if (this.audioChunks.length === 0) return;
        
        try {
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
            const base64Audio = await this.blobToBase64(audioBlob);
            
            // Send voice input to backend
            this.sendVoiceInput(base64Audio);
            
            // Simulate user message in chat
            this.addChatMessage('You', '🎤 Voice input recorded', 'user');
            
        } catch (error) {
            console.error('Error processing audio:', error);
            this.addChatMessage('System', 'Error processing voice input', 'assistant');
        }
        
        this.updateVoiceFeedback('Ready to help you shop!', false);
    }

    blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }

    sendVoiceInput(audioData) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            this.addChatMessage('System', 'Not connected to backend', 'assistant');
            return;
        }

        const message = {
            type: 'voice_input',
            audio_data: audioData,
            timestamp: new Date().toISOString()
        };

        this.ws.send(JSON.stringify(message));
    }

    handleWebSocketMessage(data) {
        try {
            const message = JSON.parse(data);
            console.log('Received message:', message);

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
                    this.addChatMessage('System', `Error: ${message.message}`, 'assistant');
                    break;
                case 'echo':
                    console.log('Echo response:', message.data);
                    break;
                default:
                    console.log('Unknown message type:', message.type);
            }
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }

    handleVoiceResponse(message) {
        this.addChatMessage('AI Assistant', message.ai_response, 'assistant');
        
        // Update feedback
        this.updateVoiceFeedback('Ready to help you shop!', false);
    }

    handleShoppingUpdate(message) {
        switch (message.action) {
            case 'item_added':
                this.addChatMessage('System', `Added: ${message.item.name}`, 'assistant');
                this.loadShoppingList();
                break;
            case 'list_cleared':
                this.addChatMessage('System', 'Shopping list cleared', 'assistant');
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

    updateVoiceButton(recording) {
        const voiceBtn = document.getElementById('voiceBtn');
        const btnText = voiceBtn.querySelector('.btn-text');
        
        if (recording) {
            voiceBtn.classList.add('recording');
            btnText.textContent = 'Recording...';
        } else {
            voiceBtn.classList.remove('recording');
            btnText.textContent = 'Hold to Speak';
        }
    }

    updateVoiceFeedback(text, isRecording) {
        const feedbackText = document.querySelector('.feedback-text');
        const waveform = document.getElementById('waveform');
        
        feedbackText.textContent = text;
        
        if (isRecording) {
            waveform.style.background = 'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)';
        } else {
            waveform.style.background = 'linear-gradient(90deg, #e5e7eb 0%, #d1d5db 100%)';
        }
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
            this.addChatMessage('System', 'Could not load shopping list', 'assistant');
        }
    }

    updateShoppingList(items) {
        this.shoppingList = items;
        const shoppingListContainer = document.getElementById('shoppingList');
        
        if (items.length === 0) {
            shoppingListContainer.innerHTML = `
                <div class="empty-state">
                    <p>🎯 Start by saying what you need to buy!</p>
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
            this.addChatMessage('System', 'Not connected to backend', 'assistant');
            return;
        }

        const message = {
            type: 'shopping_action',
            action: 'clear_list'
        };

        this.ws.send(JSON.stringify(message));
    }

    removeShoppingItem(itemName) {
        // For PoC, we'll just remove from local list
        // In production, this would send a message to the backend
        this.shoppingList = this.shoppingList.filter(item => item.name !== itemName);
        this.updateShoppingList(this.shoppingList);
        this.addChatMessage('System', `Removed: ${itemName}`, 'assistant');
    }

    testConnection() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.addChatMessage('System', '✅ WebSocket connection is working!', 'assistant');
        } else {
            this.addChatMessage('System', '❌ WebSocket connection is not working', 'assistant');
        }
    }

    showLoading(show) {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (show) {
            loadingOverlay.classList.add('show');
        } else {
            loadingOverlay.classList.remove('show');
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ShopEATApp();
});

// Handle page visibility changes to manage WebSocket connection
document.addEventListener('visibilitychange', () => {
    if (document.hidden && window.app && window.app.ws) {
        // Page is hidden, could close WebSocket to save resources
        console.log('Page hidden');
    } else if (!document.hidden && window.app && (!window.app.ws || window.app.ws.readyState !== WebSocket.OPEN)) {
        // Page is visible and WebSocket is not connected, try to reconnect
        console.log('Page visible, attempting to reconnect');
        window.app.connectWebSocket();
    }
});
