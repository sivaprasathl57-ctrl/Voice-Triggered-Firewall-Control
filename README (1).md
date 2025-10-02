
# 🔒 Voice-Triggered Firewall Control
In this project I can do in Kali Linux(optional) and You can do as a cmd(Windows also) Or other OS 

📌 Project Description

The Voice-Triggered Firewall Control project is a Python-based security automation tool that allows users to manage firewall rules using voice commands. It integrates speech recognition (STT) to understand spoken instructions, command parsing to map those instructions to firewall rules, and text-to-speech (TTS) for real-time feedback.

The project enables hands-free control over Linux firewall utilities such as UFW (Uncomplicated Firewall) or iptables, allowing users to dynamically enable/disable the firewall, block or allow ports, and check firewall status using only their voice.

# 📊 Features

- ✅ Enable/Disable Firewall

- ✅ Check Firewall Status

- ✅ Block specific ports

- ✅ Allow specific ports

- ✅ Voice feedback for every action

# 🛠️ Technologies Used

- Python 3.x

- Libraries:

   speech_recognition → Voice recognition (Google API or offline PocketSphinx)

   pyttsx3 → Text-to-Speech feedback

   os / subprocess → Execute firewall commands

- Firewall Tools:

  UFW (Uncomplicated Firewall)

  iptables (low-level packet filtering)

# ⚙️ Workflow

- Audio Capture

- Microphone records the user’s voice input.

- Speech-to-Text (STT)

- Converts spoken commands into text using speech_recognition library.

Example: “Block port 22”.

- Command Parsing

- Python script interprets the text and matches it to firewall actions.

Example: "block port 22" → ufw deny 22.

- Firewall Execution

- Executes UFW/iptables command on the system.

- Text-to-Speech (TTS) Feedback

- Provides audio confirmation to the user via pyttsx3.

Example: “Port 22 has been blocked.”

![1](https://github.com/user-attachments/assets/d4854b50-0a32-4106-b604-b1af415fb242)


## Installation

 1. System Requirements

- OS: Kali Linux / Ubuntu / Debian-based

- Python: 3.8+ (check with python3 --version)

- Firewall tool: ufw (comes pre-installed on Kali, but verify)

- Internet connection (if using Google Speech API; optional if using offline PocketSphinx)

- Microphone (working input device)

- Speakers (for TTS feedback)

2. Install Firewall Tool (UFW)
```bash
sudo apt install ufw -y
```

Enable UFW (optional at first):
```bash
sudo ufw enable
```
3. Create Virtual Environment
```bash
sudo apt install python3-venv -y
python3 -m venv myenv
source myenv/bin/activate
```
Now you’re inside (myenv) virtual environment.
5. Install Python Dependencies
```bash
pip install --upgrade pip
pip install speechrecognition pyttsx3 pyaudio pocketsphinx
```
⚠️ If pyaudio fails to build:
```bash
sudo apt install portaudio19-dev python3-pyaudio -y
pip install pyaudio
```
6. Test Audio Setup

Check if your microphone works:
```bash
arecord -l
```

Test recording:
```bash
arecord test.wav
aplay test.wav
```
7. Create Project File

Create voice_firewall.py:
```bash
nano voice_firewall.py
```
8. Run the Project

Activate environment:
```bash
source myenv/bin/activate
```
Run script:
```bash
python3 voice_firewall.py
```
Speak:

- "Enable firewall"

- "Block port 22"

- "Allow port 80"

- "Status"
✅ After these steps, you’ll have a fully working voice-controlled firewall
## Screenshots

![2](https://github.com/user-attachments/assets/8164e414-cd59-4e9b-b9b9-abe5bab88718)

![3(2)](https://github.com/user-attachments/assets/632c8dc4-3b8f-47b2-898d-fa9f0d5bea81)

![3](https://github.com/user-attachments/assets/d786085d-16d0-4a78-b5bb-68c9d00a046e)

![4](https://github.com/user-attachments/assets/49c2b21a-6a38-4423-8004-546d8962ed59)



## Demo
https://github.com/user-attachments/assets/9b393615-907b-40a6-9364-4ed6c5363d14

