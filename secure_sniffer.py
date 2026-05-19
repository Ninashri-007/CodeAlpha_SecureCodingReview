from scapy.all import sniff, IP, TCP, UDP, ICMP
import logging
import argparse
import os
import sys
from datetime import datetime

# -------------------------------
# Logging Configuration
# -------------------------------

logging.basicConfig(
    filename="sniffer.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------------------------------
# Admin Privilege Check
# -------------------------------

if os.name != "nt":
    if os.geteuid() != 0:
        print("Please run as root.")
        sys.exit()

# -------------------------------
# CLI Arguments
# -------------------------------

parser = argparse.ArgumentParser(description="Secure Packet Sniffer")

parser.add_argument(
    "-c",
    "--count",
    type=int,
    default=20,
    help="Number of packets to capture"
)

parser.add_argument(
    "-p",
    "--protocol",
    type=str,
    default="ALL",
    help="Protocol Filter: TCP/UDP/ICMP/ALL"
)

args = parser.parse_args()

# -------------------------------
# Blacklist Loading
# -------------------------------

blacklist = []

if os.path.exists("blacklist.txt"):
    with open("blacklist.txt", "r") as file:
        blacklist = [line.strip() for line in file.readlines()]

# -------------------------------
# Suspicious Port List
# -------------------------------

suspicious_ports = [21, 22, 23, 3389]

print("\n========== SECURE PACKET SNIFFER ==========")
print(f"Protocol Filter : {args.protocol}")
print(f"Packet Count    : {args.count}")
print("===========================================\n")

# -------------------------------
# Packet Processing
# -------------------------------

def process_packet(packet):

    try:

        if IP in packet:

            src = packet[IP].src
            dst = packet[IP].dst

            protocol = "OTHER"

            if TCP in packet:
                protocol = "TCP"
                sport = packet[TCP].sport
                dport = packet[TCP].dport

            elif UDP in packet:
                protocol = "UDP"
                sport = packet[UDP].sport
                dport = packet[UDP].dport

            elif ICMP in packet:
                protocol = "ICMP"
                sport = "-"
                dport = "-"

            else:
                sport = "-"
                dport = "-"

            # -------------------------------
            # Protocol Filtering
            # -------------------------------

            if args.protocol != "ALL":
                if protocol != args.protocol.upper():
                    return

            # -------------------------------
            # Blacklist Detection
            # -------------------------------

            if src in blacklist:
                alert = f"[ALERT] Blacklisted IP Detected: {src}"
                print(alert)
                logging.warning(alert)

            # -------------------------------
            # Suspicious Port Detection
            # -------------------------------

            if isinstance(dport, int):
                if dport in suspicious_ports:
                    alert = f"[WARNING] Suspicious Port Access: {dport}"
                    print(alert)
                    logging.warning(alert)

            # -------------------------------
            # Safe Packet Display
            # -------------------------------

            print(f"""
Timestamp : {datetime.now()}
Protocol  : {protocol}
Source IP : {src}
Dest IP   : {dst}
Src Port  : {sport}
Dst Port  : {dport}
----------------------------------------
""")

            # -------------------------------
            # Secure Logging
            # -------------------------------

            logging.info(
                f"{protocol} | {src}:{sport} -> {dst}:{dport}"
            )

    except Exception as e:
        logging.error(f"Packet Processing Error: {e}")

# -------------------------------
# Start Sniffing
# -------------------------------

try:

    sniff(
        prn=process_packet,
        store=False,
        count=args.count
    )

    print("\nPacket Capture Completed Safely.")

except KeyboardInterrupt:
    print("\nSniffer stopped by user.")

except Exception as e:
    logging.critical(f"Fatal Error: {e}")
    print(f"Error: {e}")