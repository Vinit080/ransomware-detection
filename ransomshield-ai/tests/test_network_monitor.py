import pytest
from scapy.all import IP, UDP, DNS, DNSQR
from agents.host_side.network_monitor import NetworkMonitor

class MockRequests:
    def __init__(self):
        self.posted_data = []
        
    def post(self, url, json, timeout):
        self.posted_data.append(json)
        class MockResponse:
            status_code = 202
        return MockResponse()

def test_network_monitor_dns_extraction(monkeypatch):
    # Mock requests.post
    mock_req = MockRequests()
    monkeypatch.setattr("agents.host_side.network_monitor.requests.post", mock_req.post)
    
    monitor = NetworkMonitor(ingest_url="http://mock", run_id="test-run-1", batch_size=1)
    
    # Craft a fake DNS packet
    pkt = IP(src="192.168.1.100", dst="8.8.8.8") / UDP(sport=12345, dport=53) / DNS(rd=1, qd=DNSQR(qname="malicious-c2.com"))
    
    # Process packet
    monitor.process_packet(pkt)
    
    # Verify the event queue was flushed due to batch_size=1
    assert len(mock_req.posted_data) == 1
    batch = mock_req.posted_data[0]
    
    assert len(batch) == 1
    event = batch[0]
    assert event["event_type"] == "dns_query"
    assert event["run_id"] == "test-run-1"
    assert event["event_data"]["query"] == "malicious-c2.com."
    assert event["event_data"]["source_ip"] == "192.168.1.100"

def test_network_monitor_flow_extraction(monkeypatch):
    mock_req = MockRequests()
    monkeypatch.setattr("agents.host_side.network_monitor.requests.post", mock_req.post)
    
    monitor = NetworkMonitor(ingest_url="http://mock", run_id="test-run-2", batch_size=1)
    
    # Craft a fake UDP packet (not DNS)
    pkt = IP(src="192.168.1.100", dst="10.0.0.5") / UDP(sport=5000, dport=8000) / b"fake payload"
    
    monitor.process_packet(pkt)
    
    assert len(mock_req.posted_data) == 1
    batch = mock_req.posted_data[0]
    
    event = batch[0]
    assert event["event_type"] == "network_flow"
    assert event["event_data"]["protocol"] == "UDP"
    assert event["event_data"]["source_ip"] == "192.168.1.100"
    assert event["event_data"]["destination_ip"] == "10.0.0.5"
    assert event["event_data"]["destination_port"] == 8000
