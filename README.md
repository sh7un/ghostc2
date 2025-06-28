# ghostc2

A simple, extensible python C2 framework for learning offensive security, red teaming, and socket programming.

## Features
- Reverse shell agent
- Command execution
- File exfiltration
- Modular design
- Easy to extend
- Clean(ish) code

## Usage
1. Clone this repo
2. Run ```pip install -r requirements.txt``` with cmd or your console
3. Set `HOST` in `vx_agent.py` to your IP
4. Run `vx_server.py` to listen
5. Deploy `vx_agent.py` on target (test system only)
6. Type commands like a boss

## TODO
- Add AES encryption module
- Add persistence module
- Convert agent to Windows `.exe` (YOU can do this by installing nuitka, pyinstaller or auto-py-to-exe and compiling it yourself.)
- Obfuscate agent script

## Disclaimer
!!! For educational use only. You break, you buy. !!!

---
