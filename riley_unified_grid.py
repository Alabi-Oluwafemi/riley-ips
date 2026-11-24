# RILEY UNIFIED GRID v2.3 - FINAL - File + Network IPS with Auto-Kill
# Built by Oluwafemi Alabi - Riley Consultech
import os, time, datetime, json, subprocess, threading
from collections import defaultdict

# --- CONFIG ---
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")
QUARANTINE = os.path.join(DOWNLOADS, "_RILEY_QUARANTINE")
os.makedirs(QUARANTINE, exist_ok=True)
LOG_FILE = os.path.join(DOWNLOADS, "unified_grid_log.json")
HTML_FILE = os.path.join(DOWNLOADS, "unified_dashboard.html")
AUTO_KILL = True
WHITELISTED_PROCESSES = ["pia-service.exe", "pia_service.exe", "pia-client.exe", "pia_client.exe", "openvpn.exe", "wireguard.exe"]
WHITELISTED_IPS = []
SUSPICIOUS_KEYWORDS = [b"mimikatz", b"meterpreter", b"reverse_shell", b"powershell -enc", b"invoke-mimikatz", b"keylogger"]
FAKE_DOCS = [".pdf.exe", ".docx.exe", ".doc.exe", ".jpg.exe", ".png.exe", ".xls.exe", ".xlsx.exe", ".zip.exe", ".txt.exe"]
SUSPICIOUS_PORTS = {5555, 6666, 6667, 8080, 9001, 1337, 12345, 54321}
C2_PORTS = {4444, 31337}
SCAN_THRESHOLD = 15
logs = []
logs_lock = threading.Lock()

def normalize(name):
    return name.strip().lower().replace("_", "-").replace(" ", "")

def log_event(level, title, detail, process, ip_port, grid):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    event = {"time": now, "level": level, "title": title, "detail": detail, "process": process, "ip": ip_port, "grid": grid}
    with logs_lock:
        logs.append(event)
        if len(logs) > 100:
            logs.pop(0)
        try:
            with open(LOG_FILE, "w") as f:
                json.dump(logs, f, indent=2)
        except Exception:
            pass
    print(f"\n[{level}] [{grid}] {now} | {title}")
    print(f"  -> {detail} | {process} | {ip_port}")
    update_html()

def update_html():
    with logs_lock:
        rows = ""
        for l in reversed(logs[-50:]):
            color = "#dc3545" if l['level'] in ["CRITICAL", "BLOCKED", "KILLED"] else "#ffc107" if l['level'] == "WARNING" else "#28a745"
            rows += f"<tr><td>{l['time']}</td><td>{l['grid']}</td><td style='background:{color};color:white'>{l['level']}</td><td>{l['title']}</td><td>{l['detail']}</td><td>{l['process']} {l['ip']}</td></tr>"
        html = f"""<html><head><meta http-equiv="refresh" content="3"><title>Riley Unified Grid</title><style>body{{font-family:Arial;padding:20px;background:#0f1115;color:#eee}} h1{{color:#a78bfa}} .card{{background:#1a1d24;padding:15px;border-radius:10px;margin:10px 0}} table{{border-collapse:collapse;width:100%}} th{{background:#6f42c1;color:white;padding:10px}} td{{border:1px solid #333;padding:8px}}</style></head><body><h1>RILEY UNIFIED GRID v2.3</h1><p>File Grid + Network Grid + Auto-Kill | Live | Auto-refresh every 3s | Total Events: {len(logs)} | Auto-Kill: {'ON' if AUTO_KILL else 'OFF'}</p><div class="card"><b>Status:</b> LIVE - Monitoring Downloads + Network | Whitelisted: {', '.join(WHITELISTED_PROCESSES)}</div><table><tr><th>Time</th><th>Grid</th><th>Level</th><th>Title</th><th>Detail</th><th>Process / File</th></tr>{rows}</table><p>Dashboard file: {HTML_FILE}</p></body></html>"""
        try:
            with open(HTML_FILE, "w", encoding="utf-8") as f:
                f.write(html)
        except Exception:
            pass

def scan_file(filepath):
    score = 0
    reasons = []
    try:
        with open(filepath, "rb") as f:
            data = f.read(50000).lower()
            for kw in SUSPICIOUS_KEYWORDS:
                if kw in data:
                    score += 40
                    reasons.append(f"Keyword: {kw.decode()}")
        name = os.path.basename(filepath).lower()
        if any(name.endswith(x) for x in FAKE_DOCS):
            score += 30
            reasons.append("Double extension trick")
        if "temp" in filepath.lower() and name.endswith(".exe"):
            score += 20
            reasons.append("EXE from Temp")
    except Exception:
        pass
    return score, reasons

def file_grid():
    print("[FILE GRID] Started - Watching Downloads...")
    seen = set()
    while True:
        try:
            for root, dirs, files in os.walk(DOWNLOADS):
                if "_RILEY_QUARANTINE" in root:
                    continue
                for fn in files:
                    fp = os.path.join(root, fn)
                    try:
                        key = f"{fp}-{os.path.getmtime(fp)}"
                    except Exception:
                        continue
                    if key in seen:
                        continue
                    seen.add(key)
                    score, reasons = scan_file(fp)
                    if score >= 70:
                        try:
                            dest = os.path.join(QUARANTINE, fn)
                            os.rename(fp, dest)
                            log_event("BLOCKED", "MALWARE QUARANTINED", f"Score {score} | {reasons} -> Moved to Quarantine", fn, fp, "FILE")
                        except Exception as e:
                            log_event("WARNING", "Quarantine Failed", str(e), fn, fp, "FILE")
                    elif score >= 30:
                        log_event("WARNING", "SUSPICIOUS FILE", f"Score {score} | {reasons}", fn, fp, "FILE")
        except Exception as e:
            print(f"File Grid error: {e}")
        time.sleep(2)

def get_connections():
    conns = []
    try:
        out = subprocess.check_output(["netstat", "-ano", "-p", "TCP"], text=True, errors="ignore")
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 5 and parts[0] == "TCP" and parts[3] == "ESTABLISHED":
                foreign = parts[2]
                pid = parts[4]
                if ":" in foreign:
                    ip, port = foreign.rsplit(":", 1)
                    try:
                        conns.append({"ip": ip, "port": int(port), "pid": pid})
                    except Exception:
                        pass
    except Exception:
        pass
    return conns

def get_proc(pid):
    try:
        out = subprocess.check_output(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"], text=True, errors="ignore")
        if '"' in out:
            return out.split('"')[1]
    except Exception:
        pass
    return f"PID:{pid}"

def is_private(ip):
    return ip.startswith("10.") or ip.startswith("192.168.") or ip.startswith("172.16.") or ip.startswith("127.")

def kill_process(pid, proc_name, ip_port):
    if not AUTO_KILL:
        return False
    try:
        subprocess.check_output(["taskkill", "/F", "/PID", str(pid)], text=True, errors="ignore")
        log_event("KILLED", "C2 PROCESS TERMINATED", "Auto-Kill executed for C2 connection. Process killed.", proc_name, f"PID {pid} | {ip_port}", "NETWORK")
        return True
    except Exception as e:
        log_event("WARNING", "Auto-Kill Failed", f"Could not kill PID {pid}: {e}", proc_name, ip_port, "NETWORK")
        return False

def network_grid():
    print("[NETWORK GRID] Started - Watching Connections + Auto-Kill ON...")
    seen = set()
    history = []
    while True:
        now = datetime.datetime.now()
        conns = get_connections()
        by_ip = defaultdict(list)
        for c in conns:
            by_ip[c["ip"]].append(c)
            history.append((now, c["ip"], c["port"]))
        history = [h for h in history if (now - h[0]).total_seconds() < 10]
        for ip, clist in by_ip.items():
            if is_private(ip):
                continue
            if ip in WHITELISTED_IPS:
                continue
            ports = set(p for t, i, p in history if i == ip)
            if len(ports) >= SCAN_THRESHOLD:
                key = f"scan-{ip}"
                if key not in seen:
                    seen.add(key)
                    log_event("CRITICAL", "PORT SCAN DETECTED", f"{len(ports)} ports to {ip} in 10s", get_proc(clist[0]["pid"]), f"{ip}:{clist[0]['port']}", "NETWORK")
            for c in clist:
                proc = get_proc(c["pid"])
                proc_clean = normalize(proc)
                whitelist_clean = [normalize(w) for w in WHITELISTED_PROCESSES]
                if proc_clean in whitelist_clean:
                    continue
                if proc_clean in ["msedge.exe", "chrome.exe", "firefox.exe", "teams.exe"] and c["port"] not in C2_PORTS:
                    continue
                if c["port"] in C2_PORTS:
                    key = f"c2-{ip}-{c['port']}-{c['pid']}"
                    if key not in seen:
                        seen.add(key)
                        log_event("CRITICAL", "POSSIBLE C2 CONNECTION", f"Connection to C2 port {c['port']}", proc, f"{ip}:{c['port']}", "NETWORK")
                        kill_process(c["pid"], proc, f"{ip}:{c['port']}")
                elif c["port"] in SUSPICIOUS_PORTS:
                    key = f"susp-{ip}-{c['port']}-{c['pid']}"
                    if key not in seen:
                        seen.add(key)
                        log_event("WARNING", "SUSPICIOUS PORT", f"Connection to uncommon port {c['port']}", proc, f"{ip}:{c['port']}", "NETWORK")
        time.sleep(3)

if __name__ == "__main__":
    print("=" * 70)
    print("RILEY UNIFIED GRID v2.3 - FILE + NETWORK + AUTO-KILL")
    print(f"Watching: {DOWNLOADS}")
    print(f"Dashboard: {HTML_FILE}")
    print(f"Auto-Kill: {'ON' if AUTO_KILL else 'OFF'} | Whitelisted: {WHITELISTED_PROCESSES}")
    print("Press CTRL+C to stop")
    print("=" * 70)
    update_html()
    t1 = threading.Thread(target=file_grid, daemon=True)
    t2 = threading.Thread(target=network_grid, daemon=True)
    t1.start()
    t2.start()
    try:
        while True:
            print(f"\r[{datetime.datetime.now().strftime('%H:%M:%S')}] Unified Grid v2.3 LIVE | Events: {len(logs)} | Auto-Kill ON...   ", end="", flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nUnified Grid stopped. Open unified_dashboard.html to see full report.")