# Voice Control System

A speech recognition system that responds to voice commands for different rooms using PocketSphinx.

## Overview

This project implements a simple voice command system that can recognize room names (Living Room, Kitchen, Bedroom) and an exit command. When a command is recognized, the system responds with a text-to-speech confirmation using Flite.

## Requirements

The project requires the following dependencies:
- Python 3.x
- PocketSphinx 5.0.4
- PyAudio 0.2.14
- Flite (speech synthesis)

All Python dependencies are listed in the [`requirements.txt`](requirements.txt) file.

## Files in the Project

- [`voice_command.py`](voice_command.py): Main application that listens for voice commands
- [`list_audio_devices.py`](list_audio_devices.py): Utility to list available audio input devices
- [`room_commands.jsgf`](room_commands.jsgf): Grammar file defining the commands
- [`room_vocabulary.dic`](room_vocabulary.dic): Dictionary file with phonetic pronunciations
- [`requirements.txt`](requirements.txt): Python dependencies

## Setup Instructions

1. Install required packages:
   ```
   pip install -r requirements.txt
   ```

2. Install Flite text-to-speech engine:
   - On Ubuntu/Debian: `sudo apt-get install flite`
   - On other systems: refer to [Flite documentation](http://www.festvox.org/flite/)

3. Ensure PocketSphinx acoustic models are installed (usually at `/usr/share/pocketsphinx/model/en-us`)

4. Run the [`list_audio_devices.py`](list_audio_devices.py) script to identify your microphone:
   ```
   python list_audio_devices.py
   ```

5. Update the `mic_device_index` in [`voice_command.py`](voice_command.py) (line 179) with your microphone's index number

## Running the Application

Execute the main script:
```
python voice_command.py
```

Once running, you can say any of the following commands:
- "Living Room"
- "Kitchen"
- "Bedroom"
- "Exit" (terminates the program)

## Troubleshooting

- If you receive errors about audio devices, run [`list_audio_devices.py`](list_audio_devices.py) to check available devices
- Ensure the paths in the configuration section of [`voice_command.py`](voice_command.py) match your system
- If speech recognition is poor, you may need to adjust the microphone settings or improve acoustic conditions

## How It Works

1. The system loads a grammar file that defines the commands it can recognize
2. Audio is captured from the microphone in real-time
3. PocketSphinx processes the audio and attempts to match it against known commands
4. When a command is recognized, a confirmation is spoken using Flite
5. The system continues listening until "Exit" is spoken or Ctrl+C is pressed