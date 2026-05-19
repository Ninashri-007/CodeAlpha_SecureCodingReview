from scapy.all import sniff, IP

print("Starting Vulnerable Packet Sniffer...")

captured_packets = []

def process_packet(packet):

    # Vulnerability 1: Infinite storage
    captured_packets.append(packet)

    # Vulnerability 2: No exception handling
    if IP in packet:
        src = packet[IP].src
        dst = packet[IP].dst

        print(f"Packet From {src} -> {dst}")

# Vulnerability 3: Infinite sniffing
sniff(prn=process_packet, store=True)