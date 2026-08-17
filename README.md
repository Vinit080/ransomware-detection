# Ransomware Behavior Analysis Sandbox

An advanced, M.E. (Master of Engineering) level cybersecurity platform designed to securely analyze ransomware telemetry using a dual-engine architecture: Rule-based heuristics (YARA) and Generative AI with Retrieval-Augmented Generation (RAG).

## Features

- **Secure Telemetry Pipeline**: JSON telemetry payloads (Process, File, and Network events) are transmitted using AES-256-GCM encryption to ensure integrity and confidentiality.
- **Rule-Based Engine (YARA)**: Rapidly scans incoming telemetry for known indicators of compromise (IoCs) and ransomware behavioral heuristics (e.g., mass high-entropy file writes, VSS deletion).
- **Generative AI Engine (LangChain + OpenAI + ChromaDB)**:
  - **RAG (Retrieval-Augmented Generation)**: Leverages a local Chroma Vector Database seeded with threat intelligence to provide context to the LLM.
  - **Semantic Analysis**: Analyzes complex, obfuscated telemetry to explain the malware's intent and automatically map behaviors to the MITRE ATT&CK framework.
- **Fusion Engine**: Intelligently aggregates the findings from both the heuristic scanner and the LLM to calculate a final Risk Score and Classification.
- **Simulator Mode**: Includes a built-in telemetry simulator that generates highly realistic benign and ransomware behaviors for testing the pipeline without needing a live hypervisor setup.

## Architecture

```text
                 Simulator (Generates Telemetry)
                              │
                    AES-256-GCM Encryption
                              ▼
                 Secure Telemetry Collection API
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
      Rule-Based Engine                 GenAI Engine
       (YARA Python)                 (OpenAI + ChromaDB)
              │                               │
              └───────────────┬───────────────┘
                              ▼
                        Fusion Engine
                    (Risk Scoring & MITRE)
```

## Setup & Installation

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Add your OpenAI API key to the `.env` file:
   ```env
   OPENAI_API_KEY=your_key_here
   TELEMETRY_AES_KEY=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
   CHROMA_DB_DIR=./chroma_db
   ```

3. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

4. Test the pipeline via the interactive docs:
   Visit `http://127.0.0.1:8000/docs` in your browser.
