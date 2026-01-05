"""
Test Microphone - Emergency Alert System

This script helps you test your microphone setup and volume levels.
Run this before using the wake word detector to ensure your microphone works.
"""

import pyaudio
import numpy as np
import time

def list_devices():
    """List all audio input devices"""
    pa = pyaudio.PyAudio()
    print("\n🎤 Available Audio Input Devices:")
    print("=" * 70)
    
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"\n  Device [{i}]: {info['name']}")
            print(f"    Sample Rate: {int(info['defaultSampleRate'])} Hz")
            print(f"    Input Channels: {info['maxInputChannels']}")
            if i == pa.get_default_input_device_info()['index']:
                print("    ★ DEFAULT DEVICE")
    
    pa.terminate()
    print("\n" + "=" * 70 + "\n")


def test_microphone(device_index=None, duration=5):
    """Test microphone by recording and showing volume levels"""
    
    print(f"\n🎙️  Testing Microphone (Device: {device_index if device_index else 'Default'})")
    print("=" * 70)
    
    pa = pyaudio.PyAudio()
    
    try:
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024,
            input_device_index=device_index
        )
        
        print(f"\n✅ Microphone opened successfully!")
        print(f"   Recording for {duration} seconds...")
        print(f"   Speak into your microphone to see volume levels\n")
        
        start_time = time.time()
        max_volume = 0
        
        while time.time() - start_time < duration:
            try:
                # Read audio data
                data = stream.read(1024, exception_on_overflow=False)
                
                # Convert to numpy array and calculate volume
                audio_data = np.frombuffer(data, dtype=np.int16)
                volume = np.abs(audio_data).mean()
                max_volume = max(max_volume, volume)
                
                # Create visual volume bar
                bar_length = int(volume / 100)
                bar = "█" * min(bar_length, 50)
                
                # Show volume with color coding
                if volume < 500:
                    status = "🔇 Too quiet"
                elif volume < 2000:
                    status = "✅ Good level"
                else:
                    status = "🔊 Loud"
                
                print(f"\rVolume: {volume:6.0f} {bar:50s} {status}", end="", flush=True)
                
            except Exception as e:
                print(f"\n❌ Error reading audio: {e}")
                break
        
        print(f"\n\n📊 Test Results:")
        print(f"   Maximum Volume: {max_volume:.0f}")
        
        if max_volume < 300:
            print(f"   ⚠️  Volume very low - check microphone settings")
            print(f"      • Increase microphone volume in Windows Sound Settings")
            print(f"      • Speak closer to the microphone")
            print(f"      • Check if microphone is muted")
        elif max_volume < 1000:
            print(f"   ⚠️  Volume somewhat low - wake word detection may be unreliable")
            print(f"      Consider increasing microphone volume")
        else:
            print(f"   ✅ Volume good! Wake word detection should work well")
        
        stream.stop_stream()
        stream.close()
        
    except Exception as e:
        print(f"\n❌ Error opening microphone: {e}")
        print(f"\nTroubleshooting:")
        print(f"  • Make sure microphone is plugged in")
        print(f"  • Check Windows Sound Settings (mic permissions)")
        print(f"  • Try a different device index")
        
    finally:
        pa.terminate()
    
    print("\n" + "=" * 70 + "\n")


def main():
    print("\n" + "=" * 70)
    print("   🎤 Microphone Test Tool")
    print("=" * 70)
    
    # List all devices
    list_devices()
    
    # Ask user which device to test
    print("Select action:")
    print("  [Enter] - Test default microphone")
    print("  [number] - Test specific device by index")
    print("  [q] - Quit")
    
    choice = input("\nYour choice: ").strip()
    
    if choice.lower() == 'q':
        print("\nExiting...")
        return
    
    device_index = None
    if choice.isdigit():
        device_index = int(choice)
        print(f"\nTesting device {device_index}...")
    else:
        print(f"\nTesting default device...")
    
    # Test the microphone
    test_microphone(device_index=device_index, duration=5)
    
    print("Test complete! You can now use the wake word detector.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test cancelled by user\n")
