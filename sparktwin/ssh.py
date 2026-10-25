"""Optional read-only SSH discovery using the already-configured system OpenSSH client."""
from __future__ import annotations
import re, subprocess
from pathlib import Path

VALID_HOST = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.@-]{0,253}$")


def aliases(config_path=None):
    path=Path(config_path) if config_path else Path.home()/".ssh"/"config"
    if not path.is_file(): return []
    # Display ordinary aliases only; OpenSSH itself processes Include/ProxyJump.
    out=[]
    try:
        for line in path.read_text(encoding="utf-8",errors="replace").splitlines():
            match=re.match(r"^\s*Host\s+(.+?)\s*(?:#.*)?$",line,re.I)
            if match:
                for a in match.group(1).split():
                    if VALID_HOST.fullmatch(a) and not any(x in a for x in "*?!") and a not in out:
                        out.append(a)
    except OSError: return []
    return out[:250]


def inspect(host: str, timeout=12, runner=subprocess.run):
    if not isinstance(host,str) or not VALID_HOST.fullmatch(host):
        raise ValueError("Use a saved SSH alias or hostname; no shell symbols or whitespace")
    # Host-key acceptance must be verified out-of-band using normal SSH first.
    command="printf 'MEMINFO\\n'; cat /proc/meminfo; printf '\\nHOSTINFO\\n'; uname -srm; printf '\\nGPUINFO\\n'; (nvidia-smi -L || true) 2>/dev/null"
    args=["ssh","-o","BatchMode=yes","-o","StrictHostKeyChecking=yes",
          "-o","ConnectTimeout=6","-o","NumberOfPasswordPrompts=0",host,command]
    try:
        result=runner(args,capture_output=True,text=True,timeout=timeout,check=False)
    except FileNotFoundError as e: raise RuntimeError("System OpenSSH client is not installed") from e
    except subprocess.TimeoutExpired as e: raise RuntimeError("SSH inspection timed out") from e
    if result.returncode!=0:
        raise RuntimeError("SSH failed. Check network, known_hosts fingerprint and key/agent authentication. "
                           + (result.stderr or "")[-450:])
    text=result.stdout
    if "MEMINFO\n" not in text or "HOSTINFO\n" not in text:
        raise RuntimeError("Unexpected remote diagnostic response")
    meta=dict((a, int(b)) for a,b in re.findall(r"^(MemTotal|MemAvailable):\s+(\d+) kB",text,re.M))
    if "MemTotal" not in meta or "MemAvailable" not in meta:
        raise RuntimeError("Remote Linux /proc/meminfo missing expected fields")
    hostinfo=text.split("HOSTINFO\n",1)[1].split("\nGPUINFO\n",1)[0].strip()[:200]
    gpu=text.split("GPUINFO\n",1)[-1].strip()[:500] if "GPUINFO\n" in text else ""
    return {"host": host, "system":hostinfo,"gpu":gpu or "Not reported by nvidia-smi",
            "memory_total_gib":round(meta["MemTotal"]*1024/1024**3,3),
            "memory_available_gib":round(meta["MemAvailable"]*1024/1024**3,3),
            "observed":True,
            "note":"Read-only snapshot of shared system memory. This does not measure isolated GPU VRAM or prove model fit."}
