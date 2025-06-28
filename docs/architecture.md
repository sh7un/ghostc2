# GhostC2 Architecture

GhostC2 is a **modular Python Command & Control framework** designed for educational red-teaming and controlled testing. Its design follows a clear separation of concerns:

## 1. Core Components

- **vx_server.py**  
  - Listens for agent connections over TCP.  
  - Offers an interactive CLI (`ghostc2>`) for issuing commands.  
  - Uses `modules/comms.py` for reliable, length-prefixed JSON+base64 transport.  
  - Delegates file transfers to `modules/file_transfer.py`.

- **vx_agent.py**  
  - Connects back to the server.  
  - Performs a simple handshake to ensure sync.  
  - Listens for commands via `comms.rrecv()` and replies with `comms.rsend()`.  
  - Handles:
    - **Directory changes** (`cd`)  
    - **File exfiltration** (`download <file>`)  
    - **Arbitrary shell commands** via `subprocess.check_output`

- **setup.py**
  - Compiles vx_agent and vx_setup to tools/compiled. If you want it to be a linux executable, you need to run the script IN linux.
  - Bundles all needed libraries into the EXE (or whatever your system's executable is) so it can run almost natively.

## 2. Modules

- **modules/comms.py**  
  - Implements `rsend()` and `rrecv()` with:
    - 16-byte length header  
    - JSON wrapping  
    - `{"__b64__": "<data>"}` marker for binary  
    - Exact-length reads & trims  
- **modules/file_transfer.py**  
  - `send(sock, cmd)` → reads a local file, sends it as raw bytes via `comms.rsend()`  
  - `receive(sock, cmd)` → triggers send, streams in raw bytes, writes to disk  

## 3. Workflow

1. **Clone repo**  
2. **Install dependencies** (`pip install -r requirements.txt`)  
3. **Build** (optional):  
   ```bash
   python setup.py
4. **Launch Server**:
   ```bash
   python vx_server.py
   ```
5. **Deploy Agent** on test VM/host:

   ```bash
   python vx_agent.py
   ```
6. **Use CLI**: `ghostc2> help`, `cd`, `download`, `exit`, etc.

## 4. Future Roadmap

* AES-encrypted comms
* Modular plugin system (`modules/`)
* Cross-platform support (Windows service, macOS launch agent)
* Automated persistence options
* Stealth & obfuscation layers
* YOUR Suggestions