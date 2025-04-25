import os
import subprocess
import shlex
import sys
from pocketsphinx import Decoder, Config
import pyaudio # Required for microphone input

# --- Configuration ---
# IMPORTANT: Update these paths to match your system and file locations!
# You need the path to the acoustic model directory (e.g., en-us)
MODELDIR = "/usr/share/pocketsphinx/model/en-us" # Example path - CHECK YOUR INSTALLATION!
# Paths to your custom dictionary and grammar files
DICT_FILE = "room_vocabulary.dic"       # Make sure this file is in the same directory as the script, or provide a full path
GRAMMAR_FILE = "room_commands.jsgf"      # Make sure this file is in the same directory as the script, or provide a full path
GRAMMAR_NAME = "room_commands"            # This must match the 'grammar' name inside your .jsgf file

# Responses for recognized commands
RESPONSES = {
    "living room": "Acknowledged, Living Room.",
    "kitchen": "Affirmative, Kitchen.",
    "bedroom": "Understood, Bedroom.",
    "exit": "Exiting program." # Or whatever response you want
}

# --- Flite TTS Function ---
def speak_flite(text):
    """Calls the flite executable to speak the given text."""
    try:
        command = shlex.split(f'flite -voice slt -t "{text}"')
        subprocess.run(command, check=True, capture_output=True, text=True)
        # print(f"Spoke: {text}")
    except FileNotFoundError:
        print("\nError: Flite executable not found.")
        print("Please ensure Flite is installed and the 'flite' command is in your system's PATH.")
    except subprocess.CalledProcessError as e:
        print(f"\nError calling Flite: {e}")
        print(f"Stderr: {e.stderr}")
    except Exception as e:
        print(f"\nAn unexpected error occurred while trying to speak: {e}")

# --- PocketSphinx Recognition Setup ---
def setup_decoder():
    """Sets up and returns the PocketSphinx decoder config (without grammar/lm initially)."""
    # Check if required files exist (Dictionary and Model are needed for basic init)
    if not os.path.exists(DICT_FILE):
        print(f"Error: Dictionary file not found at {DICT_FILE}")
        return None
    # Basic model directory check
    if not os.path.exists(MODELDIR) or not os.path.exists(os.path.join(MODELDIR, 'en-us')): # Basic check
         print(f"Error: Acoustic model directory not found or incomplete at {MODELDIR}")
         print("Ensure MODELDIR points to the directory containing 'en-us' or the specific model folder.")
         return None

    # Use absolute paths for robustness
    abs_dict_path = os.path.abspath(DICT_FILE)
    abs_model_path = os.path.abspath(os.path.join(MODELDIR, 'en-us'))

    print(f"Attempting to initialize decoder with:")
    print(f"  Dict: {abs_dict_path}")
    print(f"  Model: {abs_model_path}")

    # Create a decoder configuration - DO NOT include jsgf or lm here initially
    config = Config(
        hmm=abs_model_path,
        dict=abs_dict_path,
        # jsgf=abs_grammar_path, # <-- REMOVE or comment out this line
        #sample_rate=16000,
    )

    # Initialize the decoder
    try:
        decoder = Decoder(config)
        print("PocketSphinx decoder initialized successfully (basic config).")
        return decoder
    except Exception as e:
        print(f"Error initializing PocketSphinx decoder: {e}")
        print("Please double-check paths to your model and dictionary files.")
        return None

def recognize_from_mic(decoder, audio_source):
    """
    Reads audio from the source and performs recognition.
    This function contains the main loop.
    Simplified utterance detection without deprecated get_in_speech().
    """
    print("\nReady! Say one of the commands: Living Room, Kitchen, Bedroom, Exit.")
    speak_flite("Ready! Say one of the commands: Living Room, Kitchen, Bedroom, Exit.")

    RATE = audio_source._rate
    CHUNK = 1024

    decoder.start_utt() # Start a new utterance

    try:
        while True:
            try:
                # Read audio data from the stream (this will block until audio is available)
                audio_chunk = audio_source.read(CHUNK, exception_on_overflow=False) # Add exception handling for overflow

            except IOError as e:
                 # This can happen if the audio device is disconnected or has an issue
                 print(f"\nError reading audio stream: {e}. Exiting.")
                 break # Exit the loop on error
            except Exception as e:
                 print(f"\nAn unexpected error occurred while reading audio: {e}. Exiting.")
                 break

            # Process the audio chunk
            # in_speech and force flags are often False for continuous processing
            decoder.process_raw(audio_chunk, False, False)

            # Check for a hypothesis after processing the chunk
            # hyp() returns the current best guess. It might change as more audio is processed.
            hypothesis = decoder.hyp()

            # --- Simplified Command Detection Logic ---
            # We check if a hypothesis exists and if it matches one of our commands.
            # In a real-world robust application, you would add more complex logic here:
            # - Check confidence score (hypothesis.prob)
            # - Monitor for periods of silence to truly detect end-of-utterance
            # - Use PocketSphinx's internal endpointer if reliable in your version/config
            # For this example, if we see a hypothesis matching a command, we'll act on it.

            if hypothesis:
                recognized_text = hypothesis.hypstr # Get the recognized string
                if recognized_text: # Ensure the hypothesis is not empty
                     # Clean up the recognized text
                     cleaned_text = recognized_text.lower().replace('<s>', '').replace('</s>', '').strip()

                     # Check if the cleaned text is one of our expected commands
                     if cleaned_text in RESPONSES:
                         # We detected a command!
                         print(f"\nRecognized: {recognized_text}") # Print the raw recognition
                         print(f"--- Command Detected: {cleaned_text} ---") # Print the cleaned command

                         # Act on the command
                         response = RESPONSES[cleaned_text]
                         speak_flite(response)
                         if cleaned_text == "exit":
                                print("Exiting program.")
                                break

                         # After detecting and acting on a command, finalize the current utterance
                         # and immediately start listening for the next one.
                         decoder.end_utt()
                         decoder.start_utt()
                         print("\nReady! Say one of the commands:")
                         # Continue the while loop to process more audio

            # You might want a small sleep here in a non-blocking read loop
            # to prevent high CPU usage, but PyAudio's blocking read handles this.


    except KeyboardInterrupt:
        print("\nStopping recognition.")
        decoder.end_utt() # Clean up the last utterance
    except Exception as e:
        print(f"\nAn unhandled error occurred during the recognition loop: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    # 1. Setup the decoder with base config
    decoder = setup_decoder()
    if decoder is None:
        sys.exit("Failed to setup PocketSphinx decoder.")

    # --- Load and Activate the Grammar Search ---
    try:
        # Ensure the grammar file exists before trying to add it
        abs_grammar_path = os.path.abspath(GRAMMAR_FILE)
        if not os.path.exists(abs_grammar_path):
             print(f"Error: Grammar file not found at {abs_grammar_path}")
             sys.exit("Failed to load grammar.")

        # Add the grammar file as a named search module
        # This method is listed in the activate_search docs
        decoder.add_jsgf_file(GRAMMAR_NAME, abs_grammar_path)
        print(f"Grammar file '{GRAMMAR_FILE}' loaded and added as search '{GRAMMAR_NAME}'.")

        # Activate the search module we just added
        decoder.activate_search(GRAMMAR_NAME)
        print(f"Grammar search '{GRAMMAR_NAME}' activated.")

    except Exception as e:
        # This catch will hopefully provide a more specific error if add_jsgf_file fails
        print(f"\nError loading or activating grammar search '{GRAMMAR_NAME}': {e}")
        print("Please ensure the grammar file path is correct and the grammar syntax is valid.")
        sys.exit("Failed to setup grammar search.")


    # 3. Setup Microphone Audio Input using PyAudio
    p = None
    stream = None
    try:
        p = pyaudio.PyAudio()
        mic_device_index=4
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        input_device_index=mic_device_index,
                        frames_per_buffer=1024)

        print("Microphone audio stream opened.")

        # 4. Start the recognition loop
        recognize_from_mic(decoder, stream)

    except ImportError:
        print("\nError: PyAudio is not installed.")
        print("Install it with: pip install pyaudio")
        print("Cannot run microphone input without PyAudio.")
    except Exception as e:
        print(f"\nError setting up microphone audio: {e}")
        print("Please check your microphone connection and PyAudio installation.")
    finally:
        if stream is not None:
            stream.stop_stream()
            stream.close()
            print("Microphone audio stream closed.")
        if p is not None:
            p.terminate()
            print("PyAudio terminated.")

    print("Script finished.")