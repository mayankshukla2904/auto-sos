/**
 * Emergency Alert System - WhatsApp Service
 * 
 * This service:
 * 1. Maintains a persistent WhatsApp connection using Baileys
 * 2. Exposes an HTTP API (port 3000) for sending alerts
 * 3. Handles authentication and session management
 * 4. Provides detailed logging
 */

const { default: makeWASocket, DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');
const express = require('express');
const fs = require('fs');
const path = require('path');

// Load configuration
const config = JSON.parse(fs.readFileSync('config.json', 'utf8'));

// Global WhatsApp socket
let sock = null;
let isConnected = false;

// Express HTTP server for receiving alert requests
const app = express();
app.use(express.json());

// Serve static files for the dashboard
app.use(express.static('public'));

/**
 * Initialize WhatsApp connection
 */
async function connectToWhatsApp() {
    try {
        // Load or create authentication state
        const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
        
        // Get latest Baileys version
        const { version, isLatest } = await fetchLatestBaileysVersion();
        console.log(`Using WA v${version.join('.')}, isLatest: ${isLatest}`);
        
        // Create WhatsApp socket
        sock = makeWASocket({
            version,
            auth: state,
            printQRInTerminal: false,
            browser: ['Emergency Alert System', 'Chrome', '1.0.0'],
            defaultQueryTimeoutMs: undefined,
        });

        // Handle connection updates
        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;
            
            if (qr) {
                console.log('\n📱 Scan this QR code with WhatsApp (Settings → Linked Devices):\n');
                qrcode.generate(qr, { small: true });
                console.log('\n');
            }
            
            if (connection === 'close') {
                const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
                console.log('❌ Connection closed. Reconnecting:', shouldReconnect);
                
                isConnected = false;
                
                if (shouldReconnect) {
                    // Reconnect after a delay
                    setTimeout(() => connectToWhatsApp(), 3000);
                } else {
                    console.log('⚠️  Logged out. Please restart and scan QR code again.');
                }
            } else if (connection === 'open') {
                console.log('✅ WhatsApp connected successfully!');
                isConnected = true;
            }
        });

        // Save credentials when updated
        sock.ev.on('creds.update', saveCreds);
        
    } catch (error) {
        console.error('❌ Error connecting to WhatsApp:', error);
        setTimeout(() => connectToWhatsApp(), 5000);
    }
}

/**
 * Send WhatsApp message to multiple recipients
 */
async function sendWhatsAppMessage(recipients, message) {
    if (!isConnected || !sock) {
        throw new Error('WhatsApp is not connected');
    }
    
    try {
        const timestamp = new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' });
        console.log(`[${timestamp}] Sending message to ${recipients.length} recipient(s)`);
        
        // Send to all recipients
        const sendPromises = recipients.map(async (recipient) => {
            try {
                await sock.sendMessage(recipient, { text: message });
                console.log(`[${timestamp}] ✅ Message sent to ${recipient}`);
                return { recipient, success: true };
            } catch (error) {
                console.error(`[${timestamp}] ❌ Failed to send to ${recipient}:`, error.message);
                return { recipient, success: false, error: error.message };
            }
        });
        
        const results = await Promise.all(sendPromises);
        const successCount = results.filter(r => r.success).length;
        
        console.log(`[${timestamp}] ✅ Successfully sent ${successCount}/${recipients.length} messages`);
        return { success: true, results };
    } catch (error) {
        console.error('❌ Error sending message:', error);
        throw error;
    }
}

/**
 * HTTP endpoint for receiving alert requests
 */
app.post('/alert', async (req, res) => {
    try {
        const now = new Date();
        const timestamp = now.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' });
        console.log(`\n[${timestamp}] 🚨 ALERT RECEIVED`);
        
        // Format time and date for Indian timezone
        const time = now.toLocaleTimeString('en-IN', { 
            timeZone: 'Asia/Kolkata',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true 
        });
        const date = now.toLocaleDateString('en-IN', { 
            timeZone: 'Asia/Kolkata',
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
        
        // Get location from request or use default
        const location = req.body.location || config.whatsapp.defaultLocation;
        
        // Replace placeholders in message template
        let message = config.whatsapp.alertMessage
            .replace('{location}', location)
            .replace('{time}', time)
            .replace('{date}', date);
        
        // Allow custom message override
        if (req.body.message) {
            message = req.body.message;
        }
        
        // Get recipients from request or use config
        const recipients = req.body.recipients || config.whatsapp.recipients;
        
        // Check if WhatsApp is connected
        if (!isConnected) {
            console.log(`[${timestamp}] ⚠️  WhatsApp not connected, cannot send alert`);
            return res.status(503).json({ 
                success: false, 
                error: 'WhatsApp not connected' 
            });
        }
        
        // Send the message to all recipients
        const result = await sendWhatsAppMessage(recipients, message);
        
        res.json({ 
            success: true, 
            message: 'Alert sent to all recipients',
            timestamp: now.toISOString(),
            recipients: recipients.length,
            results: result.results
        });
        
    } catch (error) {
        console.error('❌ Error processing alert:', error);
        res.status(500).json({ 
            success: false, 
            error: error.message 
        });
    }
});

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
    res.json({
        status: 'running',
        whatsappConnected: isConnected,
        timestamp: new Date().toISOString()
    });
});

/**
 * Test endpoint - useful for manual testing
 */
app.post('/test', async (req, res) => {
    try {
        if (!isConnected) {
            return res.status(503).json({ error: 'WhatsApp not connected' });
        }
        
        const now = new Date();
        const time = now.toLocaleTimeString('en-IN', { 
            timeZone: 'Asia/Kolkata',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true 
        });
        const date = now.toLocaleDateString('en-IN', { 
            timeZone: 'Asia/Kolkata',
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
        
        const testMessage = `🧪 Test Alert from Guardian System\n\nTime: ${time}\nDate: ${date}\n\nThis is a test message. System is working correctly!`;
        const result = await sendWhatsAppMessage(config.whatsapp.recipients, testMessage);
        
        res.json({ 
            success: true, 
            message: 'Test message sent to all recipients',
            results: result.results 
        });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

/**
 * Start the service
 */
async function start() {
    console.log('=================================================');
    console.log('🚨 Emergency Alert System - WhatsApp Service');
    console.log('=================================================\n');
    
    // Connect to WhatsApp
    console.log('📡 Connecting to WhatsApp...');
    await connectToWhatsApp();
    
    // Start HTTP server
    const port = config.whatsapp.port || 3000;
    app.listen(port, 'localhost', () => {
        console.log(`\n🌐 HTTP server listening on http://localhost:${port}`);
        console.log('\nEndpoints:');
        console.log(`  GET  /        - Safety Dashboard`);
        console.log(`  POST /alert  - Send emergency alert`);
        console.log(`  POST /test   - Send test message`);
        console.log(`  GET  /health - Check service status`);
        console.log('\n✅ Service ready! Waiting for alerts...\n');
        console.log(`📊 View Dashboard: http://localhost:${port}`);
    });
}

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('\n\n⚠️  Shutting down gracefully...');
    if (sock) {
        sock.end();
    }
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n\n⚠️  Shutting down gracefully...');
    if (sock) {
        sock.end();
    }
    process.exit(0);
});

// Start the service
start().catch(console.error);
