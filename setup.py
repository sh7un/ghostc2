# setup.py
import os
import subprocess
import shutil

COMPILED_DIR = "tools/compiled"
FILES = ["vx_server.py", "vx_agent.py"]

def ensure_dir():
    os.makedirs(COMPILED_DIR, exist_ok=True)

def compile_file(file):
    name = os.path.splitext(os.path.basename(file))[0]
    print(f"[+] Compiling {file}...")
    subprocess.run([
        "pyinstaller",
        "--onefile",
        "--distpath", COMPILED_DIR,
        "--workpath", "build",
        "--specpath", "build",
        file
    ], check=True)
    print(f"[+] Output: {COMPILED_DIR}/{name}.exe" if os.name == "nt" else f"[+] Output: {COMPILED_DIR}/{name}")

def cleanup():
    shutil.rmtree("build", ignore_errors=True)
    for f in FILES:
        spec = os.path.splitext(f)[0] + ".spec"
        if os.path.exists(spec):
            os.remove(spec)

if __name__ == "__main__":
    ensure_dir()
    for f in FILES:
        if not os.path.exists(f):
            print(f"[!] Skipping: {f} not found.")
            continue
        compile_file(f)
    cleanup()
    print("\n[✔] Compilation complete. Check ./tools/compiled/")
