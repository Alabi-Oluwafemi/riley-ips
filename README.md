# 🛡️ RILEY UNIFIED GRID v2.3
### File + Network Intrusion Prevention System (IPS) with Auto-Kill

**Built by Oluwafemi Alabi — Riley Consultech**

Riley Unified Grid is a lightweight, real-time Intrusion Prevention System for Windows that monitors your files and your network at the same time — and fights back automatically.

It doesn't just detect attacks. It kills them.

---

## 🚀 What It Does

| Grid | What It Monitors | What It Does |
| :--- | :--- | :--- |
| **FILE GRID** | Downloads folder | Quarantines malware, flags double-extension tricks, fake docs, and malicious keywords |
| **NETWORK GRID** | All outbound TCP connections | Detects C2 connections, port scans, and suspicious ports |
| **AUTO-KILL** | C2 processes | Automatically terminates the attacking process in < 1 second |

---

## ✨ Key Features

- **Real-Time File IPS** — Scans every new file in Downloads, quarantines on score >= 70
- **Real-Time Network IPS** — Monitors `netstat` every 3 seconds for C2, scans, and suspicious ports
- **Auto-Kill Engine** — Kills C2 processes on ports `4444` and `31337` automatically via `taskkill /F`
- **Smart Whitelist** — VPNs, browsers, and trusted apps are never flagged. Normalization handles `pia-service.exe` vs `pia_service.exe`, case, and spacing
- **Live Dashboard** — Auto-refreshing HTML SOC dashboard in `Downloads/unified_dashboard.html`
- **JSON Logging** — Full event log in `Downloads/unified_grid_log.json`
- **Zero Dependencies** — Pure Python standard library. No installs. No cloud. No telemetry.

---

## 📸 Live Kill Proof <img width="1085" height="466" alt="Screenshot 2026-11-24 145344" src="https://github.com/user-attachments/assets/26ff1f05-78a4-48a0-ae51-bf7fcfa839c4" />
<img width="1353" height="587" alt="Screenshot 2026-11-24 144227" src="https://github.com/user-attachments/assets/638668ec-8d59-466c-bcc3-e400a81821fd" />

Real test, real kill — 1 second from detection to termination:



Dashboard shows `CRITICAL` → `KILLED` in the same second.

**False-positive test:** With VPN on, Grid runs at `Events: 0` — no alerts for trusted VPN traffic.

---

## ⚙️ Detection Logic

### File Grid Scoring
| Signal | Score |
| :--- | :--- |
| Malicious keyword (`mimikatz`, `meterpreter`, `reverse_shell`, `keylogger`, `powershell -enc`) | +40 |
| Double extension (`.pdf.exe`, `.docx.exe`, `.jpg.exe`) | +30 |
| EXE from Temp folder | +20 |

- **Score >= 70:** File moved to `_RILEY_QUARANTINE` → `BLOCKED`
- **Score >= 30:** Flagged → `WARNING`

### Network Grid
| Signal | Action |
| :--- | :--- |
| Connection to C2 port `4444`, `31337` | `CRITICAL` + Auto-Kill |
| Connection to suspicious port `5555, 6666, 6667, 8080, 9001, 1337, 12345, 54321` | `WARNING` |
| 15+ ports to same IP in 10s | `CRITICAL` — Port Scan Detected |
| Private IPs (`10.x`, `192.168.x`, `127.0.0.1`) | Ignored |
| Whitelisted processes | Ignored |

---

## 🛠️ Installation

**Requirements:** Windows 10/11 + Python 3.10+

```powershell
# 1. Clone
git clone https://github.com/uncleriley089/riley-unified-grid.git
cd riley-unified-grid

# 2. Verify file (no errors = perfect)
py -m py_compile riley_unified_grid.py

# 3. Run
py riley_unified_grid.py

# You'll see
RILEY UNIFIED GRID v2.3 - FILE + NETWORK + AUTO-KILL
[FILE GRID] Started - Watching Downloads...
[NETWORK GRID] Started - Watching Connections + Auto-Kill ON...


# To view live dashboard
Start-Process "$env:USERPROFILE\Downloads\unified_dashboard.html"

Test Auto-Kill (Safe)
Keep Grid running in Window 1. In Window 2:powershellpy -c "import socket, time; s=socket.create_connection(('portquiz.net', 4444)); print('Connected'); time.sleep(15)"Expected: Grid logs CRITICAL → KILLED for python.exe in 1 second.

⚠️ Do NOT test with PowerShell's $client.Connect() — Auto-Kill will kill PowerShell itself. Use the Python test above.

Built in Lagos, Nigeria. 🇳🇬
Detect. Kill. Protect.

Real test, real kill — 1 second from detection to termination:

