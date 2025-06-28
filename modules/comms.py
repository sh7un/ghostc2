# modules/comms.py
import json
import base64

HEADER_SIZE = 16  # fixed-width header

def rsend(sock, data, dtype="output", filename=None):
    """
    Sends a type-aware message over socket. 
    - dtype: 'output', 'error', 'file'
    """
    if isinstance(data, bytes):
        payload = {"__b64__": base64.b64encode(data).decode()}
    else:
        payload = data

    wrapper = {
        "type": dtype,
        "payload": payload
    }

    if filename:
        wrapper["filename"] = filename

    blob = json.dumps(wrapper).encode()
    length = f"{len(blob):<{HEADER_SIZE}}".encode()
    sock.sendall(length + blob)


def rrecv(sock):
    length_bytes = sock.recv(HEADER_SIZE)
    if not length_bytes:
        return None
    try:
        total = int(length_bytes.decode().strip())
    except Exception as e:
        print(f"[!] Invalid header {length_bytes!r}: {e}")
        return None

    data = b""
    while len(data) < total:
        chunk = sock.recv(min(1024, total - len(data)))
        if not chunk:
            break
        data += chunk

    if len(data) > total:
        data = data[:total]

    try:
        decoded = json.loads(data.decode())
    except Exception as e:
        print(f"[!] JSON decode failed on {data[:100]!r}…: {e}")
        return None

    # Binary unwrap inside payload
    if isinstance(decoded, dict) and isinstance(decoded.get("payload"), dict):
        if "__b64__" in decoded["payload"]:
            try:
                decoded["payload"] = base64.b64decode(decoded["payload"]["__b64__"])
            except Exception as e:
                print(f"[!] Base64 decode failed: {e}")
                return None

    return decoded

