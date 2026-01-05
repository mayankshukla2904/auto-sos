# AutoSOS - Voice-Activated Emergency Alert System

A simple emergency alert system that detects the word "help" and automatically sends WhatsApp messages to emergency contacts.

## 🚀 Quick Setup Guide (For Complete Beginners)

Follow these steps **exactly** to get the system running on your laptop:

### Step 1: Install Required Software

1. **Install Node.js** (JavaScript Runtime)
   - Go to: https://nodejs.org/
   - Download the **LTS version** (recommended)
   - Run the installer and click "Next" until finished
   - Restart your computer

2. **Install Python** (Programming Language)
   - Go to: https://www.python.org/downloads/
   - Download **Python 3.10 or higher**
   - **IMPORTANT**: Check "Add Python to PATH" during installation
   - Click "Install Now"
   - Restart your computer

3. **Install Git** (Version Control)
   - Go to: https://git-scm.com/download/win
   - Download and install with default settings

### Step 2: Download This Project

Open **Command Prompt** or **PowerShell** and run:
```bash
cd Desktop
git clone https://github.com/mayankshukla2904/auto-sos.git
cd auto-sos
```

### Step 3: Install Node.js Dependencies

In the same terminal window, run:
```bash
npm install
```
Wait for it to finish (may take 1-2 minutes).

### Step 4: Install Python Dependencies

**For Windows:**
```bash
pip install requests numpy
pip install pvporcupine
pip install pyaudio
```

**If PyAudio fails on Windows**, download the wheel file:
- Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
- Download the file matching your Python version (e.g., `PyAudio‑0.2.13‑cp310‑cp310‑win_amd64.whl` for Python 3.10)
- Install it:
```bash
pip install path\to\PyAudio‑0.2.13‑cp310‑cp310‑win_amd64.whl
```

### Step 5: Configure Your Emergency Contacts

1. Open `config.json` file in Notepad
2. Replace the phone numbers with your emergency contacts:
   ```json
   "recipients": [
     "91XXXXXXXXXX@s.whatsapp.net",
     "91YYYYYYYYYY@s.whatsapp.net"
   ]
   ```
   **Format**: Country code + phone number + `@s.whatsapp.net`
   - Example: For Indian number 9876543210, use `919876543210@s.whatsapp.net`
3. Change the location if needed (e.g., "Home", "Office", "School")
4. Save and close the file

### Step 6: Start the WhatsApp Service

Open a terminal and run:
```bash
node whatsapp_service.js
```

You will see a **QR code** in the terminal:
1. Open WhatsApp on your phone
2. Go to **Settings** → **Linked Devices**
3. Tap **"Link a Device"**
4. Scan the QR code shown in the terminal
5. Wait for "✅ WhatsApp connected successfully!" message

**Keep this terminal window open!**

### Step 7: Start the Voice Detector

Open a **NEW** terminal window (keep the first one running):
```bash
cd Desktop\auto-sos
python wake_word_detector.py
```

You should see:
```
🎤 Listening for wake word 'help'...
```

**Keep both terminal windows open!**

### Step 8: Test the System

Say **"help"** clearly near your microphone. You should see:
- Terminal shows: `🚨 ALERT TRIGGERED! Sending to WhatsApp...`
- All emergency contacts receive a WhatsApp message

## 📱 Web Dashboard

Open your browser and go to: http://localhost:3000

Here you can:
- See connection status
- Send test alerts
- Manually trigger emergency alerts

## 🔧 Troubleshooting

### "Command not found" errors
- Make sure you restarted your computer after installing Node.js and Python
- Check if Python is in PATH: run `python --version`
- Check if Node is in PATH: run `node --version`

### Microphone not working
- Check Windows microphone permissions
- Go to: Settings → Privacy → Microphone → Allow apps to access microphone

### WhatsApp not connecting
- Make sure your phone has internet connection
- Delete the `auth_info_baileys` folder and scan QR code again
- Only one device can be linked at a time

### Wake word not detected
- Speak clearly and louder
- Check if microphone is working (try recording voice)
- Adjust sensitivity in `config.json` (default is 0.5, try 0.3 for more sensitive)

## 📋 Daily Usage

1. Open two terminal windows
2. In Terminal 1: `node whatsapp_service.js` (scan QR if needed)
3. In Terminal 2: `python wake_word_detector.py`
4. System is now active and listening!

## 🛑 To Stop the System

Press `Ctrl+C` in both terminal windows.

## 📞 Support

For issues, visit: https://github.com/mayankshukla2904/auto-sos/issues

---
**Made with ❤️ for Safety**
