import pyaudio

def list_audio_devices():
    """Lists all available PyAudio input devices."""
    p = None
    try:
        p = pyaudio.PyAudio()
        print("Available audio input devices:")
        print("-" * 30)
        found_input_device = False
        # Get the number of available devices
        num_devices = p.get_device_count()
        if num_devices == 0:
             print("No audio devices found.")
             return

        # Iterate through all devices and print input device info
        for i in range(num_devices):
            device_info = p.get_device_info_by_index(i)
            # Check if the device has any input channels
            if device_info.get('maxInputChannels', 0) > 0:
                print(f"Index: {i}")
                print(f"  Name: {device_info.get('name', 'N/A')}")
                # Get Host API info
                host_api_info = p.get_host_api_info_by_index(device_info.get('hostApi', 0))
                print(f"  Host API: {host_api_info.get('name', 'N/A')}")
                print(f"  Max Input Channels: {device_info.get('maxInputChannels', 0)}")
                print("-" * 10)
                found_input_device = True

        if not found_input_device:
            print("No audio input devices with input channels found.")

    except ImportError:
        print("Error: PyAudio is not installed. Please install it using 'pip install pyaudio'")
    except Exception as e:
        print(f"An error occurred while listing devices: {e}")
    finally:
        # Terminate the PyAudio instance
        if p is not None:
            p.terminate()

if __name__ == "__main__":
    list_audio_devices()