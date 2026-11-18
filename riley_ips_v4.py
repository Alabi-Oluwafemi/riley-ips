# RILEY CONSULTECH - IPS v3.0 FINAL | IDS + AUTO-BLOCK + REPORT
# Fixed: Always generates report, auto-unblock, whitelist safe, no crash on CTRL+C

import pywhatkit

MY_PHONE = "+2341234567890"  # <- PUT YOUR REAL NUMBER HERE

def send_whatsapp_alert(ip, reason):
    try:
        msg = f"🚨 RILEY IPS ALERT - Attacker Blocked: {ip} | Reason: {reason} | Action: Blocked 10 mins"
        pywhatkit.sendwhatmsg_instantly(MY_PHONE, msg, wait_time=10, tab_close=True, close_time=3)
        print(f"📱 WhatsApp alert sent for {ip}")
    except Exception as e:
        print(f"⚠️ WhatsApp alert failed: {e}")
        print(f"📱 WhatsApp alert sent for {ip}")
    except Exception as e:
        print(f"⚠️ WhatsApp alert failed: {e}")
import time
import threading
import subprocess
import os
from datetime import datetime, timedelta
from collections import defaultdict, deque

try:
    from scapy.all import sniff, IP, ICMP, TCP, UDP
except ImportError:
    print("ERROR: Scapy not installed. Run: pip install scapy")
    exit()

# ============ CONFIG ============
WHITELIST = {'127.0.0.1', '192.168.8.1', '8.8.8.8', '1.1.1.1'}
THRESHOLD = 100  # packets in WINDOW to trigger block
WINDOW = 10  # seconds
BLOCK_TIME = 600  # 10 minutes = 600 seconds
REPORT_FILE = "riley_ips_report.html"
# ================================

alerts = 0
blocked_ips = {}  # ip -> unblock_time
packet_counts = defaultdict(lambda: deque())
alert_log = []
total_packets = 0
start_time = datetime.now()

def run_cmd(cmd):
    try:
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"CMD Error: {e}")

def block_ip(ip):
    global alerts
    if ip in WHITELIST:
        return
    if ip in blocked_ips:
        return
    print(f"\n🚫 [BLOCKED] {ip} - Flood detected - Blocking for 10 mins")
    send_whatsapp_alert(ip, f"Flood: >{THRESHOLD} packets in {WINDOW}s")
    run_cmd(f'netsh advfirewall firewall add rule name="RileyIPS_Block_{ip}" dir=in action=block remoteip={ip}')
    run_cmd(f'netsh advfirewall firewall add rule name="RileyIPS_Block_Out_{ip}" dir=out action=block remoteip={ip}')
    unblock_time = datetime.now() + timedelta(seconds=BLOCK_TIME)
    blocked_ips[ip] = unblock_time
    alerts += 1
    alert_log.append({
        'time': datetime.now().strftime("%H:%M:%S"),
        'ip': ip,
        'reason': f'Flood: >{THRESHOLD} packets in {WINDOW}s',
        'action': 'Blocked 10 mins'
    })

def unblock_ip(ip):
    print(f"\n✅ [UNBLOCKED] {ip} - 10 mins expired")
    run_cmd(f'netsh advfirewall firewall delete rule name="RileyIPS_Block_{ip}"')
    run_cmd(f'netsh advfirewall firewall delete rule name="RileyIPS_Block_Out_{ip}"')
    if ip in blocked_ips:
        del blocked_ips[ip]

def unblock_checker():
    while True:
        time.sleep(10)
        now = datetime.now()
        for ip in list(blocked_ips.keys()):
            if now >= blocked_ips[ip]:
                unblock_ip(ip)

def packet_handler(pkt):
    global total_packets
    if IP in pkt:
        src = pkt[IP].src
        if src in WHITELIST:
            return
        if src in blocked_ips:
            return
        total_packets += 1
        now = time.time()
        packet_counts[src].append(now)
        # Keep only packets in WINDOW
        while packet_counts[src] and packet_counts[src][0] < now - WINDOW:
            packet_counts[src].popleft()
        if len(packet_counts[src]) > THRESHOLD:
            block_ip(src)
            packet_counts[src].clear()

def dashboard():
    while True:
        time.sleep(15)
        now = datetime.now().strftime("%H:%M:%S")
        print(f"\nRILEY IPS LIVE | {now} | Alerts: {alerts} | Blocked: {len(blocked_ips)} | Total Packets: {total_packets}")
        if len(blocked_ips) == 0:
            print("✅ No IPs currently blocked")
        else:
            for ip, until in blocked_ips.items():
                print(f"🚫 Currently Blocked: {ip} until {until.strftime('%H:%M:%S')}")

def generate_report():
    # THIS ALWAYS RUNS - even with 0 alerts
    duration = datetime.now() - start_time
    html = f"""<html><head><title>Riley Consultech IPS Report</title>
    <style>body{{font-family:Arial;padding:20px;background:#f4f4f4}}
    .box{{background:white;padding:20px;border-radius:10px;max-width:800px;margin:auto}}
    h1{{color:#1a73e8}} table{{width:100%;border-collapse:collapse}}
    th,td{{border:1px solid #ddd;padding:8px;text-align:left}} th{{background:#1a73e8;color:white}}
    .ok{{color:green}} .bad{{color:red}}</style></head>
    <body><div class="box">
    <h1>🛡️ RILEY CONSULTECH - IPS Report v3.0</h1>
    <p><b>Start:</b> {start_time.strftime('%Y-%m-%d %H:%M:%S')} | <b>End:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | <b>Duration:</b> {duration}</p>
    <p><b>Total Packets Seen:</b> {total_packets} | <b>Total Alerts:</b> {alerts} | <b>Currently Blocked:</b> {len(blocked_ips)}</p>
    <p><b>Whitelist:</b> {', '.join(WHITELIST)}</p>
    <h2>Alerts Log</h2>
    """
    if len(alert_log) == 0:
        html += "<p class='ok'>✅ No attacks detected. Network was clean. Whitelisted traffic (router/DNS) was correctly ignored.</p>"
    else:
        html += "<table><tr><th>Time</th><th>Attacker IP</th><th>Reason</th><th>Action</th></tr>"
        for a in alert_log:
            html += f"<tr><td>{a['time']}</td><td>{a['ip']}</td><td>{a['reason']}</td><td>{a['action']}</td></tr>"
        html += "</table>"
    html += f"<h2>Blocked IPs</h2><p>{', '.join(blocked_ips.keys()) if blocked_ips else 'None - All clear'}</p>"
    html += "<p><i>Generated by Riley Consultech IPS v3.0</i></p></div></body></html>"
    with open(REPORT_FILE, "w") as f:
        f.write(html)
    print(f"\n📄 Report saved: {os.path.abspath(REPORT_FILE)}")

if __name__ == "__main__":
    print("="*60)
    print("RILEY CONSULTECH - IPS v3.0 | IDS + AUTO-BLOCK")
    print(f"Whitelist: {WHITELIST}")
    print(f"Threshold: {THRESHOLD} packets in {WINDOW}s = BLOCK for 10 mins")
    print("Press CTRL+C to stop and generate report")
    print("="*60)

    threading.Thread(target=unblock_checker, daemon=True).start()
    threading.Thread(target=dashboard, daemon=True).start()

    try:
        sniff(prn=packet_handler, store=False)
    except KeyboardInterrupt:
        print("\n\nStopping IPS...")
    except Exception as e:
        print(f"\nError: {e}")
        print("Tip: Run CMD as Administrator and check Npcap is installed")
    finally:
        # ALWAYS generate report - even with 0 alerts
        generate_report()
        print("IPS stopped. Report ready.")