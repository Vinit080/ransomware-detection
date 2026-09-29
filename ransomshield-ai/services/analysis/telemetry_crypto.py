"""
Authenticated telemetry with AES-256-GCM and sequence-bound associated data (AAD).

Guest side  : Sender.seal(event) -> wire record (bytes)
Trusted side: Receiver.open(record) -> event or raises TelemetryRejected

What this DOES provide (given the key stays secret):
  * integrity/authenticity of each record   (GCM tag)
  * detection of replay, reordering, duplication and DROPPED records (session id + strictly increasing seq in AAD)
  * detection of records from another session
What it does NOT provide:
  * protection after an attacker extracts the session key from the guest (forgery becomes possible)
  * a key ratchet (future work; not implemented here)
Use Receiver.finish(expected_last_seq) to detect truncation at the end of a stream.
"""
import json, os, struct
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class TelemetryRejected(Exception): pass

def new_session_key(): return AESGCM.generate_key(bit_length=256)

def _aad(session_id: bytes, seq: int) -> bytes:
    return session_id + struct.pack(">Q", seq)

class Sender:
    def __init__(self, key: bytes, session_id: bytes = None):
        self._aes = AESGCM(key); self.session_id = session_id or os.urandom(8); self.seq = 0
    def seal(self, event: dict) -> bytes:
        self.seq += 1
        nonce = os.urandom(12)                      # 96-bit random nonce; << 2^32 records/session
        ct = self._aes.encrypt(nonce, json.dumps(event, sort_keys=True).encode(), _aad(self.session_id, self.seq))
        return self.session_id + struct.pack(">Q", self.seq) + nonce + ct

class Receiver:
    def __init__(self, key: bytes, session_id: bytes):
        self._aes = AESGCM(key); self.session_id = session_id; self.last_seq = 0
    def open(self, rec: bytes) -> dict:
        if len(rec) < 8+8+12+16: raise TelemetryRejected("short record")
        sid, seq = rec[:8], struct.unpack(">Q", rec[8:16])[0]
        nonce, ct = rec[16:28], rec[28:]
        if sid != self.session_id: raise TelemetryRejected("wrong session")
        if seq != self.last_seq + 1:
            raise TelemetryRejected(f"sequence violation (got {seq}, expected {self.last_seq+1})")
        try: pt = self._aes.decrypt(nonce, ct, _aad(sid, seq))
        except Exception: raise TelemetryRejected("authentication failed")
        self.last_seq = seq
        return json.loads(pt)
    def finish(self, expected_last_seq: int):
        if self.last_seq != expected_last_seq: raise TelemetryRejected("stream truncated")

class PlainReceiver:
    """Config E: AES-GCM with NO sequence binding (AAD empty) - for the ablation."""
    def __init__(self, key): self._aes = AESGCM(key)
    def seal(self, event, sender_nonce=None):
        nonce = os.urandom(12); return nonce + self._aes.encrypt(nonce, json.dumps(event, sort_keys=True).encode(), b"")
    def open(self, rec):
        try: return json.loads(self._aes.decrypt(rec[:12], rec[12:], b""))
        except Exception: raise TelemetryRejected("authentication failed")
