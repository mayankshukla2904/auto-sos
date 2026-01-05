"""
Emergency Alert System - Wake Word Detector

This script:
1. Continuously listens to microphone input
2. Detects the wake word "help" using Porcupine
3. Sends HTTP request to WhatsApp service when detected
4. Implements debouncing to prevent spam
5. Provides detailed logging

Platform: Cross-platform (Windows, Linux, Raspberry Pi)
"""

import pvporcupine
import pyaudio
import struct
import requests
import json
import time
from datetime import datetime

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

# Extract settings
SENSITIVITY = config['detection']['sensitivity']
COOLDOWN_SECONDS = config['detection']['cooldownSeconds']
DEVICE_INDEX = config['detection'].get('audioDeviceIndex', None)
WHATSAPP_PORT = config['whatsapp'].get('port', 3000)
WHATSAPP_URL = f"http://localhost:{WHATSAPP_PORT}/alert"

# Debouncing - track last detection time
last_detection_time = 0


def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def send_alert():
    """Send alert to WhatsApp service via HTTP"""
    global last_detection_time
    
    current_time = time.time()
    
    # Check cooldown period
    if current_time - last_detection_time < COOLDOWN_SECONDS:
        elapsed = int(current_time - last_detection_time)
        log(f"⏸️  Cooldown active ({elapsed}s / {COOLDOWN_SECONDS}s), skipping alert")
        return False
    
    try:
        log("📤 Sending alert to WhatsApp service...")
        
        # Send POST request to WhatsApp service
        response = requests.post(
            WHATSAPP_URL,
            json={"message": config['whatsapp']['alertMessage']},
            timeout=10
        )
        
        if response.status_code == 200:
            log("✅ Alert sent successfully!")
            last_detection_time = current_time
            return True
        else:
            log(f"❌ Alert failed: HTTP {response.status_code}")
            log(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        log("❌ Cannot connect to WhatsApp service. Is it running?")
        log("   Start it with: node whatsapp_service.js")
        return False
    except Exception as e:
        log(f"❌ Error sending alert: {e}")
        return False


def list_audio_devices():
    """List all available audio input devices"""
    pa = pyaudio.PyAudio()
    print("\n🎤 Available audio devices:")
    print("-" * 60)
    
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:  # Only show input devices
            print(f"  [{i}] {info['name']}")
            print(f"      Sample Rate: {int(info['defaultSampleRate'])} Hz")
            print(f"      Channels: {info['maxInputChannels']}")
            print()
    
    pa.terminate()
    print("-" * 60 + "\n")


def test_whatsapp_service():
    """Check if WhatsApp service is running"""
    try:
        response = requests.get(f"http://localhost:{WHATSAPP_PORT}/health", timeout=3)
        data = response.json()
        
        if data.get('whatsappConnected'):
            log("✅ WhatsApp service is connected and ready")
            return True
        else:
            log("⚠️  WhatsApp service is running but not connected to WhatsApp")
            log("   Please scan the QR code in the WhatsApp service terminal")
            return False
            
    except requests.exceptions.ConnectionError:
        log("❌ WhatsApp service is not running!")
        log("   Please start it first: node whatsapp_service.js")
        return False
    except Exception as e:
        log(f"⚠️  Warning: Could not check WhatsApp service status: {e}")
        return False


def main():
    """Main wake word detection loop"""
    
    print("\n" + "=" * 60)
    print("🚨 Emergency Alert System - Wake Word Detector")
    print("=" * 60 + "\n")
    
    # List audio devices
    list_audio_devices()
    
    # Test WhatsApp service connection
    log("🔍 Checking WhatsApp service...")
    service_ready = test_whatsapp_service()
    
    if not service_ready:
        log("\n⚠️  WARNING: WhatsApp service is not ready. Alerts may fail.")
        log("   Press Ctrl+C to exit, or any other key to continue anyway...")
        try:
            input()
        except KeyboardInterrupt:
            log("\nExiting...")
            return
    
    # Initialize Porcupine
    log("\n🎯 Initializing Porcupine wake word engine...")
    
    try:
        # Create Porcupine detector with built-in "help me" keyword
        # Note: Porcupine doesn't have "help" as a built-in keyword,
        # but has "hey pico" which we'll use for demonstration.
        # For production, you'd need to train a custom model for "help"
        # or use one of the built-in keywords.
        
        porcupine = pvporcupine.create(
            access_key='',  # Free tier - no key needed for built-in keywords
            keywords=['picovoice'],  # Built-in keyword (change to custom model for "help")
            sensitivities=[SENSITIVITY]
        )
        
        log(f"✅ Porcupine initialized (v{porcupine.version})")
        log(f"   Sample Rate: {porcupine.sample_rate} Hz")
        log(f"   Frame Length: {porcupine.frame_length}")
        log(f"   Sensitivity: {SENSITIVITY}")
        log(f"   Cooldown: {COOLDOWN_SECONDS} seconds")
        
    except Exception as e:
        log(f"❌ Failed to initialize Porcupine: {e}")
        log("\n💡 For production use with custom 'help' keyword:")
        log("   1. Sign up at https://console.picovoice.ai/")
        log("   2. Train a custom wake word 'help'")
        log("   3. Download the .ppn file")
        log("   4. Use keyword_paths=['path/to/help.ppn'] instead of keywords")
        return
    
    # Initialize PyAudio
    log("\n🎤 Opening audio stream...")
    pa = pyaudio.PyAudio()
    
    try:
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
            input_device_index=DEVICE_INDEX
        )
        
        device_info = pa.get_device_info_by_index(
            DEVICE_INDEX if DEVICE_INDEX is not None 
            else pa.get_default_input_device_info()['index']
        )
        log(f"✅ Audio stream opened: {device_info['name']}")
        
    except Exception as e:
        log(f"❌ Failed to open audio stream: {e}")
        porcupine.delete()
        pa.terminate()
        return
    
    log("\n" + "=" * 60)
    log("🎧 LISTENING FOR WAKE WORD: 'picovoice'")
    log("   (For production, replace with custom 'help' model)")
    log("   Press Ctrl+C to stop")
    log("=" * 60 + "\n")
    
    try:
        while True:
            # Read audio frame
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            
            # Process audio frame
            keyword_index = porcupine.process(pcm)
            
            # Wake word detected!
            if keyword_index >= 0:
                log("🚨 WAKE WORD DETECTED!")
                send_alert()
                
    except KeyboardInterrupt:
        log("\n\n⚠️  Stopping wake word detector...")
        
    finally:
        # Cleanup
        log("🧹 Cleaning up resources...")
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        porcupine.delete()
        log("✅ Shutdown complete\n")


if __name__ == "__main__":
    main()
