# 🛡️ Riley Unified Grid v2.3 - File + Network IPS with Auto-Kill

**Stop attacks in 1 second. No Python needed.**

> Detects ransomware files + C2 reverse shells and **kills the attacker process automatically.**

![Version](https://img.shields.io/badge/version-v2.3-red)
![Platform](https://img.shields.io/badge/platform-Windows-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ⬇️ Download for Windows (No Python Needed)

**For Clients / Business Users - Just Download & Run:**

👉 **[Download RileyGrid-v2.3.exe](https://github.com/Alabi-Oluwafemi/riley-ips/releases/tag/v2.3)** 👈

1. Download `RileyGrid-v2.3.exe` from Releases
2. Right-click → **Run as Administrator**
3. Done. You are protected.

> ⚠️ Windows will say "Unknown Publisher" → Click `More info` → `Run anyway`. This is normal for new security tools.

---

## 🔥 What It Does - Proven Live

| Threat | Detection | Action |
| :--- | :--- | :--- |
| Ransomware File Created | `.locked`, `.encrypted`, `.pay` in Downloads | **Auto-Quarantine + Alert** |
| C2 / Reverse Shell | Connection to port `4444`, `1337`, `8080` | **Auto-Kill Process in <1s** |


---

## ✨ Features - v2.3

- **Unified Grid** - File Grid + Network Grid in ONE dashboard
- **Auto-Kill Engine** - Kills C2 processes automatically, no manual action
- **Live Dashboard** - `unified_dashboard.html` with real-time events
- **File Watcher** - Monitors Downloads, Documents, Desktop for ransomware
- **Network Watcher** - Monitors all outbound connections
- **Zero Dependencies** - EXE version needs no Python

---

## 🛠️ For Developers (Run From Source)

```powershell
git clone https://github.com/Alabi-Oluwafemi/riley-ips.git
cd riley-ips
pip install -r requirements.txt
python riley_unified_grid.py
