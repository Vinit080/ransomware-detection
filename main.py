from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import uvicorn
import json

from models.telemetry import TelemetryPayload
from core.crypto import encrypt_telemetry, decrypt_telemetry
from services.simulator import generate_mock_ransomware_telemetry, generate_benign_telemetry
from services.fusion import fusion_engine

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Ransomware Behavior Analysis Sandbox API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EncryptedPayload(BaseModel):
    data: str # hex string of encrypted bytes

@app.post("/api/v1/telemetry/secure")
async def receive_secure_telemetry(payload: EncryptedPayload):
    """
    Secure Telemetry Collection Layer.
    Receives AES-256-GCM encrypted telemetry, decrypts it, and forwards to Fusion Engine.
    """
    try:
        encrypted_bytes = bytes.fromhex(payload.data)
        decrypted_bytes = decrypt_telemetry(encrypted_bytes)
        
        telemetry_dict = json.loads(decrypted_bytes.decode('utf-8'))
        telemetry = TelemetryPayload(**telemetry_dict)
        
        # Pass to Fusion Engine
        report = fusion_engine.analyze_session(telemetry)
        
        return {
            "status": "success", 
            "report": report,
            "raw_telemetry": telemetry_dict
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Telemetry processing failed: {str(e)}")


@app.get("/api/v1/simulate/ransomware")
async def simulate_ransomware():
    """
    Simulator Endpoint: Generates mock ransomware telemetry, encrypts it, 
    and simulates sending it to the secure endpoint.
    """
    telemetry = generate_mock_ransomware_telemetry()
    telemetry_json = telemetry.model_dump_json()
    
    # Encrypt for secure transmission
    encrypted_bytes = encrypt_telemetry(telemetry_json.encode('utf-8'))
    
    # In a real scenario, the sandbox would POST this to the server.
    # Here we just pass it to the handler directly for demonstration.
    payload = EncryptedPayload(data=encrypted_bytes.hex())
    return await receive_secure_telemetry(payload)


@app.get("/api/v1/simulate/benign")
async def simulate_benign():
    """
    Simulator Endpoint: Generates benign telemetry.
    """
    telemetry = generate_benign_telemetry()
    telemetry_json = telemetry.model_dump_json()
    encrypted_bytes = encrypt_telemetry(telemetry_json.encode('utf-8'))
    payload = EncryptedPayload(data=encrypted_bytes.hex())
    return await receive_secure_telemetry(payload)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
