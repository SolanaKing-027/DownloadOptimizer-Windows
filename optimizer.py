import subprocess
import os
import time
import platform
import psutil
import requests
import datetime
import logging
from collections import defaultdict

VERSION = "v1.0.0"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/DeinUsername/DeinRepo/main/version.txt"  # Anpassen!

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Konfiguration
MAX_CPU_THRESHOLD = 80  # Maximale CPU-Nutzung (%) vor einer Aktion
MAX_MEMORY_THRESHOLD = 300 * 1024 * 1024  # Maximale RAM-Nutzung (in Bytes)
MAX_NET_THRESHOLD = 0.5  # Maximale prozentuale Verringerung der Netzwerkgeschwindigkeit

excluded_processes = ["steam.exe", "EpicGamesLauncher.exe", "UE4Editor.exe", "explorer.exe", "python.exe"]

# Funktion zum Scannen und Bewerten von Prozessen
def score_process(proc):
    score = 0
    try:
        cpu = proc.cpu_percent(interval=0.1)
        mem = proc.memory_info().rss
        threads = proc.num_threads()
        user = proc.username()
        net = proc.connections(kind='inet')

        # Prozesse, die Systemdienste oder Sicherheitssoftware betreffen, sollen nicht beendet werden
        if any(excluded in user for excluded in ["SYSTEM", "Service", "LocalService", "NetworkService"]):
            return 0

        # Bewertung basierend auf CPU- und RAM-Nutzung
        if cpu > MAX_CPU_THRESHOLD:
            score += 30
        if mem > MAX_MEMORY_THRESHOLD:
            score += 30
        if threads > 30:
            score += 10
        if len(net) > 0:
            score += 30

        return score
    except Exception as e:
        logging.error(f"Error scoring process {proc.info['name']}: {e}")
        return 0

# Dynamische Entscheidung zur Prozessbehandlung
def decide_action(score, proc):
    if score >= 80:
        return "terminate"
    elif score >= 50:
        return "efficiency"
    else:
        return "ok"

# Funktion zur Durchführung des Auto-Optimierungsprozesses
def auto_optimize():
    print("[AI] Running full auto optimization...\n")
    time.sleep(0.5)

    # Dynamische Entscheidung für Prozesse
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        score = score_process(proc)

        action = decide_action(score, proc)

        if action == "terminate":
            logging.info(f"[AI] Terminating: {proc.info['name']} (Score: {score})")
            try:
                psutil.Process(proc.info['pid']).terminate()
            except:
                logging.warning(f"[AI] Could not terminate process {proc.info['name']}")
        elif action == "efficiency":
            logging.info(f"[AI] Suggest Efficiency Mode: {proc.info['name']} (Score: {score})")
            # Hier könnte die CPU- und RAM-Nutzung reduziert werden (Prozesspriorität setzen)
            proc.nice(psutil.IDLE_PRIORITY_CLASS)
        else:
            logging.info(f"[AI] OK: {proc.info['name']} (Score: {score})")

    print("\n[✓] Optimization complete.\n")

# Netzwerkgeschwindigkeit messen
def get_network_speed():
    # Für eine bessere Messung könnte die `speedtest-cli`-Bibliothek genutzt werden
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000  # Mbps
        upload_speed = st.upload() / 1_000_000  # Mbps
        return download_speed, upload_speed
    except Exception as e:
        logging.error(f"Error getting network speed: {e}")
        return 0, 0

# Funktion zur Durchführung eines intelligenten Scans
def intelligent_scan():
    print("[*] Scanning user-level background processes...\n")
    time.sleep(1)

    # Prozesse scannen und bewerten
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        score = score_process(proc)

        action = decide_action(score, proc)

        if action == "terminate":
            print(f">> [HIGH] {proc.info['name']} (Score: {score}) - Terminating")
        elif action == "efficiency":
            print(f">> [MEDIUM] {proc.info['name']} (Score: {score}) - Efficiency Mode Suggested")
        else:
            print(f">> [LOW] {proc.info['name']} (Score: {score}) - OK")

    print("\n[✓] Scan complete.\n")

# Funktion zum Setzen des Leistungsmodus
def set_performance_mode():
    print("[*] Activating High Performance mode...")
    subprocess.run(["powercfg", "/setactive", "SCHEME_MAX"], shell=True)
    subprocess.run(["powercfg", "-change", "-monitor-timeout-ac", "0"], shell=True)
    subprocess.run(["powercfg", "-change", "-disk-timeout-ac", "0"], shell=True)
    print("[+] Power settings optimized.\n")

# Funktion zum Zurücksetzen der Stromversorgung
def reset_power_mode():
    print("[*] Reverting to Balanced mode...")
    subprocess.run(["powercfg", "/setactive", "SCHEME_BALANCED"], shell=True)
    print("[+] Power settings reverted.\n")

# Funktion zur Überprüfung auf Updates
def check_for_updates():
    print("[*] Checking for updates from GitHub...")
    try:
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200:
            latest_version = response.text.strip()
            if latest_version != VERSION:
                print(f"[!] Update available: {latest_version}")
                print("Visit: https://github.com/DeinUsername/DeinRepo to download.")
            else:
                print("[✓] You are using the latest version.")
        else:
            print("[!] Could not fetch version info from GitHub.")
    except Exception as e:
        print(f"[!] Error checking update: {e}")

# Hauptmenü
def show_menu():
    clear()
    print("=" * 50)
    print("        Intelligent System Optimizer")
    print("=" * 50)
    print(f"Current Version: {VERSION}")
    print("[1] Optimize system for MAXIMUM download speed")
    print("[2] Scan background processes and suggest actions")
    print("[3] Full intelligent auto-optimization")
    print("[4] Stop Boost (reset power settings)")
    print("[5] Check for updates")
    print("[6] Exit")
    print()

# Hauptprogramm
def main():
    if platform.system() != "Windows":
        print("[!] This script is only for Windows systems.")
        return

    while True:
        show_menu()
        choice = input("Select an option (1-6): ").strip()
        if choice == '1':
            set_performance_mode()
            input("Press Enter to return to the menu...")
        elif choice == '2':
            intelligent_scan()
            input("Press Enter to return to the menu...")
        elif choice == '3':
            set_performance_mode()
            auto_optimize()
            input("Press Enter to return to the menu...")
        elif choice == '4':
            reset_power_mode()
            input("Press Enter to return to the menu...")
        elif choice == '5':
            check_for_updates()
            input("Press Enter to return to the menu...")
        elif choice == '6':
            print("Exiting optimizer...")
            break
        else:
            print("Invalid input. Try again.")
            time.sleep(1)

if __name__ == "__main__":
    main()
