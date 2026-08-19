import os
import sys
import time
import json
import argparse
import requests
from typing import List, Dict, Any
from scapy.all import sniff, IP, TCP, UDP, DNS, DNSQR

class NetworkMonitor:
    def __init__(self, ingest_url: str, run_id: str, interface: str = None, batch_size: int = 20, batch_interval_sec: float = 2.0):
        self.ingest_url = ingest_url
        self.run_id = run_id
        self.interface = interface
        self.batch_size = batch_size
        self.batch_interval_sec = batch_interval_sec
        
        self.event_queue: List[Dict[str, Any]] = []
        self.last_flush_time = time.time()
        
    def enqueue_event(self, event_type: str, event_data: Dict[str, Any]):
        event = {
            "run_id": self.run_id,
            "event_type": event_type,
            "event_data": event_data
        }
        self.event_queue.append(event)
        
        now = time.time()
        if len(self.event_queue) >= self.batch_size or (now - self.last_flush_time) >= self.batch_interval_sec:
            self.flush()

    def flush(self):
        if not self.event_queue:
            return
            
        batch = self.event_queue.copy()
        self.event_queue.clear()
        self.last_flush_time = time.time()
        
        try:
            resp = requests.post(self.ingest_url, json=batch, timeout=2.0)
            if resp.status_code != 202:
                print(f"Failed to ingest network batch: {resp.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Network error syncing telemetry: {e}")

    def process_packet(self, packet):
        """Callback for scapy sniffer"""
        if IP in packet:
            ip_layer = packet[IP]
            
            # DNS Extraction
            if packet.haslayer(DNS) and packet.haslayer(DNSQR):
                query = packet[DNSQR].qname.decode('utf-8') if packet[DNSQR].qname else ""
                if query:
                    self.enqueue_event(
                        event_type="dns_query",
                        event_data={
                            "source_ip": ip_layer.src,
                            "query": query,
                            "record_type": packet[DNSQR].qtype
                        }
                    )
                    return # Skip flow logging for DNS to avoid noise

            # Standard Flow Metadata (TCP/UDP)
            protocol = "UNKNOWN"
            src_port = 0
            dst_port = 0
            if TCP in packet:
                protocol = "TCP"
                src_port = packet[TCP].sport
                dst_port = packet[TCP].dport
            elif UDP in packet:
                protocol = "UDP"
                src_port = packet[UDP].sport
                dst_port = packet[UDP].dport
                
            if protocol != "UNKNOWN":
                self.enqueue_event(
                    event_type="network_flow",
                    event_data={
                        "source_ip": ip_layer.src,
                        "destination_ip": ip_layer.dst,
                        "source_port": src_port,
                        "destination_port": dst_port,
                        "protocol": protocol,
                        "length": len(packet)
                    }
                )

    def start_sniffing(self):
        print(f"Starting host-side network monitoring on interface: {self.interface or 'ALL'}")
        print(f"Target SandboxRun ID: {self.run_id}")
        
        # In a real environment, we would use BPF filters to only capture traffic 
        # originating from or destined to the specific Sandbox VM IP.
        sniff(iface=self.interface, prn=self.process_packet, store=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Host-side Network Monitor")
    parser.add_argument("--url", type=str, required=True, help="Ingest URL on host")
    parser.add_argument("--run-id", type=str, required=True, help="Sandbox Run ID")
    parser.add_argument("--interface", type=str, default=None, help="Network interface to sniff")
    args = parser.parse_args()
    
    monitor = NetworkMonitor(ingest_url=args.url, run_id=args.run_id, interface=args.interface)
    try:
        monitor.start_sniffing()
    except KeyboardInterrupt:
        monitor.flush()
        sys.exit(0)
