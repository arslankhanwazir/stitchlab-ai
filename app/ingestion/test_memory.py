"""
M0.1 Memory test:
Runs after parsing documents, invokes Ollama with test prompt,
measures RAM before and after, checks for OOM errors.
"""

import subprocess
import time
import ctypes

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]

def get_avail_phys_mb():
    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    return round(stat.ullAvailPhys / (1024 * 1024), 2)

def run_test():
    print("=== M0.1 Stage 0 Memory Test ===")
    ram_before = get_avail_phys_mb()
    print(f"Available physical RAM before Ollama run: {ram_before} MB")
    
    ollama_cmd = [
        r"F:\Ollama\ollama.exe",
        "run",
        "llama3.2:3b",
        "Reply with one short sentence about document assistants."
    ]
    
    t0 = time.time()
    try:
        res = subprocess.run(
            ollama_cmd,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=True
        )
        elapsed = round(time.time() - t0, 2)
        output = res.stdout.strip()
        oom_error = False
    except subprocess.CalledProcessError as e:
        elapsed = round(time.time() - t0, 2)
        output = f"ERROR: {e.stderr}"
        oom_error = True
    
    ram_after = get_avail_phys_mb()
    print(f"Ollama output: {output}")
    print(f"Elapsed time: {elapsed} s")
    print(f"Available physical RAM after Ollama run: {ram_after} MB")
    print(f"RAM difference: {round(ram_before - ram_after, 2)} MB")
    print(f"Out of memory error: {oom_error}")
    
    return {
        "ram_before_mb": ram_before,
        "ram_after_mb": ram_after,
        "elapsed_s": elapsed,
        "output": output,
        "oom_error": oom_error,
    }

if __name__ == "__main__":
    run_test()
