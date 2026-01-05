"""
Emergency Alert System - Wake Word Detector (Vosk Version)

This version uses Vosk for speech recognition - it's completely offline
and can detect any word including "help" without custom training.

Vosk is heavier than Porcupine but more flexible and truly offline.
"""

import pyaudio
import json
import requests
import time
from datetime import datetime
from vosk import Model, KaldiRecognizer

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

# Extract settings
WAKE_WORDS = [word.lower() for word in config['detection'].get('wakeWords', ['help'])]
COOLDOWN_SECONDS = config['detection']['cooldownSeconds']
DEVICE_INDEX = config['detection'].get('audioDeviceIndex', None)
WHATSAPP_PORT = config['whatsapp'].get('port', 3000)
WHATSAPP_URL = f"http://localhost:{WHATSAPP_PORT}/alert"

# Debouncing
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
            return False
            
    except requests.exceptions.ConnectionError:
        log("❌ Cannot connect to WhatsApp service. Is it running?")
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
        if info['maxInputChannels'] > 0:
            print(f"  [{i}] {info['name']}")
            print(f"      Sample Rate: {int(info['defaultSampleRate'])} Hz")
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
            return False
            
    except requests.exceptions.ConnectionError:
        log("❌ WhatsApp service is not running!")
        log("   Please start it first: node whatsapp_service.js")
        return False
    except Exception as e:
        log(f"⚠️  Could not check WhatsApp service: {e}")
        return False


def main():
    """Main wake word detection loop"""
    
    print("\n" + "=" * 60)
    print("🚨 Emergency Alert System - Wake Word Detector (Vosk)")
    print("=" * 60 + "\n")
    
    list_audio_devices()
    
    log("🔍 Checking WhatsApp service...")
    service_ready = test_whatsapp_service()
    
    if not service_ready:
        log("\n⚠️  WARNING: WhatsApp service is not ready.")
        log("   Press Ctrl+C to exit, or Enter to continue...")
        try:
            input()
        except KeyboardInterrupt:
            log("\nExiting...")
            return
    
    # Initialize Vosk model
    log("\n🎯 Loading Vosk speech recognition model...")
    log("   (First run will download ~40MB model)")
    
    try:
        # Use small English model for fast detection
        model = Model(model_name="vosk-model-small-en-us-0.15")
        recognizer = KaldiRecognizer(model, 16000)
        recognizer.SetWords(False)  # We only need the text, not word timings
        
        log("✅ Vosk model loaded successfully")
        
    except Exception as e:
        log(f"❌ Failed to load Vosk model: {e}")
        log("\n💡 Install Vosk model manually:")
        log("   pip install vosk")
        log("   The model will auto-download on first run")
        return
    
    # Initialize PyAudio
    log("\n🎤 Opening audio stream...")
    pa = pyaudio.PyAudio()
    
    try:
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4000,
            input_device_index=DEVICE_INDEX
        )
        
        device_info = pa.get_device_info_by_index(
            DEVICE_INDEX if DEVICE_INDEX is not None 
            else pa.get_default_input_device_info()['index']
        )
        log(f"✅ Audio stream opened: {device_info['name']}")
        
    except Exception as e:
        log(f"❌ Failed to open audio stream: {e}")
        pa.terminate()
        return
    
    log("\n" + "=" * 60)
    log(f"🎧 LISTENING FOR WAKE WORDS: {', '.join(WAKE_WORDS[:5])}{'...' if len(WAKE_WORDS) > 5 else ''}")
    log(f"   Total wake words: {len(WAKE_WORDS)}")
    log(f"   Cooldown: {COOLDOWN_SECONDS} seconds")
    log("   Press Ctrl+C to stop")
    log("=" * 60 + "\n")
    
    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get('text', '').lower()
                
                if text:
                    # Show what was recognized (helps with debugging)
                    log(f"Recognized: '{text}'")
                    
                    # Check if any wake word is in the recognized text
                    detected_words = [word for word in WAKE_WORDS if word in text]
                    if detected_words:
                        log(f"🚨 WAKE WORD DETECTED: '{detected_words[0]}'")
                        send_alert()
                        
    except KeyboardInterrupt:
        log("\n\n⚠️  Stopping wake word detector...")
        
    finally:
        log("🧹 Cleaning up resources...")
        stream.stop_stream()
        stream.close()
        pa.terminate()
        log("✅ Shutdown complete\n")


if __name__ == "__main__":
    main()
